"""
NovaNest Decision Intelligence Agent (Phase 06.2)
-------------------------------------------------
Synthesizes cross-domain platform state, empirical Root Cause Analysis (RCA),
Digital Twin systemic risk / ripple chains, What-If scenario simulations,
and grounded Next Best Actions across Financial, Customer, Operations, and Restaurant engines.

Strict Grounding & Security Rules:
- Requires `operator` (or `admin`) RBAC scope.
- Permitted SQL tables: `orders`, `customers`, `restaurants`, `deliveries`, `riders`, `promotions`.
- Never fabricates recommendations, savings, or guaranteed simulation outcomes.
- Preserves `is_confirmed_loss=False` on all leakage / discount subsidy references and
  tags all Phase 05 ML / heuristic simulations cleanly with `is_production_ready=False`.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd

from python.ai.agents.base import (
    BaseDomainAgent,
    ensure_python_path,
    filter_df_by_city,
    make_provenance,
    safe_round,
    sanitize_scalar,
    sanitize_table_rows,
)
from python.ai.agents.context import AgentContext
from python.ai.agents.contracts import (
    ActionRecommendation,
    AgentDomain,
    AgentError,
    AgentRequest,
    AgentResult,
    AgentStatus,
    ChartSpec,
    DataProvenance,
    GroundedFact,
    ModelCaveat,
    SeverityLevel,
    SqlAuditTrace,
    sanitize_text,
)


def _infer_decision_intent(request: AgentRequest) -> str:
    if request.intent:
        return request.intent.strip().lower()
    q = request.user_query.lower()
    if any(k in q for k in ("what if", "what-if", "simulat", "scenario", "increase", "decrease", "reduce", "cap")):
        return "what_if_simulation"
    if any(k in q for k in ("why", "root cause", "cause", "reason", "driver")):
        return "root_cause"
    if any(k in q for k in ("twin", "ripple", "cascade", "systemic", "chain")):
        return "systemic_risk"
    if any(k in q for k in ("recommend", "action", "next best", "nba", "strategy", "priorit")):
        return "next_best_action"
    return "decision_synthesis"


def _infer_impact_event(query: str) -> str:
    q = query.lower()
    if any(k in q for k in ("discount", "subsidy", "leak", "promo")):
        return "discount_subsidy_surge"
    if any(k in q for k in ("surge", "spike", "demand")):
        return "demand_spike"
    if any(k in q for k in ("restaurant", "merchant", "partner", "cancel")):
        return "merchant_churn"
    return "operations_delay"


class DecisionAgent(BaseDomainAgent):
    """Domain intelligence agent for RCA, What-If simulations, Digital Twin, and NBA synthesis."""

    AGENT_ID = "decision_agent"
    DOMAIN = AgentDomain.DECISION
    VERSION = "1.0.0"
    DESCRIPTION = (
        "Executes empirical root-cause analysis, what-if scenario simulations, Digital Twin systemic "
        "risk mapping, and Next-Best-Action synthesis under strict numerical grounding."
    )
    CAPABILITIES = (
        "business_recommendations",
        "root_cause_analysis",
        "what_if_simulations",
        "systemic_risk_assessment",
        "cross_domain_synthesis",
    )
    SUPPORTED_INTENTS = (
        "decision_synthesis",
        "root_cause",
        "what_if_simulation",
        "systemic_risk",
        "next_best_action",
        "sql",
    )
    ALLOWED_TABLES = ("orders", "customers", "restaurants", "deliveries", "riders", "promotions")
    ALLOWED_DATASETS = (
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
    )
    REQUIRED_SCOPES = ("operator",)

    def _generate_grounded_nbas(
        self,
        *,
        orders: pd.DataFrame,
        customers: pd.DataFrame,
        restaurants: pd.DataFrame,
        churn_df: pd.DataFrame,
        alerts_df: pd.DataFrame,
        leakage_df: pd.DataFrame,
        data_gaps: List[str],
    ) -> List[ActionRecommendation]:
        ensure_python_path()
        from python.decision.next_best_action import (
            generate_customer_next_best_actions,
            generate_operational_next_best_actions,
            generate_restaurant_next_best_actions,
        )

        recs: List[ActionRecommendation] = []
        raw_actions: List[Dict[str, Any]] = []

        if not orders.empty and not customers.empty:
            try:
                from python.intelligence.customer.clv import calculate_customer_clv
                from python.intelligence.customer.rfm import calculate_advanced_rfm

                rfm_df = calculate_advanced_rfm(orders, customers)
                clv_df = calculate_customer_clv(orders, customers)
                if churn_df is not None and not churn_df.empty:
                    raw_actions.extend(generate_customer_next_best_actions(churn_df, clv_df, rfm_df))
                else:
                    data_gaps.append("customer_churn_predictions missing: customer NBA rules omitted")
            except Exception as exc:
                data_gaps.append(f"Customer NBA engine skipped: {exc}")

        if not orders.empty and not restaurants.empty:
            try:
                from python.intelligence.restaurant.benchmarking import calculate_restaurant_benchmarks
                from python.intelligence.restaurant.health_score import calculate_restaurant_health_score
                from python.intelligence.restaurant.risk_detection import detect_restaurant_risks

                health_df = calculate_restaurant_health_score(restaurants, orders)
                risk_df = detect_restaurant_risks(health_df)
                bench_df = calculate_restaurant_benchmarks(health_df)
                raw_actions.extend(generate_restaurant_next_best_actions(risk_df, bench_df))
            except Exception as exc:
                data_gaps.append(f"Restaurant NBA engine skipped: {exc}")

        if (alerts_df is not None and not alerts_df.empty) or (leakage_df is not None and not leakage_df.empty):
            try:
                raw_actions.extend(generate_operational_next_best_actions(alerts_df, leakage_df))
            except Exception as exc:
                data_gaps.append(f"Operational NBA engine skipped: {exc}")

        for item in raw_actions[:12]:
            if not isinstance(item, dict):
                continue
            target_type = str(item.get("target_type", "Platform"))
            evidence = str(item.get("detected_condition", ""))
            is_rev_ops = "revenue" in target_type.lower() or "leakage" in evidence.lower()
            confidence = (
                "Unconfirmed Heuristic Screening (is_confirmed_loss=False)"
                if is_rev_ops
                else "Empirically Derived From Platform Datasets"
            )
            expected_impact = str(item.get("reason", ""))
            if is_rev_ops:
                expected_impact = f"{expected_impact} (Unconfirmed screening exposure; no verified net savings claimed.)"
            recs.append(
                ActionRecommendation(
                    title=sanitize_text(str(item.get("entity_name", "Strategic Action")))[:200],
                    target_type=sanitize_text(target_type)[:80],
                    entity_id=sanitize_text(str(item.get("entity_id", "")))[:80],
                    evidence=sanitize_text(evidence)[:500],
                    expected_impact=sanitize_text(expected_impact)[:500],
                    confidence=confidence,
                    action=sanitize_text(str(item.get("recommended_action", "")))[:500],
                    priority=sanitize_text(str(item.get("priority", "Medium")))[:32],
                    recommendation_id=str(item.get("recommendation_id", f"REC-DEC-{len(recs)+1:03d}")),
                    business_problem=sanitize_text(str(item.get("reason", evidence)))[:500],
                    proposed_action=sanitize_text(str(item.get("recommended_action", "")))[:500],
                    expected_benefit=sanitize_text(str(item.get("expected_benefit", expected_impact)))[:500],
                    implementation_cost=float(item.get("implementation_cost", 0.0)),
                    net_financial_impact=float(item.get("net_financial_impact", 0.0)),
                    risk_and_uncertainty=sanitize_text(str(item.get("risk_and_uncertainty", "Subject to operational variance; requires human review.")))[:500],
                    confidence_tier=str(item.get("confidence_tier", "OPERATIONAL_GATED" if is_rev_ops else "MODERATE")),
                    measurement_period=str(item.get("measurement_period", "30 days")),
                    success_metric=sanitize_text(str(item.get("success_metric", "Operational metric recovery")))[:200],
                    lifecycle_status=str(item.get("lifecycle_status", "Proposed")),
                    human_approval_required=bool(item.get("human_approval_required", True)),
                    is_simulation_projection=bool(item.get("is_simulation_projection", True)),
                )
            )
        return recs

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
        ensure_python_path()
        intent = _infer_decision_intent(request)
        city_filter = request.filters.get("city")
        filters_desc = [f"city={city_filter}"] if city_filter else []

        orders_raw = data.get("orders", pd.DataFrame())
        customers_raw = data.get("customers", pd.DataFrame())
        restaurants_raw = data.get("restaurants", pd.DataFrame())
        deliveries_raw = data.get("deliveries", pd.DataFrame())
        riders_raw = data.get("riders", pd.DataFrame())
        churn_raw = data.get("customer_churn_predictions", pd.DataFrame())
        alerts_raw = data.get("operational_alerts", pd.DataFrame())
        leakage_raw = data.get("revenue_leakage", pd.DataFrame())
        orders_eng_raw = data.get("orders_engineered", pd.DataFrame())

        if orders_raw.empty:
            return AgentResult(
                request_id=request.request_id,
                execution_id=request.execution_id,
                agent_id=self.AGENT_ID,
                domain=self.DOMAIN,
                status=AgentStatus.BLOCKED,
                summary="Primary 'orders' dataset is missing or empty; decision intelligence blocked.",
                provenance=[make_provenance(data_source_label, "orders", orders_raw)],
                errors=[
                    AgentError(
                        code="MISSING_PRIMARY_DATASET",
                        message="Primary 'orders' dataset is required for decision intelligence.",
                        agent_id=self.AGENT_ID,
                        recoverable=True,
                        severity=SeverityLevel.ERROR,
                    )
                ],
                data_gaps=["orders dataset missing or empty"],
            )

        # Apply optional city scope consistently across tables
        restaurants = filter_df_by_city(restaurants_raw, city_filter) if city_filter else restaurants_raw
        customers = filter_df_by_city(customers_raw, city_filter) if city_filter else customers_raw
        riders = filter_df_by_city(riders_raw, city_filter) if city_filter else riders_raw
        orders = orders_raw
        deliveries = deliveries_raw
        orders_eng = orders_eng_raw
        if city_filter:
            if not restaurants.empty and "restaurant_id" in orders.columns:
                orders = orders[orders["restaurant_id"].isin(set(restaurants["restaurant_id"]))].copy()
            elif not customers.empty and "customer_id" in orders.columns:
                orders = orders[orders["customer_id"].isin(set(customers["customer_id"]))].copy()
            else:
                orders = filter_df_by_city(orders, city_filter)
            if not deliveries.empty and "order_id" in deliveries.columns:
                deliveries = deliveries[deliveries["order_id"].isin(set(orders["order_id"]))].copy()
            if not orders_eng.empty and "order_id" in orders_eng.columns:
                orders_eng = orders_eng[orders_eng["order_id"].isin(set(orders["order_id"]))].copy()

        data_gaps: List[str] = []
        if orders.empty:
            return AgentResult(
                request_id=request.request_id,
                execution_id=request.execution_id,
                agent_id=self.AGENT_ID,
                domain=self.DOMAIN,
                status=AgentStatus.PARTIAL,
                summary=f"No orders matched city filter '{city_filter}'.",
                provenance=[make_provenance(data_source_label, "orders", orders_raw, filters_applied=filters_desc)],
                data_gaps=[f"Zero matching orders for city '{city_filter}'"],
            )

        scoped_bundle: Dict[str, pd.DataFrame] = {
            "orders": orders,
            "customers": customers,
            "restaurants": restaurants,
            "deliveries": deliveries,
            "riders": riders,
            "orders_engineered": orders_eng,
            "customer_churn_predictions": churn_raw,
            "operational_alerts": alerts_raw,
            "revenue_leakage": leakage_raw,
            "ratings_reviews": data.get("ratings_reviews", pd.DataFrame()),
            "promotions": data.get("promotions", pd.DataFrame()),
        }

        # Check upstream findings for pre-computed metrics from Stage 1 (Zero-Copy Metric Reuse)
        upstream_list = request.metadata.get("upstream_findings") or []
        upstream_facts_map: Dict[str, Any] = {}
        upstream_metrics_map: Dict[str, Any] = {}
        if isinstance(upstream_list, list):
            for item in upstream_list:
                if isinstance(item, dict):
                    m = item.get("metrics") or {}
                    if isinstance(m, dict):
                        upstream_metrics_map.update(m)
                    for f in item.get("facts") or []:
                        if isinstance(f, dict):
                            if f.get("kpi_id"):
                                upstream_facts_map[f["kpi_id"]] = f.get("value")
                            if f.get("label"):
                                upstream_facts_map[f["label"]] = f.get("value")

        # Core cross-domain aligned baseline metrics (must align identically with Financial/Ops/Rest/Customer!)
        if not city_filter and "KPI-01" in upstream_facts_map and "KPI-02" in upstream_facts_map:
            gmv_inr = safe_round(float(upstream_facts_map["KPI-01"]), 2)
            net_revenue_inr = safe_round(float(upstream_facts_map["KPI-02"]), 2)
            total_orders = int(upstream_facts_map.get("KPI-05", len(orders)))
        else:
            delivered = orders[orders["order_status"] == "Delivered"] if "order_status" in orders.columns else orders
            non_cancelled = orders[orders["order_status"] != "Cancelled"] if "order_status" in orders.columns else orders
            net_revenue_inr = (
                safe_round(delivered["final_amount"].sum(), 2) if "final_amount" in delivered.columns else 0.0
            )
            gmv_inr = (
                safe_round(non_cancelled["order_amount"].sum(), 2) if "order_amount" in non_cancelled.columns else 0.0
            )
            total_orders = int(len(orders))

        facts: List[GroundedFact] = [
            GroundedFact(
                label="Gross Merchandise Value (GMV)",
                value=gmv_inr,
                unit="INR",
                kpi_id=None if city_filter else "KPI-01",
                source=f"{data_source_label}:orders",
            ),
            GroundedFact(
                label="Net Revenue (Platform Inflow)",
                value=net_revenue_inr,
                unit="INR",
                kpi_id=None if city_filter else "KPI-02",
                source=f"{data_source_label}:orders",
            ),
            GroundedFact(
                label="Total Orders Placed",
                value=total_orders,
                unit="orders",
                kpi_id=None if city_filter else "KPI-05",
                source=f"{data_source_label}:orders",
            ),
        ]
        metrics: Dict[str, Any] = {
            "gmv_inr": gmv_inr,
            "net_revenue_inr": net_revenue_inr,
            "total_orders": total_orders,
        }

        if not city_filter and "KPI-08" in upstream_facts_map:
            sla_rate = safe_round(float(upstream_facts_map["KPI-08"]), 2)
            avg_deliv_val = upstream_facts_map.get("KPI-09", upstream_metrics_map.get("avg_delivery_time_mins"))
            if avg_deliv_val is not None:
                metrics["avg_delivery_time_mins"] = safe_round(float(avg_deliv_val), 2)
            metrics["sla_breach_rate_pct"] = sla_rate
            facts.append(
                GroundedFact(
                    label="Delivery SLA Breach Rate",
                    value=sla_rate,
                    unit="%",
                    kpi_id="KPI-08",
                    source=f"{data_source_label}:deliveries",
                )
            )
        elif not deliveries.empty and "delivery_duration" in deliveries.columns:
            durations = pd.to_numeric(deliveries["delivery_duration"], errors="coerce").dropna()
            if not durations.empty:
                avg_deliv = safe_round(durations.mean(), 2)
                sla_rate = safe_round((int((durations > 45.0).sum()) / len(deliveries)) * 100.0, 2)
                metrics["avg_delivery_time_mins"] = avg_deliv
                metrics["sla_breach_rate_pct"] = sla_rate
                facts.append(
                    GroundedFact(
                        label="Delivery SLA Breach Rate",
                        value=sla_rate,
                        unit="%",
                        kpi_id=None if city_filter else "KPI-08",
                        source=f"{data_source_label}:deliveries",
                    )
                )
        else:
            data_gaps.append("deliveries dataset or delivery_duration missing: SLA cross-domain telemetry partial")

        charts: List[ChartSpec] = []
        table_rows: List[Dict[str, Any]] = []
        caveats: List[ModelCaveat] = []

        # 1. Empirical Root Cause Analysis via python/ai/analyst/root_cause.py
        rca_drivers: List[str] = []
        rca_payload_dict: Optional[Dict[str, Any]] = None
        try:
            from python.ai.analyst.root_cause import perform_root_cause_analysis
            from python.ai.agents.output_verifier import _NUMBER_IN_PROSE_RE

            rca = perform_root_cause_analysis(request.user_query, scoped_bundle)
            rca_payload_dict = rca
            rca_drivers = [sanitize_text(str(x)) for x in rca.get("contributing_factors", []) if x]
            rca_rows = [
                {"category": "observed_fact", "detail": sanitize_text(str(x))}
                for x in rca.get("observed_facts", [])
            ] + [
                {"category": "contributing_factor", "detail": sanitize_text(str(x.get("evidence", x) if isinstance(x, dict) else str(x)))}
                for x in rca.get("contributing_factors", [])
            ] + [
                {"category": "uncertainty", "detail": sanitize_text(str(x))}
                for x in rca.get("uncertainties", [])
            ]
            if intent == "root_cause" and rca_rows:
                table_rows = rca_rows
            metrics["rca_findings_count"] = int(len(rca_drivers))

            # Ground empirical RCA numbers into verified facts
            for fact_text in rca.get("observed_facts", []):
                for m in _NUMBER_IN_PROSE_RE.finditer(str(fact_text)):
                    try:
                        v_num = float(m.group("num").replace(",", ""))
                        facts.append(
                            GroundedFact(
                                label=f"RCA Empirical Fact ({m.group(0).strip()})",
                                value=v_num,
                                source=f"{data_source_label}:root_cause_analysis",
                                is_confirmed=True,
                            )
                        )
                    except ValueError:
                        continue
            for cf in rca.get("contributing_factors", []):
                ev_str = str(cf.get("evidence", "")) if isinstance(cf, dict) else str(cf)
                for m in _NUMBER_IN_PROSE_RE.finditer(ev_str):
                    try:
                        v_num = float(m.group("num").replace(",", ""))
                        facts.append(
                            GroundedFact(
                                label=f"RCA Contributing Evidence ({m.group(0).strip()})",
                                value=v_num,
                                source=f"{data_source_label}:root_cause_analysis",
                                is_confirmed=True,
                            )
                        )
                    except ValueError:
                        continue
        except Exception as exc:
            data_gaps.append(f"Root cause engine skipped: {exc}")

        # 2. Digital Twin Systemic Risk & Dependency Chain via python/digital_twin/
        twin_alerts_count = 0
        try:
            from python.digital_twin.twin_dependencies import get_structured_impact_chain
            from python.digital_twin.twin_engine import build_digital_twin_state

            twin_state = build_digital_twin_state(scoped_bundle)
            twin_alerts_count = int(len(getattr(twin_state, "alerts", []) or []))
            metrics["digital_twin_alerts"] = twin_alerts_count
            event_type = str(request.filters.get("event_type") or _infer_impact_event(request.user_query))
            chain = get_structured_impact_chain(event_type)
            chain_steps = chain.get("ripple_steps", [])
            if intent == "systemic_risk" and chain_steps:
                table_rows = [
                    {
                        "event_type": event_type,
                        "trigger": chain.get("trigger", event_type),
                        "step_order": idx + 1,
                        "ripple_step": step,
                        "systemic_impact": chain.get("impact", ""),
                    }
                    for idx, step in enumerate(chain_steps)
                ]
        except Exception as exc:
            data_gaps.append(f"Digital Twin engine skipped: {exc}")

        # 3. What-If Simulation via simulation_agent / scenario_engine (when requested or synthesized)
        sim_rev_diff: Optional[float] = None
        if intent == "what_if_simulation" or any(
            k in request.user_query.lower() for k in ("what if", "what-if", "simulat", "scenario")
        ):
            try:
                from python.ai.analyst.simulation_agent import execute_conversational_simulation

                sim_out = execute_conversational_simulation(request.user_query, scoped_bundle)
                fin_imp = sim_out.get("financial_impact", {})
                ops_imp = sim_out.get("operations_impact", {})
                cust_imp = sim_out.get("customer_impact", {})
                sim_rev_diff = safe_round(fin_imp.get("revenue_diff", 0.0), 2)
                sim_base_rev = safe_round(fin_imp.get("baseline_revenue", 0.0), 2)
                sim_new_rev = safe_round(fin_imp.get("simulated_revenue", 0.0), 2)
                metrics["sim_baseline_revenue_inr"] = sim_base_rev
                metrics["sim_simulated_revenue_inr"] = sim_new_rev
                metrics["sim_revenue_diff_inr"] = sim_rev_diff
                metrics["sim_eta_diff_mins"] = safe_round(ops_imp.get("ETA_Diff_Mins", 0.0), 2)
                metrics["sim_churn_reduction_accounts"] = int(cust_imp.get("Churn_Reduction", 0))
                facts.extend(
                    [
                        GroundedFact(
                            label="Simulated Revenue Delta (What-If Scenario)",
                            value=sim_rev_diff,
                            unit="INR",
                            source="scenario_engine",
                            is_confirmed=False,
                        ),
                        GroundedFact(
                            label="Simulated Baseline Revenue",
                            value=sim_base_rev,
                            unit="INR",
                            source="scenario_engine",
                            is_confirmed=False,
                        ),
                        GroundedFact(
                            label="Simulated Projected Revenue",
                            value=sim_new_rev,
                            unit="INR",
                            source="scenario_engine",
                            is_confirmed=False,
                        ),
                    ]
                )
                comp_rows = sim_out.get("comparison_data", [])
                if comp_rows:
                    table_rows = comp_rows
                    charts.append(
                        ChartSpec(
                            chart_type="bar",
                            title=f"Simulation Comparison: {sim_out.get('scenario_name', 'What-If')}",
                            x_key="metric",
                            y_key="Simulated",
                            data=sanitize_table_rows(comp_rows, max_rows=20),
                        )
                    )
            except Exception as exc:
                data_gaps.append(f"Scenario simulation skipped: {exc}")

        caveats.append(
            ModelCaveat(
                model_name="decision_simulation_and_nba",
                domain="decision",
                validation_status="HEURISTIC_SIMULATION",
                metric_summary=f"digital_twin_alerts={twin_alerts_count}, rca_drivers={len(rca_drivers)}",
                warning=(
                    "What-If simulation projections and Next-Best-Action estimates reflect heuristic parameter "
                    "models rather than guaranteed cash savings; leakage signals remain unconfirmed (is_confirmed_loss=False)."
                ),
                is_production_ready=False,
            )
        )

        # 4. Strategic Next Best Actions (strictly derived from real platform data)
        recommendations = self._generate_grounded_nbas(
            orders=orders,
            customers=customers,
            restaurants=restaurants,
            churn_df=churn_raw,
            alerts_df=alerts_raw,
            leakage_df=leakage_raw,
            data_gaps=data_gaps,
        )
        metrics["recommendations_count"] = int(len(recommendations))
        facts.append(
            GroundedFact(
                label="Grounded Next Best Actions Emitted",
                value=len(recommendations),
                unit="actions",
                source=f"{data_source_label}:next_best_action",
            )
        )

        if sql_rows:
            table_rows = sql_rows
        elif not table_rows and recommendations:
            table_rows = [
                {
                    "title": r.title,
                    "target_type": r.target_type,
                    "priority": r.priority,
                    "action": r.action,
                    "evidence": r.evidence,
                }
                for r in recommendations[:15]
            ]

        provenance: List[DataProvenance] = [
            make_provenance(data_source_label, "orders", orders, filters_applied=filters_desc),
        ]
        for ds_name, df_ref in (
            ("customers", customers),
            ("restaurants", restaurants),
            ("deliveries", deliveries),
            ("riders", riders),
            ("operational_alerts", alerts_raw),
        ):
            if not df_ref.empty:
                provenance.append(make_provenance(data_source_label, ds_name, df_ref))
        if not leakage_raw.empty:
            provenance.append(
                make_provenance(
                    data_source_label,
                    "revenue_leakage",
                    leakage_raw,
                    is_confirmed_loss=False,
                )
            )

        scope_label = f" for city '{city_filter}'" if city_filter else " platform-wide"
        sla_txt = (
            f", SLA breach rate {metrics['sla_breach_rate_pct']:.2f}%"
            if "sla_breach_rate_pct" in metrics
            else ""
        )
        sim_txt = (
            f"; simulated scenario projected revenue delta ₹{sim_rev_diff:,.2f} (unconfirmed heuristic)"
            if sim_rev_diff is not None
            else ""
        )
        if intent == "root_cause" and rca_payload_dict and rca_payload_dict.get("observed_facts"):
            primary_fact = rca_payload_dict["observed_facts"][0]
            summary = f"Root Cause Intelligence{scope_label}: {primary_fact}"
            rca_lines = [f"- {fact}" for fact in rca_payload_dict.get("observed_facts", [])]
            for cf in rca_payload_dict.get("contributing_factors", []):
                if isinstance(cf, dict):
                    rca_lines.append(f"- **{cf.get('factor', 'Factor')}** ({cf.get('correlation_strength', 'Observed')}): {cf.get('evidence', '')}")
            narrative_parts = [
                f"### Root Cause Diagnostic: {rca_payload_dict.get('investigation_target', 'Empirical Platform Analysis')}\n"
                + "\n".join(rca_lines),
                "Cross-domain synthesis combines empirical Root Cause Analysis, Digital Twin state, and grounded Next Best Actions without claiming unverified net cash recovery (is_confirmed_loss=False).",
            ]
        else:
            summary = (
                f"Decision intelligence{scope_label}: GMV ₹{gmv_inr:,.2f}, Net Revenue ₹{net_revenue_inr:,.2f}"
                f"{sla_txt}, {len(recommendations):,} grounded Next Best Actions, and {twin_alerts_count:,} "
                f"Digital Twin alerts{sim_txt}."
            )
            narrative_parts = [
                "Cross-domain synthesis combines empirical Root Cause Analysis, Digital Twin state, and "
                "grounded Next Best Actions without claiming unverified net cash recovery (is_confirmed_loss=False).",
            ]
        if data_gaps:
            narrative_parts.append(f"Data gaps: {'; '.join(data_gaps)}.")

        status = AgentStatus.PARTIAL if data_gaps else AgentStatus.SUCCESS
        return AgentResult(
            request_id=request.request_id,
            execution_id=request.execution_id,
            agent_id=self.AGENT_ID,
            domain=self.DOMAIN,
            status=status,
            summary=summary,
            narrative=" ".join(narrative_parts),
            facts=facts,
            metrics=metrics,
            table_rows=sanitize_table_rows(table_rows),
            charts=charts,
            recommendations=recommendations,
            caveats=caveats,
            provenance=provenance,
            sql_traces=[sql_trace] if sql_trace is not None else [],
            is_confirmed_loss=False if not leakage_raw.empty else None,
            data_gaps=data_gaps,
        )


__all__ = ["DecisionAgent"]
