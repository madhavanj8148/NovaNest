# NovaNest Data Quality & Forensic Integrity Evidence Report
## Recalculated Dataset-Wise Metrics, Invariant Audit & Edge-Case Disclosures
**Document Version:** 1.0.0  
**Phase:** Phase 24.1 — Independent Evidence Verification  
**Author:** Independent Senior Data Engineering Auditor  
**Status:** Complete Independent Recalculation  

---

## 1. Executive Summary & Audit Mandate

The user instructions state:
> *"Recalculate: Null counts, Duplicate primary keys, Duplicate business records, Foreign-key orphan counts, Invalid statuses, Invalid dates, Financial inconsistencies. Provide dataset-wise results, not just aggregate claims."*

This document presents the complete dataset-wise empirical re-computation across all **10 relational tables** and **304,405 records** in `datasets/cleaned/`. 

Our independent recalculation substantiates the high structural health of the database while exposing a critical nuance missed in the Phase 24 report: **67 orders deviate from the linear financial equation due to a ₹50.00 minimum payment floor**.

---

## 2. Table-by-Table Data Profiling & Recalculated Metrics

Every metric in the table below was computed via fresh, independent programmatic execution directly on raw files:

```
+------------------+---------+------+------------+--------+--------------+------------------+---------------------+
| Table Name       | Rows    | Cols | Null Cells | Null % | Dup. PK Rows | Dup. Non-PK Rows | Primary Key Field   |
+------------------+---------+------+------------+--------+--------------+------------------+---------------------+
| customers        | 5,000   | 10   | 0          | 0.00%  | 0            | 0                | customer_id         |
| restaurants      | 1,500   | 9    | 0          | 0.00%  | 0            | 0                | restaurant_id       |
| riders           | 4,000   | 7    | 0          | 0.00%  | 0            | 0                | rider_id            |
| orders           | 49,971  | 12   | 0          | 0.00%  | 0            | 0                | order_id            |
| deliveries       | 49,971  | 5    | 0          | 0.00%  | 0            | 0                | delivery_id         |
| payments         | 49,971  | 4    | 0          | 0.00%  | 0            | 0                | payment_id          |
| ratings_reviews  | 28,792  | 5    | 0          | 0.00%  | 0            | 0                | review_id           |
| menu_items       | 15,000  | 6    | 0          | 0.00%  | 0            | 0                | item_id             |
| promotions       | 200     | 5    | 0          | 0.00%  | 0            | 0                | promotion_id        |
| app_events       | 100,000 | 3    | 0          | 0.00%  | 0            | 71,049 *         | event_id            |
+------------------+---------+------+------------+--------+--------------+------------------+---------------------+
| TOTAL ECOSYSTEM  | 304,405 | 66   | 0          | 0.00%  | 0            | 71,049           | 10 Unique PKs       |
+------------------+---------+------+------------+--------+--------------+------------------+---------------------+
```
*\* Note on `app_events`: The 71,049 duplicate non-PK tuples represent repeated clickstream actions by the same customer (e.g. repeated "Menu View" or "App Open" sessions). Because the cleaned schema contains only `(event_id, customer_id, event_type)` without event timestamps, repeated actions share identical non-PK values.*

---

## 3. Referential Integrity & Foreign Key Orphan Recalculation

All nine relational foreign key dependencies were audited using exact set exclusion tests:

```sql
-- Evaluated query pattern
SELECT COUNT(*) FROM child_table WHERE fk NOT IN (SELECT pk FROM parent_table);
```

### Dataset-Wise Foreign Key Audit Results:
1. **`orders.customer_id` $\rightarrow$ `customers.customer_id`:**
   - Keys tested: 49,971 | Orphan rows: **0** ($100.00\%$ referential integrity)
2. **`orders.restaurant_id` $\rightarrow$ `restaurants.restaurant_id`:**
   - Keys tested: 49,971 | Orphan rows: **0** ($100.00\%$ referential integrity)
3. **`orders.item_id` $\rightarrow$ `menu_items.item_id`:**
   - Keys tested: 49,971 | Orphan rows: **0** ($100.00\%$ referential integrity)
4. **`deliveries.order_id` $\rightarrow$ `orders.order_id`:**
   - Keys tested: 49,971 | Orphan rows: **0** ($100.00\%$ referential integrity)
5. **`deliveries.rider_id` $\rightarrow$ `riders.rider_id`:**
   - Keys tested: 49,971 | Orphan rows: **0** ($100.00\%$ referential integrity)
6. **`payments.order_id` $\rightarrow$ `orders.order_id`:**
   - Keys tested: 49,971 | Orphan rows: **0** ($100.00\%$ referential integrity)
7. **`ratings_reviews.order_id` $\rightarrow$ `orders.order_id`:**
   - Keys tested: 28,792 | Orphan rows: **0** ($100.00\%$ referential integrity)
8. **`menu_items.restaurant_id` $\rightarrow$ `restaurants.restaurant_id`:**
   - Keys tested: 15,000 | Orphan rows: **0** ($100.00\%$ referential integrity)
9. **`app_events.customer_id` $\rightarrow$ `customers.customer_id`:**
   - Keys tested: 100,000 | Orphan rows: **0** ($100.00\%$ referential integrity)

**Referential Integrity Status:** **Zero orphan records across all 304,405 rows.**

---

## 4. Status Enumeration & Date Field Quality Audit

### 4.1 Status Field Categorical Enumerations
```
+-------------------+--------------------+------------------------+------------------------------------------+
| Table Name        | Status Column      | Permitted Values       | Distribution & Invalid Count             |
+-------------------+--------------------+------------------------+------------------------------------------+
| orders            | order_status       | Delivered, Cancelled   | Delivered: 47,994, Cancelled: 1,977 (0)  |
| payments          | payment_method     | UPI, Card, COD, Wallet | UPI: 27,434, Card: 12,493, COD: 6,047,   |
|                   |                    |                        | Wallet: 3,997 (0 invalid)                |
| restaurants       | city               | 5 South Indian Cities  | Chennai: 454, Bangalore: 380, Hyd: 305,  |
|                   |                    |                        | Coimbatore: 216, Vijayawada: 145 (0)     |
| customers         | customer_segment   | 10 RFM Tiers           | 5,000 valid segments (0 invalid)         |
+-------------------+--------------------+------------------------+------------------------------------------+
```

### 4.2 Date & Timestamp Parsing Audit
Every temporal column was parsed using strict ISO conversion; invalid dates were coerced to `NaT`:
- **`orders.order_datetime`:**
  - Valid timestamps: 49,971 / 49,971 (Invalid `NaT`: **0**)
  - Min Date: `2025-06-17 15:45:00`
  - Max Date: `2026-06-17 15:35:20` (Span: exactly 365 calendar days)
- **`customers.signup_date`:**
  - Valid timestamps: 5,000 / 5,000 (Invalid `NaT`: **0**)
  - Min Date: `2024-06-16 00:00:00`
  - Max Date: `2026-06-16 00:00:00`
- **`promotions.start_date` & `end_date`:**
  - Valid timestamps: 200 / 200 (Invalid `NaT`: **0**)
  - Zero date inversions (`end_date >= start_date` holds for 100% of campaigns).

---

## 5. Financial Invariant Audit: Discovery of 67 Minimum-Floor Rows

### 5.1 The Linear Invariant Check
In Phase 24, `DATA_QUALITY_RESULTS.md` stated:
> *"For every order in orders.csv, the following invariant was evaluated: final_amount = order_amount + delivery_fee - discount_amount. Discrepancies / Imbalances: 0."*

Our independent audit tested this claim row-by-row:
```python
diff = df['final_amount'] - (df['order_amount'] + df['delivery_fee'] - df['discount_amount'])
mismatches = df[diff.abs() > 0.01]
```
- **Total Mismatched Rows Found:** **67 rows**
- **Match Rate:** $49,904 / 49,971 = \mathbf{99.866\%}$
- **Discrepancy Rate:** $67 / 49,971 = \mathbf{0.134\%}$

### 5.2 Inspection of Mismatched Rows
A sample of the 67 rows demonstrates an unmistakable, deterministic pattern:

```
+------------+--------------+--------------+-----------------+---------------+--------------+------------+
| Order ID   | Order Amount | Delivery Fee | Discount Amount | Linear Sum    | Actual Final | Delta (₹)  |
+------------+--------------+--------------+-----------------+---------------+--------------+------------+
| O0000721   | ₹80.00       | ₹27.00       | ₹61.00          | ₹46.00        | ₹50.00       | +₹4.00     |
| O0001115   | ₹85.00       | ₹27.00       | ₹97.00          | ₹15.00        | ₹50.00       | +₹35.00    |
| O0003816   | ₹87.00       | ₹21.00       | ₹81.00          | ₹27.00        | ₹50.00       | +₹23.00    |
| O0004405   | ₹84.00       | ₹26.00       | ₹67.00          | ₹43.00        | ₹50.00       | +₹7.00     |
| O0004603   | ₹93.00       | ₹31.00       | ₹82.00          | ₹42.00        | ₹50.00       | +₹8.00     |
| O0004674   | ₹80.00       | ₹24.00       | ₹69.00          | ₹35.00        | ₹50.00       | +₹15.00    |
| O0005247   | ₹86.00       | ₹26.00       | ₹99.00          | ₹13.00        | ₹50.00       | +₹37.00    |
| O0005437   | ₹103.00      | ₹20.00       | ₹87.00          | ₹36.00        | ₹50.00       | +₹14.00    |
| O0006256   | ₹97.00       | ₹22.00       | ₹70.00          | ₹49.00        | ₹50.00       | +₹1.00     |
| O0006490   | ₹81.00       | ₹44.00       | ₹82.00          | ₹43.00        | ₹50.00       | +₹7.00     |
+------------+--------------+--------------+-----------------+---------------+--------------+------------+
```

### 5.3 Root-Cause Analysis
- In all 67 orders, high promotional discounts resulted in a calculated payable amount below ₹50.00.
- Every single one of these 67 orders has **`final_amount = ₹50.00`** (Unique final amounts across all 67 rows: `[50]`).
- This reflects the platform's **Minimum Order Checkout Floor**:
  $$\text{final\_amount} = \max(50.00, \text{order\_amount} + \text{delivery\_fee} - \text{discount\_amount})$$

### 5.4 Auditor Impact Assessment
- The financial impact of the clamp across the 67 orders is **₹861.00** in retained cash inflow.
- Because `Net Revenue` is canonically computed as `SUM(final_amount)` rather than the linear component sum, the reported figure of **₹46,425,992.00** remains 100% accurate.
- However, the Phase 24 audit's assertion that the linear invariant holds across 100% of orders with 0 discrepancies was factually incorrect.

---

## 6. Data Quality Auditor Scorecard

```
+---------------------------------------------------------------------------------------------------------+
| Quality Check                  | Expected Standard | Audited Result   | Compliance Status               |
+---------------------------------------------------------------------------------------------------------+
| Missing / Null Values          | 0.00% across all  | 0 Nulls in 304k  | 100% PASS ✅                     |
| Primary Key Uniqueness         | 100.00%           | 0 Duplicate PKs  | 100% PASS ✅                     |
| Business Record Uniqueness     | 100.00%           | 0 Dupes (ex-app) | 100% PASS ✅                     |
| Foreign Key Referential Health | 0 Broken Joins    | 0 Broken Joins   | 100% PASS ✅                     |
| Date Parsing & Temporal Health | 0 Invalid NaT     | 0 Invalid NaT    | 100% PASS ✅                     |
| Categorical Status Validity    | 100% Valid Enums  | 0 Malformed      | 100% PASS ✅                     |
| Financial Invariant Integrity  | 100.00%           | 99.866% (67 diff)| PASS WITH EXPLANATION ⚠️         |
+---------------------------------------------------------------------------------------------------------+
```

---
**Auditor Signature:** Independent Senior Data Engineering Auditor  
**Date of Audit:** 2026-11-18  
