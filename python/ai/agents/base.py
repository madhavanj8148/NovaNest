"""
NovaNest Domain Agents - Shared Execution Base, Scoped SQL Sandbox & Helpers
---------------------------------------------------------------------------
Provides `BaseDomainAgent` and shared helpers reused across the five Phase 06.2
domain intelligence agents:
- FinancialAgent
- CustomerAgent
- OperationsAgent
- RestaurantAgent
- DecisionAgent

Guarantees every agent enforces:
- Strict principal isolation and RBAC scope checks before data access
- Narrow per-agent SQL table ACLs (`validate_sql_ast` + scoped RO SQLite)
- Least-privilege dataset slicing per agent
- Deterministic `OutputVerifier` grounding over emitted `summary` & `narrative`
- Structured `ExecutionTracer` spans and bounded `AgentContext` history
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from functools import lru_cache
import json
import math
from pathlib import Path
import re
import sys
import time
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import pandas as pd

from python.ai.agents.context import (
    AgentContext,
    AgentExecutionHistoryEntry,
    KpiDefinitionEntry,
    extract_dataset_metadata_from_frames,
    load_certified_kpi_entries,
)
from python.ai.agents.contracts import (
    AgentDomain,
    AgentError,
    AgentExecutionMetadata,
    AgentRequest,
    AgentResult,
    AgentStatus,
    DataProvenance,
    GroundedFact,
    ModelCaveat,
    SeverityLevel,
    SqlAuditTrace,
    neutralize_untrusted_text,
    sanitize_text,
    utc_now,
)
from python.ai.agents.output_verifier import OutputVerifier, VerificationOutcome
from python.ai.agents.registry import AgentAvailability, AgentRegistration, AgentRegistry
from python.ai.agents.tracing import ExecutionTracer, TraceVerificationOutcome
from python.ai.analyst.sql_agent import (
    DATASET_TO_SQLITE_TABLE_MAP,
    build_readonly_sqlite_connection,
    execute_safe_sql,
)
from python.ai.analyst.sql_ast import MAX_ROW_LIMIT, validate_sql_ast


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PYTHON_DIR = PROJECT_ROOT / "python"
MODELS_DIR = PROJECT_ROOT / "models"


def ensure_python_path() -> None:
    """Ensure repository root and `python/` directory are importable for bare internal imports."""
    for candidate in (str(PROJECT_ROOT), str(PYTHON_DIR)):
        if candidate not in sys.path:
            sys.path.insert(0, candidate)


@lru_cache(maxsize=16)
def load_model_v2_json(relative_path: str) -> Dict[str, Any]:
    """Load Phase 05 v2 model validation JSON safely without mutating artifacts."""
    path = MODELS_DIR / relative_path
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def load_model_active_metadata(model_name: str) -> Dict[str, Any]:
    """Load active version metadata from ModelRegistry with honest confidence tier."""
    try:
        from python.ml.model_registry import model_registry
        _, meta = model_registry.load_active_model(model_name)
        return meta
    except Exception:
        # Fallback to legacy v2
        return load_model_v2_json(f"{model_name}/model_metadata.json")


def make_model_caveat_from_registry(model_name: str, domain: str) -> ModelCaveat:
    """Construct verified ModelCaveat enforcing honest confidence gating."""
    meta = load_model_active_metadata(model_name)
    tier = meta.get("confidence_tier", "LOW_EMPIRICAL")
    caveat = meta.get("confidence_caveat", "Empirical validation indicates synthetic data bounds.")
    ver = meta.get("version", "v3")
    algo = meta.get("algorithm", "Unknown")
    metrics = meta.get("evaluation_metrics", {})

    metric_summary_parts = [f"Version: {ver}", f"Algo: {algo}"]
    if "best_model_metrics" in metrics:
        bm = metrics["best_model_metrics"]
        if "roc_auc" in bm and bm["roc_auc"] is not None:
            metric_summary_parts.append(f"ROC-AUC: {bm['roc_auc']}")
        if "mae" in bm and bm["mae"] is not None:
            metric_summary_parts.append(f"MAE: {bm['mae']}")
        if "r2_score" in bm and bm["r2_score"] is not None:
            metric_summary_parts.append(f"R²: {bm['r2_score']}")
    metric_str = ", ".join(metric_summary_parts)[:290]

    return ModelCaveat(
        model_name=f"{model_name} ({ver})",
        domain=domain,
        validation_status=f"PHASE_07_{tier}",
        metric_summary=metric_str,
        warning=caveat[:490],
        is_production_ready=(tier == "HIGH"),
    )


@lru_cache(maxsize=1)
def get_certified_kpi_catalog() -> Dict[str, KpiDefinitionEntry]:
    """Return cached certified KPI catalog keyed by `kpi_id`."""
    return load_certified_kpi_entries()


def safe_float(value: Any, default: float = 0.0) -> float:
    """Convert scalar to finite float, falling back safely on None/NaN/Inf."""
    try:
        num = float(value)
        return num if math.isfinite(num) else default
    except (TypeError, ValueError):
        return default


def safe_round(value: Any, digits: int = 2, default: float = 0.0) -> float:
    """Round a scalar safely to `digits` decimals if finite."""
    return round(safe_float(value, default=default), digits)


def sanitize_scalar(val: Any) -> Any:
    """Convert numpy/pandas/timestamp scalars cleanly to redacted JSON-safe primitives."""
    if val is None:
        return None
    if isinstance(val, bool):
        return val
    if hasattr(val, "item") and callable(getattr(val, "item")):
        try:
            val = val.item()
        except Exception:
            pass
    if isinstance(val, (int,)):
        return int(val)
    if isinstance(val, float):
        if not math.isfinite(val):
            return None
        return round(val, 4)
    if isinstance(val, (pd.Timestamp,)):
        return val.isoformat()
    if pd.isna(val):
        return None
    if isinstance(val, str):
        return neutralize_untrusted_text(val)
    return neutralize_untrusted_text(str(val))


def sanitize_table_rows(rows: Iterable[Dict[str, Any]], max_rows: int = 100) -> List[Dict[str, Any]]:
    """Sanitize and clamp structured row dicts for safe inclusion in `AgentResult.table_rows`."""
    cleaned: List[Dict[str, Any]] = []
    for idx, row in enumerate(rows):
        if idx >= max_rows:
            break
        if not isinstance(row, dict):
            continue
        cleaned.append({str(k): sanitize_scalar(v) for k, v in row.items()})
    return cleaned


def df_to_table_rows(df: Optional[pd.DataFrame], max_rows: int = 25) -> List[Dict[str, Any]]:
    """Convert a DataFrame slice safely to bounded JSON-safe dicts."""
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return []
    return sanitize_table_rows(df.head(max_rows).to_dict(orient="records"), max_rows=max_rows)


def filter_df_by_city(df: Optional[pd.DataFrame], city: Optional[str]) -> pd.DataFrame:
    """Filter a DataFrame by `city` / `City` / `restaurant_city` / `order_city` case-insensitively."""
    if df is None or not isinstance(df, pd.DataFrame):
        return pd.DataFrame()
    if not city:
        return df
    target = str(city).strip().lower()
    if not target:
        return df
    for col in ("city", "City", "restaurant_city", "order_city", "customer_city"):
        if col in df.columns:
            mask = df[col].astype(str).str.strip().str.lower() == target
            return df.loc[mask].copy()
    return df


def extract_sql_from_request(request: AgentRequest) -> Optional[str]:
    """Extract optional explicit SQL query requested via filters or SQL intent."""
    raw = request.filters.get("sql_query") or request.filters.get("sql")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    if (request.intent or "").strip().lower() == "sql":
        candidate = request.user_query.strip()
        if re.match(r"^(?:select|with)\b", candidate, re.IGNORECASE):
            return candidate
    return None


def run_scoped_sql(
    sql: str,
    data: Dict[str, pd.DataFrame],
    allowed_tables: Sequence[str],
    *,
    timeout_seconds: float = 2.0,
    max_rows: int = MAX_ROW_LIMIT,
) -> Tuple[Optional[SqlAuditTrace], List[Dict[str, Any]], Optional[AgentError]]:
    """
    Execute an optional read-only SQL query under strict AST table ACL validation
    and an ephemeral SQLite sandbox populated ONLY with `allowed_tables`.
    """
    allowed_set = {t.strip().lower() for t in allowed_tables if str(t).strip()}
    is_valid, sanitized_sql, msg = validate_sql_ast(
        sql=sql,
        allowed_tables=allowed_set,
        max_row_limit=min(max_rows, MAX_ROW_LIMIT),
        default_row_limit=25,
    )
    if not is_valid:
        return (
            None,
            [],
            AgentError(
                code="SQL_PERMISSION_DENIED",
                message=msg,
                recoverable=True,
                severity=SeverityLevel.WARNING,
            ),
        )

    scoped_data: Dict[str, pd.DataFrame] = {}
    for dataset_key, meta in DATASET_TO_SQLITE_TABLE_MAP.items():
        sqlite_tbl = meta["sqlite_table"].lower()
        if sqlite_tbl in allowed_set or dataset_key.lower() in allowed_set:
            frame = data.get(dataset_key)
            if isinstance(frame, pd.DataFrame) and not frame.empty:
                scoped_data[dataset_key] = frame

    conn = None
    t0 = time.monotonic()
    try:
        conn = build_readonly_sqlite_connection(scoped_data)
        df_res, exec_msg = execute_safe_sql(
            sanitized_sql,
            conn,
            timeout_seconds=timeout_seconds,
            max_rows=min(max_rows, MAX_ROW_LIMIT),
        )
    except Exception as exc:
        return (
            None,
            [],
            AgentError(
                code="SQL_EXECUTION_ERROR",
                message=f"Scoped SQL execution failed: {sanitize_text(str(exc))}",
                recoverable=True,
                severity=SeverityLevel.ERROR,
            ),
        )
    finally:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass

    elapsed_ms = round(max(0.0, (time.monotonic() - t0) * 1000.0), 3)
    if df_res is None:
        return (
            None,
            [],
            AgentError(
                code="SQL_EXECUTION_REJECTED",
                message=sanitize_text(exec_msg or "SQL query returned no result."),
                recoverable=True,
                severity=SeverityLevel.WARNING,
            ),
        )

    tables_used = [
        tbl
        for tbl in sorted(allowed_set)
        if re.search(rf"\b{re.escape(tbl)}\b", sanitized_sql, re.IGNORECASE)
    ]
    rows = df_to_table_rows(df_res, max_rows=min(max_rows, MAX_ROW_LIMIT))
    trace = SqlAuditTrace(
        sql=sanitized_sql,
        tables_accessed=tables_used,
        row_count=len(rows),
        execution_ms=elapsed_ms,
        validated_by_ast=True,
    )
    return trace, rows, None


def safe_compute_all_kpis(data: Dict[str, pd.DataFrame]) -> Optional[Dict[str, Dict[str, Any]]]:
    """
    Invoke `python.analytics.kpi_engine.compute_all_kpis` safely when core order columns
    exist, returning a `kpi_id -> dict` mapping or `None` if source data is incomplete.
    """
    ensure_python_path()
    orders = data.get("orders")
    if orders is None or not isinstance(orders, pd.DataFrame) or orders.empty:
        return None
    required_order_cols = {"order_id", "customer_id", "restaurant_id", "order_amount", "final_amount", "order_status"}
    if not required_order_cols.issubset(set(orders.columns)):
        return None

    deliveries = data.get("deliveries")
    restaurants = data.get("restaurants")
    riders = data.get("riders")
    customers = data.get("customers")
    orders_eng = data.get("orders_engineered")

    if any(
        df is None or not isinstance(df, pd.DataFrame) or df.empty
        for df in (deliveries, restaurants, riders, customers, orders_eng)
    ):
        return None

    try:
        from python.analytics.kpi_engine import compute_all_kpis

        raw_list = compute_all_kpis(orders, deliveries, restaurants, riders, customers, orders_eng)
        return {item["kpi_id"]: item for item in raw_list if isinstance(item, dict) and "kpi_id" in item}
    except Exception:
        return None


def make_provenance(
    source_name: str,
    dataset_or_table: str,
    df: Optional[pd.DataFrame],
    *,
    source_type: str = "csv",
    filters_applied: Optional[List[str]] = None,
    is_confirmed_loss: Optional[bool] = None,
) -> DataProvenance:
    """Construct a `DataProvenance` record cleanly from an observed DataFrame or artifact."""
    row_count = int(len(df)) if isinstance(df, pd.DataFrame) else None
    return DataProvenance(
        source_name=source_name,
        source_type=source_type,
        dataset_or_table=dataset_or_table,
        row_count=row_count,
        filters_applied=filters_applied or [],
        is_confirmed_loss=is_confirmed_loss,
    )


def map_verification_to_trace(outcome: VerificationOutcome) -> TraceVerificationOutcome:
    """Translate OutputVerifier outcome enum into ExecutionTracer verification enum."""
    if outcome == VerificationOutcome.VERIFIED:
        return TraceVerificationOutcome.VERIFIED
    if outcome == VerificationOutcome.PARTIAL:
        return TraceVerificationOutcome.PARTIAL
    return TraceVerificationOutcome.REJECTED


class BaseDomainAgent(ABC):
    """
    Abstract base class enforcing NovaNest Phase 06.1 security, RBAC, tracing,
    table-ACL, and deterministic output verification guarantees for every Phase 06.2 agent.
    """

    AGENT_ID: str = "base_domain_agent"
    DOMAIN: AgentDomain = AgentDomain.GENERAL
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "NovaNest domain intelligence agent."
    CAPABILITIES: Tuple[str, ...] = ()
    SUPPORTED_INTENTS: Tuple[str, ...] = ()
    ALLOWED_TABLES: Tuple[str, ...] = ()
    ALLOWED_DATASETS: Tuple[str, ...] = ()
    REQUIRED_SCOPES: Tuple[str, ...] = ("read",)
    DEFAULT_TIMEOUT_SECONDS: float = 5.0

    def __init__(self, *, strict_verification: bool = True) -> None:
        self._strict_verification = strict_verification

    @property
    def registration(self) -> AgentRegistration:
        """Build the operational `AgentRegistration` descriptor for `AgentRegistry`."""
        return AgentRegistration(
            agent_id=self.AGENT_ID,
            domain=self.DOMAIN,
            version=self.VERSION,
            description=self.DESCRIPTION,
            capabilities=list(self.CAPABILITIES),
            supported_intents=list(self.SUPPORTED_INTENTS),
            input_contract=AgentRequest,
            output_contract=AgentResult,
            allowed_tables=list(self.ALLOWED_TABLES),
            required_scopes=list(self.REQUIRED_SCOPES),
            availability=AgentAvailability.OPERATIONAL,
            is_implemented=True,
            timeout_seconds=self.DEFAULT_TIMEOUT_SECONDS,
        )

    def register_into(self, registry: AgentRegistry, overwrite: bool = True) -> AgentRegistration:
        """Register this agent and its `.execute` handler into `registry`."""
        return registry.register(self.registration, handler=self.execute, overwrite=overwrite)

    def _build_terminal_result(
        self,
        request: AgentRequest,
        *,
        status: AgentStatus,
        code: str,
        message: str,
        severity: SeverityLevel = SeverityLevel.WARNING,
        started_at: Any = None,
        t0: float = 0.0,
        timed_out: bool = False,
        cancelled: bool = False,
    ) -> AgentResult:
        elapsed_ms = round(max(0.0, (time.monotonic() - t0) * 1000.0), 3) if t0 else 0.0
        err = AgentError(
            code=code,
            message=sanitize_text(message),
            agent_id=self.AGENT_ID,
            recoverable=(status != AgentStatus.BLOCKED),
            severity=severity,
        )
        return AgentResult(
            request_id=request.request_id,
            execution_id=request.execution_id,
            agent_id=self.AGENT_ID,
            domain=self.DOMAIN,
            status=status,
            summary=err.message,
            errors=[err],
            execution=AgentExecutionMetadata(
                request_id=request.request_id,
                execution_id=request.execution_id,
                agent_id=self.AGENT_ID,
                agent_version=self.VERSION,
                started_at_utc=started_at or utc_now(),
                finished_at_utc=utc_now(),
                elapsed_ms=elapsed_ms,
                timed_out=timed_out,
                cancelled=cancelled,
            ),
        )

    def _finalize_observability(
        self,
        result: AgentResult,
        context: AgentContext,
        tracer: Optional[ExecutionTracer],
        span_id: Optional[str],
        verification_outcome: TraceVerificationOutcome,
        verification_notes: Optional[List[str]] = None,
    ) -> None:
        """Record execution telemetry onto both `AgentContext` and optional `ExecutionTracer`."""
        elapsed = result.execution.elapsed_ms if result.execution else 0.0
        try:
            context.record_execution_step(
                AgentExecutionHistoryEntry(
                    agent_id=self.AGENT_ID,
                    domain=self.DOMAIN,
                    status=result.status,
                    elapsed_ms=elapsed,
                    summary=result.summary[:240] if result.summary else "",
                )
            )
        except PermissionError:
            pass
        if tracer is not None and span_id is not None:
            tracer.record_agent_result(
                span_id,
                result,
                verification_outcome=verification_outcome,
                verification_notes=verification_notes or [],
            )

    def execute(
        self,
        request: AgentRequest,
        context: AgentContext,
        *,
        data: Optional[Dict[str, pd.DataFrame]] = None,
        tracer: Optional[ExecutionTracer] = None,
        verifier: Optional[OutputVerifier] = None,
        principal_scopes: Optional[Sequence[str]] = None,
    ) -> AgentResult:
        """
        Validate identity/RBAC/ACL/lifecycle constraints, slice authorized datasets,
        execute domain analysis, verify numerical grounding, and emit traced `AgentResult`.
        """
        started_at = utc_now()
        t0 = time.monotonic()

        span_id: Optional[str] = None
        if tracer is not None:
            tracer.start_trace(
                request_id=request.request_id,
                principal_id=context.principal_id,
                session_id=context.session_id,
            )
            span_id = tracer.start_span(
                request_id=request.request_id,
                agent_id=self.AGENT_ID,
                domain=self.DOMAIN,
                metadata={"intent": request.intent or "general"},
            )

        # 1. Principal isolation check
        try:
            context.assert_principal(request.principal_id)
        except PermissionError as exc:
            res = self._build_terminal_result(
                request,
                status=AgentStatus.BLOCKED,
                code="PRINCIPAL_ISOLATION_VIOLATION",
                message=str(exc),
                severity=SeverityLevel.CRITICAL,
                started_at=started_at,
                t0=t0,
            )
            self._finalize_observability(res, context, tracer, span_id, TraceVerificationOutcome.REJECTED)
            return res

        # 2. Agent target validation
        if request.agent_id != self.AGENT_ID:
            res = self._build_terminal_result(
                request,
                status=AgentStatus.BLOCKED,
                code="AGENT_ID_MISMATCH",
                message=f"Request targeted '{request.agent_id}', cannot execute on '{self.AGENT_ID}'.",
                severity=SeverityLevel.WARNING,
                started_at=started_at,
                t0=t0,
            )
            self._finalize_observability(res, context, tracer, span_id, TraceVerificationOutcome.REJECTED)
            return res

        # 3. Cooperative cancellation & deadline checks
        if context.is_cancelled():
            res = self._build_terminal_result(
                request,
                status=AgentStatus.CANCELLED,
                code="EXECUTION_CANCELLED",
                message="Request cancelled prior to domain execution.",
                severity=SeverityLevel.INFO,
                started_at=started_at,
                t0=t0,
                cancelled=True,
            )
            self._finalize_observability(res, context, tracer, span_id, TraceVerificationOutcome.NOT_RUN)
            return res

        if context.is_expired():
            res = self._build_terminal_result(
                request,
                status=AgentStatus.TIMEOUT,
                code="EXECUTION_TIMEOUT",
                message="Request deadline expired prior to domain execution.",
                severity=SeverityLevel.ERROR,
                started_at=started_at,
                t0=t0,
                timed_out=True,
            )
            self._finalize_observability(res, context, tracer, span_id, TraceVerificationOutcome.NOT_RUN)
            return res

        # 4. RBAC scope authorization
        effective_scopes = (
            {str(s).strip().lower() for s in principal_scopes if str(s).strip()}
            if principal_scopes is not None
            else set(context.principal_scopes)
        )
        needed_scopes = {s.lower() for s in self.REQUIRED_SCOPES} | {s.lower() for s in request.required_scopes}
        missing_scopes = sorted(s for s in needed_scopes if s not in effective_scopes)
        if missing_scopes:
            res = self._build_terminal_result(
                request,
                status=AgentStatus.BLOCKED,
                code="RBAC_SCOPE_DENIED",
                message=f"Insufficient scopes for '{self.AGENT_ID}': missing {missing_scopes}.",
                severity=SeverityLevel.ERROR,
                started_at=started_at,
                t0=t0,
            )
            self._finalize_observability(res, context, tracer, span_id, TraceVerificationOutcome.REJECTED)
            return res

        # 5. SQL Table ACL enforcement
        permitted_tables = set(self.ALLOWED_TABLES)
        requested_tables_raw = list(request.allowed_tables)
        extra_req = request.filters.get("requested_tables")
        if isinstance(extra_req, (list, tuple, set)):
            requested_tables_raw.extend(str(t) for t in extra_req)
        unauthorized_tables = sorted(
            {t.strip().lower() for t in requested_tables_raw if str(t).strip()} - permitted_tables
        )
        if unauthorized_tables:
            res = self._build_terminal_result(
                request,
                status=AgentStatus.BLOCKED,
                code="TABLE_ACL_DENIED",
                message=(
                    f"Unauthorized SQL table(s) requested for '{self.AGENT_ID}': {unauthorized_tables}. "
                    f"Permitted: {sorted(permitted_tables)}."
                ),
                severity=SeverityLevel.ERROR,
                started_at=started_at,
                t0=t0,
            )
            self._finalize_observability(res, context, tracer, span_id, TraceVerificationOutcome.REJECTED)
            return res

        # 6. Load data cleanly and slice strictly to permitted datasets
        try:
            ensure_python_path()
            if data is None:
                from api.loader import load_data

                full_data, data_source_label = load_data()
            elif isinstance(data, dict):
                full_data = data
                data_source_label = "Supplied In-Memory Store"
            else:
                res = self._build_terminal_result(
                    request,
                    status=AgentStatus.ERROR,
                    code="INVALID_DATA_STORE",
                    message="Supplied `data` store must be a dictionary of DataFrames.",
                    severity=SeverityLevel.ERROR,
                    started_at=started_at,
                    t0=t0,
                )
                self._finalize_observability(res, context, tracer, span_id, TraceVerificationOutcome.REJECTED)
                return res

            scoped_data: Dict[str, pd.DataFrame] = {}
            for ds_name in self.ALLOWED_DATASETS:
                candidate = full_data.get(ds_name)
                if candidate is None:
                    continue
                if not isinstance(candidate, pd.DataFrame):
                    res = self._build_terminal_result(
                        request,
                        status=AgentStatus.ERROR,
                        code="INVALID_DATASET_TYPE",
                        message=f"Dataset '{ds_name}' must be a pandas DataFrame, got {type(candidate).__name__}.",
                        severity=SeverityLevel.ERROR,
                        started_at=started_at,
                        t0=t0,
                    )
                    self._finalize_observability(res, context, tracer, span_id, TraceVerificationOutcome.REJECTED)
                    return res
                scoped_data[ds_name] = candidate

            for meta_entry in extract_dataset_metadata_from_frames(scoped_data).values():
                try:
                    context.register_dataset_metadata(meta_entry)
                except ValueError:
                    break

            # 7. Optional scoped SQL path
            sql_query = extract_sql_from_request(request)
            sql_trace: Optional[SqlAuditTrace] = None
            sql_rows: List[Dict[str, Any]] = []
            if sql_query is not None:
                effective_tables = (
                    [t for t in request.allowed_tables if t in permitted_tables]
                    if request.allowed_tables
                    else list(self.ALLOWED_TABLES)
                )
                sql_trace, sql_rows, sql_err = run_scoped_sql(
                    sql_query,
                    scoped_data,
                    effective_tables,
                    timeout_seconds=min(2.0, request.timeout_seconds),
                )
                if sql_err is not None:
                    res = AgentResult(
                        request_id=request.request_id,
                        execution_id=request.execution_id,
                        agent_id=self.AGENT_ID,
                        domain=self.DOMAIN,
                        status=AgentStatus.BLOCKED
                        if sql_err.code == "SQL_PERMISSION_DENIED"
                        else AgentStatus.ERROR,
                        summary=sql_err.message,
                        errors=[
                            AgentError(
                                code=sql_err.code,
                                message=sql_err.message,
                                agent_id=self.AGENT_ID,
                                recoverable=sql_err.recoverable,
                                severity=sql_err.severity,
                            )
                        ],
                        execution=AgentExecutionMetadata(
                            request_id=request.request_id,
                            execution_id=request.execution_id,
                            agent_id=self.AGENT_ID,
                            agent_version=self.VERSION,
                            started_at_utc=started_at,
                            finished_at_utc=utc_now(),
                            elapsed_ms=round(max(0.0, (time.monotonic() - t0) * 1000.0), 3),
                        ),
                    )
                    self._finalize_observability(res, context, tracer, span_id, TraceVerificationOutcome.REJECTED)
                    return res

            # 8. Execute domain specialization
            result = self._run_domain(
                request=request,
                context=context,
                data=scoped_data,
                data_source_label=data_source_label,
                sql_trace=sql_trace,
                sql_rows=sql_rows,
            )

        except Exception as exc:
            res = self._build_terminal_result(
                request,
                status=AgentStatus.ERROR,
                code="DOMAIN_EXECUTION_ERROR",
                message=f"Unexpected error in '{self.AGENT_ID}': {exc}",
                severity=SeverityLevel.ERROR,
                started_at=started_at,
                t0=t0,
            )
            self._finalize_observability(res, context, tracer, span_id, TraceVerificationOutcome.REJECTED)
            return res

        # 9. Verify numerical grounding & compliance via OutputVerifier
        active_verifier = verifier or OutputVerifier(load_default_kpis=True)
        prose_to_verify = "\n".join(p for p in (result.summary, result.narrative) if p and p.strip())
        report = active_verifier.verify(
            prose_to_verify,
            facts=result.facts,
            agent_results=[result],
            include_kpi_catalog=True,
        )
        trace_ver_outcome = map_verification_to_trace(report.outcome)
        ver_notes = [f"{v.code}: {v.message}" for v in report.violations]

        if self._strict_verification and report.outcome == VerificationOutcome.REJECTED:
            err_msg = "; ".join(ver_notes) or "Output verification rejected ungrounded claims."
            result = result.model_copy(
                update={
                    "status": AgentStatus.ERROR,
                    "errors": list(result.errors)
                    + [
                        AgentError(
                            code="OUTPUT_VERIFICATION_FAILED",
                            message=sanitize_text(err_msg),
                            agent_id=self.AGENT_ID,
                            recoverable=False,
                            severity=SeverityLevel.ERROR,
                        )
                    ],
                }
            )

        elapsed_ms = round(max(0.0, (time.monotonic() - t0) * 1000.0), 3)
        final_result = result.model_copy(
            update={
                "execution": AgentExecutionMetadata(
                    request_id=request.request_id,
                    execution_id=request.execution_id,
                    agent_id=self.AGENT_ID,
                    agent_version=self.VERSION,
                    started_at_utc=started_at,
                    finished_at_utc=utc_now(),
                    elapsed_ms=elapsed_ms,
                    timed_out=(result.status == AgentStatus.TIMEOUT),
                    cancelled=(result.status == AgentStatus.CANCELLED),
                )
            }
        )
        self._finalize_observability(
            final_result,
            context,
            tracer,
            span_id,
            trace_ver_outcome,
            verification_notes=ver_notes,
        )
        return final_result

    @abstractmethod
    def _run_domain(
        self,
        *,
        request: AgentRequest,
        context: AgentContext,
        data: Dict[str, pd.DataFrame],
        data_source_label: str,
        sql_trace: Optional[SqlAuditTrace],
        sql_rows: List[Dict[str, Any]],
    ) -> AgentResult:
        """Compute grounded domain metrics, provenance, caveats, and summary."""


__all__ = [
    "BaseDomainAgent",
    "MODELS_DIR",
    "PROJECT_ROOT",
    "PYTHON_DIR",
    "df_to_table_rows",
    "ensure_python_path",
    "extract_sql_from_request",
    "filter_df_by_city",
    "get_certified_kpi_catalog",
    "load_model_active_metadata",
    "load_model_v2_json",
    "make_model_caveat_from_registry",
    "make_provenance",
    "run_scoped_sql",
    "safe_compute_all_kpis",
    "safe_float",
    "safe_round",
    "sanitize_scalar",
    "sanitize_table_rows",
]
