"""
Phase 06.2 Verification Suite — Domain Intelligence Agents
-----------------------------------------------------------
Independently validates all five Phase 06.2 domain agents, their security/RBAC/SQL ACL
boundaries, source-data & KPI accuracy, degraded missing/invalid-dataset handling,
experimental ML caveat honesty, OutputVerifier grounding, ExecutionTracer spans,
concurrent execution, and cross-agent metric consistency.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import sys
import time
import unittest
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api.loader import load_data
import python.ai.agents as agents_pkg
from python.ai.agents import (
    AgentAvailability,
    AgentContext,
    AgentDomain,
    AgentRegistry,
    AgentRequest,
    AgentStatus,
    CustomerAgent,
    DecisionAgent,
    ExecutionTracer,
    FinancialAgent,
    OperationsAgent,
    OutputVerifier,
    RestaurantAgent,
    TraceVerificationOutcome,
    VerificationOutcome,
    build_domain_agents,
    create_default_domain_registry,
)


def _make_context(
    *,
    principal_id: str = "tester_operator",
    role: str = "operator",
    scopes: list[str] | None = None,
    query: str = "Analyze platform performance",
    session_id: str = "sess_test",
    timeout_seconds: float = 20.0,
) -> AgentContext:
    return AgentContext(
        principal_id=principal_id,
        principal_role=role,
        principal_scopes=scopes if scopes is not None else ["read", "operator"],
        session_id=session_id,
        user_query=query,
        timeout_seconds=timeout_seconds,
    )


class Phase062DomainAgentsTestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.live_data, cls.source_label = load_data()
        cls.verifier = OutputVerifier(load_default_kpis=True)
        cls.first_customer_id = str(cls.live_data["customers"]["customer_id"].iloc[0])


class TestRegistryAndPhaseBoundary(Phase062DomainAgentsTestBase):
    def test_default_domain_registry_registers_five_operational_agents(self) -> None:
        reg = create_default_domain_registry(preload_planned_blueprints=True)
        operational = reg.list_agents(include_non_operational=False)
        ids = {item.agent_id for item in operational}
        self.assertEqual(
            ids,
            {
                "financial_agent",
                "customer_agent",
                "operations_agent",
                "restaurant_agent",
                "decision_agent",
            },
        )
        for desc in operational:
            self.assertEqual(desc.availability, AgentAvailability.OPERATIONAL)
            self.assertTrue(desc.is_implemented)
            self.assertIsNotNone(reg.get_handler(desc.agent_id))

    def test_phase061_planned_blueprints_still_preserved_by_default(self) -> None:
        planned_only = AgentRegistry(preload_planned_blueprints=True)
        self.assertEqual(planned_only.list_agents(include_non_operational=False), [])
        self.assertEqual(len(planned_only.list_agents(include_non_operational=True)), 5)

    def test_five_phase06_2_domain_agents_remain_registered_and_operational(self) -> None:
        reg = create_default_domain_registry()
        expected = {
            "financial_agent",
            "customer_agent",
            "operations_agent",
            "restaurant_agent",
            "decision_agent",
        }
        operational = reg.list_agents(include_non_operational=False)
        self.assertEqual({item.agent_id for item in operational}, expected)
        for agent_id in expected:
            desc = reg.get(agent_id)
            self.assertIsNotNone(desc)
            self.assertEqual(desc.availability, AgentAvailability.OPERATIONAL)
            self.assertTrue(desc.is_implemented)
            self.assertTrue(callable(reg.get_handler(agent_id)))

    def test_phase06_3_master_orchestrator_exported_and_callable(self) -> None:
        self.assertTrue(hasattr(agents_pkg, "MasterOrchestrator"))
        self.assertTrue(callable(agents_pkg.MasterOrchestrator))
        self.assertTrue(hasattr(agents_pkg, "IntentRouter"))
        self.assertTrue(callable(agents_pkg.IntentRouter))
        self.assertTrue(hasattr(agents_pkg, "synthesize_agent_results"))
        self.assertTrue(callable(agents_pkg.synthesize_agent_results))

    def test_registry_authorization_boundaries(self) -> None:
        reg = create_default_domain_registry()
        viewer_cust = reg.authorize("customer_agent", principal_scopes=["read"])
        self.assertFalse(viewer_cust.allowed)
        self.assertEqual(viewer_cust.missing_scopes, ["operator"])

        viewer_dec = reg.authorize("decision_agent", principal_scopes=["read"])
        self.assertFalse(viewer_dec.allowed)
        self.assertEqual(viewer_dec.missing_scopes, ["operator"])

        viewer_fin = reg.authorize("financial_agent", principal_scopes=["read"], requested_tables=["orders", "payments"])
        self.assertTrue(viewer_fin.allowed)

        bad_tbl = reg.authorize("financial_agent", principal_scopes=["read"], requested_tables=["customers"])
        self.assertFalse(bad_tbl.allowed)
        self.assertEqual(bad_tbl.unauthorized_tables, ["customers"])


class TestFinancialAgent(Phase062DomainAgentsTestBase):
    def setUp(self) -> None:
        self.agent = FinancialAgent()

    def test_valid_overview_matches_certified_kpis_and_unconfirmed_leakage(self) -> None:
        tracer = ExecutionTracer()
        ctx = _make_context(role="viewer", scopes=["read"], query="Give full GMV, Net Revenue, and profit overview")
        req = AgentRequest(
            agent_id="financial_agent",
            domain=AgentDomain.FINANCIAL,
            principal_id=ctx.principal_id,
            user_query=ctx.user_query,
        )
        res = self.agent.execute(req, ctx, data=self.live_data, tracer=tracer, verifier=self.verifier)

        self.assertEqual(res.status, AgentStatus.SUCCESS)
        self.assertFalse(res.is_confirmed_loss)
        self.assertAlmostEqual(res.metrics["gmv_inr"], 46590125.00, places=2)
        self.assertAlmostEqual(res.metrics["net_revenue_inr"], 46425992.00, places=2)
        self.assertAlmostEqual(res.metrics["net_aov_inr"], 967.33, places=2)
        self.assertAlmostEqual(res.metrics["take_rate_pct"], 22.48, places=2)
        self.assertAlmostEqual(res.metrics["realized_profit_inr"], 10953031.58, places=2)
        self.assertAlmostEqual(res.metrics["contribution_margin_pct"], 23.59, places=2)
        self.assertGreater(res.metrics["leakage_flagged_orders"], 0)
        self.assertTrue(any(c.domain == "financial" and not c.is_production_ready for c in res.caveats))
        self.assertTrue(any(p.dataset_or_table == "orders" for p in res.provenance))

        trace = tracer.get_trace(req.request_id, principal_id=ctx.principal_id)
        self.assertIsNotNone(trace)
        self.assertEqual(len(trace.spans), 1)
        self.assertEqual(trace.spans[0].verification_outcome, TraceVerificationOutcome.VERIFIED)

    def test_financial_intents_and_city_filter(self) -> None:
        for intent in ("revenue_trends", "financial_comparison", "financial_anomalies"):
            ctx = _make_context(query=f"Run {intent}", scopes=["read"])
            req = AgentRequest(
                agent_id="financial_agent",
                domain=AgentDomain.FINANCIAL,
                principal_id=ctx.principal_id,
                user_query=ctx.user_query,
                intent=intent,
                filters={"city": "Chennai"},
            )
            res = self.agent.execute(req, ctx, data=self.live_data, verifier=self.verifier)
            self.assertEqual(res.status, AgentStatus.SUCCESS)
            self.assertGreater(res.metrics["net_revenue_inr"], 0.0)
            self.assertLess(res.metrics["net_revenue_inr"], 46425992.00)
            self.assertGreater(len(res.table_rows), 0)

    def test_financial_scoped_sql_execution_and_acl_enforcement(self) -> None:
        ctx = _make_context(scopes=["read"], query="SQL breakdown of order statuses")
        ok_req = AgentRequest(
            agent_id="financial_agent",
            domain=AgentDomain.FINANCIAL,
            principal_id=ctx.principal_id,
            user_query="SELECT order_status, COUNT(*) AS cnt FROM orders GROUP BY order_status LIMIT 10",
            intent="sql",
        )
        ok_res = self.agent.execute(ok_req, ctx, data=self.live_data, verifier=self.verifier)
        self.assertEqual(ok_res.status, AgentStatus.SUCCESS)
        self.assertEqual(len(ok_res.sql_traces), 1)
        self.assertTrue(ok_res.sql_traces[0].validated_by_ast)
        self.assertEqual(ok_res.sql_traces[0].tables_accessed, ["orders"])

        # Table outside financial ACL (`customers`) must fail closed
        bad_sql_req = AgentRequest(
            agent_id="financial_agent",
            domain=AgentDomain.FINANCIAL,
            principal_id=ctx.principal_id,
            user_query="SELECT * FROM customers LIMIT 5",
            intent="sql",
        )
        bad_res = self.agent.execute(bad_sql_req, ctx, data=self.live_data, verifier=self.verifier)
        self.assertEqual(bad_res.status, AgentStatus.BLOCKED)
        self.assertEqual(bad_res.errors[0].code, "SQL_PERMISSION_DENIED")

        # System table probe
        sys_req = AgentRequest(
            agent_id="financial_agent",
            domain=AgentDomain.FINANCIAL,
            principal_id=ctx.principal_id,
            user_query="SELECT name FROM sqlite_master LIMIT 5",
            intent="sql",
        )
        sys_res = self.agent.execute(sys_req, ctx, data=self.live_data, verifier=self.verifier)
        self.assertEqual(sys_res.status, AgentStatus.BLOCKED)
        self.assertEqual(sys_res.errors[0].code, "SQL_PERMISSION_DENIED")

        # Requested ACL table mismatch
        acl_req = AgentRequest(
            agent_id="financial_agent",
            domain=AgentDomain.FINANCIAL,
            principal_id=ctx.principal_id,
            user_query="Summary",
            allowed_tables=["customers"],
        )
        acl_res = self.agent.execute(acl_req, ctx, data=self.live_data, verifier=self.verifier)
        self.assertEqual(acl_res.status, AgentStatus.BLOCKED)
        self.assertEqual(acl_res.errors[0].code, "TABLE_ACL_DENIED")

    def test_financial_missing_and_partial_datasets(self) -> None:
        ctx = _make_context(scopes=["read"])
        req = AgentRequest(
            agent_id="financial_agent",
            domain=AgentDomain.FINANCIAL,
            principal_id=ctx.principal_id,
            user_query="GMV overview",
        )
        blocked_res = self.agent.execute(req, ctx, data={}, verifier=self.verifier)
        self.assertEqual(blocked_res.status, AgentStatus.BLOCKED)
        self.assertEqual(blocked_res.errors[0].code, "MISSING_PRIMARY_DATASET")

        # Partial data: only orders supplied without orders_engineered
        partial_data = {"orders": self.live_data["orders"].head(50).copy()}
        partial_res = self.agent.execute(req, ctx, data=partial_data, verifier=self.verifier)
        self.assertEqual(partial_res.status, AgentStatus.PARTIAL)
        self.assertNotIn("realized_profit_inr", partial_res.metrics)
        self.assertTrue(len(partial_res.data_gaps) > 0)

        # Invalid schema missing final_amount
        bad_orders = pd.DataFrame({"order_id": ["O1"], "order_amount": [100.0], "order_status": ["Delivered"]})
        schema_res = self.agent.execute(req, ctx, data={"orders": bad_orders}, verifier=self.verifier)
        self.assertEqual(schema_res.status, AgentStatus.ERROR)
        self.assertEqual(schema_res.errors[0].code, "SCHEMA_MISMATCH")


class TestCustomerAgent(Phase062DomainAgentsTestBase):
    def setUp(self) -> None:
        self.agent = CustomerAgent()

    def test_rbac_blocks_viewer_read_only_scope(self) -> None:
        viewer_ctx = _make_context(role="viewer", scopes=["read"], query="Customer retention and churn")
        req = AgentRequest(
            agent_id="customer_agent",
            domain=AgentDomain.CUSTOMER,
            principal_id=viewer_ctx.principal_id,
            user_query=viewer_ctx.user_query,
        )
        res = self.agent.execute(req, viewer_ctx, data=self.live_data, verifier=self.verifier)
        self.assertEqual(res.status, AgentStatus.BLOCKED)
        self.assertEqual(res.errors[0].code, "RBAC_SCOPE_DENIED")

    def test_valid_customer_intelligence_kpis_and_experimental_churn_caveat(self) -> None:
        ctx = _make_context(role="operator", scopes=["read", "operator"], query="Customer RFM, retention cohorts, and churn")
        req = AgentRequest(
            agent_id="customer_agent",
            domain=AgentDomain.CUSTOMER,
            principal_id=ctx.principal_id,
            user_query=ctx.user_query,
        )
        res = self.agent.execute(req, ctx, data=self.live_data, verifier=self.verifier)
        self.assertEqual(res.status, AgentStatus.SUCCESS)
        self.assertEqual(res.metrics["total_customers"], 5000)
        self.assertAlmostEqual(res.metrics["repeat_purchase_rate_pct"], 99.94, places=2)
        self.assertAlmostEqual(res.metrics["cohort_m1_retention_pct"], 53.36, places=2)
        self.assertAlmostEqual(res.metrics["realized_arpu_inr"], 9285.20, places=2)
        self.assertEqual(res.metrics["high_risk_churn_customers"], 781)
        self.assertAlmostEqual(res.metrics["high_risk_churn_pct"], 15.62, places=2)

        self.assertEqual(len(res.caveats), 1)
        self.assertFalse(res.caveats[0].is_production_ready)
        self.assertIn(res.caveats[0].validation_status, ("PHASE_07_LOW_EMPIRICAL", "NEEDS_MORE_DATA"))
        self.assertTrue(any(s in res.caveats[0].metric_summary for s in ("0.5161", "0.5218", "ROC-AUC")))

    def test_customer_360_lookup_and_cohort_intent(self) -> None:
        ctx = _make_context(role="operator", scopes=["read", "operator"])
        c360_req = AgentRequest(
            agent_id="customer_agent",
            domain=AgentDomain.CUSTOMER,
            principal_id=ctx.principal_id,
            user_query="Look up Customer 360 profile",
            intent="customer_360",
            filters={"customer_id": self.first_customer_id},
        )
        c360_res = self.agent.execute(c360_req, ctx, data=self.live_data, verifier=self.verifier)
        self.assertEqual(c360_res.status, AgentStatus.SUCCESS)
        self.assertEqual(len(c360_res.table_rows), 1)
        self.assertEqual(c360_res.table_rows[0]["customer_id"], self.first_customer_id)

        cohort_req = AgentRequest(
            agent_id="customer_agent",
            domain=AgentDomain.CUSTOMER,
            principal_id=ctx.principal_id,
            user_query="Show cohort matrix",
            intent="cohort_analysis",
        )
        cohort_res = self.agent.execute(cohort_req, ctx, data=self.live_data, verifier=self.verifier)
        self.assertEqual(cohort_res.status, AgentStatus.SUCCESS)
        self.assertGreater(len(cohort_res.table_rows), 0)

    def test_customer_missing_datasets_and_sql_acl(self) -> None:
        ctx = _make_context(role="operator", scopes=["read", "operator"])
        req = AgentRequest(
            agent_id="customer_agent",
            domain=AgentDomain.CUSTOMER,
            principal_id=ctx.principal_id,
            user_query="Customer intelligence",
        )
        blocked = self.agent.execute(req, ctx, data={}, verifier=self.verifier)
        self.assertEqual(blocked.status, AgentStatus.BLOCKED)

        # Without churn predictions: must emit PARTIAL with explicit gap, NEVER fabricate probabilities
        no_churn = {
            "customers": self.live_data["customers"].head(20).copy(),
            "orders": self.live_data["orders"].head(50).copy(),
        }
        partial = self.agent.execute(req, ctx, data=no_churn, verifier=self.verifier)
        self.assertEqual(partial.status, AgentStatus.PARTIAL)
        self.assertNotIn("avg_churn_probability", partial.metrics)
        self.assertTrue(any("churn" in g.lower() for g in partial.data_gaps))

        # SQL table `riders` outside customer ACL rejected
        bad_sql = AgentRequest(
            agent_id="customer_agent",
            domain=AgentDomain.CUSTOMER,
            principal_id=ctx.principal_id,
            user_query="SELECT * FROM riders LIMIT 5",
            intent="sql",
        )
        sql_denied = self.agent.execute(bad_sql, ctx, data=self.live_data, verifier=self.verifier)
        self.assertEqual(sql_denied.status, AgentStatus.BLOCKED)
        self.assertEqual(sql_denied.errors[0].code, "SQL_PERMISSION_DENIED")


class TestOperationsAgent(Phase062DomainAgentsTestBase):
    def setUp(self) -> None:
        self.agent = OperationsAgent()

    def test_valid_operations_metrics_and_non_production_ml_caveats(self) -> None:
        ctx = _make_context(role="viewer", scopes=["read"], query="Analyze delivery performance, SLA breaches, and ETA")
        req = AgentRequest(
            agent_id="operations_agent",
            domain=AgentDomain.OPERATIONS,
            principal_id=ctx.principal_id,
            user_query=ctx.user_query,
        )
        res = self.agent.execute(req, ctx, data=self.live_data, verifier=self.verifier)
        self.assertEqual(res.status, AgentStatus.SUCCESS)
        self.assertAlmostEqual(res.metrics["avg_delivery_time_mins"], 37.38, places=2)
        self.assertAlmostEqual(res.metrics["sla_breach_rate_pct"], 32.26, places=2)
        self.assertEqual(res.metrics["sla_breach_count"], 16119)
        self.assertAlmostEqual(res.metrics["rider_efficiency_orders_per_rider"], 12.49, places=2)
        self.assertEqual(res.metrics["operational_anomalies_count"], 2184)

        self.assertGreaterEqual(len(res.caveats), 3)
        statuses = {c.model_name.split()[0]: c.validation_status for c in res.caveats}
        prod_map = {c.model_name.split()[0]: c.is_production_ready for c in res.caveats}
        self.assertIn(statuses["eta_prediction"], ("PHASE_07_LOW_EMPIRICAL", "BASELINE_ONLY"))
        self.assertIn(statuses["demand_forecast"], ("PHASE_07_LOW_EMPIRICAL", "BASELINE_ONLY"))
        self.assertFalse(prod_map.get("eta_prediction", False))
        self.assertFalse(prod_map.get("demand_forecast", False))

    def test_operations_intents_sql_acl_and_missing_data(self) -> None:
        ctx = _make_context(role="viewer", scopes=["read"])
        for intent in ("rider_performance", "demand_forecasting", "operational_anomalies"):
            req = AgentRequest(
                agent_id="operations_agent",
                domain=AgentDomain.OPERATIONS,
                principal_id=ctx.principal_id,
                user_query=f"Run {intent}",
                intent=intent,
            )
            res = self.agent.execute(req, ctx, data=self.live_data, verifier=self.verifier)
            self.assertEqual(res.status, AgentStatus.SUCCESS)
            self.assertGreater(len(res.table_rows), 0)

        # Forbidden table (`customers`) in operations SQL
        bad_sql = AgentRequest(
            agent_id="operations_agent",
            domain=AgentDomain.OPERATIONS,
            principal_id=ctx.principal_id,
            user_query="SELECT * FROM customers LIMIT 5",
            intent="sql",
        )
        bad_res = self.agent.execute(bad_sql, ctx, data=self.live_data, verifier=self.verifier)
        self.assertEqual(bad_res.status, AgentStatus.BLOCKED)
        self.assertEqual(bad_res.errors[0].code, "SQL_PERMISSION_DENIED")

        # Empty data store -> BLOCKED
        blocked = self.agent.execute(
            AgentRequest(
                agent_id="operations_agent",
                domain=AgentDomain.OPERATIONS,
                principal_id=ctx.principal_id,
                user_query="SLA overview",
            ),
            ctx,
            data={},
            verifier=self.verifier,
        )
        self.assertEqual(blocked.status, AgentStatus.BLOCKED)


class TestRestaurantAgent(Phase062DomainAgentsTestBase):
    def setUp(self) -> None:
        self.agent = RestaurantAgent()

    def test_valid_restaurant_metrics_avg_rating_and_caveat(self) -> None:
        ctx = _make_context(role="viewer", scopes=["read"], query="Restaurant throughput, ratings, and risk summary")
        req = AgentRequest(
            agent_id="restaurant_agent",
            domain=AgentDomain.RESTAURANT,
            principal_id=ctx.principal_id,
            user_query=ctx.user_query,
        )
        res = self.agent.execute(req, ctx, data=self.live_data, verifier=self.verifier)
        self.assertEqual(res.status, AgentStatus.SUCCESS)
        self.assertEqual(res.metrics["total_restaurants"], 1500)
        self.assertAlmostEqual(res.metrics["avg_restaurant_throughput_inr"], 30950.66, places=2)
        self.assertAlmostEqual(res.metrics["avg_restaurant_rating"], 4.25, places=2)
        self.assertEqual(res.metrics["critical_risk_restaurants"], 3)
        self.assertEqual(res.metrics["at_risk_restaurants"], 397)
        self.assertEqual(len(res.caveats), 1)
        self.assertFalse(res.caveats[0].is_production_ready)
        self.assertIn(res.caveats[0].validation_status, ("PHASE_07_LOW_EMPIRICAL", "NEEDS_MORE_DATA"))

    def test_restaurant_intents_sql_acl_and_degraded_modes(self) -> None:
        ctx = _make_context(role="viewer", scopes=["read"], timeout_seconds=60.0)
        for intent in ("restaurant_risk", "ratings_and_menu", "restaurant_benchmarks", "restaurant_demand"):
            req = AgentRequest(
                agent_id="restaurant_agent",
                domain=AgentDomain.RESTAURANT,
                principal_id=ctx.principal_id,
                user_query=f"Run {intent}",
                intent=intent,
            )
            res = self.agent.execute(req, ctx, data=self.live_data, verifier=self.verifier)
            self.assertEqual(res.status, AgentStatus.SUCCESS)
            self.assertGreater(len(res.table_rows), 0)

        bad_sql = AgentRequest(
            agent_id="restaurant_agent",
            domain=AgentDomain.RESTAURANT,
            principal_id=ctx.principal_id,
            user_query="SELECT * FROM deliveries LIMIT 5",
            intent="sql",
        )
        bad_res = self.agent.execute(bad_sql, ctx, data=self.live_data, verifier=self.verifier)
        self.assertEqual(bad_res.status, AgentStatus.BLOCKED)
        self.assertEqual(bad_res.errors[0].code, "SQL_PERMISSION_DENIED")

        partial_res = self.agent.execute(
            AgentRequest(
                agent_id="restaurant_agent",
                domain=AgentDomain.RESTAURANT,
                principal_id=ctx.principal_id,
                user_query="Catalog check",
            ),
            ctx,
            data={"restaurants": self.live_data["restaurants"].head(25).copy()},
            verifier=self.verifier,
        )
        self.assertEqual(partial_res.status, AgentStatus.PARTIAL)
        self.assertNotIn("avg_restaurant_throughput_inr", partial_res.metrics)

        blocked_res = self.agent.execute(
            AgentRequest(
                agent_id="restaurant_agent",
                domain=AgentDomain.RESTAURANT,
                principal_id=ctx.principal_id,
                user_query="Catalog check",
            ),
            ctx,
            data={},
            verifier=self.verifier,
        )
        self.assertEqual(blocked_res.status, AgentStatus.BLOCKED)


class TestDecisionAgent(Phase062DomainAgentsTestBase):
    def setUp(self) -> None:
        self.agent = DecisionAgent()

    def test_decision_requires_operator_scope(self) -> None:
        viewer_ctx = _make_context(role="viewer", scopes=["read"])
        req = AgentRequest(
            agent_id="decision_agent",
            domain=AgentDomain.DECISION,
            principal_id=viewer_ctx.principal_id,
            user_query="Generate recommendations",
        )
        res = self.agent.execute(req, viewer_ctx, data=self.live_data, verifier=self.verifier)
        self.assertEqual(res.status, AgentStatus.BLOCKED)
        self.assertEqual(res.errors[0].code, "RBAC_SCOPE_DENIED")

    def test_decision_synthesis_rca_simulation_twin_and_nba(self) -> None:
        for intent, query in (
            ("decision_synthesis", "Synthesize platform priorities"),
            ("root_cause", "Why is delivery SLA breach high?"),
            ("what_if_simulation", "What if we reduce discount by 5%?"),
            ("systemic_risk", "Show Digital Twin downstream ripple for operations_delay"),
            ("next_best_action", "Recommend next best actions across platform"),
        ):
            ctx = _make_context(role="operator", scopes=["read", "operator"], query=query, timeout_seconds=45.0)
            req = AgentRequest(
                agent_id="decision_agent",
                domain=AgentDomain.DECISION,
                principal_id=ctx.principal_id,
                user_query=query,
                intent=intent,
            )
            res = self.agent.execute(req, ctx, data=self.live_data, verifier=self.verifier)
            self.assertEqual(res.status, AgentStatus.SUCCESS, f"Intent {intent} gaps={res.data_gaps} err={res.errors}")
            self.assertFalse(res.is_confirmed_loss)
            self.assertGreater(len(res.recommendations), 0)
            self.assertFalse(res.caveats[0].is_production_ready)
            if intent == "what_if_simulation":
                self.assertIn("sim_revenue_diff_inr", res.metrics)

    def test_decision_missing_and_acl_boundaries(self) -> None:
        ctx = _make_context(role="operator", scopes=["read", "operator"])
        blocked = self.agent.execute(
            AgentRequest(
                agent_id="decision_agent",
                domain=AgentDomain.DECISION,
                principal_id=ctx.principal_id,
                user_query="Recommendations",
            ),
            ctx,
            data={},
            verifier=self.verifier,
        )
        self.assertEqual(blocked.status, AgentStatus.BLOCKED)

        bad_sql = AgentRequest(
            agent_id="decision_agent",
            domain=AgentDomain.DECISION,
            principal_id=ctx.principal_id,
            user_query="SELECT * FROM payments LIMIT 5",
            intent="sql",
        )
        sql_denied = self.agent.execute(bad_sql, ctx, data=self.live_data, verifier=self.verifier)
        self.assertEqual(sql_denied.status, AgentStatus.BLOCKED)
        self.assertEqual(sql_denied.errors[0].code, "SQL_PERMISSION_DENIED")


class TestCrossAgentConsistencyConcurrencyAndSecurity(Phase062DomainAgentsTestBase):
    def test_concurrent_five_agent_execution_and_cross_agent_consistency(self) -> None:
        agents = build_domain_agents()
        tracer = ExecutionTracer()
        shared_ctx = _make_context(
            principal_id="ops_concurrent_lead",
            role="admin",
            scopes=["read", "operator", "admin"],
            query="Cross-domain executive snapshot",
        )

        def _invoke(item: tuple[str, object]) -> object:
            aid, agent = item
            req = AgentRequest(
                request_id=shared_ctx.request_id,
                agent_id=aid,
                domain=agent.DOMAIN,
                principal_id=shared_ctx.principal_id,
                session_id=shared_ctx.session_id,
                user_query=shared_ctx.user_query,
            )
            return agent.execute(req, shared_ctx, data=self.live_data, tracer=tracer, verifier=self.verifier)

        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(_invoke, agents.items()))

        self.assertEqual(len(results), 5)
        for res in results:
            self.assertEqual(res.status, AgentStatus.SUCCESS, f"{res.agent_id} gaps={res.data_gaps}")
            self.assertGreaterEqual(res.execution.elapsed_ms, 0.0)

        by_id = {r.agent_id: r for r in results}
        # Shared GMV & Net Revenue must match exactly across Financial, Restaurant (NetRev), Decision
        self.assertEqual(by_id["financial_agent"].metrics["net_revenue_inr"], by_id["decision_agent"].metrics["net_revenue_inr"])
        self.assertEqual(by_id["financial_agent"].metrics["net_revenue_inr"], by_id["restaurant_agent"].metrics["net_revenue_inr"])
        self.assertEqual(by_id["operations_agent"].metrics["sla_breach_rate_pct"], by_id["decision_agent"].metrics["sla_breach_rate_pct"])

        combined_text = " ".join(r.summary for r in results)
        cross_report = self.verifier.verify(combined_text, agent_results=results, include_kpi_catalog=True)
        self.assertEqual(cross_report.outcome, VerificationOutcome.VERIFIED)
        self.assertTrue(cross_report.unconfirmed_loss_preserved)
        self.assertEqual(cross_report.conflicts, [])
        self.assertEqual(cross_report.unsupported_claims, [])

        # Trace inspection
        trace = tracer.get_trace(shared_ctx.request_id, principal_id=shared_ctx.principal_id)
        self.assertIsNotNone(trace)
        self.assertEqual(len(trace.spans), 5)
        self.assertIsNone(tracer.get_trace(shared_ctx.request_id, principal_id="unauthorized_other"))

    def test_output_verifier_detects_cross_agent_conflict_and_hallucination(self) -> None:
        fin = FinancialAgent()
        dec = DecisionAgent()
        ctx = _make_context(role="admin", scopes=["read", "operator", "admin"])
        fin_res = fin.execute(
            AgentRequest(agent_id="financial_agent", domain=AgentDomain.FINANCIAL, principal_id=ctx.principal_id, user_query="Overview"),
            ctx,
            data=self.live_data,
            verifier=self.verifier,
        )
        dec_res = dec.execute(
            AgentRequest(agent_id="decision_agent", domain=AgentDomain.DECISION, principal_id=ctx.principal_id, user_query="Overview"),
            ctx,
            data=self.live_data,
            verifier=self.verifier,
        )

        # Simulated corrupted clone with conflicting net_revenue_inr
        corrupted = dec_res.model_copy(update={"metrics": {**dec_res.metrics, "net_revenue_inr": 99999999.0}})
        conflict_rep = self.verifier.verify("GMV ₹46,590,125.00", agent_results=[fin_res, corrupted])
        self.assertEqual(conflict_rep.outcome, VerificationOutcome.REJECTED)
        self.assertTrue(any(v.code == "CONFLICTING_AGENT_RESULTS" for v in conflict_rep.violations))

        hallucination_rep = self.verifier.verify(
            "Net Revenue reached ₹88,888,888.00 creating a confirmed net financial loss of ₹5,000,000.00.",
            agent_results=[fin_res],
        )
        self.assertEqual(hallucination_rep.outcome, VerificationOutcome.REJECTED)
        codes = {v.code for v in hallucination_rep.violations}
        self.assertIn("UNSUPPORTED_NUMERIC_CLAIM", codes)
        self.assertIn("UNCONFIRMED_LOSS_FRAMING", codes)

    def test_principal_isolation_cancellation_timeout_and_secret_redaction(self) -> None:
        fin = FinancialAgent()
        tracer = ExecutionTracer()
        ctx = _make_context(principal_id="alice", scopes=["read"])

        # Wrong principal
        wrong_req = AgentRequest(
            agent_id="financial_agent",
            domain=AgentDomain.FINANCIAL,
            principal_id="mallory",
            user_query="Show GMV with Bearer sk-testsecret999999999",
        )
        iso_res = fin.execute(wrong_req, ctx, data=self.live_data, tracer=tracer, verifier=self.verifier)
        self.assertEqual(iso_res.status, AgentStatus.BLOCKED)
        self.assertEqual(iso_res.errors[0].code, "PRINCIPAL_ISOLATION_VIOLATION")

        # Cancelled
        cancel_ctx = _make_context(principal_id="bob", scopes=["read"])
        cancel_ctx.cancel("user cancelled")
        can_req = AgentRequest(
            agent_id="financial_agent",
            domain=AgentDomain.FINANCIAL,
            principal_id="bob",
            user_query="Revenue summary",
        )
        can_res = fin.execute(can_req, cancel_ctx, data=self.live_data, tracer=tracer, verifier=self.verifier)
        self.assertEqual(can_res.status, AgentStatus.CANCELLED)

        # Expired deadline
        exp_ctx = _make_context(principal_id="bob", scopes=["read"], timeout_seconds=0.05)
        time.sleep(0.08)
        exp_res = fin.execute(can_req, exp_ctx, data=self.live_data, tracer=tracer, verifier=self.verifier)
        self.assertEqual(exp_res.status, AgentStatus.TIMEOUT)

        # Invalid data type fails cleanly without crash and redacts secrets in query
        secret_ctx = _make_context(
            principal_id="bob",
            scopes=["read"],
            query="Summarize orders Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTYifQ.sig12345",
        )
        self.assertNotIn("eyJhbGci", secret_ctx.user_query)
        bad_data_res = fin.execute(
            AgentRequest(
                agent_id="financial_agent",
                domain=AgentDomain.FINANCIAL,
                principal_id="bob",
                user_query="Check revenue",
            ),
            secret_ctx,
            data={"orders": "not_a_dataframe"},  # type: ignore[dict-item]
            verifier=self.verifier,
        )
        self.assertEqual(bad_data_res.status, AgentStatus.ERROR)
        self.assertEqual(bad_data_res.errors[0].code, "INVALID_DATASET_TYPE")


if __name__ == "__main__":
    unittest.main()

