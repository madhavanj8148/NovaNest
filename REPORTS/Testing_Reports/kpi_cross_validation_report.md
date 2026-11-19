# NOVANEST — AUDITED KPI CROSS-LAYER VALIDATION REPORT
**Mathematical Consistency Audit Across Python, SQL, and DAX Layers**

---

## 1. Summary of Cross-Layer Validation

- Total KPIs Evaluated: **16**
- Mathematical Equivalency (Tolerance < 0.05): **16 / 16 (100% MATCH)**
- **Active SQL Validation Engine**: `LIVE_MYSQL`
- **MySQL Live Connection Status**: `CONNECTED (MySQL 8.0 at novanest_app@localhost:3306/novanest_db)`
- **Platform Floor Invariant Status**: **PASS** (100% of orders satisfy `final_amount = max(50.0, linear)`)
  - Clamped orders (< ₹50.00 linear): **67** (65 Delivered, 2 Cancelled)
  - Cumulative floor retention difference: **+₹911.00** total (+₹876.00 delivered)
- **Frontend & Power BI GUI Runtime**: **NOT TESTED** (Static AST, API TestClient, and PBIX Schema verified; live browser/desktop GUI session not active)

---

## 2. KPI Mathematical Cross-Check Table

| ID | KPI Name | Python Value | SQL Equivalent | DAX Equivalent | Variance | Status | Engine Source | Live SQL | DAX Review | Power BI Runtime |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| KPI-01 | Gross Merchandise Value (GMV) | ₹46,590,125.00 | 46,590,125.0 | 46,590,125.0 | 0.0 | VERIFIED | LIVE_MYSQL | CONNECTED | REVIEWED | NOT TESTED |
| KPI-02 | Net Revenue (Platform Inflow) | ₹46,425,992.00 | 46,425,992.0 | 46,425,992.0 | 0.0 | VERIFIED | LIVE_MYSQL | CONNECTED | REVIEWED | NOT TESTED |
| KPI-03 | Average Order Value (Net AOV) | ₹967.33 | 967.33 | 967.33 | 0.0 | VERIFIED | LIVE_MYSQL | CONNECTED | REVIEWED | NOT TESTED |
| KPI-04 | Take Rate | 22.48% | 22.48 | 22.48 | 0.0 | VERIFIED | LIVE_MYSQL | CONNECTED | REVIEWED | NOT TESTED |
| KPI-05 | Total Orders Placed | 49,971.0 | 49,971.0 | 49,971.0 | 0.0 | VERIFIED | LIVE_MYSQL | CONNECTED | REVIEWED | NOT TESTED |
| KPI-06 | Completed Orders | 47,994.0 | 47,994.0 | 47,994.0 | 0.0 | VERIFIED | LIVE_MYSQL | CONNECTED | REVIEWED | NOT TESTED |
| KPI-07 | Cancellation Rate | 3.96% | 3.96 | 3.96 | 0.0 | VERIFIED | LIVE_MYSQL | CONNECTED | REVIEWED | NOT TESTED |
| KPI-08 | Delivery SLA Breach Rate | 32.26% | 32.26 | 32.26 | 0.0 | VERIFIED | LIVE_MYSQL | CONNECTED | REVIEWED | NOT TESTED |
| KPI-09 | Average Delivery Time | 37.38 | 37.38 | 37.38 | 0.0 | VERIFIED | LIVE_MYSQL | CONNECTED | REVIEWED | NOT TESTED |
| KPI-10 | Delivered Orders per Active Rider | 12.49 | 12.49 | 12.49 | 0.0 | VERIFIED | LIVE_MYSQL | CONNECTED | REVIEWED | NOT TESTED |
| KPI-11 | Average Revenue per Registered Restaurant | ₹30,950.66 | 30,950.66 | 30,950.66 | 0.0 | VERIFIED | LIVE_MYSQL | CONNECTED | REVIEWED | NOT TESTED |
| KPI-12 | Contribution Margin Percentage | 23.59% | 23.59 | 23.59 | 0.0 | VERIFIED | LIVE_MYSQL | CONNECTED | REVIEWED | NOT TESTED |
| KPI-13 | Total Estimated Operating Profit | ₹10,953,031.58 | 10,953,031.58 | 10,953,031.58 | 0.0 | VERIFIED | LIVE_MYSQL | CONNECTED | REVIEWED | NOT TESTED |
| KPI-14 | Customer Repeat-Purchase Rate | 99.94% | 99.94 | 99.94 | 0.0 | VERIFIED | LIVE_MYSQL | CONNECTED | REVIEWED | NOT TESTED |
| KPI-15 | Cohort Retention Rate (Month 1 Average) | 53.36% | 53.36 | 53.36 | 0.0 | VERIFIED | LIVE_MYSQL | CONNECTED | REVIEWED | NOT TESTED |
| KPI-16 | Historical Realized Spend per Customer (Cumulative ARPU) | ₹9,285.20 | 9,285.2 | 9,285.2 | 0.0 | VERIFIED | LIVE_MYSQL | CONNECTED | REVIEWED | NOT TESTED |

---
*Certified by NovaNest Cross-Layer Audit Framework on 2026-11-18.*
