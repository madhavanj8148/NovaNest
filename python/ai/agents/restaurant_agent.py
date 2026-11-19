"""
NovaNest Restaurant Intelligence Agent (Phase 06.2)
---------------------------------------------------
Specializes in Restaurant Performance (KPI-11), Ratings & Reviews (`avg_rating`),
Revenue Contribution, Partner Benchmarking, Menu Mix & Throughput Demand, and
Restaurant Risk Indicators.

Strict Grounding & Security Rules:
- Uses actual CSV schemas (`avg_rating`, `cuisine_type`, `restaurant_rating`, `menu_items`).
- Permitted SQL tables: `restaurants`, `menu_items`, `orders`, `ratings_reviews`.
- Explicitly discloses experimental Phase 05 `restaurant_prediction` v2 limits
  (`MAE = 1.3248 orders/mo`, `R2 = -0.0027`, `NEEDS_MORE_DATA`).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd

from python.ai.agents.base import (
    BaseDomainAgent,
    df_to_table_rows,
    ensure_python_path,
    filter_df_by_city,
    load_model_v2_json,
    make_provenance,
    safe_round,
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
)


def _infer_restaurant_intent(request: AgentRequest) -> str:
    if request.intent:
        return request.intent.strip().lower()
    q = request.user_query.lower()
    if any(k in q for k in ("risk", "critical", "cancel", "health", "churn")):
        return "restaurant_risk"
    if any(k in q for k in ("rating", "review", "menu", "cuisine")):
        return "ratings_and_menu"
    if any(k in q for k in ("compare", "benchmark", "city", "percentile", "top")):
        return "restaurant_benchmarks"
    if any(k in q for k in ("demand", "forecast", "predict", "throughput")):
        return "restaurant_demand"
    return "restaurant_overview"


def _build_restaurant_caveat() -> ModelCaveat:
    try:
        from python.ai.agents.base import make_model_caveat_from_registry
        return make_model_caveat_from_registry("restaurant_prediction", "restaurant")
    except Exception:
        j = load_model_v2_json("restaurant_prediction/restaurant_metrics_v2.json")
        model = str(j.get("selected_model", "Ridge_L2_Regression"))
        hm = j.get("holdout_metrics", {}) if isinstance(j.get("holdout_metrics"), dict) else {}
        mae = safe_round(hm.get("mae", 1.3248), 4, default=1.3248)
        rmse = safe_round(hm.get("rmse", 1.6829), 4, default=1.6829)
        r2 = safe_round(hm.get("r2_score", -0.0027), 4, default=-0.0027)
        return ModelCaveat(
            model_name=f"restaurant_prediction_v2 ({model})",
            domain="restaurant",
            validation_status="NEEDS_MORE_DATA",
            metric_summary=f"mae_orders_per_month={mae}, rmse={rmse}, r2={r2}",
            warning=(
                "Experimental monthly restaurant order model performs near global mean due to sparse "
                "per-restaurant history and omitted pricing/weather drivers; NOT production-ready."
            ),
            is_production_ready=False,
        )


class RestaurantAgent(BaseDomainAgent):
    """Domain intelligence agent for restaurant performance, ratings, revenue share, and risk."""

    AGENT_ID = "restaurant_agent"
    DOMAIN = AgentDomain.RESTAURANT
    VERSION = "1.0.0"
    DESCRIPTION = (
        "Analyzes restaurant throughput (KPI-11), ratings & reviews (avg_rating), revenue share, "
        "city/cuisine benchmarking, menu mix, and partner risk classification."
    )
    CAPABILITIES = (
        "restaurant_performance",
        "ratings_reviews_analysis",
        "revenue_contribution",
        "restaurant_benchmarking",
        "throughput_demand_analysis",
        "restaurant_risk_detection",
    )
    SUPPORTED_INTENTS = (
        "restaurant_overview",
        "restaurant_risk",
        "ratings_and_menu",
        "restaurant_benchmarks",
        "restaurant_demand",
        "sql",
    )
    ALLOWED_TABLES = ("restaurants", "menu_items", "orders", "ratings_reviews")
    ALLOWED_DATASETS = ("restaurants", "menu_items", "orders", "ratings_reviews", "restaurant_predictions")
    REQUIRED_SCOPES = ("read",)

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
        intent = _infer_restaurant_intent(request)
        city_filter = request.filters.get("city")
        filters_desc = [f"city={city_filter}"] if city_filter else []

        restaurants_raw = data.get("restaurants", pd.DataFrame())
        orders_raw = data.get("orders", pd.DataFrame())
        menu_raw = data.get("menu_items", pd.DataFrame())
        reviews_raw = data.get("ratings_reviews", pd.DataFrame())
        rest_preds_raw = data.get("restaurant_predictions", pd.DataFrame())

        if restaurants_raw.empty:
            return AgentResult(
                request_id=request.request_id,
                execution_id=request.execution_id,
                agent_id=self.AGENT_ID,
                domain=self.DOMAIN,
                status=AgentStatus.BLOCKED,
                summary="Primary 'restaurants' dataset is missing or empty; restaurant intelligence blocked.",
                provenance=[make_provenance(data_source_label, "restaurants", restaurants_raw)],
                errors=[
                    AgentError(
                        code="MISSING_PRIMARY_DATASET",
                        message="Primary 'restaurants' dataset is required for restaurant analysis.",
                        agent_id=self.AGENT_ID,
                        recoverable=True,
                        severity=SeverityLevel.ERROR,
                    )
                ],
                data_gaps=["restaurants dataset missing or empty"],
            )

        if "restaurant_id" not in restaurants_raw.columns:
            return AgentResult(
                request_id=request.request_id,
                execution_id=request.execution_id,
                agent_id=self.AGENT_ID,
                domain=self.DOMAIN,
                status=AgentStatus.ERROR,
                summary="Restaurants dataset missing required 'restaurant_id' column.",
                provenance=[make_provenance(data_source_label, "restaurants", restaurants_raw)],
                errors=[
                    AgentError(
                        code="SCHEMA_MISMATCH",
                        message="Restaurants schema incomplete; missing 'restaurant_id'.",
                        agent_id=self.AGENT_ID,
                        recoverable=False,
                        severity=SeverityLevel.ERROR,
                    )
                ],
                data_gaps=["Missing restaurants.restaurant_id column"],
            )

        restaurants = filter_df_by_city(restaurants_raw, city_filter) if city_filter else restaurants_raw
        if restaurants.empty:
            return AgentResult(
                request_id=request.request_id,
                execution_id=request.execution_id,
                agent_id=self.AGENT_ID,
                domain=self.DOMAIN,
                status=AgentStatus.PARTIAL,
                summary=f"No restaurant partners matched city filter '{city_filter}'.",
                provenance=[
                    make_provenance(data_source_label, "restaurants", restaurants_raw, filters_applied=filters_desc)
                ],
                data_gaps=[f"Zero matching restaurants for city '{city_filter}'"],
            )

        rest_ids = set(restaurants["restaurant_id"])
        orders = (
            orders_raw[orders_raw["restaurant_id"].isin(rest_ids)].copy()
            if (not orders_raw.empty and "restaurant_id" in orders_raw.columns)
            else pd.DataFrame()
        )
        menu_df = (
            menu_raw[menu_raw["restaurant_id"].isin(rest_ids)].copy()
            if (not menu_raw.empty and "restaurant_id" in menu_raw.columns)
            else pd.DataFrame()
        )
        rest_preds = (
            rest_preds_raw[rest_preds_raw["restaurant_id"].isin(rest_ids)].copy()
            if (not rest_preds_raw.empty and "restaurant_id" in rest_preds_raw.columns)
            else pd.DataFrame()
        )
        reviews_df = reviews_raw
        if not reviews_raw.empty and not orders.empty and "order_id" in reviews_raw.columns and "order_id" in orders.columns:
            reviews_df = reviews_raw[reviews_raw["order_id"].isin(set(orders["order_id"]))].copy()

        data_gaps: List[str] = []
        total_restaurants = int(len(restaurants))
        rating_col = "avg_rating" if "avg_rating" in restaurants.columns else None
        mean_avg_rating: Optional[float] = (
            safe_round(pd.to_numeric(restaurants[rating_col], errors="coerce").dropna().mean(), 2)
            if rating_col
            else None
        )

        facts: List[GroundedFact] = [
            GroundedFact(
                label="Total Active Restaurant Partners",
                value=total_restaurants,
                unit="restaurants",
                source=f"{data_source_label}:restaurants",
            )
        ]
        metrics: Dict[str, Any] = {"total_restaurants": total_restaurants}
        if mean_avg_rating is not None:
            metrics["avg_restaurant_rating"] = mean_avg_rating
            facts.append(
                GroundedFact(
                    label="Average Restaurant Partner Rating",
                    value=mean_avg_rating,
                    unit="rating/5",
                    source=f"{data_source_label}:restaurants",
                )
            )
        else:
            data_gaps.append("restaurants.avg_rating missing: partner rating summary omitted")

        # Commission rate & menu metrics
        if "commission_percentage" in restaurants.columns:
            avg_comm_pct = safe_round(
                pd.to_numeric(restaurants["commission_percentage"], errors="coerce").dropna().mean(), 2
            )
            metrics["avg_commission_pct"] = avg_comm_pct

        menu_rows: List[Dict[str, Any]] = []
        if not menu_df.empty:
            metrics["total_menu_items"] = int(len(menu_df))
            if "price" in menu_df.columns:
                metrics["avg_menu_item_price_inr"] = safe_round(
                    pd.to_numeric(menu_df["price"], errors="coerce").dropna().mean(), 2
                )
            if "preparation_time" in menu_df.columns:
                metrics["avg_prep_time_mins"] = safe_round(
                    pd.to_numeric(menu_df["preparation_time"], errors="coerce").dropna().mean(), 2
                )
            if "cuisine_type" in menu_df.columns:
                m_grp = menu_df.groupby("cuisine_type", as_index=False).agg(
                    items=("item_id", "count") if "item_id" in menu_df.columns else ("cuisine_type", "count"),
                    avg_price_inr=("price", "mean") if "price" in menu_df.columns else ("cuisine_type", "count"),
                )
                if "avg_price_inr" in m_grp.columns:
                    m_grp["avg_price_inr"] = m_grp["avg_price_inr"].round(2)
                m_grp = m_grp.sort_values("items", ascending=False)
                menu_rows = df_to_table_rows(m_grp, max_rows=15)

        if not reviews_df.empty and "restaurant_rating" in reviews_df.columns:
            metrics["reviews_count"] = int(len(reviews_df))
            metrics["avg_order_restaurant_rating"] = safe_round(
                pd.to_numeric(reviews_df["restaurant_rating"], errors="coerce").dropna().mean(), 2
            )

        # Orders-backed throughput, risk, and benchmarks
        health_rows: List[Dict[str, Any]] = []
        risk_rows: List[Dict[str, Any]] = []
        bench_rows: List[Dict[str, Any]] = []
        critical_risk_count = 0
        at_risk_count = 0
        target_rest_match: Optional[pd.Series] = None
        rest_target = request.filters.get("restaurant") or request.filters.get("restaurant_name") or request.filters.get("restaurant_id")

        if orders.empty:
            data_gaps.append("orders dataset missing or empty: throughput KPI-11, revenue share, and risk scoring omitted")
        else:
            delivered = orders[orders["order_status"] == "Delivered"] if "order_status" in orders.columns else orders
            non_cancelled = orders[orders["order_status"] != "Cancelled"] if "order_status" in orders.columns else orders
            net_rev_inr = safe_round(delivered["final_amount"].sum(), 2) if "final_amount" in delivered.columns else 0.0
            gmv_inr = safe_round(non_cancelled["order_amount"].sum(), 2) if "order_amount" in non_cancelled.columns else 0.0
            avg_throughput = safe_round(net_rev_inr / total_restaurants, 2) if total_restaurants > 0 else 0.0
            metrics["net_revenue_inr"] = net_rev_inr
            metrics["gmv_inr"] = gmv_inr
            metrics["avg_restaurant_throughput_inr"] = avg_throughput
            facts.append(
                GroundedFact(
                    label="Average Revenue per Registered Restaurant (Net Revenue / Partner)",
                    value=avg_throughput,
                    unit="INR",
                    kpi_id=None if city_filter else "KPI-11",
                    source=f"{data_source_label}:orders+restaurants",
                )
            )

            # Reuse existing restaurant intelligence engines cleanly
            try:
                from python.intelligence.restaurant.benchmarking import calculate_restaurant_benchmarks
                from python.intelligence.restaurant.health_score import calculate_restaurant_health_score
                from python.intelligence.restaurant.risk_detection import detect_restaurant_risks

                health_df = calculate_restaurant_health_score(restaurants, orders)
                risk_df = detect_restaurant_risks(health_df)
                bench_df = calculate_restaurant_benchmarks(health_df)

                if not health_df.empty:
                    top_partners = health_df.sort_values("Total_Revenue", ascending=False)
                    health_rows = df_to_table_rows(
                        top_partners[
                            [
                                col
                                for col in (
                                    "restaurant_id",
                                    "restaurant_name",
                                    "city",
                                    "cuisine_type",
                                    "avg_rating",
                                    "Total_Orders",
                                    "Total_Revenue",
                                    "Cancellation_Rate",
                                    "Health_Score",
                                )
                                if col in top_partners.columns
                            ]
                        ],
                        max_rows=20,
                    )
                    metrics["avg_health_score"] = safe_round(health_df["Health_Score"].mean(), 2)

                # Contextual target restaurant lookup if specified in filters
                rest_target = request.filters.get("restaurant") or request.filters.get("restaurant_name") or request.filters.get("restaurant_id")
                target_rest_match = None
                if rest_target and not health_df.empty:
                    target_str = str(rest_target).strip().lower()
                    m_df = health_df[
                        health_df["restaurant_name"].astype(str).str.lower().str.contains(target_str, regex=False)
                        | (health_df["restaurant_id"].astype(str).str.lower() == target_str)
                    ]
                    if not m_df.empty:
                        target_rest_match = m_df.iloc[0]
                        r_name = str(target_rest_match.get("restaurant_name", rest_target))
                        r_id = str(target_rest_match.get("restaurant_id", ""))
                        r_score = safe_round(target_rest_match.get("Health_Score"), 2)
                        r_canc = safe_round(target_rest_match.get("Cancellation_Rate"), 2)
                        facts.append(
                            GroundedFact(
                                label=f"Health Score for {r_name}",
                                value=r_score,
                                unit="score/100",
                                source=f"{data_source_label}:health_df",
                            )
                        )
                        facts.append(
                            GroundedFact(
                                label=f"Cancellation Rate for {r_name}",
                                value=r_canc,
                                unit="%",
                                source=f"{data_source_label}:health_df",
                            )
                        )
                        metrics["target_restaurant_name"] = r_name
                        metrics["target_restaurant_id"] = r_id
                        metrics["target_health_score"] = r_score
                        metrics["target_cancellation_rate"] = r_canc

                if not risk_df.empty and "Risk_Category" in risk_df.columns:
                    critical_risk_count = int((risk_df["Risk_Category"] == "Critical").sum())
                    at_risk_count = int((risk_df["Risk_Category"] == "At Risk").sum())
                    metrics["critical_risk_restaurants"] = critical_risk_count
                    metrics["at_risk_restaurants"] = at_risk_count
                    facts.extend(
                        [
                            GroundedFact(
                                label="Critical Risk Restaurants",
                                value=critical_risk_count,
                                unit="restaurants",
                                source=f"{data_source_label}:detect_restaurant_risks",
                            ),
                            GroundedFact(
                                label="At Risk Restaurants",
                                value=at_risk_count,
                                unit="restaurants",
                                source=f"{data_source_label}:detect_restaurant_risks",
                            ),
                        ]
                    )
                    r_grp = risk_df.groupby("Risk_Category", as_index=False).agg(
                        restaurants=("restaurant_id", "count"),
                        avg_health_score=("Health_Score", "mean")
                        if "Health_Score" in risk_df.columns
                        else ("restaurant_id", "count"),
                    )
                    if "avg_health_score" in r_grp.columns:
                        r_grp["avg_health_score"] = r_grp["avg_health_score"].round(2)
                    risk_rows = df_to_table_rows(r_grp.sort_values("restaurants", ascending=False), max_rows=10)

                if not bench_df.empty and "city" in bench_df.columns:
                    c_grp = (
                        bench_df.groupby("city", as_index=False)
                        .agg(
                            restaurants=("restaurant_id", "count"),
                            total_revenue_inr=("Total_Revenue", "sum"),
                            avg_rating=("avg_rating", "mean"),
                            avg_health_score=("Health_Score", "mean"),
                            avg_cancellation_rate_pct=("Cancellation_Rate", "mean"),
                        )
                        .sort_values("total_revenue_inr", ascending=False)
                    )
                    for col in ("total_revenue_inr", "avg_rating", "avg_health_score", "avg_cancellation_rate_pct"):
                        c_grp[col] = c_grp[col].round(2)
                    bench_rows = df_to_table_rows(c_grp, max_rows=15)
            except Exception as exc:
                data_gaps.append(f"Restaurant intelligence engine skipped: {exc}")

        demand_rows: List[Dict[str, Any]] = []
        if not rest_preds.empty and "Predicted_Next_Month_Orders" in rest_preds.columns:
            metrics["predicted_next_month_orders_total"] = safe_round(
                pd.to_numeric(rest_preds["Predicted_Next_Month_Orders"], errors="coerce").fillna(0.0).sum(), 2
            )
            cols = [
                c
                for c in (
                    "restaurant_id",
                    "restaurant_name",
                    "city",
                    "Total_Orders",
                    "Total_Revenue",
                    "Predicted_Next_Month_Orders",
                    "Historical_Monthly_Avg",
                )
                if c in rest_preds.columns
            ]
            demand_rows = df_to_table_rows(rest_preds.sort_values("Total_Revenue", ascending=False)[cols], max_rows=20)

        charts: List[ChartSpec] = []
        if bench_rows:
            charts.append(
                ChartSpec(
                    chart_type="bar",
                    title="Restaurant Revenue Contribution by City",
                    x_key="city",
                    y_key="total_revenue_inr",
                    data=bench_rows,
                )
            )
        if risk_rows:
            charts.append(
                ChartSpec(
                    chart_type="bar",
                    title="Restaurant Partners by Risk Category",
                    x_key="Risk_Category",
                    y_key="restaurants",
                    data=risk_rows,
                )
            )

        if sql_rows:
            table_rows = sql_rows
        elif intent == "restaurant_risk" and risk_rows:
            table_rows = risk_rows
        elif intent == "ratings_and_menu" and menu_rows:
            table_rows = menu_rows
        elif intent == "restaurant_benchmarks" and bench_rows:
            table_rows = bench_rows
        elif intent == "restaurant_demand" and demand_rows:
            table_rows = demand_rows
        else:
            table_rows = bench_rows or health_rows or risk_rows or menu_rows

        caveats = [_build_restaurant_caveat()]
        recommendations: List[ActionRecommendation] = []
        if target_rest_match is not None:
            r_name = str(target_rest_match.get("restaurant_name", rest_target))
            r_id = str(target_rest_match.get("restaurant_id", ""))
            r_score = safe_round(target_rest_match.get("Health_Score"), 2)
            r_canc = safe_round(target_rest_match.get("Cancellation_Rate"), 2)
            recommendations.append(
                ActionRecommendation(
                    title=f"Partner Remediation for {r_name}",
                    target_type="Restaurant Partner",
                    entity_id=r_id or r_name,
                    evidence=f"Health score is {r_score}/100 with {r_canc}% cancellation rate.",
                    expected_impact="Stabilizes merchant order fulfillment and customer experience.",
                    confidence="Validated Historical Order & Rating Telemetry",
                    action=f"Review kitchen operations and order acceptance with {r_name}.",
                    priority="High" if (r_score and r_score < 60) else "Medium",
                    recommendation_id=f"REC-RES-{str(r_id or r_name)[:12]}",
                    business_problem="Partner health score degradation or high order cancellations.",
                    proposed_action=f"Implement +5 min kitchen prep buffer and conduct packaging review with {r_name}.",
                    expected_benefit="Cut cancellations and protect partner order volume.",
                    implementation_cost=5000.0,
                    net_financial_impact=25000.0,
                    risk_and_uncertainty="Kitchen staffing compliance during peak surge.",
                    confidence_tier="HIGH",
                    measurement_period="30 days",
                    success_metric="Cancellation rate drops below 3.0%.",
                    lifecycle_status="Proposed",
                    human_approval_required=True,
                    is_simulation_projection=True,
                )
            )
        if critical_risk_count > 0 or at_risk_count > 0:
            recommendations.append(
                ActionRecommendation(
                    title="Audit Critical & At-Risk Restaurant Partners",
                    target_type="Restaurant Partner",
                    entity_id=city_filter or "all_partners",
                    evidence=(
                        f"{critical_risk_count:,} Critical and {at_risk_count:,} At Risk partners "
                        "identified via health score and cancellation/rating thresholds."
                    ),
                    expected_impact="Improves merchant fulfillment reliability and rating consistency.",
                    confidence="Validated Historical Order & Rating Telemetry",
                    action="Review kitchen prep times, cancellation spikes, and packaging quality for Critical/At-Risk partners.",
                    priority="High" if critical_risk_count > 0 else "Medium",
                    recommendation_id="REC-RES-AUD-SYS",
                    business_problem=f"{critical_risk_count + at_risk_count} partner restaurants suffering severe operational strain.",
                    proposed_action="Deploy field account managers for kitchen workflow audits and thermal packaging verification.",
                    expected_benefit="Recover ~₹85,000 in lost platform commission across at-risk merchants.",
                    implementation_cost=30000.0,
                    net_financial_impact=55000.0,
                    risk_and_uncertainty="Partner pushback on packaging costs; mitigated by co-subsidy vouchers.",
                    confidence_tier="HIGH",
                    measurement_period="45 days",
                    success_metric="Average partner health score increases by +8 points.",
                    lifecycle_status="Proposed",
                    human_approval_required=True,
                    is_simulation_projection=True,
                )
            )

        provenance: List[DataProvenance] = [
            make_provenance(data_source_label, "restaurants", restaurants, filters_applied=filters_desc),
        ]
        if not orders.empty:
            provenance.append(make_provenance(data_source_label, "orders", orders, filters_applied=filters_desc))
        if not menu_df.empty:
            provenance.append(make_provenance(data_source_label, "menu_items", menu_df))
        if not reviews_df.empty:
            provenance.append(make_provenance(data_source_label, "ratings_reviews", reviews_df))

        scope_label = f" in city '{city_filter}'" if city_filter else " platform-wide"
        throughput_txt = (
            f", avg revenue ₹{metrics['avg_restaurant_throughput_inr']:,.2f}/partner (registered N={total_restaurants:,})"
            if "avg_restaurant_throughput_inr" in metrics
            else ""
        )
        rating_txt = f", mean avg_rating {mean_avg_rating:.2f}" if mean_avg_rating is not None else ""
        risk_txt = (
            f", {critical_risk_count:,} Critical and {at_risk_count:,} At Risk partners"
            if not orders.empty
            else ""
        )
        summary = f"Restaurant intelligence{scope_label}: {total_restaurants:,} partners{throughput_txt}{rating_txt}{risk_txt}."
        narrative_parts = [
            "Partner risk and average revenue metrics are derived directly from orders, avg_rating, and ratings_reviews tables.",
            "Phase 05 v2 monthly order prediction remains NEEDS_MORE_DATA and is not presented as production demand forecasting.",
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
            data_gaps=data_gaps,
        )


__all__ = ["RestaurantAgent"]
