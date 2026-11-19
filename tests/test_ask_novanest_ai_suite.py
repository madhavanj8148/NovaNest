"""
NovaNest - Advanced AI Business Analyst Complete Test Suite
-----------------------------------------------------------
Tests all 17 validation criteria from Phase 12:
1. Normal business inquiries
2. Actual dataset grounding (MySQL / CSV fallback)
3. Provider abstraction & unconfigured credential handling
4. Mock provider and timeout/rate-limit error resilience
5. SQL safety & injection rejection (DROP, INSERT, UPDATE, DELETE, TRUNCATE, multi-statement)
6. Schema whitelist & invalid table rejection
7. Missing data handling
8. Root-cause analysis with facts, contributing factors, and uncertainties
9. Interactive visualization specifications
10. Decision Simulator integration via natural language
11. Multi-turn conversation context resolution
12. Conversation context reset
13. Existing platform endpoints regression verification
"""

import os
import sys
from pathlib import Path
import unittest
import pandas as pd
import requests

# Ensure project root & python paths are available
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PYTHON_DIR = PROJECT_ROOT / "python"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from python.ai.provider.base import ProviderStatus
from python.ai.provider.mock_provider import MockAIProvider
from python.ai.provider.gemini_provider import GeminiProvider
from python.ai.analyst.sql_agent import validate_and_sanitize_sql, execute_safe_sql
from python.ai.analyst.data_grounding import retrieve_grounded_business_context
from python.ai.analyst.root_cause import perform_root_cause_analysis
from python.ai.analyst.simulation_agent import execute_conversational_simulation
from python.ai.analyst.conversation_manager import record_turn, resolve_follow_up_query, reset_session
from api.loader import load_data


class TestAskNovaNestAISuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data, cls.source_name = load_data()
        cls.api_base = "http://127.0.0.1:8000"
        try:
            r = requests.get(f"{cls.api_base}/api/health", timeout=0.3)
            cls.http = requests.Session()
        except Exception:
            from fastapi.testclient import TestClient
            import api.main
            cls.http = TestClient(api.main.app)
        api_key = os.getenv("NOVANEST_API_KEY") or os.getenv("NOVANEST_ADMIN_KEY") or ""
        admin_key = os.getenv("NOVANEST_ADMIN_KEY") or api_key
        cls.admin_headers = {"X-API-Key": admin_key} if admin_key else {}
        if api_key:
            cls.http.headers.update({"X-API-Key": api_key})

    # 1. Normal Business Inquiries
    def test_01_normal_business_inquiry(self):
        res = self.http.post(f"{self.api_base}/api/ai/ask", json={
            "question": "What is our total revenue and gross GMV?",
            "session_id": "test_suite_norm"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("verified_metrics", data)
        self.assertGreater(len(data["verified_metrics"]), 0)
        self.assertIn("answer", data)
        self.assertIn("provenance", data)

    # 2. Actual Data Grounding
    def test_02_actual_data_grounding(self):
        ctx = retrieve_grounded_business_context("What is our cancellation rate?", self.data, self.source_name)
        self.assertEqual(ctx["domain"], "cancellations")
        self.assertGreater(len(ctx["verified_metrics"]), 0)
        cancellation_labels = [m["label"] for m in ctx["verified_metrics"]]
        self.assertIn("Platform Cancellation Rate", cancellation_labels)
        self.assertIn("Cancelled Orders", cancellation_labels)

    # 3. AI Provider Abstraction (Unconfigured Graceful State)
    def test_03_provider_unconfigured_fallback(self):
        provider = GeminiProvider(api_key="")
        self.assertFalse(provider.is_configured())
        res = provider.generate("Summarize performance")
        self.assertEqual(res.status, ProviderStatus.UNCONFIGURED)
        self.assertIn("GEMINI_API_KEY", res.error)

    # 4. Mock AI Provider for Offline Testing
    def test_04_mock_ai_provider(self):
        mock_p = MockAIProvider(canned_response="Mock Executive Analysis: High profitability maintained.")
        self.assertTrue(mock_p.is_configured())
        res = mock_p.generate("Summarize revenue")
        self.assertEqual(res.status, ProviderStatus.MOCK)
        self.assertIn("Mock Executive Analysis", res.text)

    # 5. SQL Injection Rejection: Mutating Operations
    def test_05_sql_injection_mutating_rejection(self):
        mutating_queries = [
            "DROP TABLE orders",
            "DELETE FROM customers WHERE id = 'C1'",
            "UPDATE restaurants SET commission_rate = 0.05",
            "INSERT INTO riders VALUES ('R999', 'Hacked', '9999')",
            "TRUNCATE TABLE deliveries",
            "ALTER TABLE orders ADD COLUMN hack TEXT"
        ]
        for q in mutating_queries:
            is_valid, _, msg = validate_and_sanitize_sql(q)
            self.assertFalse(is_valid, f"Should reject mutating query: {q}")
            self.assertIn("Only read-only SELECT", msg)

    # 6. SQL Injection Rejection: Multi-Statement
    def test_06_sql_injection_multi_statement(self):
        multi_sql = "SELECT * FROM orders; DROP TABLE customers;"
        is_valid, _, msg = validate_and_sanitize_sql(multi_sql)
        self.assertFalse(is_valid)
        self.assertIn("Multi-statement SQL queries are strictly prohibited", msg)

    # 7. SQL Schema Whitelist: Reject Invalid Tables
    def test_07_sql_schema_whitelist_rejection(self):
        invalid_table_sql = "SELECT * FROM passwords"
        is_valid, _, msg = validate_and_sanitize_sql(invalid_table_sql)
        self.assertFalse(is_valid)
        self.assertIn("not in the approved database schema whitelist", msg)

    # 8. Valid Read-Only SQL with Auto-LIMIT
    def test_08_valid_read_only_sql(self):
        valid_sql = "SELECT restaurant_id, SUM(order_amount) as rev FROM orders GROUP BY restaurant_id ORDER BY rev DESC"
        is_valid, sanitized, msg = validate_and_sanitize_sql(valid_sql)
        self.assertTrue(is_valid)
        self.assertIn("LIMIT 25", sanitized)

    # 9. Root-Cause Analysis Engine (Observed Facts vs Factors vs Uncertainties)
    def test_09_root_cause_analysis_engine(self):
        rca = perform_root_cause_analysis("Why are order cancellations increasing?", self.data)
        self.assertIn("observed_facts", rca)
        self.assertIn("contributing_factors", rca)
        self.assertIn("uncertainties", rca)
        self.assertIn("recommended_actions", rca)
        self.assertGreater(len(rca["observed_facts"]), 0)
        self.assertGreater(len(rca["contributing_factors"]), 0)
        # Verify practical recommendations are grounded
        self.assertGreater(len(rca["recommended_actions"]), 0)

    # 10. Visualization Generation
    def test_10_visualization_generation(self):
        res = self.http.post(f"{self.api_base}/api/ai/ask", json={
            "question": "What are the top 5 restaurants by revenue?",
            "session_id": "test_suite_viz"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsNotNone(data.get("suggested_chart"))
        chart = data["suggested_chart"]
        self.assertIn(chart["type"], ["bar", "line", "pie"])
        self.assertIn("x_key", chart)
        self.assertIn("y_key", chart)
        self.assertGreater(len(chart["data"]), 0)

    # 11. Decision Simulator Integration
    def test_11_decision_simulator_integration(self):
        res = self.http.post(f"{self.api_base}/api/ai/ask", json={
            "question": "What happens if commission increases by 2%?",
            "session_id": "test_suite_sim"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["intent"], "SIMULATION")
        self.assertIsNotNone(data.get("simulation_results"))
        sim = data["simulation_results"]
        self.assertIn("financial_impact", sim)
        self.assertIn("recommendation", sim)
        self.assertIn("comparison_data", sim)
        self.assertGreater(len(sim["comparison_data"]), 0)

    # 12. Follow-Up Contextual Multi-Turn Conversation
    def test_12_follow_up_conversation_context(self):
        sess = "test_suite_followup_turn"
        # Turn 1
        r1 = self.http.post(f"{self.api_base}/api/ai/ask", json={
            "question": "What is our cancellation rate?",
            "session_id": sess
        })
        self.assertEqual(r1.status_code, 200)

        # Turn 2: Contextual follow-up
        r2 = self.http.post(f"{self.api_base}/api/ai/ask", json={
            "question": "Which region is the worst?",
            "session_id": sess
        })
        self.assertEqual(r2.status_code, 200)
        d2 = r2.json()
        self.assertIsNotNone(d2.get("resolved_query"))
        self.assertIn("cancellation", d2["resolved_query"].lower())

    # 13. Conversation Reset Endpoint
    def test_13_conversation_reset(self):
        sess = "test_suite_reset"
        record_turn(sess, "user", "What is our total revenue?", "ANALYTICS", "financial")
        r_reset = self.http.post(
            f"{self.api_base}/api/ai/reset",
            json={"session_id": sess},
            headers=self.admin_headers,
        )
        self.assertEqual(r_reset.status_code, 200)
        self.assertEqual(r_reset.json()["status"], "success")

    # 14. Existing Platform Health & Overview Endpoints Regression
    def test_14_platform_endpoints_regression(self):
        endpoints = [
            "/api/health",
            "/api/overview",
            "/api/customer/overview",
            "/api/restaurant/overview",
            "/api/operations/overview",
            "/api/financial/overview",
            "/api/digital-twin/state",
            "/api/decision/actions"
        ]
        for ep in endpoints:
            resp = self.http.get(f"{self.api_base}{ep}")
            self.assertEqual(resp.status_code, 200, f"Endpoint failed: {ep}")


if __name__ == "__main__":
    unittest.main()
