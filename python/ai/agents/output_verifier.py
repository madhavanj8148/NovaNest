"""
NovaNest Multi-Agent Foundation - Deterministic Numeric & Grounding OutputVerifier
----------------------------------------------------------------------------------
Verifies candidate narratives and agent results against certified KPI definitions,
grounded numerical facts, structured SQL/analytics table rows, and provenance rules.

Enforcement Guarantees:
1. Matches currency (INR, Cr, Lakhs, international & Indian commas), percentages,
   counts, and durations within explicit precision-aware tolerances.
2. Flags unsupported / fabricated numbers not traceable to supplied evidence.
3. Detects conflicting numeric claims across multiple AgentResult objects.
4. Flags missing/blocked source data and incomplete coverage honestly.
5. Never converts unconfirmed financial screening risks (`is_confirmed_loss=False`,
   `revenue_leakage`) into confirmed losses.
"""

from __future__ import annotations

from enum import Enum
import math
import re
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field

from python.ai.agents.context import KpiDefinitionEntry, load_certified_kpi_entries
from python.ai.agents.contracts import AgentResult, AgentStatus, GroundedFact, sanitize_text
from python.ai.analyst.sql_ast import ALLOWED_TABLES


class VerificationOutcome(str, Enum):
    VERIFIED = "verified"
    PARTIAL = "partial"
    REJECTED = "rejected"


class VerificationSeverity(str, Enum):
    WARNING = "warning"
    CRITICAL = "critical"


class ExtractedClaim(BaseModel):
    """Numeric claim extracted from candidate narrative text."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    raw_text: str
    normalized_value: float
    kind: str  # "currency", "percentage", "scalar"
    unit_scale: str = "unit"  # "cr", "lakh", "k", "pct", "unit"
    decimals: int = 0
    matched_evidence: Optional[str] = None
    is_supported: bool = False


class VerificationViolation(BaseModel):
    """Specific verification failure or safety rule breach."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    message: str
    severity: VerificationSeverity = VerificationSeverity.CRITICAL
    raw_claim: Optional[str] = None
    expected_reference: Optional[str] = None


class ConflictDetail(BaseModel):
    """Detected disagreement between two agent outputs on the same metric/KPI."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    metric_key: str
    agent_a: str
    value_a: float
    agent_b: str
    value_b: float


class VerificationReport(BaseModel):
    """Structured audit report returned by `OutputVerifier.verify(...)`."""

    model_config = ConfigDict(extra="forbid")

    outcome: VerificationOutcome
    is_verified: bool
    checked_claims: List[ExtractedClaim] = Field(default_factory=list)
    supported_claims_count: int = 0
    unsupported_claims: List[str] = Field(default_factory=list)
    violations: List[VerificationViolation] = Field(default_factory=list)
    conflicts: List[ConflictDetail] = Field(default_factory=list)
    missing_data_flags: List[str] = Field(default_factory=list)
    unconfirmed_loss_preserved: bool = True


# Strip benign structural tokens (bullets, KPI IDs, version tags, dates) before numeric extraction
_BULLET_PREFIX_RE = re.compile(r"(?m)^\s*\d+[\.\)]\s+")
_STRUCTURAL_TOKEN_RE = re.compile(
    r"\b(?:KPI-\d+|Phase\s+\d+(?:\.\d+)?|v\d+(?:\.\d+)*|\d{4}-\d{2}-\d{2}|"
    r"Month\s+\d+|Wave\s+\d+|Page\s+\d+(?:/\d+)?|C360)\b",
    re.IGNORECASE,
)
_NUMBER_IN_PROSE_RE = re.compile(
    r"(?P<currency>₹|INR\s*|Rs\.?\s*)?"
    r"(?P<num>-?\d+(?:,\d{2,3})*(?:\.\d+)?|-?\d+(?:\.\d+)?)"
    r"(?:\s*(?P<suffix>Cr\b|Crore\b|Crores\b|L\b|Lakh\b|Lakhs\b|K\b|%))?",
    re.IGNORECASE,
)

# Detect confirmed-loss wording on screening/leakage statements
_CONFIRMED_LOSS_RE = re.compile(
    r"\b(?:confirmed\s+(?:net\s+)?(?:financial\s+|revenue\s+)?loss|"
    r"verified\s+(?:net\s+)?(?:financial\s+|revenue\s+)?loss|"
    r"proven\s+(?:net\s+|financial\s+|revenue\s+)?loss|"
    r"guaranteed\s+(?:net\s+|financial\s+|revenue\s+)?loss|"
    r"definitely\s+lost|"
    r"(?:actual\s+)?realized\s+(?:financial\s+|revenue\s+)?loss)\b",
    re.IGNORECASE,
)
_NEGATION_OR_SCREENING_PREFIX_RE = re.compile(
    r"(?:not\s+(?:a\s+)?|unconfirmed|no\s+|without\s+|never\s+|is_confirmed_loss\s*=\s*false|"
    r"potential|candidate|screening)\s*$",
    re.IGNORECASE,
)
_LEAKAGE_MENTION_RE = re.compile(
    r"\b(?:leakage|promo|discount|subsidy|anomal|screening|unconfirmed)\b",
    re.IGNORECASE,
)

# Known NovaNest internal tables, engineered datasets, ML outputs, and analytics engines
_KNOWN_PROVENANCE_DATASETS = frozenset(
    set(ALLOWED_TABLES)
    | {
        "orders_table",
        "orders_engineered",
        "customer_churn_predictions",
        "restaurant_predictions",
        "operational_anomalies",
        "operational_alerts",
        "revenue_leakage",
        "sqlite",
        "digital_twin_engine",
        "analytics_engine",
        "kpi_definitions",
    }
)
_FABRICATED_SOURCE_PROSE_RE = re.compile(
    r"(?:source|provenance|from\s+table|dataset)\s*[:=]\s*['\"]?([a-zA-Z0-9_.\-]+(?:\.[a-zA-Z0-9_]+)?)",
    re.IGNORECASE,
)
_DISALLOWED_EXTERNAL_SOURCE_RE = re.compile(
    r"\b(?:sqlite_master|sqlite_schema|information_schema|pg_catalog|mysql\.user|"
    r"external_crm|oracle_dw|snowflake|salesforce|bloomberg|fabricated_\w+|unverified_\w+)\b",
    re.IGNORECASE,
)

# Experimental ML overclaim & missing caveat detection
_ML_OVERCLAIM_RE = re.compile(
    r"\b(?:production[- ]?ready|certified\s+(?:for\s+production|ml\s+model|predictor|forecast)|"
    r"100%\s+accurate|guaranteed\s+(?:accurate|forecast|prediction)|definitive\s+(?:ml\s+)?(?:forecast|prediction))\b",
    re.IGNORECASE,
)
_ML_TERM_RE = re.compile(
    r"\b(?:churn|eta\s+(?:model|prediction)|demand\s+forecast|restaurant\s+prediction|anomaly\s+detection|ml\s+model|machine\s+learning)\b",
    re.IGNORECASE,
)
_ML_PREDICTION_MENTION_RE = re.compile(
    r"\b(?:churn\s+probability|high\s+risk\s+churn|predicted\s+eta|demand\s+forecast|predicted\s+next[- ]month)\b",
    re.IGNORECASE,
)
_ML_DISCLAIMER_MARKER_RE = re.compile(
    r"(?:experimental|baseline_only|baseline\s+only|needs_more_data|not\s+production[- ]?ready|"
    r"production[- ]?ready\s*=\s*false|is_production_ready\s*=\s*false|directional|caveat|screening\s+only)",
    re.IGNORECASE,
)

# Explicit KPI definition inversions & KPI-ID mismatch checks
_KPI_DEF_CONTRA_RULES: List[Tuple[str, re.Pattern[str], str]] = [
    (
        "KPI-01",
        re.compile(
            r"\b(?:gmv|gross\s+merchandise\s+value)\b[^.!?\n]{0,80}\b(?:includes?\s+cancelled|with\s+cancelled\s+orders|uses?\s+final_amount)\b",
            re.IGNORECASE,
        ),
        "KPI-01 (GMV) excludes cancelled orders (`order_status != 'Cancelled'`) and sums `order_amount`.",
    ),
    (
        "KPI-02",
        re.compile(
            r"\bnet\s+revenue\b[^.!?\n]{0,80}\b(?:includes?\s+cancelled|before\s+discounts|ignores?\s+order_status|uses?\s+order_amount)\b",
            re.IGNORECASE,
        ),
        "KPI-02 (Net Revenue) sums `final_amount` strictly WHERE `order_status = 'Delivered'`.",
    ),
    (
        "KPI-04",
        re.compile(
            r"\btake\s+rate\b[^.!?\n]{0,80}(?:=|is|equals)\s*(?:net\s+revenue|realized\s+profit|total\s+profit)\s*/\s*gmv",
            re.IGNORECASE,
        ),
        "KPI-04 (Take Rate) is `(Total Commission Revenue / GMV) * 100`.",
    ),
]
_KPI_ID_VALUE_RE = re.compile(
    r"\b(?P<kpi>KPI-\d{2})\b[\s\)]*(?:is|are|was|were|reached|totals?|equals?|stands\s+at|=|:)\s*"
    r"(?P<claim>(?:₹|INR\s*|Rs\.?\s*)?-?\d+(?:,\d{2,3})*(?:\.\d+)?(?:\s*(?:Cr|Crores?|L|Lakhs?|K|%))?)",
    re.IGNORECASE,
)
_EMPTY_EVIDENCE_VALUES = frozenset({"", "n/a", "na", "none", "tbd", "unknown", "assumed", "placeholder"})


def _count_decimals(num_str: str) -> int:
    if "." not in num_str:
        return 0
    return len(num_str.split(".", 1)[1])


def _normalize_label(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")


def _extract_numeric_claims(text: str) -> List[ExtractedClaim]:
    """Extract currency, percentage, and scalar numeric claims while ignoring benign IDs/bullets."""
    if not text:
        return []

    masked = _BULLET_PREFIX_RE.sub(" ", text)
    masked = _STRUCTURAL_TOKEN_RE.sub(" ", masked)

    claims: List[ExtractedClaim] = []
    for m in _NUMBER_IN_PROSE_RE.finditer(masked):
        raw = m.group(0).strip()
        num_str = m.group("num")
        suffix = (m.group("suffix") or "").strip().lower()
        has_currency = bool(m.group("currency"))

        try:
            base_val = float(num_str.replace(",", ""))
        except ValueError:
            continue

        if not math.isfinite(base_val):
            continue

        # Ignore tiny ordinal/standalone single digits cleanly unless marked with %, currency, decimal, or scale
        is_plain_tiny = (
            not has_currency
            and not suffix
            and "." not in num_str
            and "," not in num_str
            and abs(base_val) < 10
        )
        if is_plain_tiny:
            continue

        decimals = _count_decimals(num_str)
        if suffix in ("cr", "crore", "crores"):
            norm = base_val * 1e7
            kind, scale = "currency", "cr"
        elif suffix in ("l", "lakh", "lakhs"):
            norm = base_val * 1e5
            kind, scale = "currency", "lakh"
        elif suffix == "k":
            norm = base_val * 1e3
            kind, scale = ("currency" if has_currency else "scalar"), "k"
        elif suffix == "%":
            norm = base_val
            kind, scale = "percentage", "pct"
        else:
            norm = base_val
            kind = "currency" if has_currency else "scalar"
            scale = "unit"

        claims.append(
            ExtractedClaim(
                raw_text=raw,
                normalized_value=norm,
                kind=kind,
                unit_scale=scale,
                decimals=decimals,
            )
        )
    return claims


def _scale_multiplier(scale: str) -> float:
    return {"cr": 1e7, "lakh": 1e5, "k": 1e3, "pct": 1.0, "unit": 1.0}.get(scale, 1.0)


def _claim_matches_reference(
    claim: ExtractedClaim,
    ref_value: float,
    rel_tol: float,
    abs_tol: float,
) -> bool:
    """
    Reconcile an extracted claim against a grounded reference value, accounting
    for unit scaling (e.g. INR <-> Cr/Lakhs) and decimal rounding precision.
    """
    mult = _scale_multiplier(claim.unit_scale)
    rounding_step = 0.5 * (10.0 ** (-claim.decimals)) * mult if claim.decimals > 0 or mult > 1.0 else 0.0
    effective_tol = max(abs(ref_value) * rel_tol, abs_tol, rounding_step + 1e-6)

    if abs(claim.normalized_value - ref_value) <= effective_tol:
        return True

    # Support ratio <-> percentage comparisons (e.g. fact stored as 0.0396 while prose states 3.96%)
    if claim.kind == "percentage" and 0.0 < abs(ref_value) <= 1.0:
        pct_tol = max(abs(ref_value * 100.0) * rel_tol, abs_tol, 0.5 * (10.0 ** (-claim.decimals)) + 1e-6)
        if abs(claim.normalized_value - (ref_value * 100.0)) <= pct_tol:
            return True

    return False


class _EvidenceItem:
    __slots__ = ("label", "value", "rel_tol", "abs_tol")

    def __init__(self, label: str, value: float, rel_tol: float, abs_tol: float) -> None:
        self.label = label
        self.value = value
        self.rel_tol = rel_tol
        self.abs_tol = abs_tol


class OutputVerifier:
    """
    Deterministic verification gate for multi-agent analytics and LLM-synthesized prose.
    Enforces KPI alignment, evidence provenance, conflict detection, missing-data reporting,
    and strict preservation of unconfirmed financial screening status.
    """

    def __init__(
        self,
        *,
        kpi_definitions: Optional[Dict[str, KpiDefinitionEntry]] = None,
        load_default_kpis: bool = True,
        default_rel_tolerance: float = 0.005,
        default_abs_tolerance: float = 0.01,
    ) -> None:
        if kpi_definitions is not None:
            self._kpis = dict(kpi_definitions)
        elif load_default_kpis:
            self._kpis = load_certified_kpi_entries()
        else:
            self._kpis = {}

        self._default_rel_tol = max(0.0, float(default_rel_tolerance))
        self._default_abs_tol = max(0.0, float(default_abs_tolerance))

    def _collect_evidence(
        self,
        *,
        facts: Optional[List[GroundedFact]],
        agent_results: Optional[List[AgentResult]],
        extra_metrics: Optional[Dict[str, float | int]],
        include_kpi_catalog: bool,
    ) -> Tuple[List[_EvidenceItem], bool]:
        evidence: List[_EvidenceItem] = []
        has_unconfirmed_leakage = False

        if include_kpi_catalog:
            for kpi_id, entry in self._kpis.items():
                if entry.value is not None:
                    evidence.append(
                        _EvidenceItem(
                            label=f"{kpi_id}:{entry.name}",
                            value=float(entry.value),
                            rel_tol=self._default_rel_tol,
                            abs_tol=self._default_abs_tol,
                        )
                    )

        for fact in facts or []:
            if fact.is_confirmed_loss is False:
                has_unconfirmed_leakage = True
            if isinstance(fact.value, (int, float)) and not isinstance(fact.value, bool):
                evidence.append(
                    _EvidenceItem(
                        label=f"fact:{fact.label}",
                        value=float(fact.value),
                        rel_tol=max(self._default_rel_tol, fact.tolerance_rel),
                        abs_tol=max(self._default_abs_tol, fact.tolerance_abs),
                    )
                )

        if extra_metrics:
            for k, v in extra_metrics.items():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    evidence.append(
                        _EvidenceItem(
                            label=f"metric:{k}",
                            value=float(v),
                            rel_tol=self._default_rel_tol,
                            abs_tol=self._default_abs_tol,
                        )
                    )

        for res in agent_results or []:
            if res.is_confirmed_loss is False:
                has_unconfirmed_leakage = True
            for prov in res.provenance:
                if prov.is_confirmed_loss is False:
                    has_unconfirmed_leakage = True
                if prov.row_count is not None:
                    evidence.append(
                        _EvidenceItem(
                            label=f"{res.agent_id}:row_count:{prov.source_name}",
                            value=float(prov.row_count),
                            rel_tol=0.0,
                            abs_tol=0.0,
                        )
                    )
            for fact in res.facts:
                if fact.is_confirmed_loss is False:
                    has_unconfirmed_leakage = True
                if isinstance(fact.value, (int, float)) and not isinstance(fact.value, bool):
                    evidence.append(
                        _EvidenceItem(
                            label=f"{res.agent_id}:{fact.label}",
                            value=float(fact.value),
                            rel_tol=max(self._default_rel_tol, fact.tolerance_rel),
                            abs_tol=max(self._default_abs_tol, fact.tolerance_abs),
                        )
                    )
            for k, v in res.metrics.items():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    evidence.append(
                        _EvidenceItem(
                            label=f"{res.agent_id}:{k}",
                            value=float(v),
                            rel_tol=self._default_rel_tol,
                            abs_tol=self._default_abs_tol,
                        )
                    )
            for idx, row in enumerate(res.table_rows):
                for col, cell in row.items():
                    if isinstance(cell, (int, float)) and not isinstance(cell, bool):
                        evidence.append(
                            _EvidenceItem(
                                label=f"{res.agent_id}:row[{idx}].{col}",
                                value=float(cell),
                                rel_tol=self._default_rel_tol,
                                abs_tol=self._default_abs_tol,
                            )
                        )
                    elif isinstance(cell, str) and cell:
                        for m in _NUMBER_IN_PROSE_RE.finditer(cell):
                            try:
                                val = float(m.group("num").replace(",", ""))
                                evidence.append(
                                    _EvidenceItem(
                                        label=f"{res.agent_id}:row[{idx}].{col}",
                                        value=val,
                                        rel_tol=self._default_rel_tol,
                                        abs_tol=self._default_abs_tol,
                                    )
                                )
                            except ValueError:
                                continue
            for rec in res.recommendations:
                if isinstance(rec.implementation_cost, (int, float)) and not isinstance(rec.implementation_cost, bool):
                    evidence.append(
                        _EvidenceItem(
                            label=f"{res.agent_id}:rec:{rec.recommendation_id}.cost",
                            value=float(rec.implementation_cost),
                            rel_tol=self._default_rel_tol,
                            abs_tol=self._default_abs_tol,
                        )
                    )
                if isinstance(rec.net_financial_impact, (int, float)) and not isinstance(rec.net_financial_impact, bool):
                    evidence.append(
                        _EvidenceItem(
                            label=f"{res.agent_id}:rec:{rec.recommendation_id}.impact",
                            value=float(rec.net_financial_impact),
                            rel_tol=self._default_rel_tol,
                            abs_tol=self._default_abs_tol,
                        )
                    )
                for rec_text in (rec.evidence, rec.expected_benefit, rec.action):
                    if rec_text:
                        for m in _NUMBER_IN_PROSE_RE.finditer(str(rec_text)):
                            try:
                                val = float(m.group("num").replace(",", ""))
                                evidence.append(
                                    _EvidenceItem(
                                        label=f"{res.agent_id}:rec:{rec.recommendation_id}",
                                        value=val,
                                        rel_tol=self._default_rel_tol,
                                        abs_tol=self._default_abs_tol,
                                    )
                                )
                            except ValueError:
                                continue
            for caveat in res.caveats:
                combined_caveat_text = f"{caveat.metric_summary} {caveat.warning}"
                for m in _NUMBER_IN_PROSE_RE.finditer(combined_caveat_text):
                    try:
                        val = float(m.group("num").replace(",", ""))
                        evidence.append(
                            _EvidenceItem(
                                label=f"caveat:{caveat.model_name}",
                                value=val,
                                rel_tol=self._default_rel_tol,
                                abs_tol=self._default_abs_tol,
                            )
                        )
                    except ValueError:
                        continue

        return evidence, has_unconfirmed_leakage

    def _detect_agent_conflicts(self, agent_results: List[AgentResult]) -> List[ConflictDetail]:
        """Compare shared KPI IDs and normalized metric/fact keys across distinct agents."""
        by_key: Dict[str, List[Tuple[str, float]]] = {}

        for res in agent_results:
            seen_for_agent: Dict[str, float] = {}
            for fact in res.facts:
                if not isinstance(fact.value, (int, float)) or isinstance(fact.value, bool):
                    continue
                canonical = f"kpi:{fact.kpi_id.upper()}" if fact.kpi_id else f"label:{_normalize_label(fact.label)}"
                seen_for_agent[canonical] = float(fact.value)
            for k, v in res.metrics.items():
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    seen_for_agent[f"metric:{_normalize_label(k)}"] = float(v)

            for key, val in seen_for_agent.items():
                by_key.setdefault(key, []).append((res.agent_id, val))

        conflicts: List[ConflictDetail] = []
        seen_pairs: set[Tuple[str, str, str]] = set()
        for key, items in by_key.items():
            if len(items) < 2:
                continue
            base_agent, base_val = items[0]
            for other_agent, other_val in items[1:]:
                if base_agent == other_agent:
                    continue
                tol = max(max(abs(base_val), abs(other_val)) * self._default_rel_tol, self._default_abs_tol)
                if abs(base_val - other_val) > tol:
                    sig = (key, base_agent, other_agent)
                    if sig not in seen_pairs:
                        seen_pairs.add(sig)
                        conflicts.append(
                            ConflictDetail(
                                metric_key=key,
                                agent_a=base_agent,
                                value_a=base_val,
                                agent_b=other_agent,
                                value_b=other_val,
                            )
                        )
        return conflicts

    def _check_unconfirmed_loss_framing(
        self,
        text: str,
        has_unconfirmed_leakage: bool,
    ) -> Optional[VerificationViolation]:
        """
        Fail closed if candidate text asserts unconfirmed screening risks/leakage
        as confirmed or guaranteed financial losses.
        """
        if not text:
            return None

        for match in _CONFIRMED_LOSS_RE.finditer(text):
            prefix_window = text[max(0, match.start() - 48) : match.start()]
            if _NEGATION_OR_SCREENING_PREFIX_RE.search(prefix_window):
                continue

            surrounding = text[max(0, match.start() - 120) : min(len(text), match.end() + 120)]
            if has_unconfirmed_leakage or _LEAKAGE_MENTION_RE.search(surrounding):
                return VerificationViolation(
                    code="UNCONFIRMED_LOSS_FRAMING",
                    message=(
                        "Candidate output presents unconfirmed screening leakage or promotional discount risk "
                        "as a confirmed financial loss (`is_confirmed_loss=False` invariant breached)."
                    ),
                    severity=VerificationSeverity.CRITICAL,
                    raw_claim=match.group(0),
                    expected_reference="is_confirmed_loss=False (investigation/screening candidate only)",
                )
        return None

    def _check_provenance(
        self,
        text: str,
        agent_results: List[AgentResult],
    ) -> List[VerificationViolation]:
        violations: List[VerificationViolation] = []
        for res in agent_results:
            for prov in res.provenance:
                if _DISALLOWED_EXTERNAL_SOURCE_RE.search(prov.source_name):
                    violations.append(
                        VerificationViolation(
                            code="FABRICATED_PROVENANCE",
                            message=f"Disallowed or external source '{prov.source_name}' cited by '{res.agent_id}'.",
                            severity=VerificationSeverity.CRITICAL,
                            raw_claim=prov.source_name,
                        )
                    )
                if prov.dataset_or_table and prov.source_type in ("csv", "sqlite", "mysql"):
                    parts = [p.strip().lower() for p in re.split(r"[,+]", prov.dataset_or_table) if p.strip()]
                    bad_parts = [p for p in parts if p not in _KNOWN_PROVENANCE_DATASETS]
                    if bad_parts:
                        violations.append(
                            VerificationViolation(
                                code="FABRICATED_PROVENANCE",
                                message=(
                                    f"Unknown/unauthorized provenance dataset/table(s) {bad_parts} "
                                    f"reported by '{res.agent_id}'."
                                ),
                                severity=VerificationSeverity.CRITICAL,
                                raw_claim=prov.dataset_or_table,
                            )
                        )

        if _DISALLOWED_EXTERNAL_SOURCE_RE.search(text):
            m = _DISALLOWED_EXTERNAL_SOURCE_RE.search(text)
            assert m is not None
            violations.append(
                VerificationViolation(
                    code="FABRICATED_PROVENANCE",
                    message=f"Candidate prose cites disallowed/fabricated source '{m.group(0)}'.",
                    severity=VerificationSeverity.CRITICAL,
                    raw_claim=m.group(0),
                )
            )
        else:
            for match in _FABRICATED_SOURCE_PROSE_RE.finditer(text):
                token = match.group(1).strip().lower()
                if (
                    token
                    and "." not in token
                    and token not in _KNOWN_PROVENANCE_DATASETS
                    and token not in {"csv", "sqlite", "mysql", "verified", "analytics", "digital", "orders_table"}
                    and ("_" in token or "fake" in token or "ext" in token or "mock" in token)
                ):
                    violations.append(
                        VerificationViolation(
                            code="FABRICATED_PROVENANCE",
                            message=f"Unrecognized dataset/table provenance '{token}' claimed in prose.",
                            severity=VerificationSeverity.CRITICAL,
                            raw_claim=match.group(0),
                        )
                    )
        return violations

    def _check_experimental_ml_claims(
        self,
        text: str,
        agent_results: List[AgentResult],
    ) -> List[VerificationViolation]:
        violations: List[VerificationViolation] = []
        if not text:
            return violations

        for m in _ML_OVERCLAIM_RE.finditer(text):
            prefix = text[max(0, m.start() - 32) : m.start()]
            suffix = text[m.end() : min(len(text), m.end() + 20)]
            if re.search(r"(?:not|never|non|false|isn't|is\s+not|without)\s*$", prefix, re.IGNORECASE):
                continue
            if re.search(r"^\s*(?:=|:|\bis\b)\s*(?:false|no|0|not)\b", suffix, re.IGNORECASE):
                continue
            window = text[max(0, m.start() - 100) : min(len(text), m.end() + 100)]
            has_unready_caveat = any(not c.is_production_ready for res in agent_results for c in res.caveats)
            if has_unready_caveat or _ML_TERM_RE.search(window):
                violations.append(
                    VerificationViolation(
                        code="EXPERIMENTAL_ML_OVERCLAIM",
                        message=(
                            "Candidate output presents experimental ML predictions/models as "
                            "production-ready or guaranteed facts (`is_production_ready=False`)."
                        ),
                        severity=VerificationSeverity.CRITICAL,
                        raw_claim=m.group(0),
                        expected_reference="is_production_ready=False (experimental baseline only)",
                    )
                )
                break

        unready_caveats = [c for res in agent_results for c in res.caveats if not c.is_production_ready]
        if unready_caveats and _ML_PREDICTION_MENTION_RE.search(text) and not _ML_DISCLAIMER_MARKER_RE.search(text):
            violations.append(
                VerificationViolation(
                    code="MISSING_ML_CAVEAT",
                    message=(
                        "Experimental ML predictions referenced without required non-production reliability caveat."
                    ),
                    severity=VerificationSeverity.CRITICAL,
                    raw_claim=_ML_PREDICTION_MENTION_RE.search(text).group(0),  # type: ignore[union-attr]
                )
            )
        return violations

    def _check_kpi_definitions(
        self,
        text: str,
        *,
        facts: Optional[List[GroundedFact]],
        agent_results: List[AgentResult],
        include_kpi_catalog: bool,
    ) -> List[VerificationViolation]:
        violations: List[VerificationViolation] = []
        if not text:
            return violations

        for kpi_id, pat, ref_desc in _KPI_DEF_CONTRA_RULES:
            m = pat.search(text)
            if m:
                violations.append(
                    VerificationViolation(
                        code="KPI_DEFINITION_MISMATCH",
                        message=f"Incorrect business definition stated for {kpi_id}: {ref_desc}",
                        severity=VerificationSeverity.CRITICAL,
                        raw_claim=m.group(0),
                        expected_reference=ref_desc,
                    )
                )

        if include_kpi_catalog and self._kpis:
            is_filtered = any(bool(p.filters_applied) for res in agent_results for p in res.provenance)
            if not is_filtered:
                fact_kpi_values: Dict[str, List[Tuple[float, float, float]]] = {}
                for f in (facts or []) + [f for r in agent_results for f in r.facts]:
                    if f.kpi_id and isinstance(f.value, (int, float)) and not isinstance(f.value, bool):
                        fact_kpi_values.setdefault(f.kpi_id.upper(), []).append(
                            (float(f.value), max(self._default_rel_tol, f.tolerance_rel), max(self._default_abs_tol, f.tolerance_abs))
                        )
                for m in _KPI_ID_VALUE_RE.finditer(text):
                    kid = m.group("kpi").upper()
                    parsed_claims = _extract_numeric_claims(m.group("claim"))
                    if not parsed_claims:
                        continue
                    claim = parsed_claims[0]
                    refs: List[Tuple[float, float, float]] = list(fact_kpi_values.get(kid, []))
                    if not refs and kid in self._kpis and self._kpis[kid].value is not None:
                        refs = [(float(self._kpis[kid].value), self._default_rel_tol, self._default_abs_tol)]
                    if refs and not any(_claim_matches_reference(claim, rv, rt, at) for rv, rt, at in refs):
                        violations.append(
                            VerificationViolation(
                                code="KPI_DEFINITION_MISMATCH",
                                message=f"Numeric claim '{claim.raw_text}' does not match certified {kid} definition/value.",
                                severity=VerificationSeverity.CRITICAL,
                                raw_claim=m.group(0),
                                expected_reference=f"{kid}={refs[0][0]}",
                            )
                        )
        return violations

    def _check_recommendations(
        self,
        agent_results: List[AgentResult],
    ) -> List[VerificationViolation]:
        violations: List[VerificationViolation] = []
        for res in agent_results:
            if not res.recommendations:
                continue
            has_backing_telemetry = bool(res.facts or res.metrics or res.table_rows or res.provenance)
            for rec in res.recommendations:
                ev_clean = (rec.evidence or "").strip().lower()
                act_clean = (rec.action or "").strip().lower()
                if ev_clean in _EMPTY_EVIDENCE_VALUES or not act_clean or not has_backing_telemetry:
                    violations.append(
                        VerificationViolation(
                            code="UNSUPPORTED_RECOMMENDATION",
                            message=(
                                f"Recommendation '{rec.title}' from '{res.agent_id}' lacks grounded "
                                "evidence, actionable steps, or supporting telemetry."
                            ),
                            severity=VerificationSeverity.CRITICAL,
                            raw_claim=rec.title,
                        )
                    )
        return violations

    def verify(
        self,
        candidate_text: str,
        *,
        facts: Optional[List[GroundedFact]] = None,
        agent_results: Optional[List[AgentResult]] = None,
        extra_metrics: Optional[Dict[str, float | int]] = None,
        include_kpi_catalog: bool = True,
        require_non_empty_text: bool = True,
    ) -> VerificationReport:
        """
        Verify candidate prose and agent outputs against grounded facts, KPI definitions,
        cross-agent consistency, missing data status, and unconfirmed-loss rules.
        """
        safe_text = sanitize_text(candidate_text or "")
        violations: List[VerificationViolation] = []
        missing_data_flags: List[str] = []

        if require_non_empty_text and not safe_text.strip():
            violations.append(
                VerificationViolation(
                    code="EMPTY_OUTPUT",
                    message="Candidate output cannot be empty.",
                    severity=VerificationSeverity.CRITICAL,
                )
            )

        for res in agent_results or []:
            if res.status in (
                AgentStatus.BLOCKED,
                AgentStatus.ERROR,
                AgentStatus.TIMEOUT,
                AgentStatus.CANCELLED,
                AgentStatus.PARTIAL,
            ):
                missing_data_flags.append(f"{res.agent_id}:{res.status.value}")
            for gap in res.data_gaps:
                flag = f"{res.agent_id}:gap:{gap}"
                if flag not in missing_data_flags:
                    missing_data_flags.append(flag)

        evidence, has_unconfirmed_leakage = self._collect_evidence(
            facts=facts,
            agent_results=agent_results,
            extra_metrics=extra_metrics,
            include_kpi_catalog=include_kpi_catalog,
        )

        loss_violation = self._check_unconfirmed_loss_framing(safe_text, has_unconfirmed_leakage)
        unconfirmed_loss_preserved = loss_violation is None
        if loss_violation is not None:
            violations.append(loss_violation)

        results_list = list(agent_results or [])
        violations.extend(self._check_provenance(safe_text, results_list))
        violations.extend(self._check_experimental_ml_claims(safe_text, results_list))
        violations.extend(
            self._check_kpi_definitions(
                safe_text,
                facts=facts,
                agent_results=results_list,
                include_kpi_catalog=include_kpi_catalog,
            )
        )
        violations.extend(self._check_recommendations(results_list))

        conflicts = self._detect_agent_conflicts(results_list)
        for conflict in conflicts:
            violations.append(
                VerificationViolation(
                    code="CONFLICTING_AGENT_RESULTS",
                    message=(
                        f"Conflicting values for '{conflict.metric_key}': "
                        f"{conflict.agent_a}={conflict.value_a} vs {conflict.agent_b}={conflict.value_b}."
                    ),
                    severity=VerificationSeverity.CRITICAL,
                    expected_reference=f"{conflict.agent_a}={conflict.value_a}",
                )
            )

        claims = _extract_numeric_claims(safe_text)
        checked_claims: List[ExtractedClaim] = []
        unsupported_claims: List[str] = []
        supported_count = 0

        for claim in claims:
            matched_label: Optional[str] = None
            for ev in evidence:
                if _claim_matches_reference(claim, ev.value, ev.rel_tol, ev.abs_tol):
                    matched_label = ev.label
                    break

            if matched_label is not None:
                supported_count += 1
                checked_claims.append(
                    claim.model_copy(update={"is_supported": True, "matched_evidence": matched_label})
                )
            else:
                unsupported_claims.append(claim.raw_text)
                checked_claims.append(claim.model_copy(update={"is_supported": False}))
                violations.append(
                    VerificationViolation(
                        code="UNSUPPORTED_NUMERIC_CLAIM",
                        message=f"Numeric claim '{claim.raw_text}' could not be traced to supplied evidence or KPI catalog.",
                        severity=VerificationSeverity.CRITICAL,
                        raw_claim=claim.raw_text,
                    )
                )

        if any(v.severity == VerificationSeverity.CRITICAL for v in violations):
            outcome = VerificationOutcome.REJECTED
            is_verified = False
        elif missing_data_flags:
            outcome = VerificationOutcome.PARTIAL
            is_verified = True
        else:
            outcome = VerificationOutcome.VERIFIED
            is_verified = True

        return VerificationReport(
            outcome=outcome,
            is_verified=is_verified,
            checked_claims=checked_claims,
            supported_claims_count=supported_count,
            unsupported_claims=unsupported_claims,
            violations=violations,
            conflicts=conflicts,
            missing_data_flags=missing_data_flags,
            unconfirmed_loss_preserved=unconfirmed_loss_preserved,
        )
