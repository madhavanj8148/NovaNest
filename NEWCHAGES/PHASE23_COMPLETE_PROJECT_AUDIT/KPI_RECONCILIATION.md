# NovaNest: KPI Reconciliation & Consistency Audit

**Audit Phase**: Phase 23 — Comprehensive Evidence-Based Project Audit  
**Auditor**: Senior Financial Analyst, Data Quality Engineer  
**Audit Scope**: Cross-Layer KPI Reconciliation (SQL vs. Python `kpi_engine` vs. FastAPI Endpoints vs. React/Streamlit Dashboards vs. Documentation)  
**Reference Engine**: `python/analytics/kpi_engine.py`  
**Date**: November 2026  

---

## 1. Executive Summary: The Cross-Layer Ground Truth

To achieve absolute decision integrity, NovaNest defines **16 Certified Core Business KPIs** implemented in `python/analytics/kpi_engine.py` and validated via `python/analytics/validate_kpis.py`. 

This audit compares the exact mathematical outputs of `kpi_engine.py` against:
1. Raw SQL calculations over `datasets/cleaned/` (304,405 records)
2. Backend REST endpoints in `api/main.py`
3. Frontend views in `frontend/src/views/`
4. Streamlit pages in `streamlit_app/pages/`
5. Published figures in historical documentation and research paper drafts

---

## 2. Canonical 16-KPI Ground Truth Matrix

The following table documents the empirical ground truth computed by executing `compute_all_kpis()` against the canonical datasets:

| KPI ID | KPI Formal Name | Canonical Value | Unit | Direct SQL Calculation Logic | Status Tier in Code | Reconciliation Finding / Discrepancy Note |
| :--- | :--- | :---:| :---:| :--- | :---: | :--- |
| **KPI-01** | Gross Merchandise Value (GMV) | **46,590,125.00** | INR | `SUM(order_amount) WHERE order_status != 'Cancelled'` | **Verified** | **100% Consistent across all layers.** Excludes cancelled orders. |
| **KPI-02** | Net Revenue (Platform Inflow) | **46,425,992.00** | INR | `SUM(final_amount) WHERE order_status = 'Delivered'` | **Verified** | **100% Consistent.** Reflects post-discount consumer settlements. |
| **KPI-03** | Average Order Value (Net AOV) | **967.33** | INR | `KPI-02 / Delivered Orders` (46,425,992 / 47,994) | **Verified** | **100% Consistent.** Gross AOV is ₹970.75 (GMV / Delivered). |
| **KPI-04** | Platform Take Rate | **22.48%** | % | Realized Commission / Delivered GMV | **Divergence** | `kpi_engine.py` computes **22.48%**. Some historical docs cited 19.82%. |
| **KPI-05** | Total Orders Placed | **49,971** | Count | `COUNT(*) FROM orders` | **Verified** | **100% Consistent.** Matches CSV line count exactly. |
| **KPI-06** | Completed Orders | **47,994** | Count | `COUNT(*) WHERE order_status = 'Delivered'` | **Verified** | **100% Consistent.** 96.04% fulfillment rate. Historical 34,980 reconciled. |
| **KPI-07** | Cancellation Rate | **3.96%** | % | `1,977 Cancelled / 49,971 Total * 100` | **Verified** | **100% Consistent.** Exact value is 3.9563%. |
| **KPI-08** | Delivery SLA Breach Rate | **32.26%** | % | `COUNT(delay > threshold) / Delivered * 100` | **Divergence** | Canonical `kpi_engine` calculates **32.26%**; some drafts cited 14.28%. |
| **KPI-09** | Average Delivery Time | **37.38** | Mins | `AVG(delivery_duration) FROM deliveries` | **Divergence** | Canonical data is **37.38 mins**; `API_DOCUMENTATION.md` stated 34.20 mins. |
| **KPI-10** | Orders per Active Rider | **12.49** | Orders | Delivered Orders / Distinct Active Riders | **Verified** | 47,994 / 3,842 active couriers = 12.492 orders. |
| **KPI-11** | Restaurant Gross Throughput | **30,950.66** | INR | `Delivered GMV / 1,500 Restaurants` | **Verified** | Average historical gross revenue per merchant outlet. |
| **KPI-12** | Contribution Margin % | **23.59%** | % | Estimated Contribution Profit / Net Revenue | **Verified** | Represents operating leverage on platform inflows. |
| **KPI-13** | Platform Contribution Profit | **10,953,031.58**| INR | Commissions + Fees - Subsidies - Rider Pay | **Terminology** | Named "Operating Profit" in code, but formally **Contribution Profit**. |
| **KPI-14** | Customer Repeat-Purchase Rate | **99.94%** | % | `Customers with orders >= 2 / 5,000` | **Divergence** | Lifetime repeat is **99.94%** (4,997/5k); 30-day cohort repeat is 68.20%. |
| **KPI-15** | Cohort Retention (Month 1 Avg)| **53.36%** | % | Month-1 Active Retained Customers / Cohort | **Verified** | Calculated across monthly customer registration cohorts. |
| **KPI-16** | Cumulative ARPU (Spend/Cust) | **9,285.20** | INR | `Net Revenue / 5,000 Total Customers` | **Verified** | ₹46,425,992.00 / 5,000 = ₹9,285.1984. |

---

## 3. Detailed Analysis of Discrepancies & Divergences

### 3.1 Discrepancy 1: Average Delivery Time (37.38 mins vs. 34.20 mins)
- **Direct SQL Calculation**:
  ```python
  deliveries['delivery_duration'].mean() # 37.3837 mins
  delivered_merged['delivery_duration'].mean() # 37.3948 mins
  ```
- **Documentation Claim**: `API_DOCUMENTATION.md` and some executive summaries cite **34.20 mins**.
- **Root Cause**: An early optimization notebook applied a distance-restricted subset filter (`distance_km <= 5.0`) which lowered average duration to 34.20 minutes. Across the full 49,971 deliveries (average distance 6.46 km), the canonical average duration is **37.38 minutes**.
- **Recommendation**: Align all API docs and summary cards to **37.38 minutes**.

### 3.2 Discrepancy 2: Delivery SLA Breach Rate (32.26% vs. 14.28%)
- **Canonical Calculation (`kpi_engine.py`)**:
  - `orders_engineered['is_sla_breach'] == True` yields **32.26%** of delivered orders when defining breach as actual delivery duration exceeding estimated prep + transit time by $> 10$ minutes.
- **Historical Claim**: Some draft tables cited **14.28%** based on an arbitrary static 45-minute threshold.
- **Root Cause**: Static 45-minute cutoff flags only 14.28%, while dynamic SLA formula (exceeding predicted window) flags 32.26%.
- **Recommendation**: Document the threshold sensitivity explicitly: dynamic breach rate is 32.26%, whereas severe delay (>45 mins) is 14.28%.

### 3.3 Discrepancy 3: Customer Repeat Purchase Rate (99.94% vs. 68.20%)
- **Direct SQL Calculation**:
  - In `orders.csv`, exactly 4,997 of the 5,000 customers have $\ge 2$ orders over the complete dataset history. Only 3 customers placed exactly 1 order. Hence, lifetime repeat rate is **99.94%**.
- **Historical Claim**: Multiple reports cited **68.20%**.
- **Root Cause**: 68.20% represents the **30-day cohort repeat rate** (customers who re-ordered within 30 days of initial signup), whereas 99.94% is the **lifetime unwindowed repeat rate**.
- **Recommendation**: Re-label KPI-14 in documentation as "Lifetime Repeat Rate: 99.94% (30-Day Cohort Repeat: 68.20%)" to eliminate confusion.

### 3.4 Discrepancy 4: Platform Take Rate (22.48% vs. 19.82%)
- `kpi_engine.py` computes Take Rate as:
  $$\text{Take Rate} = \frac{\text{Realized Merchant Commissions}}{\text{Delivered GMV}} \times 100 = 22.48\%$$
- An alternative calculation deducted promotional subsidies from commissions, resulting in a net take rate of 19.82%.
- **Recommendation**: Standardize terminology: **Gross Take Rate = 22.48%**, **Net Take Rate (Post-Subsidy) = 19.82%**.

### 3.5 Discrepancy 5: Profit KPI Terminology (KPI-13: ₹10,953,031.58)
- In `python/analytics/kpi_engine.py` line 124, the metric is labeled `Total Estimated Operating Profit`.
- However, standard financial accounting dictates that Operating Profit (EBIT) must deduct administrative overhead, corporate payroll, software hosting, and depreciation/amortization.
- The formula implemented in NovaNest is:
  $$\text{Contribution Profit} = \text{Commission Revenue} + \text{Delivery Fees} - \text{Promotions/Discounts} - \text{Courier Fulfillment Payouts}$$
- **Recommendation**: Never label this figure as "Net Operating Profit." Retain the audited title: **"Estimated Platform Contribution Profit"**.

---

## 4. UI Layer Parity & Verification Status

| Surface / Interface | File Path | GMV Match | Revenue Match | Delivered Match | Cancellation Match | Parity Status |
| :--- | :--- | :---:| :---:| :---:| :---:| :---: |
| **FastAPI REST API** | `api/main.py` (`/api/overview`) | ₹46.59M | ₹46.43M | 47,994 | 3.96% | **100% PARITY** |
| **React 18 Dashboard** | `frontend/src/views/ExecutiveOverviewView.tsx` | ₹46.59M | ₹46.43M | 47,994 | 3.96% | **100% PARITY** |
| **Streamlit App** | `streamlit_app/pages/01_Executive_Overview.py` | ₹46.59M | ₹46.43M | 47,994 | 3.96% | **100% PARITY** |
| **Power BI Workspace** | `powerbi/NovaNest_themed.pbix` (DAX measures) | ₹46.59M | ₹46.43M | 47,994 | 3.96% | **100% PARITY** |

All user interfaces query the central backend or evaluate identical SQL aggregate expressions, ensuring complete operational consistency.
