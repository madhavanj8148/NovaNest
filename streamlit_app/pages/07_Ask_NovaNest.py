"""
Page 7: Ask NovaNest AI — Multi-Agent Conversational Business Intelligence
--------------------------------------------------------------------------
Unified multi-agent decision intelligence powered by the FastAPI MasterOrchestrator boundary:
- 5 Domain Intelligence Agents: Financial, Customer, Operations, Restaurant, Decision
- OutputVerifier ground-truth reconciliation & AST security barrier
- Persistent conversational memory with entity and territory retention
- Contextual AI launcher integration from across all NovaNest dashboards
- Real-time 5-domain telemetry cards & multi-turn dialogue continuity
"""

from pathlib import Path
import sys
import uuid
from typing import Any, Dict, List, Optional
import pandas as pd
import streamlit as st

STREAMLIT_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = STREAMLIT_DIR.parent
for _p in (str(STREAMLIT_DIR), str(PROJECT_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import bootstrap
from config.settings import PAGE_TITLE, PAGE_ICON, LAYOUT
from utils.data_loader import load_all_datasets
from components.navigation import render_sidebar
from components.page_header import render_page_header
from components.status_components import render_section_header, render_callout, render_data_table
from components.insight_components import render_insight_summary
from components.chart_components import render_bar_chart, render_donut_chart

from ai.insights.business_insights import generate_business_insights
from utils.api_client import get_streamlit_ai_client, ApiClientError
from components.telemetry_components import render_agent_telemetry_card

st.set_page_config(page_title=f"Ask NovaNest AI — {PAGE_TITLE}", page_icon=PAGE_ICON, layout=LAYOUT)
bootstrap.inject_theme()

# Load Data and sidebar filters
data, data_source = load_all_datasets()
sidebar_filters = render_sidebar(data_source)

orders_df = data.get("orders", pd.DataFrame())
customers_df = data.get("customers", pd.DataFrame())
orders_prep = orders_df.copy()
if not orders_prep.empty:
    if "order_datetime" not in orders_prep.columns and "order_time" in orders_prep.columns:
        orders_prep["order_datetime"] = orders_prep["order_time"]
    if "final_amount" not in orders_prep.columns and "order_amount" in orders_prep.columns:
        orders_prep["final_amount"] = orders_prep["order_amount"]

# Session State Initialization (scoped cleanly per UI session)
if "ask_novanest_session_id" not in st.session_state:
    st.session_state["ask_novanest_session_id"] = f"st_{uuid.uuid4().hex[:12]}"
if "ask_novanest_last_response" not in st.session_state:
    st.session_state["ask_novanest_last_response"] = None
if "ask_novanest_history" not in st.session_state:
    st.session_state["ask_novanest_history"] = []

session_id = st.session_state["ask_novanest_session_id"]
ai_client = get_streamlit_ai_client()

# Header
render_page_header(
    title="Ask NovaNest AI",
    subtitle="Unified Multi-Agent Decision Intelligence — 5 Domain Agents, Ground-Truth Verification & Context Persistence",
    category="CONVERSATIONAL BI",
    data_source=data_source,
)

# Context Preload Banner (Triggered by contextual AI launcher from dashboard pages)
preloaded_context: Optional[Dict[str, Any]] = st.session_state.get("contextual_ai_preloaded")
if preloaded_context:
    dash_name = preloaded_context.get("dashboard_name", "Dashboard")
    sel_metric = preloaded_context.get("selected_metric", "Metric")
    ctx_city = preloaded_context.get("city")
    ctx_ent = preloaded_context.get("entity_name") or preloaded_context.get("entity_id")

    meta_parts = [f"Source: <strong>{dash_name}</strong>", f"Metric: <strong>{sel_metric}</strong>"]
    if ctx_city and ctx_city != "All":
        meta_parts.append(f"City: <strong>{ctx_city}</strong>")
    if ctx_ent:
        meta_parts.append(f"Entity: <strong>{ctx_ent}</strong>")

    col_banner, col_dismiss = st.columns([6, 1])
    with col_banner:
        st.markdown(
            f"""
            <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px; padding: 0.65rem 1rem; margin-bottom: 1rem; display: flex; align-items: center; justify-content: space-between;">
                <div style="font-size: 0.82rem; color: #93C5FD;">
                    ✨ <strong>Context Preloaded:</strong> {" • ".join(meta_parts)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_dismiss:
        if st.button("Clear Context", key="btn_clear_ctx_banner", width="stretch"):
            st.session_state.pop("contextual_ai_preloaded", None)
            st.session_state.pop("ask_novanest_preloaded_prompt", None)
            st.session_state.pop("ask_novanest_auto_submit", None)
            st.rerun()

# Quick Prompt Buttons
render_section_header("Quick Analytical & Multi-Agent Prompts", tag="PROMPT SELECTOR")
preset_row_1 = [
    "Top 5 restaurants by orders",
    "Revenue by city",
    "Analyze my business performance.",
    "Compare financial and operational performance.",
]
preset_row_2 = [
    "Why is delivery performance declining?",
    "Which restaurants need attention?",
    "Recommend actions to improve profitability.",
    "What happens if delivery time decreases by 10%?",
]

selected_prompt: Optional[str] = None
for row_idx, row_prompts in enumerate([preset_row_1, preset_row_2]):
    p_cols = st.columns(4)
    for col, pq in zip(p_cols, row_prompts):
        with col:
            if st.button(pq, key=f"btn_pq_{row_idx}_{pq}", width="stretch"):
                selected_prompt = pq

# Determine default input value (from preloaded context or button)
default_input = ""
if st.session_state.get("ask_novanest_preloaded_prompt"):
    default_input = st.session_state.get("ask_novanest_preloaded_prompt")
elif selected_prompt:
    default_input = selected_prompt

# Chat Input Form & Reset Action
col_form, col_reset = st.columns([5, 1])
with col_form:
    with st.form("ask_novanest_form", clear_on_submit=False):
        user_query = st.text_input(
            "Ask a business, operational, financial, restaurant, customer, or decision question:",
            value=default_input,
            placeholder="e.g. Analyze my business performance, Why is delivery declining?, or Recommend actions to improve profitability.",
            key="query_input",
        )
        submit_btn = st.form_submit_button("Ask NovaNest →")

with col_reset:
    st.write("")
    st.write("")
    if st.button("Reset Chat", key="btn_reset_chat", width="stretch"):
        try:
            ai_client.reset_session(session_id)
        except Exception:
            pass
        st.session_state["ask_novanest_last_response"] = None
        st.session_state["ask_novanest_history"] = []
        st.session_state.pop("contextual_ai_preloaded", None)
        st.session_state.pop("ask_novanest_preloaded_prompt", None)
        st.session_state.pop("ask_novanest_auto_submit", None)
        st.success("Conversational context and entities cleared.")

# Check if auto-submit was triggered from contextual launcher
auto_submit = bool(st.session_state.get("ask_novanest_auto_submit", False))
if auto_submit and default_input:
    # Clear the flag so subsequent runs don't loop
    st.session_state["ask_novanest_auto_submit"] = False
    active_prompt = default_input
elif selected_prompt:
    active_prompt = selected_prompt
elif submit_btn and user_query and user_query.strip():
    active_prompt = user_query.strip()
else:
    active_prompt = None

# If user submitted a query, call FastAPI MasterOrchestrator
if active_prompt:
    # Clear preloaded context after initiating query
    ctx_data_for_req = st.session_state.pop("contextual_ai_preloaded", None)
    st.session_state.pop("ask_novanest_preloaded_prompt", None)

    # Use active sidebar city or contextual city
    effective_city = (
        (ctx_data_for_req.get("city") if ctx_data_for_req else None)
        or sidebar_filters.get("city")
    )

    with st.spinner("Coordinating MasterOrchestrator across 5 domain intelligence agents..."):
        try:
            response = ai_client.ask_ai(
                question=active_prompt,
                session_id=session_id,
                city_filter=effective_city,
                filters=sidebar_filters,
                contextual_data=ctx_data_for_req,
            )
            st.session_state["ask_novanest_last_response"] = response
            st.session_state["ask_novanest_history"].append(response)
        except ApiClientError as err:
            st.session_state["ask_novanest_last_response"] = {
                "error": True,
                "message": err.message,
                "retryable": err.retryable,
                "question": active_prompt,
            }
        except Exception as exc:
            st.session_state["ask_novanest_last_response"] = {
                "error": True,
                "message": f"Unexpected execution error: {str(exc)}",
                "retryable": True,
                "question": active_prompt,
            }

active_response = st.session_state.get("ask_novanest_last_response")

if active_response:
    if active_response.get("error"):
        render_callout(
            title="AI Orchestration Error",
            message=active_response.get("message", "An unknown error occurred during execution."),
            level="danger",
        )
        if active_response.get("retryable"):
            if st.button("Retry Query", key="btn_retry_query"):
                st.session_state["ask_novanest_preloaded_prompt"] = active_response.get("question")
                st.session_state["ask_novanest_auto_submit"] = True
                st.rerun()
    else:
        prompt_display = active_response.get("question", "")
        intent = active_response.get("intent", "BUSINESS_DATA")
        provider_status = active_response.get("provider_status", "operational")
        resolved_q = active_response.get("resolved_query")
        remembered_entities = active_response.get("remembered_entities") or {}
        active_filters_ret = active_response.get("active_filters") or {}

        # Meta Banner with route, entities, and context
        entity_badges = []
        if remembered_entities.get("city"):
            entity_badges.append(f"City: <code>{remembered_entities['city']}</code>")
        if remembered_entities.get("restaurant"):
            entity_badges.append(f"Restaurant: <code>{remembered_entities['restaurant']}</code>")
        if remembered_entities.get("customer_segment"):
            entity_badges.append(f"Segment: <code>{remembered_entities['customer_segment']}</code>")
        entity_str = " &nbsp;|&nbsp; " + " • ".join(entity_badges) if entity_badges else ""

        st.markdown(
            (
                f'<div style="background: var(--nn-bg-card-elevated, #111827); border: 1px solid var(--nn-border, #1F2937); border-radius: 8px; padding: 1rem 1.25rem; margin-top: 1rem; margin-bottom: 1rem;">'
                f'<div style="font-size: 0.72rem; font-weight: 700; color: #60A5FA; text-transform: uppercase;">Inquiry & Multi-Agent Route</div>'
                f'<div style="font-size: 1.05rem; font-weight: 600; color: #FFFFFF; margin-top: 0.2rem;">"{prompt_display}"</div>'
                f'<div style="font-size: 0.78rem; color: #94A3B8; margin-top: 0.4rem;">'
                f'<strong>Intent:</strong> <span style="color: #38BDF8;">{intent}</span>'
                f'&nbsp;|&nbsp;'
                f'<strong>Engine:</strong> <span style="color: #34D399;">MasterOrchestrator v2</span>'
                f"{f'&nbsp;|&nbsp;<strong>Resolved Context:</strong> {resolved_q}' if resolved_q else ''}"
                f'{entity_str}'
                f'</div>'
                f'</div>'
            ),
            unsafe_allow_html=True,
        )

        # 5-Domain Agent Telemetry Card
        render_agent_telemetry_card(
            telemetry=active_response.get("telemetry") or active_response,
            verification_outcome=active_response.get("verification_outcome", "verified"),
            request_id=active_response.get("request_id"),
        )

        # Verified KPI Strip
        verified_metrics = active_response.get("verified_metrics") or []
        if verified_metrics:
            render_section_header("Verified Ground-Truth Metrics", tag="OUTPUT VERIFIER")
            m_cols = st.columns(min(4, len(verified_metrics)))
            for idx, metric in enumerate(verified_metrics[:8]):
                with m_cols[idx % len(m_cols)]:
                    st.metric(
                        label=str(metric.get("label", "Metric")),
                        value=str(metric.get("value", "N/A")),
                        help=f"Source: {metric.get('provenance', data_source)}",
                    )
            metrics_summary = " &nbsp;•&nbsp; ".join(
                [f"**{m.get('label')}:** <code>{m.get('value')}</code>" for m in verified_metrics[:6]]
            )
            st.markdown(
                f"<div style='font-size: 0.8rem; color: #94A3B8; margin-bottom: 0.75rem; background: rgba(255,255,255,0.02); padding: 0.4rem 0.75rem; border-radius: 6px;'>{metrics_summary}</div>",
                unsafe_allow_html=True,
            )

        # SQL Safety Barrier Panel
        sql_info = active_response.get("sql")
        if sql_info:
            sql_query = sql_info.get("query", "")
            sql_valid = sql_info.get("valid", True)
            val_msg = sql_info.get("validation_message", "")
            if not sql_valid:
                render_callout(
                    title="SQL Security Boundary Triggered",
                    message=f"{val_msg} — Query blocked by AST validator.",
                    level="danger",
                )
            else:
                st.markdown(
                    f"""
                    <div style="background: #0D1117; border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px; padding: 0.85rem 1rem; margin-bottom: 1rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.35rem;">
                            <span style="font-size: 0.72rem; font-weight: 700; color: #60A5FA; text-transform: uppercase;">Validated Read-Only SQL</span>
                            <span style="font-size: 0.7rem; font-weight: 700; color: #34D399;">Passed AST Security Barrier</span>
                        </div>
                        <code style="color: #F8FAFC; font-family: monospace; font-size: 0.85rem;">{sql_query}</code>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Primary Executive Answer & Consolidated Summary
        answer_text = active_response.get("answer") or active_response.get("consolidated_summary", "")
        if answer_text:
            render_section_header("Executive Multi-Agent Synthesis", tag=str(intent))
            st.markdown(answer_text)

        # Tabular Output
        data_rows = active_response.get("data_rows") or []
        if data_rows:
            render_section_header("Query & Breakdown Output", tag="DATA TABLE")
            render_data_table(pd.DataFrame(data_rows))

        # Suggested Visual Analytics Chart
        chart_spec = active_response.get("suggested_chart")
        if chart_spec and chart_spec.get("data"):
            chart_df = pd.DataFrame(chart_spec["data"])
            x_key = chart_spec.get("x_key")
            y_key = chart_spec.get("y_key")
            if not chart_df.empty and x_key in chart_df.columns and y_key in chart_df.columns:
                render_section_header("Visual Analytics", tag="CHART")
                if chart_spec.get("type") == "pie":
                    render_donut_chart(
                        chart_df,
                        names=x_key,
                        values=y_key,
                        title=chart_spec.get("title", "Distribution"),
                    )
                else:
                    render_bar_chart(
                        chart_df,
                        x=x_key,
                        y=y_key,
                        title=chart_spec.get("title", "Comparison"),
                    )

        # Simulation Comparison Table
        sim_res = active_response.get("simulation_results")
        if sim_res and sim_res.get("comparison_data"):
            render_section_header("Decision Simulation Comparison", tag="SIMULATOR")
            render_data_table(pd.DataFrame(sim_res["comparison_data"]))

        # Decision Agent Next Best Action Recommendations
        recs = active_response.get("recommendations") or []
        if recs:
            render_section_header("Next Best Action Recommendations", tag="DECISION AGENT")
            for rec in recs:
                render_callout(
                    title=f"{rec.get('title', 'Recommendation')} [{rec.get('priority', 'Medium')}]",
                    message=(
                        f"<strong>Action:</strong> {rec.get('action', '')}<br>"
                        f"<strong>Evidence:</strong> {rec.get('evidence', '')}<br>"
                        f"<strong>Impact / Caveat:</strong> {rec.get('expected_impact', '')} ({rec.get('confidence', '')})"
                    ),
                    level="info",
                )
else:
    # Default landing overview using certified Phase 04 metrics
    insights = generate_business_insights(orders_prep, customers_df)
    render_insight_summary(
        title="NovaNest Certified Executive Overview",
        points=insights,
        category="AI PLATFORM STATUS",
    )
