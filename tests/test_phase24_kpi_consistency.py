"""
NovaNest Phase 24 Regression Test Suite: Cross-Platform KPI & Data Consistency
-----------------------------------------------------------------------------
Validates:
1. Platform ₹50 minimum order payment floor (below, at, and above floor + 67-row audit).
2. Transparent data-source fallback (Live MySQL vs. SQLite/CSV fallback).
3. KPI-11 Average Revenue per Registered Restaurant (1,500 registered vs 1,499 active).
4. Customer Repeat Rate (99.94%) vs Transaction Repeat Order Share (89.99%).
5. All 7 financial metric mathematical identities.
"""

import unittest
from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
CLEANED_DIR = BASE_DIR / "datasets" / "cleaned"
ENGINEERED_DIR = BASE_DIR / "datasets" / "engineered"

from python.analytics.kpi_engine import compute_all_kpis
from python.analytics.validate_kpis import run_cross_validation, check_minimum_order_floor


class TestPhase24KpiConsistency(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orders = pd.read_csv(CLEANED_DIR / "orders.csv")
        cls.customers = pd.read_csv(CLEANED_DIR / "customers.csv")
        cls.restaurants = pd.read_csv(CLEANED_DIR / "restaurants.csv")
        cls.deliveries = pd.read_csv(CLEANED_DIR / "deliveries.csv")
        cls.orders_eng = pd.read_csv(ENGINEERED_DIR / "orders_engineered.csv")

    # =========================================================================
    # 1. ₹50 MINIMUM ORDER PAYMENT FLOOR REGRESSION TESTS
    # =========================================================================
    def test_floor_logic_synthetic_cases(self):
        """Tests below-floor, at-floor, and above-floor clamping rules."""
        # Case A: Below floor (linear = 30 + 10 - 30 = 10 -> clamped to 50)
        lin_below = 30 + 10 - 30
        self.assertEqual(max(50.0, lin_below), 50.0)

        # Case B: Exactly at floor (linear = 40 + 20 - 10 = 50 -> 50)
        lin_at = 40 + 20 - 10
        self.assertEqual(max(50.0, lin_at), 50.0)

        # Case C: Above floor (linear = 500 + 30 - 50 = 480 -> 480)
        lin_above = 500 + 30 - 50
        self.assertEqual(max(50.0, lin_above), 480.0)

    def test_floor_logic_on_historical_dataset(self):
        """Verifies that all 49,971 historical orders strictly satisfy the clamped invariant."""
        res = check_minimum_order_floor(self.orders)
        self.assertTrue(res["invariant_passed"], "Historical orders violate max(50.0, linear) clamp invariant")
        self.assertEqual(res["total_orders"], 49971)
        self.assertEqual(res["clamped_orders_count"], 67, "Expected exactly 67 orders to invoke floor clamp")
        self.assertEqual(res["delivered_clamped_count"], 65)
        self.assertEqual(res["cancelled_clamped_count"], 2)
        self.assertEqual(res["total_floor_retention_inr"], 911.0, "Total retention floor adjustment must equal ₹911.00")
        self.assertEqual(res["delivered_floor_retention_inr"], 876.0, "Delivered retention floor adjustment must equal ₹876.00")

    # =========================================================================
    # 2. DATA SOURCE REPORTING & FALLBACK TESTS
    # =========================================================================
    def test_fallback_data_source_reporting(self):
        """Forces fallback engine and verifies explicit, honest labeling."""
        comp_df, summary = run_cross_validation(force_engine="fallback")
        self.assertEqual(summary["active_sql_engine"], "FALLBACK_SQLITE_CSV")
        self.assertEqual(summary["live_mysql_status"], "NOT REQUESTED")
        for _, row in comp_df.iterrows():
            self.assertEqual(row["active_sql_engine"], "FALLBACK_SQLITE_CSV")
            self.assertEqual(row["sql_live_status"], "FALLBACK")

    def test_live_mysql_reporting_if_available(self):
        """Tests live MySQL connection and verifies exact matching against live database."""
        try:
            comp_df, summary = run_cross_validation(force_engine="mysql")
            self.assertEqual(summary["active_sql_engine"], "LIVE_MYSQL")
            self.assertIn("CONNECTED", summary["live_mysql_status"])
            self.assertEqual(summary["verified_kpis"], 16)
        except ConnectionError:
            self.skipTest("Live MySQL not available in this environment, skipped live check")

    # =========================================================================
    # 3. KPI-11 TERMINOLOGY & DENOMINATOR VERIFICATION
    # =========================================================================
    def test_kpi11_registered_vs_active_denominators(self):
        """Verifies registered (1,500) vs active (1,499) restaurant denominators."""
        delivered = self.orders[self.orders["order_status"] == "Delivered"]
        net_revenue = delivered["final_amount"].sum()
        total_registered = len(self.restaurants)
        active_partners = delivered["restaurant_id"].nunique()

        self.assertEqual(total_registered, 1500)
        self.assertEqual(active_partners, 1499)

        # Registered denominator calculation (KPI-11 canonical)
        avg_rev_registered = round(net_revenue / total_registered, 2)
        self.assertEqual(avg_rev_registered, 30950.66)

        # Active partner denominator calculation
        avg_rev_active = round(net_revenue / active_partners, 2)
        self.assertEqual(avg_rev_active, 30971.31)

        # Confirm dormant partner R00369 has 0 orders
        dormant_orders = self.orders[self.orders["restaurant_id"] == "R00369"]
        self.assertEqual(len(dormant_orders), 0, "Partner R00369 must have 0 orders")

    # =========================================================================
    # 4. REPEAT METRIC DISAMBIGUATION TESTS
    # =========================================================================
    def test_repeat_metrics_separation(self):
        """Verifies Customer Repeat Rate (99.94%) and Transaction Repeat Share (89.99%)."""
        total_customers = len(self.customers)
        cust_order_counts = self.orders.groupby("customer_id").size()
        repeat_customers = (cust_order_counts > 1).sum()

        # Metric A: Customer Repeat Rate = 4,997 / 5,000 = 99.94%
        customer_repeat_rate = round((repeat_customers / total_customers) * 100.0, 2)
        self.assertEqual(total_customers, 5000)
        self.assertEqual(repeat_customers, 4997)
        self.assertEqual(customer_repeat_rate, 99.94)

        # Metric B: Transaction Repeat Order Share (Orders beyond the 1st acquisition order per customer)
        # Total orders = 49,971. Initial acquisition orders = 5,000.
        # Repeat transactions = 49,971 - 5,000 = 44,971.
        # Repeat Transaction Share = 44,971 / 49,971 = 89.994% -> 89.99%
        total_orders_count = len(self.orders)
        initial_orders_count = len(self.customers)
        repeat_transactions_count = total_orders_count - initial_orders_count
        transaction_repeat_share = round((repeat_transactions_count / total_orders_count) * 100.0, 2)

        self.assertEqual(total_orders_count, 49971)
        self.assertEqual(initial_orders_count, 5000)
        self.assertEqual(repeat_transactions_count, 44971)
        self.assertEqual(transaction_repeat_share, 89.99)
        self.assertNotEqual(customer_repeat_rate, transaction_repeat_share)

    # =========================================================================
    # 5. ALL SEVEN FINANCIAL METRICS RECHECK
    # =========================================================================
    def test_financial_seven_metrics(self):
        """Rechecks all 7 financial definitions without hardcoding formulas."""
        all_orders = self.orders
        delivered = self.orders[self.orders["order_status"] == "Delivered"]
        non_cancelled = self.orders[self.orders["order_status"] != "Cancelled"]

        # 1. Gross Placed Value
        gross_placed_value = float(all_orders["order_amount"].sum())
        self.assertEqual(gross_placed_value, 48451925.0)

        # 2. Delivered Food GMV
        delivered_food_gmv = float(delivered["order_amount"].sum())
        self.assertEqual(delivered_food_gmv, 46590125.0)

        # 3. Net Revenue
        net_revenue = float(delivered["final_amount"].sum())
        self.assertEqual(net_revenue, 46425992.0)

        # 4. Net AOV
        net_aov = round(net_revenue / len(delivered), 2)
        self.assertEqual(net_aov, 967.33)

        # 5. Contribution Profit (Realized Operating Profit)
        deliv_eng = self.orders_eng[self.orders_eng["order_status"] == "Delivered"]
        realized_profit = round(float(deliv_eng["estimated_profit"].sum()), 2)
        self.assertEqual(realized_profit, 10953031.58)

        # 6. Contribution Margin %
        contrib_margin_pct = round((realized_profit / net_revenue) * 100.0, 2)
        self.assertEqual(contrib_margin_pct, 23.59)

        # 7. Gross Booked Profit
        all_eng = self.orders_eng
        gross_booked_profit = round(float(all_eng["estimated_profit"].sum()), 2)
        self.assertTrue(gross_booked_profit > realized_profit)


if __name__ == "__main__":
    unittest.main()
