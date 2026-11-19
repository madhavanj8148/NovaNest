"""
NovaNest Master Orchestrator & Multi-Agent Intelligence Engine (Phase 06.3)
---------------------------------------------------------------------------
Coordinates all five verified Phase 06.2 domain intelligence agents
(`FinancialAgent`, `CustomerAgent`, `OperationsAgent`, `RestaurantAgent`,
`DecisionAgent`) alongside hybrid semantic intent routing, principal-isolated
contexts, concurrent bounded thread-pool execution with isolated DataFrame
slices, sequential dependent reasoning, OutputVerifier verification, and
ExecutionTracer observability.

Security & Integrity Guarantees:
- Preserves SQL AST validation (`validate_sql_ast`), table ACLs, and RBAC scopes.
- Enforces strict `principal_id::session_id` isolation across memory and traces.
- Never shares mutable DataFrames between concurrent worker threads.
- Fails closed to documented limitations if OutputVerifier rejects a draft.
- Preserves `is_confirmed_loss=False` and experimental ML ModelCaveat tags.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from datetime import datetime
from enum import Enum
import math
import re
import threading
import time
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple, Union

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field

from python.ai.agents.financial_agent import FinancialAgent
from python.ai.agents.customer_agent import CustomerAgent
from python.ai.agents.operations_agent import OperationsAgent
from python.ai.agents.restaurant_agent import RestaurantAgent
from python.ai.agents.decision_agent import DecisionAgent
from python.ai.agents.base import (
    ensure_python_path,
    get_certified_kpi_catalog,
    safe_round,
    sanitize_scalar,
    sanitize_table_rows,
)
from python.ai.agents.context import (
    AgentContext,
    AgentContextManager,
    ConversationTurnSummary,
)
from python.ai.agents.contracts import (
    MAX_CONTRACT_TABLE_ROWS,
    MAX_SUMMARY_CHARS,
    AgentDomain,
    AgentError,
    AgentExecutionMetadata,
    AgentRequest,
    AgentResult,
    AgentStatus,
    ChartSpec,
    DataProvenance,
    GroundedFact,
    SqlAuditTrace,
    new_id,
    neutralize_untrusted_text,
    sanitize_text,
    sanitize_user_query,
    utc_now,
)
from python.ai.agents.output_verifier import OutputVerifier, VerificationOutcome
from python.ai.agents.registry import AgentRegistry
from python.ai.agents.synthesizer import SynthesisOutput, synthesize_agent_results
from python.ai.agents.telemetry_events import OrchestratorTelemetryEvent, TelemetryEventType
from python.ai.agents.tracing import (
    ExecutionTrace,
    ExecutionTracer,
    TraceVerificationOutcome,
)
from python.ai.analyst.conversation_manager import (
    get_session_history,
    record_turn,
    resolve_follow_up_query,
    resolve_follow_up_query_and_context,
)
from python.ai.analyst.root_cause import perform_root_cause_analysis
from python.ai.analyst.simulation_agent import execute_conversational_simulation
from python.ai.analyst.sql_agent import (
    ALLOWED_TABLES,
    build_readonly_sqlite_connection,
    execute_safe_sql,
)
from python.ai.conversational.nl_to_sql import generate_sql as generate_sql_from_query
from python.ai.analyst.sql_ast import starts_like_sql_statement, validate_sql_ast
from python.ai.analyst.universal_engine import (
    compute_calculation,
    get_offline_knowledge_response,
)
from python.ai.analyst.universal_router import classify_query


class OrchestrationMode(str, Enum):
    SINGLE_AGENT = "single_agent"
    MULTI_AGENT = "multi_agent"
    SQL_SANDBOX = "sql_sandbox"
    GENERAL_ASSISTANT = "general_assistant"


class RoutingPlan(BaseModel):
    """Typed execution plan produced by `IntentRouter` before agent dispatch."""

    model_config = ConfigDict(extra="forbid")

    raw_query: str
    resolved_query: str
    mode: OrchestrationMode
    legacy_route: str
    stage1_parallel_agents: List[str] = Field(default_factory=list)
    stage2_sequential_agents: List[str] = Field(default_factory=list)
    agent_intents: Dict[str, str] = Field(default_factory=dict)
    domain_scores: Dict[str, float] = Field(default_factory=dict)
    is_executive_overview: bool = False
    is_sql_query: bool = False
    requires_business_data: bool = True
    context_topic: str = "general"
    reasoning: str = ""

    @property
    def all_planned_agents(self) -> List[str]:
        seen: set[str] = set()
        out: List[str] = []
        for aid in self.stage1_parallel_agents + self.stage2_sequential_agents:
            if aid not in seen:
                seen.add(aid)
                out.append(aid)
        return out


# Weighted semantic concept rules (regex pattern, weight) per domain & decision trigger.
# Combined with phrase synergy and structural executive-overview cues instead of naive substrings.
_CONCEPT_RULES: Dict[str, Tuple[Tuple[re.Pattern[str], float], ...]] = {
    "financial_agent": (
        (re.compile(r"\b(?:revenue|gmv|gross\s+merchandise|sales|turnover)\b", re.I), 2.5),
        (re.compile(r"\b(?:profit|profitability|margin|contribution|unit\s+economics|take\s+rate|commission)\b", re.I), 2.6),
        (re.compile(r"\b(?:aov|average\s+order\s+value|net\s+order|gross\s+order|basket\s+size)\b", re.I), 2.4),
        (re.compile(r"\b(?:discount|discounts|promo|promotion|subsidy|subsidies|coupon|leakage)\b", re.I), 2.2),
        (re.compile(r"\b(?:financial|finance|p&l|earnings|payment|upi|cod|wallet)\b", re.I), 2.0),
    ),
    "customer_agent": (
        (re.compile(r"\b(?:customer|customers|buyer|buyers|user|users|consumer)\b", re.I), 2.0),
        (re.compile(r"\b(?:churn|attrition|retention|retain|repeat\s+rate|dormant)\b", re.I), 2.7),
        (re.compile(r"\b(?:rfm|segment|segments|segmentation|vip|cohort|cohorts)\b", re.I), 2.6),
        (re.compile(r"\b(?:clv|ltv|lifetime\s+value|customer\s+360|c360)\b", re.I), 2.5),
    ),
    "operations_agent": (
        (re.compile(r"\b(?:delivery|deliveries|fulfillment|logistics|dispatch|operations|operational)\b", re.I), 2.3),
        (re.compile(r"\b(?:eta|sla|breach|breaches|delay|delayed|delays|late|latency|delivery\s+time)\b", re.I), 2.7),
        (re.compile(r"\b(?:cancellation|cancellations|cancelled|canceled|cancel\s+rate)\b", re.I), 2.4),
        (re.compile(r"\b(?:rider|riders|fleet|courier|driver|allocation|workload)\b", re.I), 2.5),
        (re.compile(r"\b(?:demand\s+forecast|hotspot|hotspots|surge|operational\s+anomal)\b", re.I), 2.3),
    ),
    "restaurant_agent": (
        (re.compile(r"\b(?:restaurant|restaurants|merchant|merchants|partner|partners|vendor|outlet)\b", re.I), 2.5),
        (re.compile(r"\b(?:rating|ratings|review|reviews|cuisine|cuisines|menu|dish|dishes)\b", re.I), 2.4),
        (re.compile(r"\b(?:health\s+score|merchant\s+risk|partner\s+risk|kitchen|prep\s+time)\b", re.I), 2.5),
    ),
}

_CAUSAL_SIM_DECISION_RULES: Dict[str, Tuple[Tuple[re.Pattern[str], float], ...]] = {
    "root_cause": (
        (re.compile(r"^\s*why\b|\bwhy\s+(?:is|are|did|do|have|has)\b", re.I), 2.8),
        (re.compile(r"\b(?:root\s+cause|cause|causing|driver|drivers|reason|behind|declin\w*|drop\w*|increas\w*)\b", re.I), 2.1),
    ),
    "what_if_simulation": (
        (re.compile(r"\b(?:what\s+if|what-if|what\s+happens\s+if)\b", re.I), 3.4),
        (re.compile(r"\b(?:simulat\w*|scenario|counterfactual|sensitivity)\b", re.I), 2.8),
        (re.compile(r"\b(?:if\s+we\s+(?:reduce|cut|cap|increase|decrease|improve|raise|lower))\b", re.I), 2.5),
    ),
    "next_best_action": (
        (re.compile(r"\b(?:recommend\w*|next\s+best\s+action|nba|how\s+can\s+we\s+improve|improve|fix|mitigat\w*|optimi[sz]e|priorit\w*)\b", re.I), 2.4),
        (re.compile(r"\b(?:strategy|strategic|action\s+plan|interventions?)\b", re.I), 2.2),
    ),
    "systemic_risk": (
        (re.compile(r"\b(?:digital\s+twin|ripple|cascade|cascading|systemic\s+risk|dependency\s+chain)\b", re.I), 3.0),
    ),
}

_EXECUTIVE_OVERVIEW_RE = re.compile(
    r"\b(?:analy[sz]e\s+(?:my\s+|our\s+)?(?:overall\s+)?business(?:\s+performance)?|"
    r"business\s+(?:performance|health|overview|summary)|"
    r"executive\s+(?:summary|overview|briefing|dashboard)|"
    r"overall\s+(?:platform|company)\s+(?:performance|health)|"
    r"how\s+is\s+(?:novanest|the\s+platform|our\s+business)\s+(?:doing|performing))\b",
    re.I,
)

_SQL_TABLE_MENTION_HINTS: Dict[str, str] = {
    "payments": "financial_agent",
    "promotions": "financial_agent",
    "orders": "financial_agent",
    "customers": "customer_agent",
    "deliveries": "operations_agent",
    "riders": "operations_agent",
    "restaurants": "restaurant_agent",
    "menu_items": "restaurant_agent",
    "ratings_reviews": "restaurant_agent",
}

_DOMAIN_AGENT_DATASET_MAP: Dict[str, Tuple[str, ...]] = {
    "financial_agent": (
        "orders",
        "orders_engineered",
        "payments",
        "promotions",
        "revenue_leakage",
        "restaurants",
    ),
    "customer_agent": (
        "customers",
        "orders",
        "ratings_reviews",
        "customer_churn_predictions",
    ),
    "operations_agent": (
        "deliveries",
        "orders",
        "riders",
        "restaurants",
        "operational_alerts",
        "operational_anomalies",
    ),
    "restaurant_agent": (
        "restaurants",
        "menu_items",
        "orders",
        "ratings_reviews",
        "restaurant_predictions",
    ),
    "decision_agent": (
        "orders",
        "customers",
        "restaurants",
        "deliveries",
        "riders",
        "promotions",
        "orders_engineered",
        "ratings_reviews",
        "customer_churn_predictions",
        "operational_alerts",
        "operational_anomalies",
        "revenue_leakage",
    ),
}


def _slice_isolated_data(
    data: Dict[str, pd.DataFrame],
    allowed_datasets: Sequence[str],
    *,
    deep_copy: bool = False,
) -> Dict[str, pd.DataFrame]:
    """
    Provide thread-safe, isolated access to permitted datasets for a worker agent.
    Under pandas >= 3.0, Copy-on-Write (CoW) is enabled permanently by default,
    ensuring that shallow copies (`deep=False`) are completely safe against mutations:
    any write operation triggers an unshared copy of the affected column buffer.
    Set `deep_copy=True` only if legacy physical buffer duplication is explicitly requested.
    """
    sliced: Dict[str, pd.DataFrame] = {}
    for ds_name in allowed_datasets:
        df = data.get(ds_name)
        if isinstance(df, pd.DataFrame):
            sliced[ds_name] = df.copy(deep=deep_copy)
    return sliced


def _format_legacy_metric_cards(
    agent_results: Sequence[AgentResult],
) -> List[Dict[str, Any]]:
    """Build backward-compatible `verified_metrics` pill objects for React & Streamlit UIs."""
    cards: List[Dict[str, Any]] = []
    seen_labels: set[str] = set()
    for res in agent_results:
        if res.status not in (AgentStatus.SUCCESS, AgentStatus.PARTIAL):
            continue
        for fact in res.facts:
            lbl = fact.label.strip()
            if not lbl or lbl.lower() in seen_labels:
                continue
            seen_labels.add(lbl.lower())
            val_str: str
            val = fact.value
            unit = (fact.unit or "").strip()
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                if unit == "INR":
                    if abs(val) >= 1e7:
                        val_str = f"₹{val / 1e7:,.2f} Cr (₹{val:,.2f})"
                    elif abs(val) >= 1e5:
                        val_str = f"₹{val / 1e5:,.2f} L (₹{val:,.2f})"
                    else:
                        val_str = f"₹{val:,.2f}"
                elif unit == "%":
                    val_str = f"{val:,.2f}%"
                elif isinstance(val, int):
                    val_str = f"{val:,} {unit}".strip()
                else:
                    val_str = f"{val:,.2f} {unit}".strip()
            else:
                val_str = f"{val} {unit}".strip()
            cards.append(
                {
                    "label": lbl,
                    "value": val_str,
                    "provenance": fact.source or res.agent_id,
                    "kpi_id": fact.kpi_id,
                    "is_confirmed": fact.is_confirmed,
                }
            )
            if len(cards) >= 10:
                return cards
    return cards


def _build_legacy_chart(charts: Sequence[ChartSpec]) -> Optional[Dict[str, Any]]:
    if not charts:
        return None
    primary = charts[0]
    xk = primary.x_key or "label"
    yk = primary.y_key or "value"
    return {
        "title": primary.title,
        "type": primary.chart_type,
        "x_key": xk,
        "y_key": yk,
        "x": xk,
        "y": yk,
        "data": primary.data,
    }


def _build_follow_up_suggestions(plan: RoutingPlan) -> List[str]:
    if plan.mode == OrchestrationMode.GENERAL_ASSISTANT:
        return [
            "What is our total revenue and average order value?",
            "Why is profitability declining?",
            "Analyze customer churn and its financial impact.",
        ]
    planned = set(plan.all_planned_agents)
    if len(planned) > 1 or plan.is_executive_overview:
        return [
            "What happens if we reduce discounts and improve delivery SLA?",
            "Which restaurants have poor ratings and high cancellation risk?",
            "How can we improve customer retention and profitability?",
        ]
    if "financial_agent" in planned:
        return [
            "Why is profitability declining?",
            "Compare revenue and net AOV across top cities.",
            "Show promotional discount exposure and leakage screening.",
        ]
    if "customer_agent" in planned:
        return [
            "Analyze customer churn and its financial impact.",
            "Show RFM segments and repeat purchase rate.",
            "How can we improve customer retention and profitability?",
        ]
    if "operations_agent" in planned:
        return [
            "Compare delivery SLA breach rates across cities.",
            "What happens if delivery time decreases by 10%?",
            "Which restaurants have poor ratings and high cancellation risk?",
        ]
    if "restaurant_agent" in planned:
        return [
            "Which restaurants have poor ratings and high cancellation risk?",
            "Show restaurant health scores and benchmark percentiles.",
        ]
    return [
        "Analyze my business performance.",
        "What is our total revenue and average order value?",
    ]


def _pick_agent_intent(agent_id: str, query: str, decision_intent: str) -> str:
    q = query.lower()
    if agent_id == "financial_agent":
        if any(k in q for k in ("leak", "subsidy", "discount", "negative margin", "anomal")):
            return "financial_anomalies"
        if any(k in q for k in ("trend", "monthly", "growth")):
            return "revenue_trends"
        if any(k in q for k in ("compare", "city", "cities", "payment", "promo")):
            return "financial_comparison"
        return "financial_overview"
    if agent_id == "customer_agent":
        if any(k in q for k in ("cohort", "retention")):
            return "cohort_analysis"
        if any(k in q for k in ("churn", "attrition", "risk")):
            return "churn_indicators"
        if any(k in q for k in ("360", "c360", "profile")):
            return "customer_360"
        if any(k in q for k in ("rfm", "segment", "clv", "repeat")):
            return "segmentation_rfm"
        return "customer_overview"
    if agent_id == "operations_agent":
        if any(k in q for k in ("forecast", "hotspot", "demand")):
            return "demand_forecasting"
        if any(k in q for k in ("anomal", "alert", "outlier")):
            return "operational_anomalies"
        if any(k in q for k in ("rider", "fleet", "workload")):
            return "rider_performance"
        if any(k in q for k in ("eta", "sla", "breach", "delay", "delivery time", "cancel")):
            return "delivery_sla_eta"
        return "operations_overview"
    if agent_id == "restaurant_agent":
        if any(k in q for k in ("risk", "critical", "cancel", "health", "poor")):
            return "restaurant_risk"
        if any(k in q for k in ("rating", "review", "menu", "cuisine")):
            return "ratings_and_menu"
        if any(k in q for k in ("compare", "benchmark", "city", "top")):
            return "restaurant_benchmarks"
        return "restaurant_overview"
    return decision_intent or "decision_synthesis"


class IntentRouter:
    """
    Hybrid semantic + structural router mapping user inquiries to one or more
    specialized domain agents, SQL sandbox mode, or general technical reasoning.
    """

    def route(
        self,
        raw_query: str,
        resolved_query: str,
        *,
        last_topic: str = "general",
        classification: Optional[Dict[str, Any]] = None,
    ) -> RoutingPlan:
        """Analyze query semantics & structure and produce an execution `RoutingPlan`."""
        q = (resolved_query or raw_query).strip()
        cls_info = classification or classify_query(q, last_topic)
        cls_intent = str(cls_info.get("intent", "GENERAL"))
        raw_q_low = raw_query.strip().lower()

        # 1. Explicit SQL statement or explicit SQL/NL2SQL request
        # Guard against natural-language questions beginning with English "Analyze ..." or "Explain ..."
        nl_analyze_prefix = bool(
            re.match(
                r"^\s*(?:analy[sz]e\s+(?:my|our|the|customer|customers|financial|revenue|profit\w*|operations?|restaurant\w*|delivery|churn|retention|platform|business|gmv|performance|sales|discounts?|margin|cost|rider\w*)\b|explain\s+(?:the|why|how|what|when|which|whether|difference|concept|meaning)\b)",
                q,
                re.I,
            )
            and not re.search(
                r"(?:;|/\*|--|\bsqlite_|\binformation_schema\b|\bselect\b|\bunion\b|\bdrop\b|\bdelete\b|\bpragma\b|\bquery\s+plan\b)",
                q,
                re.I,
            )
        )
        explicit_sql_request = bool(
            re.search(
                r"\b(?:sql|sqlite|write\s+a\s+query|run\s+query|from\s+(?:orders|customers|restaurants|deliveries|riders|promotions|ratings_reviews|menu_items|payments))\b",
                q,
                re.I,
            )
        )
        if (starts_like_sql_statement(q) and not nl_analyze_prefix) or (cls_intent == "NL2SQL" and explicit_sql_request):
            return RoutingPlan(
                raw_query=raw_query,
                resolved_query=q,
                mode=OrchestrationMode.SQL_SANDBOX,
                legacy_route="NL2SQL",
                stage1_parallel_agents=[],
                stage2_sequential_agents=[],
                is_sql_query=True,
                requires_business_data=True,
                context_topic="cancellations" if "cancel" in q.lower() else "financial",
                reasoning="Direct read-only SQL or explicit SQL request routed to AST-validated sandbox.",
            )

        # 2. Score domain concept rules + causal/simulation decision triggers
        domain_scores: Dict[str, float] = {}
        for agent_id, rules in _CONCEPT_RULES.items():
            score = 0.0
            for pat, weight in rules:
                if pat.search(q):
                    score += weight
            if score > 0.0:
                domain_scores[agent_id] = round(score, 2)

        decision_scores: Dict[str, float] = {}
        for d_intent, rules in _CAUSAL_SIM_DECISION_RULES.items():
            score = 0.0
            for pat, weight in rules:
                if pat.search(q):
                    score += weight
            if score > 0.0:
                decision_scores[d_intent] = round(score, 2)

        top_decision_intent = (
            max(decision_scores.items(), key=lambda kv: kv[1])[0]
            if decision_scores
            else "decision_synthesis"
        )
        decision_total = max(decision_scores.values()) if decision_scores else 0.0

        # Check explicit non-business fast path (greetings, code, math, conceptual tech outside NovaNest)
        explicit_general_intents = {
            "GREETING",
            "CALCULATION",
            "PROGRAMMING",
            "TECHNICAL_COMPARISON",
            "DOCUMENTATION",
            "CONCEPTUAL",
            "GENERAL",
        }
        is_explicit_non_business = (
            cls_intent in explicit_general_intents
            and not cls_info.get("requires_business_data", False)
            and not domain_scores
            and decision_total == 0.0
            and not _EXECUTIVE_OVERVIEW_RE.search(q)
        )
        # Also catch raw topic shifts like "What is Python?" where raw_query is clearly programming/math
        if is_explicit_non_business or (
            cls_intent in ("GREETING", "CALCULATION", "PROGRAMMING")
            and not any(k in raw_q_low for k in ("revenue", "gmv", "churn", "order", "delivery", "restaurant", "profit"))
        ):
            return RoutingPlan(
                raw_query=raw_query,
                resolved_query=q,
                mode=OrchestrationMode.GENERAL_ASSISTANT,
                legacy_route=cls_intent,
                requires_business_data=False,
                context_topic="general",
                reasoning=f"Non-business query classified as '{cls_intent}'.",
            )

        # 3. Broad executive overview -> orchestrate all 4 domain agents + sequential DecisionAgent
        if _EXECUTIVE_OVERVIEW_RE.search(q):
            stage1 = ["financial_agent", "operations_agent", "customer_agent", "restaurant_agent"]
            stage2 = ["decision_agent"]
            intents = {aid: _pick_agent_intent(aid, q, "decision_synthesis") for aid in stage1 + stage2}
            return RoutingPlan(
                raw_query=raw_query,
                resolved_query=q,
                mode=OrchestrationMode.MULTI_AGENT,
                legacy_route="BUSINESS_DATA",
                stage1_parallel_agents=stage1,
                stage2_sequential_agents=stage2,
                agent_intents=intents,
                domain_scores=domain_scores,
                is_executive_overview=True,
                context_topic="executive_overview",
                reasoning="Broad business performance inquiry fanned out across all domain agents and DecisionAgent synthesis.",
            )

        # 4. Synergy refinements: ensure cross-domain causal questions pull relevant drivers
        q_low = q.lower()
        selected_stage1 = [
            aid for aid, sc in sorted(domain_scores.items(), key=lambda kv: (-kv[1], kv[0])) if sc >= 1.5
        ]

        # "Why is profitability declining?" -> financial + operations (delivery/cancellation cost drivers) + decision RCA
        if (
            "financial_agent" in selected_stage1
            and "profit" in q_low
            and any(k in q_low for k in ("why", "declin", "drop", "decreas", "caus"))
            and "operations_agent" not in selected_stage1
        ):
            selected_stage1.append("operations_agent")
            domain_scores["operations_agent"] = max(domain_scores.get("operations_agent", 0.0), 1.8)

        # Causal/impact phrases linking customer/restaurant/operations with financial impact
        if ("financial impact" in q_low or "revenue impact" in q_low or "cancel" in q_low) and "financial_agent" not in selected_stage1:
            selected_stage1.append("financial_agent")
            domain_scores["financial_agent"] = max(domain_scores.get("financial_agent", 0.0), 2.2)

        # "worst region" / "cancellation" questions keep operations_agent strong
        if not selected_stage1 and cls_info.get("requires_business_data", False):
            if "cancel" in q_low or "deliver" in q_low or "sla" in q_low:
                selected_stage1 = ["operations_agent"]
            elif "restaurant" in q_low:
                selected_stage1 = ["restaurant_agent"]
            elif "customer" in q_low or "churn" in q_low:
                selected_stage1 = ["customer_agent"]
            else:
                selected_stage1 = ["financial_agent"]

        # 5. Dependent Stage 2 DecisionAgent trigger
        selected_stage2: List[str] = []
        has_impact_word = bool(re.search(r"\b(?:impact|effect|consequence|trade-?off|improve)\b", q_low))
        if decision_total >= 2.0 or (has_impact_word and len(selected_stage1) >= 2):
            selected_stage2.append("decision_agent")

        # Pure decision/simulation query with no strong secondary data domains requested
        if not selected_stage1 and selected_stage2:
            legacy_route = (
                "SIMULATION"
                if top_decision_intent == "what_if_simulation"
                else ("ROOT_CAUSE" if top_decision_intent == "root_cause" else "RECOMMENDATIONS")
            )
            return RoutingPlan(
                raw_query=raw_query,
                resolved_query=q,
                mode=OrchestrationMode.SINGLE_AGENT,
                legacy_route=legacy_route,
                stage1_parallel_agents=["decision_agent"],
                stage2_sequential_agents=[],
                agent_intents={"decision_agent": top_decision_intent},
                domain_scores=domain_scores,
                context_topic="simulation" if legacy_route == "SIMULATION" else "financial",
                reasoning=f"Direct decision query routed to decision_agent ({top_decision_intent}).",
            )

        all_agents = selected_stage1 + selected_stage2
        if not all_agents:
            return RoutingPlan(
                raw_query=raw_query,
                resolved_query=q,
                mode=OrchestrationMode.GENERAL_ASSISTANT,
                legacy_route=cls_intent,
                requires_business_data=False,
                context_topic="general",
                reasoning="No business signal matched; routing to general assistant.",
            )

        mode = OrchestrationMode.MULTI_AGENT if len(all_agents) > 1 else OrchestrationMode.SINGLE_AGENT
        if top_decision_intent == "what_if_simulation" and "decision_agent" in selected_stage2:
            legacy_route = "SIMULATION"
        elif top_decision_intent == "root_cause" and decision_total >= 2.1:
            legacy_route = "ROOT_CAUSE"
        elif top_decision_intent == "next_best_action" and "recommend" in q_low:
            legacy_route = "RECOMMENDATIONS"
        else:
            legacy_route = "BUSINESS_DATA"

        if "cancel" in q_low:
            topic = "cancellations"
        elif "customer_agent" in all_agents and "financial_agent" not in all_agents:
            topic = "customers"
        elif "restaurant_agent" in all_agents and len(all_agents) == 1:
            topic = "restaurants"
        elif "operations_agent" in all_agents:
            topic = "operations"
        else:
            topic = "financial"

        intents = {aid: _pick_agent_intent(aid, q, top_decision_intent) for aid in all_agents}
        return RoutingPlan(
            raw_query=raw_query,
            resolved_query=q,
            mode=mode,
            legacy_route=legacy_route,
            stage1_parallel_agents=selected_stage1,
            stage2_sequential_agents=selected_stage2,
            agent_intents=intents,
            domain_scores=domain_scores,
            context_topic=topic,
            reasoning=(
                f"Hybrid semantic route selected stage1={selected_stage1}, "
                f"stage2={selected_stage2} ({top_decision_intent})."
            ),
        )


class OrchestrationOutcome(BaseModel):
    """Full structured orchestration bundle returned by `MasterOrchestrator`."""

    model_config = ConfigDict(extra="forbid")

    request_id: str
    trace_id: str
    routing_plan: RoutingPlan
    agent_result: AgentResult
    child_results: List[AgentResult] = Field(default_factory=list)
    synthesis: Optional[SynthesisOutput] = None
    trace: Optional[ExecutionTrace] = None
    provider_status: str = "offline-deterministic"
    sql_payload: Optional[Dict[str, Any]] = None
    root_cause_payload: Optional[Dict[str, Any]] = None
    simulation_payload: Optional[Dict[str, Any]] = None
    legacy_verified_metrics: List[Dict[str, Any]] = Field(default_factory=list)
    grounding_verified_override: Optional[bool] = None
    verification_outcome_override: Optional[str] = None
    active_filters: Dict[str, Any] = Field(default_factory=dict)
    remembered_entities: Dict[str, Any] = Field(default_factory=dict)

    def to_chat_response(self) -> Dict[str, Any]:
        """Adapt `OrchestrationOutcome` into FastAPI & React `/api/ai/ask` schema."""
        res = self.agent_result
        plan = self.routing_plan
        syn = self.synthesis

        recs_dicts = [r.model_dump(mode="json") for r in res.recommendations]
        rows = [dict(r) for r in res.table_rows[:15]]
        chart_dict = _build_legacy_chart(res.charts)

        sql_obj = self.sql_payload
        if sql_obj is None and res.sql_traces:
            st = res.sql_traces[0]
            sql_obj = {
                "query": st.sql,
                "valid": st.validated_by_ast,
                "validation_message": "Safe read-only AST-verified query executed",
            }

        provenance_summary = {
            "data_source": (
                ", ".join(syn.data_source_badges[:3])
                if syn and syn.data_source_badges
                else ("General Knowledge & Reasoning Engine" if not plan.requires_business_data else "NovaNest Verified Store")
            ),
            "access_mode": "Read-Only Multi-Agent Verified" if plan.requires_business_data else "Open AI Reasoning",
            "records_loaded": sum(p.row_count or 0 for p in res.provenance),
        }

        agents_invoked = [
            {
                "agent_id": child.agent_id,
                "domain": child.domain.value,
                "status": child.status.value,
                "elapsed_ms": child.execution.elapsed_ms if child.execution else 0.0,
                "stage": 2 if child.agent_id in plan.stage2_sequential_agents else 1,
                "data_sources": [p.dataset_or_table or p.source_name for p in child.provenance],
            }
            for child in self.child_results
        ]

        ver_outcome = (
            self.verification_outcome_override
            if self.verification_outcome_override is not None
            else (
                syn.verification_report.outcome.value
                if syn is not None
                else (self.trace.verification_outcome.value if self.trace else "not_run")
            )
        )
        grounding_verified = (
            self.grounding_verified_override
            if self.grounding_verified_override is not None
            else (syn.grounding_verified if syn is not None else (not plan.requires_business_data))
        )

        sql_query = sql_obj.get("query", "") if sql_obj else ""
        sql_valid = bool(sql_obj.get("valid", True)) if sql_obj else True
        val_msg = sql_obj.get("validation_message", "") if sql_obj else ""

        return {
            # Legacy Phase 06.0 / React / Streamlit fields
            "question": plan.raw_query,
            "resolved_query": plan.resolved_query if plan.resolved_query != plan.raw_query else None,
            "intent": plan.legacy_route,
            "route": plan.legacy_route,
            "requires_business_data": plan.requires_business_data,
            "answer": res.narrative or res.summary,
            "provider_status": self.provider_status,
            "verified_metrics": self.legacy_verified_metrics,
            "suggested_chart": chart_dict,
            "sql": sql_obj,
            "sql_query": sql_query,
            "sql_valid": sql_valid,
            "validation_message": val_msg,
            "data_rows": rows,
            "root_cause_analysis": self.root_cause_payload,
            "simulation_results": self.simulation_payload,
            "recommendations": recs_dicts,
            "follow_up_suggestions": _build_follow_up_suggestions(plan),
            "provenance": provenance_summary,
            "insights": [r.title for r in res.recommendations],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            # Additive Phase 06.3 Multi-Agent Observability fields
            "request_id": self.request_id,
            "trace_id": self.trace_id,
            "orchestration_mode": plan.mode.value,
            "agents_invoked": agents_invoked,
            "telemetry": {
                "agents_invoked": agents_invoked,
                "agent_execution_times": {
                    child.agent_id: (child.execution.elapsed_ms if child.execution else 0.0)
                    for child in self.child_results
                },
                "total_duration_ms": res.execution.elapsed_ms if res.execution else 0.0,
                "verification_outcome": ver_outcome,
            },
            "consolidated_summary": res.summary,
            "calculation_steps": syn.calculation_steps if syn else [],
            "ml_confidence_warnings": syn.ml_confidence_warnings if syn else [],
            "limitations": syn.limitations if syn else [],
            "data_source_badges": syn.data_source_badges if syn else [],
            "grounding_verified": grounding_verified,
            "verification_outcome": ver_outcome,
            "conflicts": [c.model_dump(mode="json") for c in (syn.conflicts if syn else [])],
            "status": res.status.value,
            # Additive Phase 06.5 Milestone 2 Conversational Memory fields
            "active_filters": self.active_filters,
            "remembered_entities": self.remembered_entities,
        }


_NON_RETRYABLE_ERROR_CODES = frozenset(
    {
        "RBAC_SCOPE_DENIED",
        "TABLE_ACL_DENIED",
        "RBAC_OR_AVAILABILITY_BLOCKED",
        "SQL_PERMISSION_DENIED",
        "SQL_AST_BLOCKED",
        "PROMPT_INJECTION_BLOCKED",
        "OUTPUT_VERIFICATION_FAILED",
        "OUTPUT_VERIFICATION_REJECTED",
        "AGENT_ID_MISMATCH",
        "PRINCIPAL_ISOLATION_VIOLATION",
        "MISSING_PRIMARY_DATASET",
        "SCHEMA_MISMATCH",
    }
)


class _AgentCircuitBreaker:
    """Thread-safe per-agent circuit breaker (CLOSED -> OPEN -> HALF_OPEN) against repeated faults."""

    def __init__(self, *, failure_threshold: int = 3, cooldown_seconds: float = 10.0) -> None:
        self._failure_threshold = max(1, int(failure_threshold))
        self._cooldown_seconds = max(0.05, float(cooldown_seconds))
        self._lock = threading.RLock()
        self._failures: Dict[str, int] = {}
        self._opened_until: Dict[str, float] = {}

    def allow_request(self, agent_id: str) -> bool:
        now = time.monotonic()
        with self._lock:
            until = self._opened_until.get(agent_id)
            if until is None:
                return True
            if now >= until:
                # Transition CLEANLY to HALF_OPEN trial window
                return True
            return False

    def record_success(self, agent_id: str) -> None:
        with self._lock:
            self._failures.pop(agent_id, None)
            self._opened_until.pop(agent_id, None)

    def record_failure(self, agent_id: str) -> None:
        now = time.monotonic()
        with self._lock:
            count = self._failures.get(agent_id, 0) + 1
            self._failures[agent_id] = count
            if count >= self._failure_threshold:
                self._opened_until[agent_id] = now + self._cooldown_seconds

    def state(self, agent_id: str) -> str:
        now = time.monotonic()
        with self._lock:
            until = self._opened_until.get(agent_id)
            if until is None:
                return "closed"
            return "open" if now < until else "half_open"


class MasterOrchestrator:
    """
    Central coordinator routing user inquiries across NovaNest's five verified
    domain intelligence agents under RBAC, SQL AST, timeout, and OutputVerifier controls.
    """

    AGENT_ID = "master_orchestrator"
    VERSION = "1.0.0"

    def __init__(
        self,
        *,
        registry: Optional[AgentRegistry] = None,
        verifier: Optional[OutputVerifier] = None,
        tracer: Optional[ExecutionTracer] = None,
        context_manager: Optional[AgentContextManager] = None,
        router: Optional[IntentRouter] = None,
        max_workers: int = 4,
        default_timeout_seconds: float = 65.0,
        per_agent_timeout_seconds: float = 35.0,
        max_concurrent_requests: int = 8,
        max_retries: int = 1,
        retry_backoff_seconds: float = 0.05,
        circuit_failure_threshold: int = 3,
        circuit_cooldown_seconds: float = 10.0,
    ) -> None:
        if registry is not None:
            self.registry = registry
        else:
            reg = AgentRegistry(preload_planned_blueprints=False)
            for cls in (FinancialAgent, CustomerAgent, OperationsAgent, RestaurantAgent, DecisionAgent):
                cls(strict_verification=True).register_into(reg, overwrite=True)
            self.registry = reg
        self.verifier = verifier or OutputVerifier(load_default_kpis=True)
        self.tracer = tracer or ExecutionTracer()
        self.context_manager = context_manager or AgentContextManager()
        self.router = router or IntentRouter()
        self.max_workers = max(1, min(int(max_workers), 8))
        self.default_timeout_seconds = max(0.5, float(default_timeout_seconds))
        self.per_agent_timeout_seconds = max(0.25, float(per_agent_timeout_seconds))
        self.max_concurrent_requests = max(1, min(int(max_concurrent_requests), 64))
        self.max_retries = max(0, min(int(max_retries), 3))
        self.retry_backoff_seconds = max(0.0, min(float(retry_backoff_seconds), 2.0))
        self._concurrency_semaphore = threading.BoundedSemaphore(self.max_concurrent_requests)
        self._circuit_breaker = _AgentCircuitBreaker(
            failure_threshold=circuit_failure_threshold,
            cooldown_seconds=circuit_cooldown_seconds,
        )

    def _resolve_principal_args(
        self,
        *,
        principal: Optional[Any],
        principal_id: Optional[str],
        principal_role: Optional[str],
        principal_scopes: Optional[Sequence[str]],
    ) -> Tuple[str, str, Set[str]]:
        if principal is not None:
            pid = str(getattr(principal, "principal_id", None) or principal_id or "anon:local")
            role = str(getattr(principal, "role", None) or principal_role or "operator")
            raw_scopes = getattr(principal, "scopes", None) or principal_scopes or ("read", "operator")
        else:
            pid = str(principal_id or "anon:local")
            role = str(principal_role or "operator")
            raw_scopes = principal_scopes if principal_scopes is not None else ("read", "operator")
        scopes = {str(s).strip().lower() for s in raw_scopes if str(s).strip()} or {"read"}
        return pid, role, scopes

    def _handle_general_query(
        self,
        *,
        request_id: str,
        trace_id: str,
        plan: RoutingPlan,
        context: AgentContext,
        ai_provider: Any,
        t0: float,
    ) -> OrchestrationOutcome:
        intent = plan.legacy_route
        q = plan.resolved_query
        provider_status = "offline-deterministic"
        answer_text = ""

        if ai_provider is not None and hasattr(ai_provider, "get_status"):
            try:
                st = ai_provider.get_status()
                if isinstance(st, dict) and st.get("status"):
                    provider_status = str(st["status"])
            except Exception:
                provider_status = "error"

        if intent == "CALCULATION":
            answer_text = compute_calculation(q)
        elif ai_provider is not None and provider_status == "ready" and hasattr(ai_provider, "generate_response"):
            try:
                ai_resp = ai_provider.generate_response(q)
                if isinstance(ai_resp, dict) and ai_resp.get("text"):
                    answer_text = str(ai_resp["text"])
                elif isinstance(ai_resp, str) and ai_resp.strip():
                    answer_text = ai_resp
            except Exception:
                provider_status = "error"

        if not answer_text:
            answer_text = get_offline_knowledge_response(q, intent)

        elapsed_ms = round(max(0.0, (time.monotonic() - t0) * 1000.0), 3)
        res = AgentResult(
            request_id=request_id,
            agent_id=self.AGENT_ID,
            domain=AgentDomain.GENERAL,
            status=AgentStatus.SUCCESS,
            summary=sanitize_text(answer_text)[:400],
            narrative=sanitize_text(answer_text),
            execution=AgentExecutionMetadata(
                request_id=request_id,
                execution_id=request_id,
                agent_id=self.AGENT_ID,
                agent_version=self.VERSION,
                elapsed_ms=elapsed_ms,
            ),
        )
        trace = self.tracer.finish_trace(
            request_id,
            status=AgentStatus.SUCCESS,
            verification_outcome=TraceVerificationOutcome.NOT_RUN,
        )
        return OrchestrationOutcome(
            request_id=request_id,
            trace_id=trace_id,
            routing_plan=plan,
            agent_result=res,
            trace=trace,
            provider_status=provider_status,
        )

    def _handle_sql_sandbox(
        self,
        *,
        request_id: str,
        trace_id: str,
        plan: RoutingPlan,
        context: AgentContext,
        data: Dict[str, pd.DataFrame],
        sqlite_conn: Any,
        t0: float,
    ) -> OrchestrationOutcome:
        q = plan.resolved_query
        direct_sql = starts_like_sql_statement(q)
        raw_sql = q if direct_sql else (generate_sql_from_query(q) or "")
        span_id = self.tracer.start_span(
            request_id=request_id,
            agent_id="sql_sandbox",
            domain=AgentDomain.OPERATIONS,
            metadata={"mode": "sql_sandbox"},
        )

        # RBAC check: direct SQL across 9 tables requires at least operator scope
        if "operator" not in context.principal_scopes:
            msg = "Insufficient RBAC scope: SQL sandbox queries require 'operator' scope."
            err = AgentError(
                code="RBAC_SCOPE_DENIED",
                message=msg,
                agent_id="sql_sandbox",
                recoverable=False,
            )
            res = AgentResult(
                request_id=request_id,
                agent_id=self.AGENT_ID,
                domain=AgentDomain.ORCHESTRATION,
                status=AgentStatus.BLOCKED,
                summary=msg,
                narrative=f"### Access Blocked\n\n{msg}",
                errors=[err],
                execution=AgentExecutionMetadata(
                    request_id=request_id,
                    execution_id=request_id,
                    agent_id=self.AGENT_ID,
                    elapsed_ms=round(max(0.0, (time.monotonic() - t0) * 1000.0), 3),
                ),
            )
            self.tracer.record_agent_result(span_id, res, verification_outcome=TraceVerificationOutcome.REJECTED)
            trace = self.tracer.finish_trace(request_id, status=AgentStatus.BLOCKED, verification_outcome=TraceVerificationOutcome.REJECTED)
            return OrchestrationOutcome(
                request_id=request_id,
                trace_id=trace_id,
                routing_plan=plan,
                agent_result=res,
                trace=trace,
                sql_payload={"query": raw_sql, "valid": False, "validation_message": msg},
            )

        is_valid, sanitized_sql, val_msg = validate_sql_ast(raw_sql)
        if not is_valid:
            msg = val_msg or "SQL query blocked by AST security validator."
            err = AgentError(code="SQL_AST_BLOCKED", message=msg, agent_id="sql_sandbox", recoverable=False)
            res = AgentResult(
                request_id=request_id,
                agent_id=self.AGENT_ID,
                domain=AgentDomain.ORCHESTRATION,
                status=AgentStatus.BLOCKED,
                summary=msg,
                narrative=f"⚠️ **SQL Security Block**: {msg}",
                errors=[err],
                execution=AgentExecutionMetadata(
                    request_id=request_id,
                    execution_id=request_id,
                    agent_id=self.AGENT_ID,
                    elapsed_ms=round(max(0.0, (time.monotonic() - t0) * 1000.0), 3),
                ),
            )
            self.tracer.record_agent_result(span_id, res, verification_outcome=TraceVerificationOutcome.REJECTED)
            trace = self.tracer.finish_trace(request_id, status=AgentStatus.BLOCKED, verification_outcome=TraceVerificationOutcome.REJECTED)
            return OrchestrationOutcome(
                request_id=request_id,
                trace_id=trace_id,
                routing_plan=plan,
                agent_result=res,
                trace=trace,
                sql_payload={"query": sanitized_sql or raw_sql, "valid": False, "validation_message": msg},
            )

        local_conn = sqlite_conn
        owned_conn = False
        if local_conn is None and data:
            local_conn = build_readonly_sqlite_connection(data)
            owned_conn = True

        df: Optional[pd.DataFrame] = None
        exec_msg = "Database engine unavailable."
        if local_conn is not None:
            try:
                df, exec_msg = execute_safe_sql(sanitized_sql, local_conn)
            finally:
                if owned_conn:
                    local_conn.close()

        if df is None:
            err = AgentError(code="SQL_EXECUTION_ERROR", message=exec_msg, agent_id="sql_sandbox", recoverable=True)
            res = AgentResult(
                request_id=request_id,
                agent_id=self.AGENT_ID,
                domain=AgentDomain.ORCHESTRATION,
                status=AgentStatus.ERROR,
                summary=exec_msg,
                narrative=f"⚠️ **SQL Execution Blocked/Failed**: {exec_msg}",
                errors=[err],
                execution=AgentExecutionMetadata(
                    request_id=request_id,
                    execution_id=request_id,
                    agent_id=self.AGENT_ID,
                    elapsed_ms=round(max(0.0, (time.monotonic() - t0) * 1000.0), 3),
                ),
            )
            self.tracer.record_agent_result(span_id, res, verification_outcome=TraceVerificationOutcome.REJECTED)
            trace = self.tracer.finish_trace(request_id, status=AgentStatus.ERROR, verification_outcome=TraceVerificationOutcome.REJECTED)
            return OrchestrationOutcome(
                request_id=request_id,
                trace_id=trace_id,
                routing_plan=plan,
                agent_result=res,
                trace=trace,
                sql_payload={"query": sanitized_sql, "valid": False, "validation_message": exec_msg},
            )

        safe_rows = sanitize_table_rows(df.head(MAX_CONTRACT_TABLE_ROWS).to_dict(orient="records"))
        tables = [
            tbl
            for tbl in sorted(ALLOWED_TABLES)
            if re.search(rf"\b{re.escape(tbl)}\b", sanitized_sql, re.IGNORECASE)
        ]
        sql_trace = SqlAuditTrace(
            sql=sanitized_sql,
            tables_accessed=tables,
            row_count=min(len(df), MAX_CONTRACT_TABLE_ROWS),
            execution_ms=round(max(0.0, (time.monotonic() - t0) * 1000.0), 3),
            validated_by_ast=True,
        )
        facts = [
            GroundedFact(
                label="SQL Records Returned",
                value=int(len(df)),
                unit="rows",
                source="Read-Only SQLite Engine",
            )
        ]
        if df.empty:
            verify_text = "The read-only SQL query executed cleanly and returned 0 rows."
            narrative = verify_text
        else:
            verify_text = (
                f"Here are the verified read-only database results ({len(df):,} rows returned).\n\n"
                "*Executed safely across AST-verified approved schema tables (see SQL Audit Trace).*"
            )
            table_md = df.head(8).to_markdown(index=False)
            narrative = (
                f"Here are the verified read-only database results ({len(df):,} rows returned):\n\n"
                f"{table_md}\n\n"
                "*Executed safely across AST-verified approved schema tables (see SQL Audit Trace).*"
            )

        provenance = [
            DataProvenance(
                source_name="SQLite Read-Only Sandbox",
                source_type="sqlite",
                dataset_or_table=",".join(tables) or "sqlite",
                row_count=int(len(df)),
            )
        ]
        res = AgentResult(
            request_id=request_id,
            agent_id=self.AGENT_ID,
            domain=AgentDomain.ORCHESTRATION,
            status=AgentStatus.SUCCESS,
            summary=f"Executed AST-verified read-only SQL across {tables or ['sqlite']} returning {len(df)} rows.",
            narrative=narrative,
            facts=facts,
            metrics={"sql_rows_returned": int(len(df))},
            table_rows=safe_rows,
            sql_traces=[sql_trace],
            provenance=provenance,
            execution=AgentExecutionMetadata(
                request_id=request_id,
                execution_id=request_id,
                agent_id=self.AGENT_ID,
                elapsed_ms=round(max(0.0, (time.monotonic() - t0) * 1000.0), 3),
            ),
        )
        report = self.verifier.verify(verify_text, facts=facts, agent_results=[res], include_kpi_catalog=False)
        trace_ver = (
            TraceVerificationOutcome.VERIFIED
            if report.outcome == VerificationOutcome.VERIFIED
            else TraceVerificationOutcome.PARTIAL
        )
        self.tracer.record_agent_result(span_id, res, verification_outcome=trace_ver)
        trace = self.tracer.finish_trace(request_id, status=AgentStatus.SUCCESS, verification_outcome=trace_ver)
        legacy_cards = [
            {"label": "Records Returned", "value": f"{len(df):,}", "provenance": "SQLite Read-Only Engine"},
            {"label": "Execution Mode", "value": "Safe Read-Only SQL (9-Table Parity)", "provenance": "AST Validator"},
        ]
        return OrchestrationOutcome(
            request_id=request_id,
            trace_id=trace_id,
            routing_plan=plan,
            agent_result=res,
            trace=trace,
            sql_payload={
                "query": sanitized_sql,
                "valid": True,
                "validation_message": "Safe read-only query executed",
            },
            legacy_verified_metrics=legacy_cards,
            grounding_verified_override=(report.outcome != VerificationOutcome.REJECTED),
            verification_outcome_override=report.outcome.value,
        )

    def _build_child_request(
        self,
        *,
        agent_id: str,
        parent_request_id: str,
        trace_id: str,
        context: AgentContext,
        user_query: str,
        intent: str,
        filters: Dict[str, Any],
        timeout_seconds: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentRequest:
        reg = self.registry.get(agent_id)
        domain = reg.domain if reg is not None else AgentDomain.GENERAL
        allowed_tables = list(reg.allowed_tables) if reg is not None else []
        required_scopes = list(reg.required_scopes) if reg is not None else ["read"]
        return AgentRequest(
            request_id=parent_request_id,
            execution_id=new_id("exec_"),
            agent_id=agent_id,
            domain=domain,
            principal_id=context.principal_id,
            session_id=context.session_id,
            user_query=user_query,
            intent=intent,
            filters=filters,
            allowed_tables=allowed_tables,
            required_scopes=required_scopes,
            timeout_seconds=max(0.1, min(timeout_seconds, 60.0)),
            trace_id=trace_id,
            metadata=metadata or {},
        )

    def _build_failure_result(
        self,
        *,
        request: AgentRequest,
        status: AgentStatus,
        code: str,
        message: str,
        elapsed_ms: float = 0.0,
        timed_out: bool = False,
        cancelled: bool = False,
    ) -> AgentResult:
        err = AgentError(
            code=code,
            message=sanitize_text(message),
            agent_id=request.agent_id,
            recoverable=(status != AgentStatus.BLOCKED),
        )
        res = AgentResult(
            request_id=request.request_id,
            execution_id=request.execution_id,
            agent_id=request.agent_id,
            domain=request.domain,
            status=status,
            summary=err.message,
            errors=[err],
            execution=AgentExecutionMetadata(
                request_id=request.request_id,
                execution_id=request.execution_id,
                agent_id=request.agent_id,
                elapsed_ms=round(max(0.0, elapsed_ms), 3),
                timed_out=timed_out,
                cancelled=cancelled,
            ),
        )
        span_id = self.tracer.start_span(
            request_id=request.request_id,
            agent_id=request.agent_id,
            domain=request.domain,
            metadata={"intent": request.intent or "general"},
        )
        self.tracer.record_agent_result(span_id, res, verification_outcome=TraceVerificationOutcome.REJECTED)
        return res

    def _prepare_agent_task(
        self,
        *,
        agent_id: str,
        parent_request_id: str,
        trace_id: str,
        context: AgentContext,
        user_query: str,
        intent: str,
        filters: Dict[str, Any],
        data: Dict[str, pd.DataFrame],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Optional[Tuple[AgentRequest, Callable[..., AgentResult], Dict[str, pd.DataFrame]]], Optional[AgentResult]]:
        """Authorize via `AgentRegistry` and prepare an isolated deep-copied data slice."""
        req = self._build_child_request(
            agent_id=agent_id,
            parent_request_id=parent_request_id,
            trace_id=trace_id,
            context=context,
            user_query=user_query,
            intent=intent,
            filters=filters,
            timeout_seconds=min(self.per_agent_timeout_seconds, max(0.25, context.remaining_seconds())),
            metadata=metadata,
        )
        if context.is_cancelled():
            return None, self._build_failure_result(
                request=req,
                status=AgentStatus.CANCELLED,
                code="EXECUTION_CANCELLED",
                message="Orchestration cancelled prior to agent dispatch.",
                cancelled=True,
            )
        if context.is_expired():
            return None, self._build_failure_result(
                request=req,
                status=AgentStatus.TIMEOUT,
                code="ORCHESTRATION_DEADLINE_EXPIRED",
                message="Request deadline expired prior to agent dispatch.",
                timed_out=True,
            )

        extra_tables_raw = filters.get("requested_tables") if isinstance(filters, dict) else None
        combined_requested = list(req.allowed_tables)
        if isinstance(extra_tables_raw, (list, tuple, set)):
            combined_requested.extend(str(t) for t in extra_tables_raw)

        decision = self.registry.authorize(
            agent_id,
            principal_scopes=context.principal_scopes,
            requested_tables=combined_requested,
        )
        if not decision.allowed:
            return None, self._build_failure_result(
                request=req,
                status=AgentStatus.BLOCKED,
                code="RBAC_OR_AVAILABILITY_BLOCKED",
                message=decision.reason,
            )

        if not self._circuit_breaker.allow_request(agent_id):
            return None, self._build_failure_result(
                request=req,
                status=AgentStatus.ERROR,
                code="CIRCUIT_BREAKER_OPEN",
                message=f"{agent_id} circuit breaker is open after consecutive runtime failures; failing fast cleanly.",
            )

        handler = self.registry.get_handler(agent_id)
        if handler is None:
            return None, self._build_failure_result(
                request=req,
                status=AgentStatus.ERROR,
                code="AGENT_HANDLER_MISSING",
                message=f"No operational handler registered for '{agent_id}'.",
            )

        allowed_ds = _DOMAIN_AGENT_DATASET_MAP.get(agent_id, tuple(data.keys()))
        isolated_data = _slice_isolated_data(data, allowed_ds)
        return (req, handler, isolated_data), None

    def _is_retryable_result(self, req: AgentRequest, res: AgentResult) -> bool:
        if req.intent == "sql":
            return False
        if res.status != AgentStatus.ERROR or not res.errors:
            return False
        first_err = res.errors[0]
        if not first_err.recoverable:
            return False
        return first_err.code not in _NON_RETRYABLE_ERROR_CODES

    def _invoke_with_retry(
        self,
        *,
        req: AgentRequest,
        handler: Callable[..., AgentResult],
        context: AgentContext,
        isolated_data: Dict[str, pd.DataFrame],
        per_attempt_timeout_s: float,
    ) -> AgentResult:
        """
        Invoke a read-only domain handler inside a child-linked `AgentContext` with
        bounded exponential-backoff retries on transient recoverable failures ONLY.
        """
        retries_used = 0
        max_attempts = 1 + self.max_retries
        last_result: Optional[AgentResult] = None

        for attempt in range(max_attempts):
            if context.is_cancelled():
                return self._build_failure_result(
                    request=req,
                    status=AgentStatus.CANCELLED,
                    code="EXECUTION_CANCELLED",
                    message="Request cancelled prior to domain retry attempt.",
                    cancelled=True,
                )
            rem = context.remaining_seconds()
            if rem <= 0.0:
                return self._build_failure_result(
                    request=req,
                    status=AgentStatus.TIMEOUT,
                    code="ORCHESTRATION_TIMEOUT",
                    message=f"{req.agent_id} exhausted remaining request deadline.",
                    timed_out=True,
                )

            attempt_timeout = max(0.05, min(per_attempt_timeout_s, rem))
            child_ctx = context.fork_for_agent(agent_id=req.agent_id, timeout_seconds=attempt_timeout)
            t0_attempt = time.monotonic()
            pool = ThreadPoolExecutor(max_workers=1)
            try:
                fut = pool.submit(
                    handler,
                    req,
                    child_ctx,
                    data=isolated_data,
                    tracer=self.tracer,
                    verifier=self.verifier,
                    principal_scopes=list(context.principal_scopes),
                )
                res = fut.result(timeout=attempt_timeout)
                if res.status in (AgentStatus.SUCCESS, AgentStatus.PARTIAL):
                    self._circuit_breaker.record_success(req.agent_id)
                    if retries_used > 0 and res.execution is not None:
                        res = res.model_copy(
                            update={"execution": res.execution.model_copy(update={"retry_count": retries_used})}
                        )
                    return res

                if res.status in (AgentStatus.BLOCKED, AgentStatus.CANCELLED):
                    return res

                last_result = res
                if res.status == AgentStatus.TIMEOUT:
                    self._circuit_breaker.record_failure(req.agent_id)
                    return res

                if not self._is_retryable_result(req, res) or attempt >= max_attempts - 1:
                    self._circuit_breaker.record_failure(req.agent_id)
                    return res

            except FuturesTimeoutError:
                child_ctx.cancel(f"{req.agent_id} timed out after {attempt_timeout:.2f}s.")
                self._circuit_breaker.record_failure(req.agent_id)
                return self._build_failure_result(
                    request=req,
                    status=AgentStatus.TIMEOUT,
                    code="AGENT_TIMEOUT",
                    message=f"{req.agent_id} exceeded per-agent execution deadline.",
                    elapsed_ms=(time.monotonic() - t0_attempt) * 1000.0,
                    timed_out=True,
                )
            except Exception as exc:
                self._circuit_breaker.record_failure(req.agent_id)
                last_result = self._build_failure_result(
                    request=req,
                    status=AgentStatus.ERROR,
                    code="AGENT_EXECUTION_ERROR",
                    message=f"{req.agent_id} failed: {sanitize_text(str(exc))}",
                    elapsed_ms=(time.monotonic() - t0_attempt) * 1000.0,
                )
                if attempt >= max_attempts - 1 or req.intent == "sql":
                    return last_result
            finally:
                pool.shutdown(wait=False, cancel_futures=True)

            # Bounded exponential backoff strictly within remaining request budget
            backoff = self.retry_backoff_seconds * (2 ** attempt)
            if context.remaining_seconds() <= backoff + 0.05:
                self._circuit_breaker.record_failure(req.agent_id)
                assert last_result is not None
                return last_result
            if backoff > 0.0:
                time.sleep(backoff)
            retries_used += 1

        self._circuit_breaker.record_failure(req.agent_id)
        assert last_result is not None
        return last_result

    def _execute_stage1_parallel(
        self,
        *,
        agent_ids: Sequence[str],
        plan: RoutingPlan,
        request_id: str,
        trace_id: str,
        context: AgentContext,
        filters: Dict[str, Any],
        data: Dict[str, pd.DataFrame],
        event_callback: Optional[Callable[[OrchestratorTelemetryEvent], None]] = None,
    ) -> List[AgentResult]:
        prepared: List[Tuple[AgentRequest, Callable[..., AgentResult], Dict[str, pd.DataFrame]]] = []
        results: List[AgentResult] = []

        for aid in agent_ids:
            task, blocked_res = self._prepare_agent_task(
                agent_id=aid,
                parent_request_id=request_id,
                trace_id=trace_id,
                context=context,
                user_query=plan.resolved_query,
                intent=plan.agent_intents.get(aid, ""),
                filters=filters,
                data=data,
            )
            if blocked_res is not None:
                results.append(blocked_res)
                if event_callback:
                    try:
                        event_callback(
                            OrchestratorTelemetryEvent(
                                request_id=request_id,
                                session_id=context.session_id,
                                event_type=TelemetryEventType.AGENT_FAILED,
                                timestamp=time.time(),
                                agent_name=aid,
                                status=blocked_res.status.value,
                                stage=1,
                                message=f"Agent {aid} blocked: {blocked_res.summary[:200]}",
                            )
                        )
                    except Exception:
                        pass
            elif task is not None:
                prepared.append(task)

        if not prepared:
            return results

        if len(prepared) == 1:
            req, handler, isolated_data = prepared[0]
            if event_callback:
                try:
                    event_callback(
                        OrchestratorTelemetryEvent(
                            request_id=request_id,
                            session_id=context.session_id,
                            event_type=TelemetryEventType.AGENT_STARTED,
                            timestamp=time.time(),
                            agent_name=req.agent_id,
                            status="running",
                            stage=1,
                            message=f"Agent {req.agent_id} started domain analysis.",
                        )
                    )
                except Exception:
                    pass

            res = self._invoke_with_retry(
                req=req,
                handler=handler,
                context=context,
                isolated_data=isolated_data,
                per_attempt_timeout_s=self.per_agent_timeout_seconds,
            )
            results.append(res)
            if event_callback:
                try:
                    evt_type = (
                        TelemetryEventType.AGENT_COMPLETED
                        if res.status in (AgentStatus.SUCCESS, AgentStatus.PARTIAL)
                        else TelemetryEventType.AGENT_FAILED
                    )
                    event_callback(
                        OrchestratorTelemetryEvent(
                            request_id=request_id,
                            session_id=context.session_id,
                            event_type=evt_type,
                            timestamp=time.time(),
                            agent_name=res.agent_id,
                            status=res.status.value,
                            duration_ms=res.execution.elapsed_ms,
                            stage=1,
                            message=(
                                f"Agent {res.agent_id} completed domain analysis ({round(res.execution.elapsed_ms, 1)}ms)."
                                if evt_type == TelemetryEventType.AGENT_COMPLETED
                                else f"Agent {res.agent_id} failed: {res.summary[:200]}"
                            ),
                        )
                    )
                except Exception:
                    pass
            return results

        pool = ThreadPoolExecutor(max_workers=min(self.max_workers, len(prepared)))
        future_entries: List[Tuple[Any, AgentRequest, float]] = []
        try:
            for req, handler, isolated_data in prepared:
                if event_callback:
                    try:
                        event_callback(
                            OrchestratorTelemetryEvent(
                                request_id=request_id,
                                session_id=context.session_id,
                                event_type=TelemetryEventType.AGENT_STARTED,
                                timestamp=time.time(),
                                agent_name=req.agent_id,
                                status="running",
                                stage=1,
                                message=f"Agent {req.agent_id} started parallel domain analysis.",
                            )
                        )
                    except Exception:
                        pass
                fut = pool.submit(
                    self._invoke_with_retry,
                    req=req,
                    handler=handler,
                    context=context,
                    isolated_data=isolated_data,
                    per_attempt_timeout_s=self.per_agent_timeout_seconds,
                )
                future_entries.append((fut, req, time.monotonic()))

            for fut, req, submitted_mono in future_entries:
                rem = context.remaining_seconds()
                res: Optional[AgentResult] = None
                if rem <= 0.0:
                    res = self._build_failure_result(
                        request=req,
                        status=AgentStatus.TIMEOUT,
                        code="ORCHESTRATION_TIMEOUT",
                        message=f"{req.agent_id} did not finish before request deadline.",
                        elapsed_ms=(time.monotonic() - submitted_mono) * 1000.0,
                        timed_out=True,
                    )
                else:
                    wait_s = max(0.02, min(self.per_agent_timeout_seconds * (1 + self.max_retries) + 0.5, rem))
                    try:
                        res = fut.result(timeout=wait_s)
                    except FuturesTimeoutError:
                        res = self._build_failure_result(
                            request=req,
                            status=AgentStatus.TIMEOUT,
                            code="AGENT_TIMEOUT",
                            message=f"{req.agent_id} exceeded per-agent execution deadline.",
                            elapsed_ms=(time.monotonic() - submitted_mono) * 1000.0,
                            timed_out=True,
                        )
                    except Exception as exc:
                        res = self._build_failure_result(
                            request=req,
                            status=AgentStatus.ERROR,
                            code="AGENT_EXECUTION_ERROR",
                            message=f"{req.agent_id} failed: {sanitize_text(str(exc))}",
                            elapsed_ms=(time.monotonic() - submitted_mono) * 1000.0,
                        )
                results.append(res)
                if event_callback and res is not None:
                    try:
                        evt_type = (
                            TelemetryEventType.AGENT_COMPLETED
                            if res.status in (AgentStatus.SUCCESS, AgentStatus.PARTIAL)
                            else TelemetryEventType.AGENT_FAILED
                        )
                        event_callback(
                            OrchestratorTelemetryEvent(
                                request_id=request_id,
                                session_id=context.session_id,
                                event_type=evt_type,
                                timestamp=time.time(),
                                agent_name=res.agent_id,
                                status=res.status.value,
                                duration_ms=res.execution.elapsed_ms,
                                stage=1,
                                message=(
                                    f"Agent {res.agent_id} completed domain analysis ({round(res.execution.elapsed_ms, 1)}ms)."
                                    if evt_type == TelemetryEventType.AGENT_COMPLETED
                                    else f"Agent {res.agent_id} failed: {res.summary[:200]}"
                                ),
                            )
                        )
                    except Exception:
                        pass
        finally:
            pool.shutdown(wait=False, cancel_futures=True)

        return results

    def _execute_stage2_sequential(
        self,
        *,
        agent_ids: Sequence[str],
        stage1_results: Sequence[AgentResult],
        plan: RoutingPlan,
        request_id: str,
        trace_id: str,
        context: AgentContext,
        filters: Dict[str, Any],
        data: Dict[str, pd.DataFrame],
        event_callback: Optional[Callable[[OrchestratorTelemetryEvent], None]] = None,
    ) -> List[AgentResult]:
        if not agent_ids:
            return []

        upstream_findings = [
            {
                "agent_id": res.agent_id,
                "status": res.status.value,
                "summary": neutralize_untrusted_text(res.summary[:300]),
                "metrics": {
                    k: v
                    for k, v in res.metrics.items()
                    if isinstance(v, (int, float, str, bool))
                },
                "facts": [
                    {
                        "label": f.label,
                        "value": f.value,
                        "unit": f.unit,
                        "kpi_id": f.kpi_id,
                        "source": f.source,
                    }
                    for f in res.facts
                    if f.value is not None
                ],
            }
            for res in stage1_results
            if res.status in (AgentStatus.SUCCESS, AgentStatus.PARTIAL)
        ]

        results: List[AgentResult] = []
        for aid in agent_ids:
            task, blocked_res = self._prepare_agent_task(
                agent_id=aid,
                parent_request_id=request_id,
                trace_id=trace_id,
                context=context,
                user_query=plan.resolved_query,
                intent=plan.agent_intents.get(aid, "decision_synthesis"),
                filters=filters,
                data=data,
                metadata={"upstream_findings": upstream_findings},
            )
            if blocked_res is not None:
                results.append(blocked_res)
                if event_callback:
                    try:
                        event_callback(
                            OrchestratorTelemetryEvent(
                                request_id=request_id,
                                session_id=context.session_id,
                                event_type=TelemetryEventType.AGENT_FAILED,
                                timestamp=time.time(),
                                agent_name=aid,
                                status=blocked_res.status.value,
                                stage=2,
                                message=f"Agent {aid} blocked: {blocked_res.summary[:200]}",
                            )
                        )
                    except Exception:
                        pass
                continue
            if task is None:
                continue

            req, handler, isolated_data = task
            if event_callback:
                try:
                    event_callback(
                        OrchestratorTelemetryEvent(
                            request_id=request_id,
                            session_id=context.session_id,
                            event_type=TelemetryEventType.AGENT_STARTED,
                            timestamp=time.time(),
                            agent_name=req.agent_id,
                            status="running",
                            stage=2,
                            message=f"Agent {req.agent_id} started decision synthesis with upstream findings.",
                        )
                    )
                except Exception:
                    pass

            res = self._invoke_with_retry(
                req=req,
                handler=handler,
                context=context,
                isolated_data=isolated_data,
                per_attempt_timeout_s=self.per_agent_timeout_seconds,
            )
            results.append(res)
            if event_callback:
                try:
                    evt_type = (
                        TelemetryEventType.AGENT_COMPLETED
                        if res.status in (AgentStatus.SUCCESS, AgentStatus.PARTIAL)
                        else TelemetryEventType.AGENT_FAILED
                    )
                    event_callback(
                        OrchestratorTelemetryEvent(
                            request_id=request_id,
                            session_id=context.session_id,
                            event_type=evt_type,
                            timestamp=time.time(),
                            agent_name=res.agent_id,
                            status=res.status.value,
                            duration_ms=res.execution.elapsed_ms,
                            stage=2,
                            message=(
                                f"Agent {res.agent_id} completed decision synthesis ({round(res.execution.elapsed_ms, 1)}ms)."
                                if evt_type == TelemetryEventType.AGENT_COMPLETED
                                else f"Agent {res.agent_id} failed: {res.summary[:200]}"
                            ),
                        )
                    )
                except Exception:
                    pass

        return results

    def orchestrate(
        self,
        query: str,
        *,
        principal: Optional[Any] = None,
        principal_id: Optional[str] = None,
        principal_role: Optional[str] = None,
        principal_scopes: Optional[Sequence[str]] = None,
        session_id: str = "default",
        data: Optional[Dict[str, pd.DataFrame]] = None,
        sqlite_conn: Any = None,
        filters: Optional[Dict[str, Any]] = None,
        timeout_seconds: Optional[float] = None,
        ai_provider: Any = None,
        cancel_immediately: bool = False,
        event_callback: Optional[Callable[[OrchestratorTelemetryEvent], None]] = None,
    ) -> OrchestrationOutcome:
        """
        Execute end-to-end multi-agent orchestration for `query` under strict
        principal isolation, RBAC gating, concurrent safety, and OutputVerifier checks.
        """
        t0 = time.monotonic()
        raw_q = (query or "").strip()
        if not raw_q:
            raise ValueError("Query cannot be blank.")
        if len(raw_q) > 4000:
            raise ValueError("Query exceeds maximum length (4000 characters).")

        pid, role, scopes = self._resolve_principal_args(
            principal=principal,
            principal_id=principal_id,
            principal_role=principal_role,
            principal_scopes=principal_scopes,
        )
        effective_timeout = timeout_seconds if timeout_seconds is not None else self.default_timeout_seconds
        acquired = self._concurrency_semaphore.acquire(timeout=max(0.05, min(effective_timeout, 2.0)))
        if not acquired:
            req_id = new_id("req_")
            trace_obj = self.tracer.start_trace(request_id=req_id, principal_id=pid, session_id=session_id)
            overloaded_plan = RoutingPlan(
                raw_query=raw_q,
                resolved_query=raw_q,
                mode=OrchestrationMode.GENERAL_ASSISTANT,
                legacy_route="GENERAL",
                requires_business_data=False,
                reasoning="Orchestrator concurrency ceiling reached; safe overload fallback returned.",
            )
            err = AgentError(
                code="CONCURRENCY_LIMIT_EXCEEDED",
                message="Orchestrator is currently at maximum concurrent capacity; please retry shortly.",
                agent_id=self.AGENT_ID,
                recoverable=True,
            )
            res = AgentResult(
                request_id=req_id,
                execution_id=req_id,
                agent_id=self.AGENT_ID,
                domain=AgentDomain.ORCHESTRATION,
                status=AgentStatus.TIMEOUT,
                summary=err.message,
                narrative=f"### Temporary Capacity Limit\n\n{err.message}",
                errors=[err],
                execution=AgentExecutionMetadata(
                    request_id=req_id,
                    execution_id=req_id,
                    agent_id=self.AGENT_ID,
                    elapsed_ms=round(max(0.0, (time.monotonic() - t0) * 1000.0), 3),
                    timed_out=True,
                ),
            )
            trace = self.tracer.finish_trace(
                req_id,
                status=AgentStatus.TIMEOUT,
                verification_outcome=TraceVerificationOutcome.REJECTED,
            )
            if event_callback:
                try:
                    event_callback(
                        OrchestratorTelemetryEvent(
                            request_id=req_id,
                            session_id=session_id,
                            event_type=TelemetryEventType.EXECUTION_FAILED,
                            timestamp=time.time(),
                            status="timeout",
                            message="Orchestrator concurrency ceiling reached; please retry shortly.",
                        )
                    )
                except Exception:
                    pass
            return OrchestrationOutcome(
                request_id=req_id,
                trace_id=trace_obj.trace_id,
                routing_plan=overloaded_plan,
                agent_result=res,
                trace=trace,
            )

        try:
            return self._orchestrate_within_slot(
                raw_q=raw_q,
                pid=pid,
                role=role,
                scopes=scopes,
                principal=principal,
                principal_id=principal_id,
                session_id=session_id,
                data=data,
                sqlite_conn=sqlite_conn,
                filters=filters,
                effective_timeout=effective_timeout,
                ai_provider=ai_provider,
                cancel_immediately=cancel_immediately,
                t0=t0,
                event_callback=event_callback,
            )
        finally:
            self._concurrency_semaphore.release()

    def _orchestrate_within_slot(
        self,
        *,
        raw_q: str,
        pid: str,
        role: str,
        scopes: Set[str],
        principal: Optional[Any],
        principal_id: Optional[str],
        session_id: str,
        data: Optional[Dict[str, pd.DataFrame]],
        sqlite_conn: Any,
        filters: Optional[Dict[str, Any]],
        effective_timeout: float,
        ai_provider: Any,
        cancel_immediately: bool,
        t0: float,
        event_callback: Optional[Callable[[OrchestratorTelemetryEvent], None]] = None,
    ) -> OrchestrationOutcome:
        request_id = new_id("req_")

        def _emit(
            event_type: TelemetryEventType,
            status: str,
            message: str,
            agent_name: Optional[str] = None,
            duration_ms: Optional[float] = None,
            stage: Optional[int] = None,
            data_dict: Optional[Dict[str, Any]] = None,
        ) -> None:
            if event_callback is None:
                return
            try:
                evt = OrchestratorTelemetryEvent(
                    request_id=request_id,
                    session_id=session_id,
                    event_type=event_type,
                    timestamp=time.time(),
                    agent_name=agent_name,
                    status=status,
                    duration_ms=duration_ms,
                    message=message,
                    stage=stage,
                    data=data_dict,
                )
                event_callback(evt)
            except Exception:
                pass

        _emit(
            TelemetryEventType.QUERY_RECEIVED,
            status="received",
            message="User query received and accepted for processing.",
        )

        try:
            cleaned_query, injection_flags, is_pure_injection = sanitize_user_query(raw_q)
            if is_pure_injection:
                trace_obj = self.tracer.start_trace(request_id=request_id, principal_id=pid, session_id=session_id)
                blocked_plan = RoutingPlan(
                    raw_query=sanitize_text(raw_q),
                    resolved_query=cleaned_query or "[BLOCKED_INJECTION]",
                    mode=OrchestrationMode.GENERAL_ASSISTANT,
                    legacy_route="GENERAL",
                    requires_business_data=False,
                    reasoning=f"Prompt injection / secret exfiltration blocked ({', '.join(injection_flags)}).",
                )
                msg = (
                    "Request blocked by prompt-injection defense: untrusted instruction override, "
                    "delimiter hijack, or credential/system-table exfiltration directives are not permitted."
                )
                err = AgentError(
                    code="PROMPT_INJECTION_BLOCKED",
                    message=msg,
                    agent_id=self.AGENT_ID,
                    recoverable=False,
                )
                res = AgentResult(
                    request_id=request_id,
                    execution_id=request_id,
                    agent_id=self.AGENT_ID,
                    domain=AgentDomain.ORCHESTRATION,
                    status=AgentStatus.BLOCKED,
                    summary=msg,
                    narrative=f"### Security Guardrail Block\n\n{msg}",
                    errors=[err],
                    data_gaps=[f"Blocked injection categories: {', '.join(injection_flags)}"],
                    execution=AgentExecutionMetadata(
                        request_id=request_id,
                        execution_id=request_id,
                        agent_id=self.AGENT_ID,
                        elapsed_ms=round(max(0.0, (time.monotonic() - t0) * 1000.0), 3),
                    ),
                )
                trace = self.tracer.finish_trace(
                    request_id,
                    status=AgentStatus.BLOCKED,
                    verification_outcome=TraceVerificationOutcome.REJECTED,
                )
                _emit(
                    TelemetryEventType.EXECUTION_FAILED,
                    status="blocked",
                    message="Request blocked by prompt-injection security guardrail.",
                )
                return OrchestrationOutcome(
                    request_id=request_id,
                    trace_id=trace_obj.trace_id,
                    routing_plan=blocked_plan,
                    agent_result=res,
                    trace=trace,
                    grounding_verified_override=False,
                    verification_outcome_override="rejected",
                )

            # 1. Resolve principal-scoped conversation history cleanly
            principal_ref = principal if principal is not None else pid
            effective_q = cleaned_query if injection_flags else raw_q
            (
                augmented_q,
                resolved_intent,
                last_topic,
                effective_filters,
                remembered_entities,
            ) = resolve_follow_up_query_and_context(
                effective_q,
                session_id,
                principal=principal_ref,
                explicit_filters=filters,
            )
            classification = classify_query(augmented_q, last_topic)
            if resolved_intent and classification.get("requires_business_data", False):
                classification["intent"] = resolved_intent

            plan = self.router.route(
                raw_q,
                augmented_q,
                last_topic=last_topic,
                classification=classification,
            )

            _emit(
                TelemetryEventType.INTENT_CLASSIFIED,
                status="classified",
                message=f"Intent classified: {plan.mode.value} (route: {plan.legacy_route}).",
                data_dict={
                    "mode": plan.mode.value,
                    "route": plan.legacy_route,
                    "stage1_agents": list(plan.stage1_parallel_agents),
                    "stage2_agents": list(plan.stage2_sequential_agents),
                },
            )

            history = get_session_history(session_id, principal=principal_ref)
            conv_summaries = [
                ConversationTurnSummary(
                    role=str(h.get("role", "user"))[:32],
                    content=str(h.get("content", ""))[:400],
                    intent=h.get("intent"),
                    context_topic=h.get("context_topic"),
                    filters=h.get("filters"),
                    entities=h.get("entities"),
                )
                for h in history[-6:]
            ]

            context = AgentContext(
                principal_id=pid,
                principal_role=role,
                principal_scopes=scopes,
                session_id=session_id,
                user_query=plan.resolved_query,
                request_id=request_id,
                business_domains=[AgentDomain.ORCHESTRATION],
                timeout_seconds=effective_timeout,
                filters=dict(effective_filters),
                conversation_context=conv_summaries,
                remembered_entities=dict(remembered_entities),
                load_default_kpis=False,
            )
            self.context_manager.put_context(context)
            trace_obj = self.tracer.start_trace(
                request_id=request_id,
                principal_id=context.principal_id,
                session_id=context.session_id,
            )
            trace_id = trace_obj.trace_id
            if cancel_immediately:
                context.cancel("Cancelled prior to execution.")

            # 2. General / Non-Business fast path
            if plan.mode == OrchestrationMode.GENERAL_ASSISTANT:
                _emit(
                    TelemetryEventType.AGENT_STARTED,
                    status="running",
                    message="Processing general assistant inquiry.",
                    agent_name="master_orchestrator",
                )
                outcome = self._handle_general_query(
                    request_id=request_id,
                    trace_id=trace_id,
                    plan=plan,
                    context=context,
                    ai_provider=ai_provider,
                    t0=t0,
                )
                outcome.active_filters = dict(effective_filters)
                outcome.remembered_entities = dict(remembered_entities)
                record_turn(
                    session_id,
                    "user",
                    raw_q,
                    plan.legacy_route,
                    "general",
                    principal=principal_ref,
                    filters=effective_filters,
                    entities=remembered_entities,
                )
                record_turn(
                    session_id,
                    "assistant",
                    outcome.agent_result.summary,
                    plan.legacy_route,
                    "general",
                    principal=principal_ref,
                    filters=effective_filters,
                    entities=remembered_entities,
                )
                _emit(
                    TelemetryEventType.RESPONSE_COMPLETED,
                    status="completed",
                    duration_ms=outcome.agent_result.execution.elapsed_ms,
                    message="General response generated successfully.",
                    agent_name="master_orchestrator",
                    data_dict=outcome.to_chat_response(),
                )
                return outcome

            # 3. Load dataset store lazily once
            ensure_python_path()
            active_data: Dict[str, pd.DataFrame]
            if data is not None:
                active_data = data
            else:
                from api.loader import load_data

                active_data, _ = load_data()

            # 4. Read-only AST-verified SQL sandbox route
            if plan.mode == OrchestrationMode.SQL_SANDBOX:
                _emit(
                    TelemetryEventType.AGENT_STARTED,
                    status="running",
                    message="Executing verified read-only SQL query against database.",
                    agent_name="sql_sandbox",
                )
                outcome = self._handle_sql_sandbox(
                    request_id=request_id,
                    trace_id=trace_id,
                    plan=plan,
                    context=context,
                    data=active_data,
                    sqlite_conn=sqlite_conn,
                    t0=t0,
                )
                outcome.active_filters = dict(effective_filters)
                outcome.remembered_entities = dict(remembered_entities)
                record_turn(
                    session_id,
                    "user",
                    raw_q,
                    "NL2SQL",
                    plan.context_topic,
                    principal=principal_ref,
                    filters=effective_filters,
                    entities=remembered_entities,
                )
                record_turn(
                    session_id,
                    "assistant",
                    outcome.agent_result.summary,
                    "NL2SQL",
                    plan.context_topic,
                    principal=principal_ref,
                    filters=effective_filters,
                    entities=remembered_entities,
                )
                _emit(
                    TelemetryEventType.AGENT_COMPLETED,
                    status="completed",
                    duration_ms=outcome.agent_result.execution.elapsed_ms,
                    message="SQL sandbox query executed successfully.",
                    agent_name="sql_sandbox",
                )
                _emit(
                    TelemetryEventType.RESPONSE_COMPLETED,
                    status="completed",
                    duration_ms=outcome.agent_result.execution.elapsed_ms,
                    message="SQL sandbox response generated successfully.",
                    agent_name="sql_sandbox",
                    data_dict=outcome.to_chat_response(),
                )
                return outcome

            # 5. Stage 1 Concurrent Independent Domain Agents
            clean_filters = dict(effective_filters)
            stage1_results = self._execute_stage1_parallel(
                agent_ids=plan.stage1_parallel_agents,
                plan=plan,
                request_id=request_id,
                trace_id=trace_id,
                context=context,
                filters=clean_filters,
                data=active_data,
                event_callback=event_callback,
            )

            # 6. Stage 2 Sequential Dependent Agents (e.g. DecisionAgent receiving upstream findings)
            stage2_results = self._execute_stage2_sequential(
                agent_ids=plan.stage2_sequential_agents,
                stage1_results=stage1_results,
                plan=plan,
                request_id=request_id,
                trace_id=trace_id,
                context=context,
                filters=clean_filters,
                data=active_data,
                event_callback=event_callback,
            )
            all_child_results = stage1_results + stage2_results

            # 7. Cross-Agent Synthesis & OutputVerifier Gate
            _emit(
                TelemetryEventType.SYNTHESIS_STARTED,
                status="synthesizing",
                message="Cross-agent synthesis and verification started.",
            )

            synthesis = synthesize_agent_results(
                user_query=plan.resolved_query,
                agent_results=all_child_results,
                verifier=self.verifier,
                kpi_catalog=get_certified_kpi_catalog(),
            )
            if injection_flags:
                sec_note = f"Prompt injection directive stripped ({', '.join(injection_flags)}) prior to routing."
                if sec_note not in synthesis.limitations:
                    synthesis = synthesis.model_copy(
                        update={"limitations": list(synthesis.limitations) + [sec_note]}
                    )

            # Optional compatibility enrichment for simulation / RCA React cards (without fabricating numbers)
            sim_payload: Optional[Dict[str, Any]] = None
            rca_payload: Optional[Dict[str, Any]] = None
            if plan.legacy_route == "SIMULATION":
                try:
                    sim_payload = execute_conversational_simulation(plan.resolved_query, active_data)
                except Exception:
                    sim_payload = None
            elif plan.legacy_route == "ROOT_CAUSE":
                try:
                    rca_payload = perform_root_cause_analysis(plan.resolved_query, active_data)
                except Exception:
                    rca_payload = None

            legacy_metrics = _format_legacy_metric_cards(all_child_results)
            elapsed_ms = round(max(0.0, (time.monotonic() - t0) * 1000.0), 3)

            consolidated_result = AgentResult(
                request_id=request_id,
                execution_id=request_id,
                agent_id=self.AGENT_ID,
                domain=AgentDomain.ORCHESTRATION,
                status=synthesis.status,
                summary=synthesis.consolidated_summary,
                narrative=synthesis.consolidated_narrative,
                facts=synthesis.facts,
                metrics=synthesis.metrics,
                table_rows=synthesis.table_rows,
                charts=synthesis.charts,
                recommendations=synthesis.recommendations,
                caveats=synthesis.caveats,
                provenance=synthesis.provenance,
                sql_traces=synthesis.sql_traces,
                errors=synthesis.errors,
                is_confirmed_loss=synthesis.is_confirmed_loss,
                data_gaps=synthesis.limitations,
                execution=AgentExecutionMetadata(
                    request_id=request_id,
                    execution_id=request_id,
                    agent_id=self.AGENT_ID,
                    agent_version=self.VERSION,
                    elapsed_ms=elapsed_ms,
                    timed_out=(synthesis.status == AgentStatus.TIMEOUT),
                    cancelled=(synthesis.status == AgentStatus.CANCELLED),
                ),
            )

            ver_map = {
                VerificationOutcome.VERIFIED: TraceVerificationOutcome.VERIFIED,
                VerificationOutcome.PARTIAL: TraceVerificationOutcome.PARTIAL,
                VerificationOutcome.REJECTED: TraceVerificationOutcome.REJECTED,
            }
            trace_ver = ver_map.get(synthesis.verification_report.outcome, TraceVerificationOutcome.PARTIAL)
            final_trace = self.tracer.finish_trace(
                request_id,
                status=synthesis.status,
                verification_outcome=trace_ver,
            )

            _emit(
                TelemetryEventType.VERIFICATION_COMPLETED,
                status=synthesis.verification_report.outcome.value,
                message=f"Output verification completed: {synthesis.verification_report.outcome.value}.",
                data_dict={
                    "outcome": synthesis.verification_report.outcome.value,
                    "is_verified": synthesis.verification_report.is_verified,
                    "supported_claims_count": synthesis.verification_report.supported_claims_count,
                    "unsupported_claims_count": len(synthesis.verification_report.unsupported_claims),
                    "violations_count": len(synthesis.verification_report.violations),
                },
            )

            # Extract verifiable facts to remember for follow-ups (provenance-backed facts)
            facts_to_remember: Dict[str, Any] = {}
            if synthesis.facts:
                for gf in synthesis.facts[:5]:
                    facts_to_remember[gf.fact_id] = {
                        "value": gf.value,
                        "label": gf.label,
                        "source": gf.source,
                        "unit": gf.unit or "",
                    }

            # Record principal-isolated conversation turn for follow-up queries
            safe_turn_q = effective_q if injection_flags else raw_q
            record_turn(
                session_id,
                "user",
                safe_turn_q,
                plan.legacy_route,
                plan.context_topic,
                principal=principal_ref,
                filters=clean_filters,
                entities=remembered_entities,
            )
            record_turn(
                session_id,
                "assistant",
                synthesis.consolidated_summary,
                plan.legacy_route,
                plan.context_topic,
                principal=principal_ref,
                filters=clean_filters,
                entities=remembered_entities,
                facts=facts_to_remember if facts_to_remember else None,
            )

            outcome = OrchestrationOutcome(
                request_id=request_id,
                trace_id=trace_id,
                routing_plan=plan,
                agent_result=consolidated_result,
                child_results=all_child_results,
                synthesis=synthesis,
                trace=final_trace,
                provider_status="offline-deterministic",
                root_cause_payload=rca_payload,
                simulation_payload=sim_payload,
                legacy_verified_metrics=legacy_metrics,
                active_filters=clean_filters,
                remembered_entities=remembered_entities,
            )

            _emit(
                TelemetryEventType.RESPONSE_COMPLETED,
                status=synthesis.status.value,
                duration_ms=elapsed_ms,
                message="Multi-agent orchestration completed successfully.",
                data_dict=outcome.to_chat_response(),
            )

            return outcome
        except Exception as exc:
            _emit(
                TelemetryEventType.EXECUTION_FAILED,
                status="failed",
                message=f"Execution error: {sanitize_text(str(exc))[:200]}",
            )
            raise
