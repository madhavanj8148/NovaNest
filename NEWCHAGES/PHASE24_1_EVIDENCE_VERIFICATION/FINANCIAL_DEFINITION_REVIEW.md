# NovaNest Financial Definition & Semantic Review Report
## Mathematical Validation, Cross-Layer Mapping & KPI-11 Terminology Evaluation
**Document Version:** 1.0.0  
**Phase:** Phase 24.1 — Independent Evidence Verification  
**Author:** Independent Senior Data Engineering Auditor  
**Status:** Complete Independent Audit  

---

## 1. Executive Summary

Financial metrics in multi-tier analytics systems are vulnerable to subtle semantic shifts between layers: what SQL calculates as a sum of filtered ledger entries can be renamed in an API payload, truncated in a UI component, or altered by a Power BI filter context.

This report independently evaluates the **seven core financial metrics** of NovaNest across SQL, Python, FastAPI, React, Streamlit, and Power BI. Furthermore, it conducts an in-depth operational and mathematical review of **KPI-11**, evaluating whether the metric should be labelled **"Restaurant Throughput"** or **"Average Revenue per Registered Restaurant."**

---

## 2. Mathematical Definitions & Source SQL for the 7 Financial Metrics

```
+--------------------------------------------------------------------------------------------------------------------+
| Financial Metric          | Mathematical Definition                                          | Reconciled Amount   |
+--------------------------------------------------------------------------------------------------------------------+
| 1. Gross Placed Value     | SUM(order_amount) across ALL orders                              | ₹48,451,925.00      |
| 2. Delivered Food GMV     | SUM(order_amount) WHERE order_status = 'Delivered'               | ₹46,590,125.00      |
| 3. Net Revenue (Inflow)   | SUM(final_amount) WHERE order_status = 'Delivered'              | ₹46,425,992.00      |
| 4. Net Average Order Value| Net Revenue / Delivered Orders (₹46,425,992 / 47,994)             | ₹967.33             |
| 5. Contribution Profit    | SUM(commission + delivery_fee - 30.0) on Delivered Orders       | ₹10,953,031.58      |
| 6. Contribution Margin %  | (Realized Contribution Profit / Net Revenue) * 100               | 23.59%              |
| 7. Gross Booked Profit    | SUM(commission + delivery_fee - 30.0) across ALL orders         | ₹11,393,907.16      |
+--------------------------------------------------------------------------------------------------------------------+
```

---

### 2.1 Metric 1: Gross Placed Value
- **Definition:** Total gross food catalog value of all order transactions initiated across the platform, including cancelled orders.
- **Mathematical Formula:**
  $$\text{Gross Placed Value} = \sum_{i=1}^{N=49,971} \text{order\_amount}_i$$
- **SQL Implementation:**
  ```sql
  SELECT SUM(order_amount) AS gross_placed_value FROM orders_table;
  ```
- **Audited Value:** **₹48,451,925.00**
- **Accounting Role:** Measures top-of-funnel customer cart demand before fulfillment failures or cancellations.

### 2.2 Metric 2: Delivered Food GMV (Canonical KPI-01)
- **Definition:** Total gross food catalog value of successfully fulfilled and delivered meals.
- **Mathematical Formula:**
  $$\text{GMV} = \sum_{i \in \mathcal{O}, \text{status}_i = \text{'Delivered'}} \text{order\_amount}_i$$
- **SQL Implementation:**
  ```sql
  SELECT SUM(order_amount) AS gmv FROM orders_table WHERE order_status = 'Delivered';
  -- In NovaNest's 2-status schema (Delivered/Cancelled), this is identically:
  SELECT SUM(order_amount) AS gmv FROM orders_table WHERE order_status != 'Cancelled';
  ```
- **Audited Value:** **₹46,590,125.00**
- **Accounting Role:** Represents the gross food volume on which merchant commissions are computed. Excludes cancelled orders ($N=1,977$, value ₹1,861,800.00).

### 2.3 Metric 3: Net Revenue / Platform Cash Inflow (Canonical KPI-02)
- **Definition:** Actual cash collected by the platform from customers on delivered orders.
- **Mathematical Formula:**
  $$\text{Net Revenue} = \sum_{i \in \mathcal{O}_{\text{deliv}}} \text{final\_amount}_i$$
  $$\text{where } \text{final\_amount}_i = \max(50.00, \text{order\_amount}_i + \text{delivery\_fee}_i - \text{discount\_amount}_i)$$
- **SQL Implementation:**
  ```sql
  SELECT SUM(final_amount) AS net_revenue FROM orders_table WHERE order_status = 'Delivered';
  ```
- **Audited Value:** **₹46,425,992.00**
- **Accounting Role:** Recognized cash inflow. (Delivered Food Amount ₹46,590,125 + Delivery Fees ₹1,919,412 - Discounts ₹2,083,545 = ₹46,425,992.00).

### 2.4 Metric 4: Net Average Order Value (Canonical KPI-03)
- **Definition:** Net cash collected per successfully completed order basket.
- **Mathematical Formula:**
  $$\text{Net AOV} = \frac{\text{Net Revenue}}{|\mathcal{O}_{\text{deliv}}|} = \frac{₹46,425,992.00}{47,994} = \mathbf{₹967.33}$$
- **Comparison with Gross AOV:**
  $$\text{Gross AOV} = \frac{\text{GMV}}{|\mathcal{O}_{\text{deliv}}|} = \frac{₹46,590,125.00}{47,994} = \mathbf{₹970.75}$$
- **Discrepancy Spread:** $\text{Gross AOV} - \text{Net AOV} = ₹3.42$ per order, representing net promotional dilution.

### 2.5 Metric 5: Platform Contribution Profit (Canonical KPI-13)
- **Definition:** Platform operational profit realized on delivered orders after merchant commission extraction, customer delivery fee collection, and rider fulfillment payout.
- **Mathematical Formula:**
  $$\text{Contribution Profit} = \sum_{i \in \mathcal{O}_{\text{deliv}}} (\text{commission\_revenue}_i + \text{delivery\_fee}_i - \text{rider\_compensation}_i)$$
  $$\text{where rider\_compensation}_i = ₹30.00 \text{ (Standard operational unit cost)}$$
- **SQL Implementation:**
  ```sql
  SELECT ROUND(SUM(estimated_profit), 2) AS contribution_profit 
  FROM vw_unit_economics 
  WHERE order_status = 'Delivered';
  ```
- **Audited Value:** **₹10,953,031.58**
- **Breakdown:**
  - Merchant Commission Revenue: ₹10,473,439.58
  - Delivery Fee Collections: ₹1,919,412.00
  - Rider Compensation Paid ($47,994 \times ₹30.00$): ₹1,439,820.00
  - Realized Operating Surplus: $₹10,473,439.58 + ₹1,919,412.00 - ₹1,439,820.00 = \mathbf{₹10,953,031.58}$.

### 2.6 Metric 6: Contribution Margin Percentage (Canonical KPI-12)
- **Definition:** Proportion of net customer inflow retained as platform operating surplus post-rider payouts.
- **Mathematical Formula:**
  $$\text{Contribution Margin \%} = \frac{\text{Contribution Profit}}{\text{Net Revenue}} \times 100 = \frac{₹10,953,031.58}{₹46,425,992.00} \times 100 = \mathbf{23.5925\%} \approx \mathbf{23.59\%}$$
- **SQL Implementation:**
  ```sql
  SELECT ROUND(100.0 * SUM(estimated_profit) / SUM(final_amount), 2) 
  FROM vw_unit_economics 
  WHERE order_status = 'Delivered';
  ```
- **Audited Value:** **23.59%**

### 2.7 Metric 7: Gross Booked Profit
- **Definition:** Theoretical operating profit computed across all initiated orders ($49,971$), assuming uncancelled status.
- **Mathematical Formula:**
  $$\text{Gross Booked Profit} = \sum_{i=1}^{49,971} \text{estimated\_profit}_i$$
- **SQL Implementation:**
  ```sql
  SELECT ROUND(SUM(estimated_profit), 2) FROM orders_engineered;
  ```
- **Audited Value:** **₹11,393,907.16** ($23.60\%$ on gross inflow of ₹48,281,651.00).
- **Audit Clarification:** Cancelled orders ($N=1,977$) account for ₹440,875.58 in unearned booked margin. Because cancelled orders are refunded and riders are not paid the ₹30 fee, only **₹10,953,031.58** is realized cash profit.

---

## 3. Cross-Layer Naming & Definition Alignment Matrix

```
+-------------------+--------------------+--------------------+--------------------+--------------------+--------------------+
| Metric            | SQL (MySQL/SQLite) | Python Engine      | FastAPI REST       | React 18 SPA       | Power BI DAX       |
+-------------------+--------------------+--------------------+--------------------+--------------------+--------------------+
| Delivered GMV     | gmv                | gmv                | total_gmv          | Gross Revenue(GMV) | Total GMV Delivered|
| Net Revenue       | net_revenue        | net_revenue        | net_platform_rev   | Net Revenue        | Net Revenue Deliv. |
| Net AOV           | net_aov            | net_aov            | avg_order_value    | Average Order Value| Average Order Value|
| Take Rate         | take_rate_pct      | take_rate          | take_rate_pct      | Platform Take Rate | Take Rate %        |
| Total Orders      | total_orders       | total_orders       | total_orders       | Total Orders       | Total Orders       |
| Delivered Orders  | completed_orders   | delivered_orders   | delivered_orders   | Fulfillment Orders | Delivered Orders   |
| Cancellation Rate | cancellation_rate  | cancel_rate        | cancellation_rate  | Cancellation Rate  | Cancellation Rate %|
| Contrib. Profit   | estimated_profit   | realized_profit    | realized_profit    | Operating Profit   | Contribution Margin|
| Contrib. Margin % | contribution_margin| contribution_margin| contribution_margin| Contrib. Margin %  | Contribution Margin%
+-------------------+--------------------+--------------------+--------------------+--------------------+--------------------+
```

### Audit Findings on Cross-Layer Naming:
1. **Gross Revenue vs. GMV:** React 18 labels `KPI-01` as *"Gross Revenue (GMV)"*, whereas in strict financial accounting, catalog food volume is Gross Merchandise Value (GMV), not platform revenue. The subtext correctly clarifies *"Non-cancelled gross transaction value"*.
2. **Net Revenue vs. Platform Inflow:** FastAPI labels `KPI-02` as `net_platform_revenue`, which is mathematically identical to `SUM(final_amount)`.
3. **Contribution Margin vs. Operating Profit:** Power BI DAX names `[Contribution Margin]` as the scalar amount (₹10.95M) and `[Contribution Margin %]` as the percentage ($23.59\%$). Python and SQL label the scalar amount as `estimated_profit` or `realized_profit`. Definitions are 100% numerically aligned.

---

## 4. In-Depth Review of KPI-11: "Throughput" vs. "Average Revenue"

### 4.1 Numerical Calculation Audit
$$\text{KPI-11 Value} = \frac{\text{Net Revenue}}{\text{Registered Restaurants}} = \frac{₹46,425,992.00}{1,500} = \mathbf{₹30,950.66}$$

### 4.2 Relational Entity Discovery: Active vs. Registered Merchants
A deep relational query between `restaurants.csv` and `orders.csv` uncovered an important operational nuance:
- Total registered restaurants: **1,500**
- Restaurants with $\ge 1$ placed order: **1,499**
- Restaurants with $\ge 1$ delivered order: **1,499**
- Exactly **one registered restaurant** received zero orders across the entire 365-day dataset:
  - **Restaurant ID:** `R00369`
  - **Restaurant Name:** `Mandal Ltd`
  - **City:** Bangalore
  - **Cuisine:** Indian

**Calculation Comparison:**
- Denominator = $1,500$ (All Registered Partners): $\frac{₹46,425,992.00}{1,500} = \mathbf{₹30,950.66}$
- Denominator = $1,499$ (Active Transacting Partners): $\frac{₹46,425,992.00}{1,499} = \mathbf{₹30,971.31}$
- Denominator = $1,500$ on Food GMV: $\frac{₹46,590,125.00}{1,500} = \mathbf{₹31,060.08}$

### 4.3 Semantic & Operations Research Evaluation of "Throughput"
In operations research, industrial engineering, and queueing theory (Little's Law, Goldratt's Theory of Constraints):
- **Throughput ($TH$):** Is strictly defined as the rate at which a system generates units or processes flow per unit time:
  $$TH = \frac{\text{Work Completed}}{\Delta t} \quad \left[\frac{\text{Orders}}{\text{Day}}, \frac{\text{Deliveries}}{\text{Hour}}\right]$$
- Dividing a cumulative annual revenue aggregate by a static count of registered accounts produces an **Entity Monetization Ratio / Average Account Yield**:
  $$\text{Yield} = \frac{\text{Total Cash Inflow}}{\text{Total Accounts}} \quad \left[\frac{\text{INR}}{\text{Merchant}}\right]$$

Conflating an annualized average account monetization figure with dynamic operational "throughput" creates analytical confusion. A platform could experience flat or declining operational throughput (fewer meals per kitchen per hour) while increasing entity yield due to basket price inflation.

### 4.4 Mathematical & Terminological Recommendation

```
+--------------------------------------------------------------------------------------------------------------------+
| Dimension                     | "Restaurant Throughput"           | "Average Revenue per Registered Restaurant"    |
+--------------------------------------------------------------------------------------------------------------------+
| Technical Accuracy            | Inaccurate (Conflates rate & sum) | 100% Mathematically & Accounting Accurate      |
| Industry Benchmark Alignment  | Confuses factory flow with yield  | Aligns with DoorDash / Zomato merchant yield   |
| Denominator Representation    | Ignores inactive partner R00369   | Explicitly states "Registered" basis (1,500)   |
| Operational Utility           | Does not measure kitchen velocity | Clearly measures partner monetization scale    |
+--------------------------------------------------------------------------------------------------------------------+
```

### Recommendation:
1. **Primary Label Change:** Deprecate *"Restaurant Throughput"* in favor of **"Average Revenue per Registered Restaurant"** (or **"Average Partner Net Inflow"**).
2. **If True Throughput is Required:** Add an operational metric: **"Average Order Volume per Restaurant"** ($32.0$ completed orders per merchant over the year, or $\approx 0.088$ orders/day).

---

## 5. Summary Conclusion
The underlying mathematical values of the 7 financial metrics are 100% reconciled across SQL, Python, FastAPI, and DAX. However, documentation and UI labels should adopt standardized accounting nomenclature, specifically resolving the "Restaurant Throughput" misnomer and distinguishing GMV from platform net revenue.
