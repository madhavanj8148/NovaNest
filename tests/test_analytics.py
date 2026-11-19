"""
NovaNest Analytics Unit & Integration Test Suite — Audited & Expanded
Verifies RFM segmentation, monthly cohort retention matrices, funnel event distribution,
audited KPI calculations, missing values, zero denominators, empty datasets, and idempotency.
"""

import sys
import unittest
from pathlib import Path
import pandas as pd
import numpy as np

# Dynamic root anchoring
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from python.analytics.rfm_segmentation import calculate_rfm_segments
from python.analytics.cohort_analysis import compute_cohort_retention_matrix
from python.analytics.funnel_analysis import analyze_marketing_funnel
from python.analytics.kpi_engine import compute_all_kpis
from python.analytics.validate_kpis import run_cross_validation


class TestNovaNestAnalyticsAudited(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cleaned_dir = BASE_DIR / "datasets" / "cleaned"
        cls.engineered_dir = BASE_DIR / "datasets" / "engineered"
        cls.orders = pd.read_csv(cls.cleaned_dir / "orders.csv")
        cls.customers = pd.read_csv(cls.cleaned_dir / "customers.csv")
        cls.events = pd.read_csv(cls.cleaned_dir / "app_events.csv")
        cls.deliv = pd.read_csv(cls.cleaned_dir / "deliveries.csv")
        cls.riders = pd.read_csv(cls.cleaned_dir / "riders.csv")
        cls.rest = pd.read_csv(cls.cleaned_dir / "restaurants.csv")
        cls.eng = pd.read_csv(cls.engineered_dir / "orders_engineered.csv")

    def test_01_rfm_dimensions_and_nulls(self):
        """Verify RFM calculates exactly 5,000 customers with zero nulls."""
        rfm, summary = calculate_rfm_segments(self.orders, self.customers)
        self.assertEqual(len(rfm), 5000, "RFM customer count must equal 5,000.")
        self.assertEqual(rfm["recency"].isnull().sum(), 0, "Recency contains nulls.")
        self.assertEqual(rfm["frequency"].isnull().sum(), 0, "Frequency contains nulls.")
        self.assertEqual(rfm["monetary"].isnull().sum(), 0, "Monetary contains nulls.")
        self.assertGreaterEqual(len(summary), 5, "Expected at least 5 business segments.")

    def test_02_rfm_monetary_parity(self):
        """Verify total monetary spend in RFM equals non-cancelled order amount."""
        rfm, _ = calculate_rfm_segments(self.orders, self.customers)
        expected_spend = self.orders[self.orders["order_status"] != "Cancelled"]["final_amount"].sum()
        actual_spend = rfm["monetary"].sum()
        self.assertAlmostEqual(actual_spend, expected_spend, places=2)

    def test_03_cohort_month_zero_is_100_percent(self):
        """Verify that Month 0 retention is exactly 100% across all monthly cohorts."""
        retention_matrix, _, stats = compute_cohort_retention_matrix(self.orders)
        self.assertIn("Month 0", retention_matrix.columns)
        for val in retention_matrix["Month 0"].dropna():
            self.assertAlmostEqual(val, 100.0, places=1)
        self.assertEqual(stats["total_acquired_customers"], 5000)

    def test_04_repeat_purchase_rate_distinct_from_cohort_retention(self):
        """Verify repeat purchase rate is 99.94% and strictly greater than Month 1 retention (~53%)."""
        _, _, stats = compute_cohort_retention_matrix(self.orders)
        self.assertAlmostEqual(stats["repeat_purchase_rate_pct"], 99.94, places=2)
        self.assertGreater(stats["repeat_purchase_rate_pct"], stats["avg_month_1_retention_pct"])
        self.assertGreater(stats["avg_month_1_retention_pct"], 40.0)

    def test_05_aov_dual_definitions_consistency(self):
        """Verify dual AOV definitions: Net AOV (967.33) and Gross AOV (970.75)."""
        kpis_df, defs = compute_all_kpis(self.orders, self.deliv, self.rest, self.riders, self.customers, self.eng)
        deliv_orders = self.orders[self.orders["order_status"] == "Delivered"]
        num_delivered = len(deliv_orders)

        net_aov = deliv_orders["final_amount"].sum() / num_delivered
        gross_aov = self.orders[self.orders["order_status"] != "Cancelled"]["order_amount"].sum() / num_delivered

        self.assertAlmostEqual(defs["KPI-03"]["value"], round(net_aov, 2), places=2)
        self.assertAlmostEqual(round(net_aov, 2), 967.33, places=2)
        self.assertAlmostEqual(round(gross_aov, 2), 970.75, places=2)
        self.assertIn("Net AOV", defs["KPI-03"]["name"])

    def test_06_contribution_margin_filter_reconciliation(self):
        """Verify Contribution Margin consistency between realized delivered profit and gross booking profit."""
        kpis_df, defs = compute_all_kpis(self.orders, self.deliv, self.rest, self.riders, self.customers, self.eng)
        deliv_eng = self.eng[self.eng["order_status"] == "Delivered"]
        deliv_net_rev = self.orders[self.orders["order_status"] == "Delivered"]["final_amount"].sum()

        realized_profit = deliv_eng["estimated_profit"].sum()
        realized_margin = (realized_profit / deliv_net_rev) * 100.0

        # KPI-12 must match realized delivered margin within 0.05
        self.assertAlmostEqual(defs["KPI-12"]["value"], round(realized_margin, 2), places=2)
        self.assertAlmostEqual(round(realized_margin, 2), 23.59, places=2)

        # Gross booking margin verification
        gross_margin = (self.eng["estimated_profit"].sum() / self.eng["final_amount"].sum()) * 100.0
        self.assertAlmostEqual(round(gross_margin, 2), 23.60, places=2)

    def test_07_clv_and_rider_utilization_terminology(self):
        """Verify metric renaming: Cumulative ARPU (KPI-16) and Deliveries per Rider (KPI-10)."""
        _, defs = compute_all_kpis(self.orders, self.deliv, self.rest, self.riders, self.customers, self.eng)

        # KPI-16 check
        self.assertIn("Cumulative ARPU", defs["KPI-16"]["name"])
        self.assertNotIn("Predictive", defs["KPI-16"]["name"])
        self.assertAlmostEqual(defs["KPI-16"]["value"], 9285.20, places=2)

        # KPI-10 check
        self.assertIn("Delivered Orders per Active Rider", defs["KPI-10"]["name"])
        self.assertEqual(defs["KPI-10"]["unit"], "Deliveries/Rider")
        self.assertAlmostEqual(defs["KPI-10"]["value"], 12.49, places=2)

    def test_08_funnel_event_schema_and_lack_of_timestamps(self):
        """Confirm app_events lacks timestamps and analyzes user stage presence without temporal assumptions."""
        self.assertEqual(list(self.events.columns), ["event_id", "customer_id", "event_type"])
        self.assertNotIn("timestamp", self.events.columns)
        self.assertNotIn("event_datetime", self.events.columns)

        funnel_df, overlap_matrix, stats = analyze_marketing_funnel(self.events)
        self.assertFalse(stats["has_timestamp_column"])
        self.assertEqual(stats["total_clickstream_events"], 100000)
        self.assertEqual(stats["total_active_app_users"], 5000)
        self.assertEqual(len(funnel_df), 6)
        self.assertEqual(overlap_matrix.shape, (6, 6))

    def test_09_restaurant_performance_dimensions(self):
        """Verify restaurant throughput, gross GMV, and order count metrics."""
        _, defs = compute_all_kpis(self.orders, self.deliv, self.rest, self.riders, self.customers, self.eng)
        kpi11 = defs["KPI-11"]
        self.assertTrue(
            "Average Revenue per Registered Restaurant" in kpi11["name"] or "Restaurant Average Gross Revenue Throughput" in kpi11["name"],
            f"Unexpected KPI-11 name: {kpi11['name']}"
        )
        self.assertAlmostEqual(kpi11["value"], 30950.66, places=2)
        # Check notes document GMV and Net Food Payout
        self.assertIn("Gross customer inflow per registered restaurant", kpi11["notes"])
        self.assertIn("Gross food GMV per restaurant", kpi11["notes"])

    def test_10_missing_values_and_empty_datasets_handling(self):
        """Verify analytical functions handle empty datasets gracefully without crashing."""
        empty_orders = pd.DataFrame(columns=self.orders.columns)
        empty_events = pd.DataFrame(columns=self.events.columns)
        empty_cust = pd.DataFrame(columns=self.customers.columns)
        empty_deliv = pd.DataFrame(columns=self.deliv.columns)
        empty_riders = pd.DataFrame(columns=self.riders.columns)
        empty_rest = pd.DataFrame(columns=self.rest.columns)
        empty_eng = pd.DataFrame(columns=self.eng.columns)

        # Funnel on empty events
        f_df, o_df, f_stats = analyze_marketing_funnel(empty_events)
        self.assertEqual(f_stats["total_clickstream_events"], 0)
        self.assertEqual(f_stats["total_active_app_users"], 0)

        # KPI engine on empty datasets
        kpis_df, defs = compute_all_kpis(
            empty_orders, empty_deliv, empty_rest, empty_riders, empty_cust, empty_eng
        )
        self.assertEqual(len(kpis_df), 16)
        self.assertEqual(defs["KPI-01"]["value"], 0.0)
        self.assertEqual(defs["KPI-03"]["value"], 0.0)
        self.assertEqual(defs["KPI-12"]["value"], 0.0)

    def test_11_repeated_execution_consistency_idempotency(self):
        """Verify repeated execution returns identical outputs without drift."""
        kpi_df1, defs1 = compute_all_kpis(self.orders, self.deliv, self.rest, self.riders, self.customers, self.eng)
        kpi_df2, defs2 = compute_all_kpis(self.orders, self.deliv, self.rest, self.riders, self.customers, self.eng)
        pd.testing.assert_frame_equal(kpi_df1, kpi_df2)

        ret1, counts1, stats1 = compute_cohort_retention_matrix(self.orders)
        ret2, counts2, stats2 = compute_cohort_retention_matrix(self.orders)
        pd.testing.assert_frame_equal(ret1, ret2)
        pd.testing.assert_frame_equal(counts1, counts2)
        self.assertEqual(stats1, stats2)

    def test_12_kpi_cross_validation_tolerances_and_statuses(self):
        """Verify all 16 KPIs match across Python, SQL logic, and DAX layers with 5 distinct status tiers."""
        comp_df, summary = run_cross_validation()
        self.assertEqual(summary["total_kpis"], 16)
        self.assertEqual(summary["verified_kpis"], 16, "All 16 KPIs must match within tolerance.")
        self.assertEqual(summary["mismatched_kpis"], 0)
        self.assertIn("python_execution_status", comp_df.columns)
        self.assertIn("sql_static_status", comp_df.columns)
        self.assertIn("sql_live_status", comp_df.columns)
        self.assertIn("dax_review_status", comp_df.columns)
        self.assertIn("powerbi_runtime_status", comp_df.columns)


if __name__ == "__main__":
    unittest.main()
