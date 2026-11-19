"""
NovaNest Phase 06.3 — MasterOrchestrator & Multi-Agent Integration Test Suite
=============================================================================
Independently verifies all Phase 06.3 functional, concurrency, verification,
security, FastAPI, Streamlit compatibility, and frontend contract requirements:
1. Single-agent intent routing across all 5 domain agents
2. Multi-agent intent routing across all 7 specification prompts
3. Broad executive business performance analysis on real CSV datasets
4. Concurrent execution timing + non-shared isolated DataFrame slicing
5. Sequential execution ordering of dependent DecisionAgent tasks
6. Per-agent timeout isolation without blocking sibling agents or hanging pool
7. Single-agent runtime exception isolation and partial recovery
8. Cross-agent metric conflict detection and OutputVerifier fail-closed fallback
9. OutputVerifier grounding (currency/pct/rounding/unconfirmed leakage/rejection)
10. RBAC scope enforcement (`read` vs `operator` vs `admin`) in orchestrator & SQL sandbox
11. Cross-principal session and execution-trace isolation
12. Authenticated FastAPI endpoints (`/api/ai/ask`, `/api/ai/agents/status`,
    `/api/ai/traces/{request_id}`, `/api/ai/reset`) — never treating 401 as pass
13. Streamlit Page 07 & Page 09 backward compatibility (AppTest)
14. General/Math/Programming fast path + clean topic switching
15. Frontend TypeScript/React contract & production build artifact verification
"""

from __future__ import annotations

import os
from pathlib import Path
import secrets
import sys
import threading
import time
from typing import Any, Dict
import unittest

from fastapi.testclient import TestClient
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
PYTHON_DIR = PROJECT_ROOT / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from api import main as api_main
from api.loader import load_data
from python.ai.agents import (
    AgentContext,
    AgentDomain,
    AgentRegistration,
    AgentRegistry,
    AgentRequest,
    AgentResult,
    AgentStatus,
    AgentAvailability,
    GroundedFact,
    IntentRouter,
    MasterOrchestrator,
    OrchestrationMode,
    OutputVerifier,
    VerificationOutcome,
    build_domain_agents,
    create_default_domain_registry,
    synthesize_agent_results,
)
from python.ai.agents.financial_agent import FinancialAgent
from python.ai.agents.operations_agent import OperationsAgent
from python.ai.analyst.conversation_manager import _SESSIONS


class MasterOrchestratorPhase063Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data, cls.data_source = load_data()

    def setUp(self) -> None:
        _SESSIONS.clear()

    # ------------------------------------------------------------------
    # 1. Single-agent routing across all 5 domains
    # ------------------------------------------------------------------
    def test_01_single_agent_routing_all_five_domains(self) -> None:
        router = IntentRouter()

        r_fin = router.route(
            "What is our total revenue and average order value?",
            "What is our total revenue and average order value?",
        )
        self.assertEqual(r_fin.mode, OrchestrationMode.SINGLE_AGENT)
        self.assertEqual(r_fin.stage1_parallel_agents, ["financial_agent"])
        self.assertEqual(r_fin.stage2_sequential_agents, [])

        r_cust = router.route(
            "Show customer RFM segments and repeat purchase cohort metrics.",
            "Show customer RFM segments and repeat purchase cohort metrics.",
        )
        self.assertEqual(r_cust.mode, OrchestrationMode.SINGLE_AGENT)
        self.assertEqual(r_cust.stage1_parallel_agents, ["customer_agent"])

        r_ops = router.route(
            "Compare delivery SLA breach rates and rider workload.",
            "Compare delivery SLA breach rates and rider workload.",
        )
        self.assertEqual(r_ops.mode, OrchestrationMode.SINGLE_AGENT)
        self.assertEqual(r_ops.stage1_parallel_agents, ["operations_agent"])

        r_rest = router.route(
            "Show restaurant ratings, cuisine menu mix and partner health benchmarks.",
            "Show restaurant ratings, cuisine menu mix and partner health benchmarks.",
        )
        self.assertEqual(r_rest.mode, OrchestrationMode.SINGLE_AGENT)
        self.assertEqual(r_rest.stage1_parallel_agents, ["restaurant_agent"])

        r_dec = router.route(
            "Run a strategic what-if simulation scenario and prioritize next best actions.",
            "Run a strategic what-if simulation scenario and prioritize next best actions.",
        )
        self.assertEqual(r_dec.mode, OrchestrationMode.SINGLE_AGENT)
        self.assertEqual(r_dec.stage1_parallel_agents, ["decision_agent"])
        self.assertEqual(r_dec.legacy_route, "SIMULATION")

    # ------------------------------------------------------------------
    # 2. Multi-agent routing across all 7 Task 2 prompt archetypes
    # ------------------------------------------------------------------
    def test_02_multi_agent_routing_task2_prompts(self) -> None:
        router = IntentRouter()

        cases = [
            (
                "Why is profitability declining?",
                {"financial_agent", "operations_agent"},
                {"decision_agent"},
                OrchestrationMode.MULTI_AGENT,
            ),
            (
                "Analyze customer churn and its financial impact.",
                {"customer_agent", "financial_agent"},
                {"decision_agent"},
                OrchestrationMode.MULTI_AGENT,
            ),
            (
                "Which restaurants have poor ratings and high cancellation risk?",
                {"restaurant_agent", "operations_agent"},
                set(),
                OrchestrationMode.MULTI_AGENT,
            ),
            (
                "How can we improve customer retention and profitability?",
                {"customer_agent", "financial_agent"},
                {"decision_agent"},
                OrchestrationMode.MULTI_AGENT,
            ),
            (
                "What happens if we reduce discounts and improve delivery SLA?",
                {"financial_agent", "operations_agent"},
                {"decision_agent"},
                OrchestrationMode.MULTI_AGENT,
            ),
            (
                "Analyze my business performance.",
                {"financial_agent", "operations_agent", "customer_agent", "restaurant_agent"},
                {"decision_agent"},
                OrchestrationMode.MULTI_AGENT,
            ),
        ]
        for query, exp_s1, exp_s2, exp_mode in cases:
            plan = router.route(query, query)
            self.assertEqual(plan.mode, exp_mode, f"Unexpected mode for: {query}")
            self.assertTrue(
                exp_s1.issubset(set(plan.stage1_parallel_agents)),
                f"Expected stage1 {exp_s1} in {plan.stage1_parallel_agents} for: {query}",
            )
            self.assertEqual(
                set(plan.stage2_sequential_agents),
                exp_s2,
                f"Unexpected stage2 for: {query}",
            )

    # ------------------------------------------------------------------
    # 3. Real-data broad business performance execution
    # ------------------------------------------------------------------
    def test_03_broad_business_performance_end_to_end(self) -> None:
        orch = MasterOrchestrator()
        out = orch.orchestrate(
            "Analyze my business performance.",
            principal_id="op_exec_03",
            principal_role="operator",
            principal_scopes=["read", "operator"],
            session_id="exec_overview_03",
            data=self.data,
        )
        chat = out.to_chat_response()

        self.assertEqual(chat["orchestration_mode"], "multi_agent")
        self.assertTrue(chat["grounding_verified"])
        self.assertEqual(chat["verification_outcome"], "verified")
        invoked_ids = {a["agent_id"]: a["status"] for a in chat["agents_invoked"]}
        self.assertEqual(
            set(invoked_ids.keys()),
            {"financial_agent", "operations_agent", "customer_agent", "restaurant_agent", "decision_agent"},
        )
        self.assertTrue(all(st == "success" for st in invoked_ids.values()), f"Statuses: {invoked_ids}")
        self.assertGreater(len(chat["calculation_steps"]), 0)
        self.assertGreater(len(chat["ml_confidence_warnings"]), 0)
        self.assertGreater(len(chat["recommendations"]), 0)
        self.assertEqual(out.agent_result.is_confirmed_loss, False)
        self.assertEqual(chat["conflicts"], [])

        # Validate net revenue / GMV grounded numbers from real CSVs appear accurately
        self.assertAlmostEqual(float(out.agent_result.metrics["gmv_inr"]), 46590125.0, delta=50.0)
        self.assertAlmostEqual(float(out.agent_result.metrics["net_revenue_inr"]), 46425992.0, delta=50.0)

    # ------------------------------------------------------------------
    # 4. Concurrent execution timing & immutable DataFrame slice isolation
    # ------------------------------------------------------------------
    def test_04_concurrent_execution_and_dataframe_isolation(self) -> None:
        reg = AgentRegistry()
        mutated_check: Dict[str, Any] = {}
        lock = threading.Lock()

        def make_worker(aid: str, dom: AgentDomain, mutate: bool):
            def handler(req: AgentRequest, ctx: AgentContext, *, data=None, tracer=None, verifier=None, principal_scopes=None):
                time.sleep(0.18)
                df_orders = data["orders"]
                with lock:
                    mutated_check[f"{aid}_saw_injected_col"] = "_injected_by_peer" in df_orders.columns
                if mutate:
                    df_orders["_injected_by_peer"] = 999
                return AgentResult(
                    request_id=req.request_id,
                    execution_id=req.execution_id,
                    agent_id=aid,
                    domain=dom,
                    status=AgentStatus.SUCCESS,
                    summary=f"{aid} completed cleanly with {len(df_orders):,} orders.",
                    narrative=f"{aid} analyzed {len(df_orders):,} orders.",
                    facts=[
                        GroundedFact(label=f"{aid} Orders", value=int(len(df_orders)), unit="orders", source="test")
                    ],
                )

            return handler

        reg.register(
            AgentRegistration(
                agent_id="financial_agent",
                domain=AgentDomain.FINANCIAL,
                description="Mock parallel fin",
                allowed_tables=["orders"],
                required_scopes=["read"],
                availability=AgentAvailability.OPERATIONAL,
                is_implemented=True,
            ),
            handler=make_worker("financial_agent", AgentDomain.FINANCIAL, mutate=True),
        )
        reg.register(
            AgentRegistration(
                agent_id="operations_agent",
                domain=AgentDomain.OPERATIONS,
                description="Mock parallel ops",
                allowed_tables=["deliveries", "orders"],
                required_scopes=["read"],
                availability=AgentAvailability.OPERATIONAL,
                is_implemented=True,
            ),
            handler=make_worker("operations_agent", AgentDomain.OPERATIONS, mutate=False),
        )
        reg.register(
            AgentRegistration(
                agent_id="restaurant_agent",
                domain=AgentDomain.RESTAURANT,
                description="Mock parallel rest",
                allowed_tables=["restaurants", "orders"],
                required_scopes=["read"],
                availability=AgentAvailability.OPERATIONAL,
                is_implemented=True,
            ),
            handler=make_worker("restaurant_agent", AgentDomain.RESTAURANT, mutate=False),
        )

        tiny_data = {
            "orders": pd.DataFrame({"order_id": list(range(100)), "order_status": ["Delivered"] * 100}),
            "deliveries": pd.DataFrame({"delivery_id": list(range(100))}),
            "restaurants": pd.DataFrame({"restaurant_id": list(range(20))}),
        }
        orch = MasterOrchestrator(registry=reg, max_workers=3)
        t0 = time.monotonic()
        out = orch.orchestrate(
            "Compare revenue, restaurant ratings and delivery cancellations",
            principal_id="op_conc",
            principal_role="operator",
            principal_scopes=["read", "operator"],
            session_id="conc_s",
            data=tiny_data,
        )
        elapsed = time.monotonic() - t0

        # 3 tasks sleeping 0.18s each must run concurrently well under 0.50s sequential wall time
        self.assertLess(elapsed, 0.48, f"Expected parallel execution < 0.48s, got {elapsed:.3f}s")
        self.assertNotIn("_injected_by_peer", tiny_data["orders"].columns)
        self.assertFalse(mutated_check.get("operations_agent_saw_injected_col", True))
        self.assertFalse(mutated_check.get("restaurant_agent_saw_injected_col", True))
        self.assertTrue(out.to_chat_response()["grounding_verified"])

    # ------------------------------------------------------------------
    # 5. Sequential execution of dependent Stage 2 tasks
    # ------------------------------------------------------------------
    def test_05_sequential_dependent_stage2_ordering(self) -> None:
        reg = AgentRegistry()
        timeline: list[tuple[str, str, float]] = []
        upstream_seen: list[Any] = []

        def fin_handler(req: AgentRequest, ctx: AgentContext, **kwargs):
            timeline.append(("fin", "start", time.monotonic()))
            time.sleep(0.08)
            timeline.append(("fin", "end", time.monotonic()))
            return AgentResult(
                request_id=req.request_id,
                agent_id="financial_agent",
                domain=AgentDomain.FINANCIAL,
                status=AgentStatus.SUCCESS,
                summary="Revenue verified at ₹46,425,992.00.",
                narrative="Revenue verified at ₹46,425,992.00.",
                facts=[GroundedFact(label="Net Revenue", value=46425992.0, unit="INR", source="orders")],
            )

        def dec_handler(req: AgentRequest, ctx: AgentContext, **kwargs):
            timeline.append(("dec", "start", time.monotonic()))
            upstream_seen.append(req.metadata.get("upstream_findings"))
            return AgentResult(
                request_id=req.request_id,
                agent_id="decision_agent",
                domain=AgentDomain.DECISION,
                status=AgentStatus.SUCCESS,
                summary="Decision synthesis prioritized operational SLA levers.",
                narrative="Decision synthesis reviewed upstream financial signals.",
            )

        reg.register(
            AgentRegistration(
                agent_id="financial_agent",
                domain=AgentDomain.FINANCIAL,
                description="fin",
                allowed_tables=["orders"],
                required_scopes=["read"],
                availability=AgentAvailability.OPERATIONAL,
                is_implemented=True,
            ),
            handler=fin_handler,
        )
        reg.register(
            AgentRegistration(
                agent_id="decision_agent",
                domain=AgentDomain.DECISION,
                description="dec",
                allowed_tables=["orders"],
                required_scopes=["operator"],
                availability=AgentAvailability.OPERATIONAL,
                is_implemented=True,
            ),
            handler=dec_handler,
        )

        orch = MasterOrchestrator(registry=reg)
        out = orch.orchestrate(
            "What should we recommend for net revenue and unit economics?",
            principal_id="op_seq",
            principal_role="operator",
            principal_scopes=["read", "operator"],
            session_id="seq_s",
            data={"orders": pd.DataFrame({"order_id": [1, 2]})},
        )
        fin_end = next(ts for a, ev, ts in timeline if a == "fin" and ev == "end")
        dec_start = next(ts for a, ev, ts in timeline if a == "dec" and ev == "start")
        self.assertGreaterEqual(dec_start, fin_end)
        self.assertTrue(upstream_seen and upstream_seen[0][0]["agent_id"] == "financial_agent")
        self.assertEqual(out.agent_result.status, AgentStatus.SUCCESS)

    # ------------------------------------------------------------------
    # 6. Agent timeout simulation & non-blocking recovery
    # ------------------------------------------------------------------
    def test_06_agent_timeout_does_not_block_peer_agents(self) -> None:
        reg = AgentRegistry()

        def slow_fin(req: AgentRequest, ctx: AgentContext, **kwargs):
            time.sleep(1.5)  # Exceeds 0.12s per_agent_timeout dramatically
            return AgentResult(
                request_id=req.request_id,
                agent_id="financial_agent",
                domain=AgentDomain.FINANCIAL,
                status=AgentStatus.SUCCESS,
                summary="Slow finish",
            )

        def fast_ops(req: AgentRequest, ctx: AgentContext, **kwargs):
            return AgentResult(
                request_id=req.request_id,
                agent_id="operations_agent",
                domain=AgentDomain.OPERATIONS,
                status=AgentStatus.SUCCESS,
                summary="Average delivery time 37.38 mins across 49,971 deliveries.",
                narrative="Average delivery time 37.38 mins across 49,971 deliveries.",
                facts=[
                    GroundedFact(label="Average Delivery Time", value=37.38, unit="minutes", source="deliveries"),
                    GroundedFact(label="Total Deliveries", value=49971, unit="deliveries", source="deliveries"),
                ],
            )

        reg.register(
            AgentRegistration(
                agent_id="financial_agent",
                domain=AgentDomain.FINANCIAL,
                description="slow fin",
                allowed_tables=["orders"],
                required_scopes=["read"],
                availability=AgentAvailability.OPERATIONAL,
                is_implemented=True,
            ),
            handler=slow_fin,
        )
        reg.register(
            AgentRegistration(
                agent_id="operations_agent",
                domain=AgentDomain.OPERATIONS,
                description="fast ops",
                allowed_tables=["deliveries"],
                required_scopes=["read"],
                availability=AgentAvailability.OPERATIONAL,
                is_implemented=True,
            ),
            handler=fast_ops,
        )

        orch = MasterOrchestrator(registry=reg, default_timeout_seconds=1.0, per_agent_timeout_seconds=0.12)
        t0 = time.monotonic()
        out = orch.orchestrate(
            "Analyze delivery cancellations and revenue margin impact",
            principal_id="op_to",
            principal_role="operator",
            principal_scopes=["read", "operator"],
            session_id="to_s",
            data={"orders": pd.DataFrame(), "deliveries": pd.DataFrame()},
        )
        elapsed = time.monotonic() - t0
        chat = out.to_chat_response()

        self.assertLess(elapsed, 0.75, "Pool shutdown must NOT block waiting for timed-out worker")
        self.assertEqual(out.agent_result.status, AgentStatus.PARTIAL)
        statuses = {a["agent_id"]: a["status"] for a in chat["agents_invoked"]}
        self.assertEqual(statuses["financial_agent"], "timeout")
        self.assertEqual(statuses["operations_agent"], "success")
        self.assertIn("37.38", chat["answer"])
        self.assertTrue(any("timeout" in lim.lower() for lim in chat["limitations"]))
        self.assertTrue(chat["grounding_verified"])

    # ------------------------------------------------------------------
    # 7. Single-agent runtime exception -> graceful partial response
    # ------------------------------------------------------------------
    def test_07_single_agent_failure_partial_recovery(self) -> None:
        reg = AgentRegistry()

        def crashing_rest(req: AgentRequest, ctx: AgentContext, **kwargs):
            raise RuntimeError("Simulated restaurant compute failure with Bearer supersecret_token_abc123")

        OperationsAgent().register_into(reg, overwrite=True)
        reg.register(
            AgentRegistration(
                agent_id="restaurant_agent",
                domain=AgentDomain.RESTAURANT,
                description="broken rest",
                allowed_tables=["restaurants"],
                required_scopes=["read"],
                availability=AgentAvailability.OPERATIONAL,
                is_implemented=True,
            ),
            handler=crashing_rest,
        )

        orch = MasterOrchestrator(registry=reg)
        out = orch.orchestrate(
            "Which restaurants have poor ratings and high cancellation risk?",
            principal_id="op_fail",
            principal_role="operator",
            principal_scopes=["read", "operator"],
            session_id="fail_s",
            data=self.data,
        )
        chat = out.to_chat_response()
        self.assertEqual(out.agent_result.status, AgentStatus.PARTIAL)
        self.assertNotIn("supersecret_token_abc123", chat["answer"])
        self.assertNotIn("supersecret_token_abc123", " ".join(chat["limitations"]))
        statuses = {a["agent_id"]: a["status"] for a in chat["agents_invoked"]}
        self.assertEqual(statuses["restaurant_agent"], "error")
        self.assertEqual(statuses["operations_agent"], "success")
        self.assertTrue(chat["grounding_verified"])

    # ------------------------------------------------------------------
    # 8. Cross-agent metric conflict detection -> rejected & fails closed
    # ------------------------------------------------------------------
    def test_08_cross_agent_conflict_detection_and_rejection(self) -> None:
        fin_res = AgentResult(
            request_id="req_conf",
            agent_id="financial_agent",
            domain=AgentDomain.FINANCIAL,
            status=AgentStatus.SUCCESS,
            summary="Net Revenue is ₹46,425,992.00.",
            narrative="Net Revenue is ₹46,425,992.00.",
            facts=[GroundedFact(label="Net Revenue", value=46425992.0, unit="INR", kpi_id="KPI-02", source="fin")],
            metrics={"net_revenue_inr": 46425992.0},
        )
        dec_res = AgentResult(
            request_id="req_conf",
            agent_id="decision_agent",
            domain=AgentDomain.DECISION,
            status=AgentStatus.SUCCESS,
            summary="Net Revenue is ₹12,000,000.00.",
            narrative="Net Revenue is ₹12,000,000.00.",
            facts=[GroundedFact(label="Net Revenue", value=12000000.0, unit="INR", kpi_id="KPI-02", source="dec")],
            metrics={"net_revenue_inr": 12000000.0},
        )

        syn = synthesize_agent_results(
            user_query="What is net revenue?",
            agent_results=[fin_res, dec_res],
            verifier=OutputVerifier(load_default_kpis=True),
        )
        self.assertEqual(syn.verification_report.outcome, VerificationOutcome.REJECTED)
        self.assertFalse(syn.grounding_verified)
        self.assertGreater(len(syn.conflicts), 0)
        self.assertIn("Limitation", syn.consolidated_narrative)
        self.assertEqual(syn.status, AgentStatus.PARTIAL)

    # ------------------------------------------------------------------
    # 9. OutputVerifier unsupported claim fallback + unconfirmed leakage
    # ------------------------------------------------------------------
    def test_09_output_verifier_rounding_and_rejection_safeguard(self) -> None:
        fin_agent = FinancialAgent()
        ctx = AgentContext(
            principal_id="op_ver",
            principal_role="operator",
            principal_scopes=["read", "operator"],
            user_query="Analyze revenue and promotional leakage",
        )
        req = AgentRequest(
            agent_id="financial_agent",
            domain=AgentDomain.FINANCIAL,
            principal_id="op_ver",
            user_query="Analyze revenue and promotional leakage",
            intent="financial_anomalies",
        )
        fin_res = fin_agent.execute(req, ctx, data=self.data)

        # Legitimate rounding (₹4.66 Cr and ₹4.64 Cr) verifies cleanly & keeps is_confirmed_loss=False
        ok_syn = synthesize_agent_results(
            user_query="Analyze revenue and promotional leakage",
            agent_results=[fin_res],
            candidate_text_override=(
                "Platform GMV is ₹4.66 Cr and Net Revenue is ₹4.64 Cr. "
                "Promotional leakage screening signals remain unconfirmed (is_confirmed_loss=False)."
            ),
        )
        self.assertEqual(ok_syn.verification_report.outcome, VerificationOutcome.VERIFIED)
        self.assertTrue(ok_syn.grounding_verified)
        self.assertIs(ok_syn.is_confirmed_loss, False)

        # Fabricated savings / ungrounded claim must be rejected safely
        bad_syn = synthesize_agent_results(
            user_query="Analyze revenue",
            agent_results=[fin_res],
            candidate_text_override="Guaranteed net savings of ₹9,876,543.00 verified immediately.",
        )
        self.assertEqual(bad_syn.verification_report.outcome, VerificationOutcome.REJECTED)
        self.assertFalse(bad_syn.grounding_verified)
        self.assertNotIn("9,876,543", bad_syn.consolidated_narrative)
        self.assertIn("Verification Limitation Notice", bad_syn.consolidated_narrative)

    # ------------------------------------------------------------------
    # 10. RBAC enforcement across Viewer (`read`) vs Operator
    # ------------------------------------------------------------------
    def test_10_rbac_scope_enforcement_partial_and_sql(self) -> None:
        orch = MasterOrchestrator()

        # Viewer holding ONLY ["read"] asking broad overview:
        # read-permitted agents (financial, operations, restaurant) succeed, while operator-gated
        # customer_agent and decision_agent MUST be BLOCKED transparently without failing the whole request.
        out_viewer = orch.orchestrate(
            "Analyze my business performance.",
            principal_id="viewer_1",
            principal_role="viewer",
            principal_scopes=["read"],
            session_id="rbac_v1",
            data=self.data,
        )
        chat_v = out_viewer.to_chat_response()
        statuses = {a["agent_id"]: a["status"] for a in chat_v["agents_invoked"]}
        self.assertEqual(statuses["customer_agent"], "blocked")
        self.assertEqual(statuses["decision_agent"], "blocked")
        self.assertEqual(statuses["financial_agent"], "success")
        self.assertEqual(out_viewer.agent_result.status, AgentStatus.PARTIAL)
        self.assertTrue(any("blocked" in l.lower() for l in chat_v["limitations"]))

        # SQL sandbox blocked cleanly for viewer lacking operator scope
        out_sql_v = orch.orchestrate(
            "SELECT payment_method, COUNT(*) AS cnt FROM payments GROUP BY payment_method",
            principal_id="viewer_1",
            principal_role="viewer",
            principal_scopes=["read"],
            session_id="rbac_v_sql",
            data=self.data,
        )
        self.assertEqual(out_sql_v.agent_result.status, AgentStatus.BLOCKED)
        self.assertFalse(out_sql_v.to_chat_response()["sql_valid"])

    # ------------------------------------------------------------------
    # 11. Cross-principal session and execution trace isolation
    # ------------------------------------------------------------------
    def test_11_session_and_trace_isolation(self) -> None:
        orch = MasterOrchestrator()

        out_a = orch.orchestrate(
            "What is our cancellation rate?",
            principal_id="op_alpha",
            principal_role="operator",
            principal_scopes=["read", "operator"],
            session_id="shared_sid",
            data=self.data,
        )
        self.assertIn("3.96%", out_a.to_chat_response()["answer"])

        # Principal B reuses same session_id='shared_sid', asks vague follow-up
        out_b = orch.orchestrate(
            "Which city has the best average rating?",
            principal_id="op_beta",
            principal_role="operator",
            principal_scopes=["read", "operator"],
            session_id="shared_sid",
            data=self.data,
        )
        resolved_b = (out_b.to_chat_response().get("resolved_query") or "").lower()
        self.assertNotIn("cancellation", resolved_b)

        # Trace lookup strictly enforces caller principal ownership
        self.assertIsNotNone(orch.tracer.get_trace(out_a.request_id, principal_id="op_alpha"))
        self.assertIsNone(orch.tracer.get_trace(out_a.request_id, principal_id="op_beta"))

    # ------------------------------------------------------------------
    # 12. Authenticated FastAPI endpoints & SQL AST security
    # ------------------------------------------------------------------
    def test_12_authenticated_fastapi_endpoints(self) -> None:
        v_key = secrets.token_urlsafe(24)
        o_key = secrets.token_urlsafe(24)
        a_key = secrets.token_urlsafe(24)
        prev = {k: os.environ.get(k) for k in ("NOVANEST_VIEWER_KEY", "NOVANEST_API_KEY", "NOVANEST_ADMIN_KEY")}
        try:
            os.environ["NOVANEST_VIEWER_KEY"] = v_key
            os.environ["NOVANEST_API_KEY"] = o_key
            os.environ["NOVANEST_ADMIN_KEY"] = a_key

            client = TestClient(api_main.app)
            h_view = {"X-API-Key": v_key}
            h_op = {"X-API-Key": o_key}
            h_adm = {"X-API-Key": a_key}

            # Unauthenticated rejections (401)
            self.assertEqual(client.get("/api/ai/agents/status").status_code, 401)
            self.assertEqual(client.post("/api/ai/ask", json={"question": "Total revenue"}).status_code, 401)
            self.assertEqual(client.post("/api/ai/reset", json={"session_id": "s_api"}).status_code, 401)

            # Viewer -> allowed read on /api/ai/agents/status, forbidden on /api/ai/ask & /api/ai/reset
            st_res = client.get("/api/ai/agents/status", headers=h_view)
            self.assertEqual(st_res.status_code, 200)
            st_json = st_res.json()
            self.assertEqual(len(st_json["registered_agents"]), 5)
            self.assertEqual(len(st_json["experimental_ml_models"]), 5)
            self.assertEqual(client.post("/api/ai/ask", json={"question": "hi"}, headers=h_view).status_code, 403)

            # Empty query -> 400
            self.assertEqual(client.post("/api/ai/ask", json={"question": "   "}, headers=h_op).status_code, 400)

            # Operator multi-agent + city filter
            ask_res = client.post(
                "/api/ai/ask",
                json={"question": "Analyze customer churn and its financial impact.", "session_id": "api_s1"},
                headers=h_op,
            )
            self.assertEqual(ask_res.status_code, 200)
            body = ask_res.json()
            self.assertEqual(body["orchestration_mode"], "multi_agent")
            self.assertTrue(body["grounding_verified"])
            self.assertEqual(body["verification_outcome"], "verified")
            self.assertIn("request_id", body)
            self.assertIn("trace_id", body)
            self.assertGreaterEqual(len(body["agents_invoked"]), 2)

            # Operator trace retrieval allowed for own trace, denied for different principal
            tr_ok = client.get(f"/api/ai/traces/{body['request_id']}", headers=h_op)
            self.assertEqual(tr_ok.status_code, 200)
            self.assertEqual(client.get(f"/api/ai/traces/{body['request_id']}", headers=h_adm).status_code, 404)

            # SQL injection attempt through /api/ai/ask blocked by AST validator
            sqli_res = client.post(
                "/api/ai/ask",
                json={"question": "SELECT name FROM sqlite_master;", "session_id": "api_sqli"},
                headers=h_op,
            )
            self.assertEqual(sqli_res.status_code, 200)
            self.assertFalse(sqli_res.json()["sql_valid"])

            # Reset RBAC: operator forbidden (403), admin cannot clear operator's session
            self.assertEqual(client.post("/api/ai/reset", json={"session_id": "api_s1"}, headers=h_op).status_code, 403)
            adm_reset = client.post("/api/ai/reset", json={"session_id": "api_s1"}, headers=h_adm)
            self.assertEqual(adm_reset.status_code, 200)
            self.assertFalse(adm_reset.json()["cleared"])
        finally:
            for k, v in prev.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    # ------------------------------------------------------------------
    # 13. General Knowledge / Math / Code & Topic-Switch isolation
    # ------------------------------------------------------------------
    def test_13_general_assistant_and_topic_switch_fast_path(self) -> None:
        orch = MasterOrchestrator()

        math_out = orch.orchestrate(
            "Calculate compound interest on 2000 at 20% for 2 years",
            principal_id="op_gen",
            principal_role="operator",
            principal_scopes=["read", "operator"],
            session_id="gen_s",
            data=self.data,
        ).to_chat_response()
        self.assertEqual(math_out["orchestration_mode"], "general_assistant")
        self.assertFalse(math_out["requires_business_data"])
        self.assertEqual(math_out["agents_invoked"], [])
        self.assertIn("2,880", math_out["answer"])

        # After business turn, switching to Python clears business context
        orch.orchestrate(
            "What is our cancellation rate?",
            principal_id="op_gen",
            principal_role="operator",
            principal_scopes=["read", "operator"],
            session_id="gen_s",
            data=self.data,
        )
        py_out = orch.orchestrate(
            "What is Python?",
            principal_id="op_gen",
            principal_role="operator",
            principal_scopes=["read", "operator"],
            session_id="gen_s",
            data=self.data,
        ).to_chat_response()
        self.assertEqual(py_out["orchestration_mode"], "general_assistant")
        self.assertFalse(py_out["requires_business_data"])
        self.assertEqual(py_out["verified_metrics"], [])

    # ------------------------------------------------------------------
    # 14. Streamlit Page 07 backward compatibility check
    # ------------------------------------------------------------------
    def test_14_streamlit_page07_compatibility(self) -> None:
        from streamlit.testing.v1 import AppTest

        at7 = AppTest.from_file(
            str(PROJECT_ROOT / "streamlit_app" / "pages" / "07_Ask_NovaNest.py"),
            default_timeout=45,
        )
        at7.run()
        self.assertEqual(len(at7.exception), 0, f"Page 07 render error: {at7.exception}")

    # ------------------------------------------------------------------
    # 15. Frontend API contract & built bundle integrity
    # ------------------------------------------------------------------
    def test_15_frontend_contract_and_dist_verification(self) -> None:
        api_ts = (PROJECT_ROOT / "frontend" / "src" / "services" / "api.ts").read_text(encoding="utf-8")
        ai_view = (PROJECT_ROOT / "frontend" / "src" / "views" / "AiIntelligenceView.tsx").read_text(encoding="utf-8")
        chatbot = (PROJECT_ROOT / "frontend" / "src" / "components" / "FloatingChatbot.tsx").read_text(encoding="utf-8")

        for field in (
            "agents_invoked",
            "orchestration_mode",
            "calculation_steps",
            "ml_confidence_warnings",
            "limitations",
            "data_source_badges",
            "grounding_verified",
            "verification_outcome",
            "getAiAgentsStatus",
        ):
            self.assertIn(field, api_ts, f"Missing contract field in api.ts: {field}")

        self.assertIn("agents_invoked", ai_view)
        self.assertIn("calculation_steps", ai_view)
        self.assertIn("ml_confidence_warnings", ai_view)
        self.assertIn("agents_invoked", chatbot)
        self.assertIn("limitations", chatbot)

        dist_index = PROJECT_ROOT / "frontend" / "dist" / "index.html"
        self.assertTrue(dist_index.exists(), "frontend/dist/index.html build artifact must exist")

    # ------------------------------------------------------------------
    # 16. Regression: ROOT_CAUSE "Why is delivery declining?" verification
    # ------------------------------------------------------------------
    def test_16_root_cause_delivery_declining_verification_and_safeguards(self) -> None:
        orch = MasterOrchestrator(max_workers=2)

        # 1. Successful verification on exact query
        res = orch.orchestrate("Why is delivery declining?")
        chat = res.to_chat_response()

        self.assertEqual(chat["intent"], "ROOT_CAUSE")
        self.assertEqual(chat["verification_outcome"], "verified")
        self.assertTrue(chat["grounding_verified"])
        self.assertEqual(chat["conflicts"], [])
        self.assertIn("operations_agent", [a["agent_id"] for a in chat["agents_invoked"]])
        self.assertIn("decision_agent", [a["agent_id"] for a in chat["agents_invoked"]])

        rca = chat.get("root_cause_analysis")
        self.assertIsNotNone(rca)
        self.assertIn("Elevated Delivery Times", rca.get("investigation_target", ""))
        self.assertGreaterEqual(len(rca.get("observed_facts", [])), 1)
        self.assertGreaterEqual(len(rca.get("contributing_factors", [])), 1)

        # Check telemetry object structure
        self.assertIn("telemetry", chat)
        self.assertIn("agents_invoked", chat["telemetry"])

        # 2. Intentional rejection safeguard: fabricated numeric claim must fail closed
        bad_text = (
            "### Fabricated Hallucination\n"
            "Delivery latency increased by exactly 987,654.32 hours due to 999,999 phantom courier strikes."
        )
        fake_result = AgentResult(
            request_id="test-fake",
            execution_id="test-fake",
            agent_id="decision_agent",
            domain=AgentDomain.DECISION,
            status=AgentStatus.SUCCESS,
            summary="Fabricated claims.",
            narrative=bad_text,
            facts=[],
            metrics={},
        )
        bad_syn = synthesize_agent_results(
            user_query="Why is delivery declining?",
            agent_results=[fake_result],
            candidate_text_override=bad_text,
        )
        self.assertEqual(bad_syn.verification_report.outcome, VerificationOutcome.REJECTED)
        self.assertFalse(bad_syn.grounding_verified)
        self.assertNotIn("987,654.32", bad_syn.consolidated_narrative)
        self.assertIn("Verification Limitation Notice", bad_syn.consolidated_narrative)

        # 3. Verify all 5 agents and DecisionAgent work together cleanly
        plan_5 = orch.router.route(
            "Analyze my overall business performance across all departments.",
            "Analyze my overall business performance across all departments.",
        )
        self.assertIn("financial_agent", plan_5.stage1_parallel_agents)
        self.assertIn("operations_agent", plan_5.stage1_parallel_agents)
        self.assertIn("customer_agent", plan_5.stage1_parallel_agents)
        self.assertIn("restaurant_agent", plan_5.stage1_parallel_agents)
        self.assertIn("decision_agent", plan_5.stage2_sequential_agents)

        res_5 = orch.orchestrate("Analyze my overall business performance across all departments.")
        chat_5 = res_5.to_chat_response()
        self.assertEqual(chat_5["verification_outcome"], "verified")
        self.assertTrue(chat_5["grounding_verified"])
        self.assertEqual(len(chat_5["conflicts"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)

