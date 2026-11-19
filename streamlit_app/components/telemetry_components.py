"""
NovaNest Multi-Agent Telemetry Card Component for Streamlit
-----------------------------------------------------------
Renders enterprise-grade telemetry status cards for MasterOrchestrator
execution across all five domain intelligence agents and OutputVerifier.

Provides visual parity with the React `AgentTelemetryCard.tsx`.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import streamlit as st

DOMAIN_AGENTS = [
    {
        "id": "financial_agent",
        "name": "Financial Intelligence",
        "stage": "Stage 1",
        "role": "GMV, Revenue & Margins",
        "icon": "💰",
    },
    {
        "id": "customer_agent",
        "name": "Customer Intelligence",
        "stage": "Stage 1",
        "role": "RFM, CLV & Churn",
        "icon": "👥",
    },
    {
        "id": "operations_agent",
        "name": "Operations Intelligence",
        "stage": "Stage 1",
        "role": "Dispatch, ETA & SLA",
        "icon": "⚡",
    },
    {
        "id": "restaurant_agent",
        "name": "Restaurant Intelligence",
        "stage": "Stage 1",
        "role": "Health Index & Risk",
        "icon": "🍽️",
    },
    {
        "id": "decision_agent",
        "name": "Decision Synthesis",
        "stage": "Stage 2",
        "role": "Actionable Interventions",
        "icon": "🧠",
    },
]


def render_agent_telemetry_card(
    telemetry: Optional[Dict[str, Any]] = None,
    events: Optional[List[Dict[str, Any]]] = None,
    is_live: bool = False,
    verification_outcome: Optional[str] = "verified",
    request_id: Optional[str] = None,
    duration_ms: Optional[float] = None,
) -> None:
    """
    Renders the unified 5-agent telemetry card in Streamlit.
    Accepts completed execution metadata or real-time event logs.
    """
    # Parse agent statuses from telemetry or event history
    invoked_ids: set[str] = set()
    if telemetry and isinstance(telemetry, dict):
        exec_times = telemetry.get("agent_execution_times") or telemetry.get("execution_times") or {}
        invoked_ids.update(exec_times.keys())
        for ag in telemetry.get("agents_invoked") or []:
            if isinstance(ag, dict) and ag.get("agent_id"):
                invoked_ids.add(ag["agent_id"])
            elif isinstance(ag, str):
                invoked_ids.add(ag)

    agent_states: Dict[str, Dict[str, Any]] = {}
    for agent in DOMAIN_AGENTS:
        if is_live:
            init_status = "pending"
        elif invoked_ids:
            init_status = "completed" if agent["id"] in invoked_ids else "skipped"
        else:
            init_status = "completed"
        agent_states[agent["id"]] = {
            "status": init_status,
            "duration_ms": None,
            "error": None,
        }

    # Extract status from events if provided
    if events:
        for evt in events:
            evt_type = evt.get("event", "") or evt.get("event_type", "")
            data = evt.get("data", {})
            ag_name = data.get("agent_name") or data.get("agent")
            if ag_name and ag_name in agent_states:
                if evt_type in ("agent_started",):
                    agent_states[ag_name]["status"] = "running"
                elif evt_type in ("agent_completed",):
                    agent_states[ag_name]["status"] = "completed"
                    if data.get("duration_ms") is not None:
                        agent_states[ag_name]["duration_ms"] = data.get("duration_ms")
                elif evt_type in ("agent_failed",):
                    agent_states[ag_name]["status"] = "error"
                    agent_states[ag_name]["error"] = data.get("safe_message", "Error")

    # If completed response metadata is passed directly
    if telemetry and isinstance(telemetry, dict):
        exec_times = telemetry.get("agent_execution_times") or telemetry.get("execution_times") or {}
        for ag_id, ms in exec_times.items():
            if ag_id in agent_states:
                agent_states[ag_id]["status"] = "completed"
                agent_states[ag_id]["duration_ms"] = ms

        # Also support agents_invoked list from to_chat_response()
        agents_invoked = telemetry.get("agents_invoked") or []
        for ag in agents_invoked:
            ag_id = ag.get("agent_id")
            if ag_id in agent_states:
                agent_states[ag_id]["status"] = "completed" if ag.get("status") == "success" else "error"
                if ag.get("elapsed_ms") is not None:
                    agent_states[ag_id]["duration_ms"] = ag.get("elapsed_ms")

        failed_agents = telemetry.get("failed_agents") or []
        for ag_id in failed_agents:
            if ag_id in agent_states:
                agent_states[ag_id]["status"] = "error"

    # Status pill color mapping
    def get_badge(status_str: str, dur_ms: Optional[float] = None) -> str:
        s = (status_str or "").lower()
        dur_str = f" ({dur_ms:.0f}ms)" if dur_ms is not None else ""
        if s == "completed":
            return f'<span style="background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); padding: 2px 8px; border-radius: 9999px; font-size: 0.68rem; font-weight: 600;">COMPLETED{dur_str}</span>'
        elif s == "running":
            return f'<span style="background: rgba(59, 130, 246, 0.2); color: #60A5FA; border: 1px solid rgba(59, 130, 246, 0.4); padding: 2px 8px; border-radius: 9999px; font-size: 0.68rem; font-weight: 600; animation: pulse 1.5s infinite;">RUNNING...</span>'
        elif s == "error":
            return '<span style="background: rgba(239, 68, 68, 0.15); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.3); padding: 2px 8px; border-radius: 9999px; font-size: 0.68rem; font-weight: 600;">FAILED</span>'
        elif s == "skipped":
            return '<span style="background: rgba(100, 116, 139, 0.15); color: #94A3B8; border: 1px solid rgba(100, 116, 139, 0.3); padding: 2px 8px; border-radius: 9999px; font-size: 0.68rem; font-weight: 600;">SKIPPED</span>'
        else:
            return '<span style="background: rgba(100, 116, 139, 0.1); color: #64748B; border: 1px solid rgba(100, 116, 139, 0.2); padding: 2px 8px; border-radius: 9999px; font-size: 0.68rem; font-weight: 600;">QUEUED</span>'

    v_badge = (
        '<span style="background: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.4); padding: 3px 10px; border-radius: 6px; font-size: 0.72rem; font-weight: 700;">✓ Ground Truth Verified</span>'
        if verification_outcome == "verified"
        else f'<span style="background: rgba(245, 158, 11, 0.2); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.4); padding: 3px 10px; border-radius: 6px; font-size: 0.72rem; font-weight: 700;">⚠ Verification: {verification_outcome}</span>'
    )

    tot_dur = f"Duration: {duration_ms:.0f}ms" if duration_ms is not None else ""
    req_str = f"Request: <code>{request_id[:12]}...</code>" if request_id else ""
    footer_meta = " • ".join([m for m in [tot_dur, req_str] if m])

    # Build agent status rows
    rows_html = []
    for ag in DOMAIN_AGENTS:
        ag_info = agent_states.get(ag["id"], {})
        badge_html = get_badge(ag_info.get("status", "pending"), ag_info.get("duration_ms"))
        stage_tag = (
            '<span style="font-size: 0.65rem; color: #38BDF8; font-weight: 700; background: rgba(56, 189, 248, 0.1); padding: 1px 5px; border-radius: 4px;">S1 PARALLEL</span>'
            if ag["stage"] == "Stage 1"
            else '<span style="font-size: 0.65rem; color: #A78BFA; font-weight: 700; background: rgba(167, 139, 250, 0.1); padding: 1px 5px; border-radius: 4px;">S2 SYNTHESIS</span>'
        )

        row = (
            f'<div style="display: flex; align-items: center; justify-content: space-between; padding: 6px 10px; margin-bottom: 4px; background: rgba(255, 255, 255, 0.02); border-radius: 6px; border: 1px solid rgba(255, 255, 255, 0.04);">'
            f'<div style="display: flex; align-items: center; gap: 8px;">'
            f'<span style="font-size: 1rem;">{ag["icon"]}</span>'
            f'<div>'
            f'<div style="font-size: 0.78rem; font-weight: 600; color: #F1F5F9;">{ag["name"]} &nbsp;{stage_tag}</div>'
            f'<div style="font-size: 0.68rem; color: #94A3B8;">{ag["role"]}</div>'
            f'</div></div>'
            f'<div>{badge_html}</div>'
            f'</div>'
        )
        rows_html.append(row)

    all_rows = "".join(rows_html)

    card_container = (
        f'<div style="background: #0B0F17; border: 1px solid rgba(59, 130, 246, 0.25); border-radius: 10px; padding: 12px 16px; margin: 12px 0; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);">'
        f'<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 8px;">'
        f'<div style="display: flex; align-items: center; gap: 8px;">'
        f'<span style="font-size: 1.1rem; color: #60A5FA;">⚡</span>'
        f'<span style="font-size: 0.82rem; font-weight: 700; color: #FFFFFF; text-transform: uppercase; letter-spacing: 0.05em;">MasterOrchestrator Multi-Agent Execution</span>'
        f'</div>'
        f'<div>{v_badge}</div>'
        f'</div>'
        f'<div style="margin-bottom: 8px;">{all_rows}</div>'
        f'<div style="display: flex; justify-content: space-between; font-size: 0.68rem; color: #64748B; margin-top: 6px; border-top: 1px solid rgba(255, 255, 255, 0.04); padding-top: 6px;">'
        f'<span>Architecture: Zero-Copy CoW Engine • AST Grounding</span>'
        f'<span>{footer_meta}</span>'
        f'</div>'
        f'</div>'
    )
    st.markdown(card_container, unsafe_allow_html=True)
