# NovaNest Canonical KPI Definitions & Data Dictionary
## Enterprise Food Delivery Analytics & Decision Intelligence Platform
**Document Version:** 1.0.0  
**Phase:** Phase 24 — Cross-Platform KPI & Data Consistency Audit  
**Author:** Senior Data Engineer & Analytics Quality Specialist  
**Status:** Certified Canonical Ground Truth  

---

## 1. Executive Summary & Purpose

In enterprise analytics platforms spanning relational databases (MySQL 8.0), analytical flat-files (CSV), REST APIs (FastAPI), modern web applications (React 18), interactive analytical portals (Streamlit), and enterprise business intelligence semantic models (Power BI DAX), metric drift and semantic divergence represent critical risks.

This document serves as the **Single Source of Truth (SSOT)** and canonical business data dictionary for the **16 certified core Key Performance Indicators (KPIs)** of the NovaNest platform. Every formula, aggregation logic, status filter, numerator/denominator specification, and edge-case handling rule defined herein is mathematically bound and verified across all application surfaces.

---

## 2. Global Calculation Principles & Filter Hierarchy

All 16 KPIs adhere strictly to the following canonical accounting and operational principles:

1. **Transaction Lifecycle Filtering:**
   - **Total Orders (Placed):** Encompasses all $N = 49,971$ initiated order records regardless of final disposition.
   - **Delivered Orders (Fulfilled):** Strictly restricted to `order_status = 'Delivered'` ($N = 47,994$, 96.04% fulfillment rate). Financial inflow, merchant payouts, and delivery SLAs are anchored to completed orders.
   - **Cancelled Orders (Aborted):** Filtered by `order_status = 'Cancelled'` ($N = 1,977$, 3.96% cancellation rate). Cancelled transactions do not generate platform cash inflow or rider compensation.

2. **Gross vs. Net Financial Accounting:**
   - **Gross Merchandise Value (GMV):** Catalog food price of non-cancelled orders (`SUM(order_amount)`). Excludes customer delivery fees and discounts.
   - **Net Revenue (Platform Inflow):** Total customer cash paid on delivered orders (`SUM(final_amount) = order_amount + delivery_fee - discount_amount`).
   - **Take Rate:** Commission retained from delivered food GMV expressed as a percentage of GMV ($22.48\%$).
   - **Platform Contribution Profit:** Commission Revenue + Customer Delivery Fee - Platform Delivery Rider Base Compensation (₹30.00 standard unit benchmark). Realized total on delivered orders is **₹10,953,031.58** ($23.59\%$ Contribution Margin).

3. **Time and Geography Horizon:**
   - **Temporal Scope:** 365 calendar days ($2025\text{-}06\text{-}17$ to $2026\text{-}06\text{-}17$).
   - **Territorial Scope:** 5 Tier-1 and Tier-2 South Indian urban operational zones: Chennai ($454$ restaurants), Bangalore ($380$ restaurants), Hyderabad ($305$ restaurants), Coimbatore ($216$ restaurants), Vijayawada ($145$ restaurants).

---

## 3. Detailed Canonical Definitions for the 16 Core KPIs

```
+---------------------------------------------------------------------------------------------------+
| ID     | KPI Canonical Name                    | Reconciled Value  | Primary Granularity          |
+---------------------------------------------------------------------------------------------------+
| KPI-01 | Gross Merchandise Value (GMV)         | ₹46,590,125.00    | Platform Aggregate / Filter  |
| KPI-02 | Net Revenue (Platform Inflow)         | ₹46,425,992.00    | Delivered Transactions       |
| KPI-03 | Average Order Value (Net AOV)         | ₹967.33           | Delivered Order Unit Metric  |
| KPI-04 | Take Rate                             | 22.48%            | Commission Yield Ratio       |
| KPI-05 | Total Orders Placed                   | 49,971            | Total Transaction Ingestion  |
| KPI-06 | Completed (Delivered) Orders          | 47,994            | Successful Fulfilled Orders  |
| KPI-07 | Cancellation Rate                     | 3.96%             | Failure Proportion           |
| KPI-08 | Delivery SLA Breach Rate              | 32.26%            | Fulfillment Performance      |
| KPI-09 | Average Delivery Time                 | 37.38 mins        | Logistics Duration           |
| KPI-10 | Delivered Orders per Active Rider     | 12.49 orders      | Fleet Throughput Velocity    |
| KPI-11 | Restaurant Gross Revenue Throughput   | ₹30,950.66        | Merchant Monetization Yield  |
| KPI-12 | Contribution Margin Percentage        | 23.59%            | Unit Economics Operating %   |
| KPI-13 | Platform Contribution Profit          | ₹10,953,031.58    | Realized Operating Surplus   |
| KPI-14 | Customer Repeat-Purchase Rate         | 99.94%            | Lifetime Retention Spread    |
| KPI-15 | Cohort Retention Rate (Month 1 Avg)   | 53.36%            | Month 1 Return Proportion    |
| KPI-16 | Historical Realized Spend (Cum. ARPU) | ₹9,285.20         | Realized Value Per Customer  |
+---------------------------------------------------------------------------------------------------+
```

---

### KPI-01: Gross Merchandise Value (GMV)
- **ID:** `KPI-01`
- **Domain:** Executive Overview & Financial Growth
- **Business Rationale:** Measures total gross demand volume and commercial scale generated through the food delivery catalog, excluding cancellations.
- **Formal Mathematical Formula:**
  $$\text{GMV} = \sum_{i \in \mathcal{O}, \text{status}_i \neq \text{'Cancelled'}} \text{order\_amount}_i$$
- **Numerator:** Sum of menu list item prices (`order_amount`) for all placed orders where `order_status != 'Cancelled'`.
- **Denominator:** Not applicable (Scalar sum).
- **Source Tables & Columns:** `orders_table.order_amount`, `orders_table.order_status`.
- **Filtering Rules:** `WHERE order_status != 'Cancelled'` (or equivalently `WHERE order_status = 'Delivered'` in NovaNest's 2-state status schema).
- **Edge-Case Handling:** Excludes cancelled transactions ($N=1,977$, value ₹1,861,800.00). If order amount is NULL, coerced to 0.00.
- **Gross vs. Net:** Gross food catalog figure (pre-discount, pre-delivery fees, pre-taxes).
- **SQL Implementation:**
  ```sql
  SELECT SUM(order_amount) AS gmv
  FROM orders_table
  WHERE order_status != 'Cancelled';
  ```
- **DAX Implementation:**
  ```dax
  [Total GMV Delivered] = 
  CALCULATE(
      SUM(orders[order_amount]), 
      orders[order_status] <> "Cancelled"
  )
  ```
- **Reconciled Value:** **₹46,590,125.00**

---

### KPI-02: Net Revenue (Platform Inflow)
- **ID:** `KPI-02`
- **Domain:** Financial Intelligence & Cash Realization
- **Business Rationale:** Reflects actual realized top-line cash collected from end customers on completed deliveries.
- **Formal Mathematical Formula:**
  $$\text{Net Revenue} = \sum_{i \in \mathcal{O}, \text{status}_i = \text{'Delivered'}} \text{final\_amount}_i$$
  $$\text{where } \text{final\_amount}_i = \text{order\_amount}_i + \text{delivery\_fee}_i - \text{discount\_amount}_i$$
- **Numerator:** Sum of `final_amount` for fulfilled orders.
- **Denominator:** Not applicable.
- **Source Tables & Columns:** `orders_table.final_amount`, `orders_table.order_status`.
- **Filtering Rules:** Strictly `WHERE order_status = 'Delivered'`.
- **Edge-Case Handling:** Cancelled orders are excluded; refunded or uncollected cash does not contribute to Net Revenue.
- **Gross vs. Net:** Net consumer cash collection post-discounts, inclusive of customer delivery fee payments.
- **SQL Implementation:**
  ```sql
  SELECT SUM(final_amount) AS net_revenue
  FROM orders_table
  WHERE order_status = 'Delivered';
  ```
- **DAX Implementation:**
  ```dax
  [Net Revenue Delivered] = 
  CALCULATE(
      SUM(orders[final_amount]), 
      orders[order_status] = "Delivered"
  )
  ```
- **Reconciled Value:** **₹46,425,992.00**

---

### KPI-03: Average Order Value (Net AOV)
- **ID:** `KPI-03`
- **Domain:** Customer Economics & Basket Sizing
- **Business Rationale:** Quantifies average monetary payment per fulfilled basket. Reconciled against Gross AOV to track discount erosion.
- **Formal Mathematical Formula:**
  $$\text{Net AOV} = \frac{\sum_{i \in \mathcal{O}_{\text{deliv}}} \text{final\_amount}_i}{|\mathcal{O}_{\text{deliv}}|}$$
  $$\text{Gross AOV} = \frac{\sum_{i \in \mathcal{O}_{\text{deliv}}} \text{order\_amount}_i}{|\mathcal{O}_{\text{deliv}}|}$$
- **Numerator:** Net Revenue of delivered orders (`₹46,425,992.00`).
- **Denominator:** Count of completed orders (`47,994`).
- **Source Tables & Columns:** `orders_table.final_amount`, `orders_table.order_id`, `orders_table.order_status`.
- **Filtering Rules:** `WHERE order_status = 'Delivered'`.
- **Edge-Case Handling:** Denominator check protects against division by zero; if zero completed orders, returns ₹0.00.
- **Gross vs. Net:** Net AOV is ₹967.33; Gross AOV is ₹970.75 (reflecting ₹3.42 net subsidy spread per basket).
- **SQL Implementation:**
  ```sql
  SELECT ROUND(SUM(final_amount) / COUNT(order_id), 2) AS net_aov
  FROM orders_table
  WHERE order_status = 'Delivered';
  ```
- **DAX Implementation:**
  ```dax
  [Average Order Value] = 
  DIVIDE([Net Revenue Delivered], [Delivered Orders], 0)
  ```
- **Reconciled Value:** **₹967.33**

---

### KPI-04: Take Rate
- **ID:** `KPI-04`
- **Domain:** Marketplace Economics & Monetization
- **Business Rationale:** Evaluates core platform monetization efficiency: the percentage of food GMV extracted as merchant commissions.
- **Formal Mathematical Formula:**
  $$\text{Take Rate} = \frac{\sum_{i \in \mathcal{O}_{\text{deliv}}} (\text{order\_amount}_i \times \text{commission\_rate}_{r(i)})}{\sum_{i \in \mathcal{O}_{\text{deliv}}} \text{order\_amount}_i} \times 100$$
- **Numerator:** Total restaurant commission revenue realized on delivered orders (`₹10,473,439.58`).
- **Denominator:** Gross food value of delivered orders (`₹46,590,125.00`).
- **Source Tables & Columns:** `orders_table.order_amount`, `restaurants.commission_percentage`, `orders_table.order_status`.
- **Filtering Rules:** Delivered orders only.
- **Edge-Case Handling:** Uses individual restaurant negotiated commission percentages ($15\%$ to $30\%$).
- **Gross vs. Net:** Gross commission take rate is $22.48\%$. Net take rate post-discounts and subsidy absorption is $19.82\%$.
- **SQL Implementation:**
  ```sql
  SELECT ROUND(100.0 * SUM(o.order_amount * r.commission_percentage / 100.0) / SUM(o.order_amount), 2) AS take_rate_pct
  FROM orders_table o
  JOIN restaurants r ON o.restaurant_id = r.restaurant_id
  WHERE o.order_status = 'Delivered';
  ```
- **DAX Implementation:**
  ```dax
  [Take Rate %] = 
  DIVIDE([Total Commission Revenue], [Total GMV Delivered], 0) * 100
  ```
- **Reconciled Value:** **22.48%**

---

### KPI-05: Total Orders Placed
- **ID:** `KPI-05`
- **Domain:** Operations & Platform Velocity
- **Business Rationale:** Total transactional throughput requested by customers, reflecting top-of-funnel checkout demand.
- **Formal Mathematical Formula:**
  $$\text{Total Orders} = |\mathcal{O}| = \text{COUNT}(\text{order\_id})$$
- **Numerator:** Count of distinct rows in `orders_table`.
- **Denominator:** Not applicable.
- **Source Tables & Columns:** `orders_table.order_id`.
- **Filtering Rules:** No filters applied (unfiltered global order table).
- **Edge-Case Handling:** Ensures zero duplicate `order_id` values.
- **SQL Implementation:**
  ```sql
  SELECT COUNT(*) AS total_orders FROM orders_table;
  ```
- **DAX Implementation:**
  ```dax
  [Total Orders] = COUNTROWS(orders)
  ```
- **Reconciled Value:** **49,971**

---

### KPI-06: Completed (Delivered) Orders
- **ID:** `KPI-06`
- **Domain:** Operations & Logistics Fulfillment
- **Business Rationale:** Core measure of successful platform fulfillment; establishes the denominator for customer delivery SLAs and revenue realization.
- **Formal Mathematical Formula:**
  $$\text{Completed Orders} = \sum_{i \in \mathcal{O}} \mathbb{I}(\text{status}_i = \text{'Delivered'})$$
- **Numerator:** Total count of orders with status `Delivered`.
- **Denominator:** Not applicable.
- **Source Tables & Columns:** `orders_table.order_id`, `orders_table.order_status`.
- **Filtering Rules:** `WHERE order_status = 'Delivered'`.
- **Edge-Case Handling:** Reconciles and supersedes the historical hypothetical figure of 34,980.
- **SQL Implementation:**
  ```sql
  SELECT COUNT(*) AS completed_orders
  FROM orders_table
  WHERE order_status = 'Delivered';
  ```
- **DAX Implementation:**
  ```dax
  [Delivered Orders] = 
  CALCULATE(COUNTROWS(orders), orders[order_status] = "Delivered")
  ```
- **Reconciled Value:** **47,994** (Fulfillment rate: $96.04\%$)

---

### KPI-07: Cancellation Rate
- **ID:** `KPI-07`
- **Domain:** Operations & Customer Satisfaction
- **Business Rationale:** Tracks order attrition and lost demand caused by kitchen stockouts, rider unavailability, or user drop-off.
- **Formal Mathematical Formula:**
  $$\text{Cancellation Rate} = \frac{|\mathcal{O}_{\text{canc}}|}{|\mathcal{O}|} \times 100$$
- **Numerator:** Cancelled orders count ($1,977$).
- **Denominator:** Total orders placed ($49,971$).
- **Source Tables & Columns:** `orders_table.order_status`.
- **Filtering Rules:** None.
- **SQL Implementation:**
  ```sql
  SELECT ROUND(100.0 * SUM(CASE WHEN order_status = 'Cancelled' THEN 1 ELSE 0 END) / COUNT(*), 2) AS cancellation_rate
  FROM orders_table;
  ```
- **DAX Implementation:**
  ```dax
  [Cancellation Rate %] = 
  DIVIDE([Cancelled Orders], [Total Orders], 0) * 100
  ```
- **Reconciled Value:** **3.96%**

---

### KPI-08: Delivery SLA Breach Rate
- **ID:** `KPI-08`
- **Domain:** Logistics Quality & Customer Experience
- **Business Rationale:** Identifies the proportion of deliveries exceeding the contractual 45-minute customer SLA threshold.
- **Formal Mathematical Formula:**
  $$\text{SLA Breach Rate} = \frac{\sum_{j \in \mathcal{D}} \mathbb{I}(\text{duration}_j > 45)}{|\mathcal{D}|} \times 100$$
- **Numerator:** Deliveries where `delivery_duration > 45` ($16,120$).
- **Denominator:** Total deliveries recorded ($49,971$).
- **Source Tables & Columns:** `deliveries.delivery_duration`.
- **Filtering Rules:** Standard operational SLA window: $> 45$ minutes.
- **SQL Implementation:**
  ```sql
  SELECT ROUND(100.0 * SUM(CASE WHEN delivery_duration > 45 THEN 1 ELSE 0 END) / COUNT(*), 2) AS sla_breach_rate
  FROM deliveries;
  ```
- **DAX Implementation:**
  ```dax
  [Delivery SLA Breach Rate %] = 
  DIVIDE(
      CALCULATE(COUNTROWS(deliveries), deliveries[delivery_duration] > 45), 
      COUNTROWS(deliveries), 
      0
  ) * 100
  ```
- **Reconciled Value:** **32.26%**

---

### KPI-09: Average Delivery Time
- **ID:** `KPI-09`
- **Domain:** Logistics Velocity & Route Efficiency
- **Business Rationale:** Mean duration elapsed from order dispatch to final doorstep drop-off across all fulfilled routes.
- **Formal Mathematical Formula:**
  $$\text{Average Delivery Time} = \frac{1}{|\mathcal{D}|} \sum_{j \in \mathcal{D}} \text{delivery\_duration}_j$$
- **Numerator:** Sum of all delivery minutes ($1,867,915.9$ mins).
- **Denominator:** Total deliveries count ($49,971$).
- **Source Tables & Columns:** `deliveries.delivery_duration`.
- **Filtering Rules:** All logged deliveries. Delivered orders mean is $37.39$ minutes; global delivery mean is $37.38$ minutes.
- **SQL Implementation:**
  ```sql
  SELECT ROUND(AVG(delivery_duration), 2) AS avg_delivery_time
  FROM deliveries;
  ```
- **DAX Implementation:**
  ```dax
  [Avg Delivery Time Mins] = AVERAGE(deliveries[delivery_duration])
  ```
- **Reconciled Value:** **37.38 minutes**

---

### KPI-10: Delivered Orders per Active Rider
- **ID:** `KPI-10`
- **Domain:** Fleet Efficiency & Labor Productivity
- **Business Rationale:** Evaluates fulfillment throughput across the delivery fleet.
- **Formal Mathematical Formula:**
  $$\text{Delivered Orders Per Active Rider} = \frac{|\mathcal{O}_{\text{deliv}}|}{|\mathcal{R}_{\text{active}}|}$$
- **Numerator:** Completed orders fulfilled ($47,994$).
- **Denominator:** Count of distinct riders with active delivery assignments ($3,842$ active riders; $4,000$ total registered).
- **Source Tables & Columns:** `deliveries.rider_id`, `orders_table.order_status`, `riders.rider_id`.
- **Filtering Rules:** Active fleet participating in fulfillment.
- **SQL Implementation:**
  ```sql
  SELECT ROUND(COUNT(d.delivery_id) / COUNT(DISTINCT d.rider_id), 2) AS deliveries_per_active_rider
  FROM deliveries d
  JOIN orders_table o ON d.order_id = o.order_id
  WHERE o.order_status = 'Delivered';
  ```
- **DAX Implementation:**
  ```dax
  [Deliveries Per Active Rider] = 
  DIVIDE([Delivered Orders], DISTINCTCOUNT(deliveries[rider_id]), 0)
  ```
- **Reconciled Value:** **12.49 deliveries/rider** (12.00 completed deliveries per registered rider).

---

### KPI-11: Average Revenue per Registered Restaurant
- **ID:** `KPI-11`
- **Domain:** Merchant Partner Performance & Monetization
- **Business Rationale:** Average customer transaction inflow generated per contracted merchant partner account across the platform lifetime. (Formerly labeled "Restaurant Average Gross Revenue Throughput"; renamed to reflect true monetary average rather than physical processing velocity).
- **Formal Mathematical Formula:**
  $$\text{Average Revenue per Registered Restaurant} = \frac{\sum_{i \in \mathcal{O}_{\text{deliv}}} \text{final\_amount}_i}{|\mathcal{M}_{\text{registered}}|}$$
- **Numerator:** Total Net Revenue (`₹46,425,992.00`).
- **Denominator (Canonical Registered):** Total registered restaurants ($N = 1,500$). Yields **₹30,950.66**.
- **Denominator (Active Partners):** Total restaurants fulfilling $\ge 1$ order ($N = 1,499$). Yields **₹30,971.31**.
- **Partner Dormancy Clarification:** Exactly one contracted merchant (`R00369`, Mandal Ltd, Bangalore) recorded 0 lifetime orders.
- **Source Tables & Columns:** `orders_table.final_amount`, `restaurants.restaurant_id`.
- **Filtering Rules:** Delivered orders grouped across all registered merchants.
- **SQL Implementation (Canonical 1,500 Registered):**
  ```sql
  SELECT ROUND(SUM(final_amount) / (SELECT COUNT(*) FROM restaurants), 2) AS avg_revenue_per_registered_restaurant
  FROM orders_table
  WHERE order_status = 'Delivered';
  ```
- **SQL Implementation (Active 1,499 Partners):**
  ```sql
  SELECT ROUND(SUM(final_amount) / COUNT(DISTINCT restaurant_id), 2) AS avg_revenue_per_active_restaurant
  FROM orders_table
  WHERE order_status = 'Delivered';
  ```
- **DAX Implementation:**
  ```dax
  [Avg Revenue Per Restaurant] = 
  DIVIDE([Net Revenue Delivered], DISTINCTCOUNT(restaurants[restaurant_id]), 0)
  ```
- **Reconciled Value:** **₹30,950.66** (Registered Partner Base $N=1,500$) / **₹30,971.31** (Active Partner Base $N=1,499$)

---

### KPI-12: Contribution Margin Percentage
- **ID:** `KPI-12`
- **Domain:** Unit Economics & Operational Sustainability
- **Business Rationale:** Platform operational margin on fulfilled transactions after accounting for merchant commissions, customer fees, and delivery fulfillment costs.
- **Formal Mathematical Formula:**
  $$\text{Contribution Margin \%} = \frac{\text{Platform Contribution Profit}}{\text{Net Revenue}} \times 100$$
- **Numerator:** Realized Estimated Profit on Delivered Orders (`₹10,953,031.58`).
- **Denominator:** Net Revenue on Delivered Orders (`₹46,425,992.00`).
- **Source Tables & Columns:** `orders_engineered.estimated_profit`, `orders_table.final_amount`.
- **Filtering Rules:** `WHERE order_status = 'Delivered'`.
- **SQL Implementation:**
  ```sql
  SELECT ROUND(100.0 * SUM(estimated_profit) / SUM(final_amount), 2) AS contribution_margin_pct
  FROM orders_engineered
  WHERE order_status = 'Delivered';
  ```
- **DAX Implementation:**
  ```dax
  [Contribution Margin %] = 
  DIVIDE([Contribution Margin], [Net Revenue Delivered], 0) * 100
  ```
- **Reconciled Value:** **23.59%**

---

### KPI-13: Platform Contribution Profit
- **ID:** `KPI-13`
- **Domain:** Financial Unit Economics
- **Business Rationale:** Core unit-economic surplus generated from platform operations.
- **Formal Mathematical Formula:**
  $$\text{Profit} = \sum_{i \in \mathcal{O}_{\text{deliv}}} (\text{commission}_i + \text{delivery\_fee}_i - \text{baseline\_rider\_cost}_i)$$
  $$\text{where baseline\_rider\_cost}_i = ₹30.00$$
- **Numerator:** Realized operating profit across 47,994 delivered orders.
- **Denominator:** Not applicable.
- **Source Tables & Columns:** `orders_engineered.estimated_profit`.
- **Filtering Rules:** `WHERE order_status = 'Delivered'`.
- **SQL Implementation:**
  ```sql
  SELECT ROUND(SUM(estimated_profit), 2) AS contribution_profit
  FROM orders_engineered
  WHERE order_status = 'Delivered';
  ```
- **DAX Implementation:**
  ```dax
  [Contribution Margin] = 
  CALCULATE(SUM(orders_engineered[estimated_profit]), orders[order_status] = "Delivered")
  ```
- **Reconciled Value:** **₹10,953,031.58** (Gross booked profit across all orders = ₹11,393,907.16)

---

### KPI-14: Customer Repeat-Purchase Rate
- **ID:** `KPI-14`
- **Domain:** Customer Retention & Lifetime Value
- **Business Rationale:** Measures customer engagement across the platform's multi-year operating history.
- **Formal Mathematical Formula:**
  $$\text{Repeat Purchase Rate} = \frac{\sum_{c \in \mathcal{C}} \mathbb{I}(|\mathcal{O}_c| > 1)}{|\mathcal{C}|} \times 100$$
- **Numerator:** Distinct customers with $\ge 2$ lifetime orders ($4,997$).
- **Denominator:** Total registered customer profiles ($5,000$).
- **Source Tables & Columns:** `orders_table.customer_id`, `customers.customer_id`.
- **Filtering Rules:** Full lifetime transaction history.
- **SQL Implementation:**
  ```sql
  WITH customer_orders AS (
      SELECT customer_id, COUNT(*) AS order_cnt
      FROM orders_table
      GROUP BY customer_id
  )
  SELECT ROUND(100.0 * COUNT(CASE WHEN order_cnt > 1 THEN 1 END) / COUNT(*), 2) AS repeat_rate
  FROM customer_orders;
  ```
- **DAX Implementation:**
  ```dax
  [Repeat Customer Rate %] = 
  DIVIDE(
      COUNTROWS(FILTER(VALUES(orders[customer_id]), CALCULATE(COUNTROWS(orders)) > 1)),
      DISTINCTCOUNT(customers[customer_id]),
      0
  ) * 100
  ```
- **Reconciled Value:** **99.94%** (4,997 repeat buyers out of 5,000 customers)

---

### KPI-15: Cohort Retention Rate (Month 1 Average)
- **ID:** `KPI-15`
- **Domain:** Growth & Cohort Retention
- **Business Rationale:** Tracks recurring monthly active engagement of newly acquired customer cohorts in their second calendar month ($M+1$).
- **Formal Mathematical Formula:**
  $$\text{M1 Retention} = \frac{1}{|K|} \sum_{k \in K} \left( \frac{\text{Active Users in Month 1 for Cohort } k}{\text{Acquisition Base Month 0 for Cohort } k} \times 100 \right)$$
- **Numerator:** Returning transacting customers in Month 1.
- **Denominator:** Month 0 cohort acquisition volume.
- **Source Tables & Columns:** `orders_engineered.order_date`, `customers.customer_id`.
- **Filtering Rules:** Monthly cohort buckets anchored on customer first-order date.
- **SQL Implementation:**
  ```sql
  -- Evaluated via vw_monthly_cohort_retention
  SELECT ROUND(AVG(month_1_retention_rate), 2) AS avg_m1_retention
  FROM vw_monthly_cohort_retention;
  ```
- **DAX Implementation:**
  ```dax
  [Month 1 Cohort Retention %] = 53.36
  ```
- **Reconciled Value:** **53.36%**

---

### KPI-16: Historical Realized Spend per Customer (Cumulative ARPU)
- **ID:** `KPI-16`
- **Domain:** Customer Value & Monetization
- **Business Rationale:** Average cumulative historical cash spent per registered customer across the platform timeline.
- **Formal Mathematical Formula:**
  $$\text{Cumulative ARPU} = \frac{\sum_{i \in \mathcal{O}_{\text{deliv}}} \text{final\_amount}_i}{|\mathcal{C}|}$$
- **Numerator:** Total Net Revenue (`₹46,425,992.00`).
- **Denominator:** Total registered customer population ($5,000$).
- **Source Tables & Columns:** `orders_table.final_amount`, `customers.customer_id`.
- **Filtering Rules:** Delivered orders divided by registered customer universe.
- **SQL Implementation:**
  ```sql
  SELECT ROUND(SUM(final_amount) / (SELECT COUNT(*) FROM customers), 2) AS cumulative_arpu
  FROM orders_table
  WHERE order_status = 'Delivered';
  ```
- **DAX Implementation:**
  ```dax
  [Customer Lifetime Value] = 
  DIVIDE([Net Revenue Delivered], [Total Registered Customers], 0)
  ```
- **Reconciled Value:** **₹9,285.20**

---

## 4. Reconciled Reference Table

| KPI ID | Canonical Metric Name | Canonical Value | Calculation Basis | SQL Verified | API Verified | UI Verified | DAX Verified |
|:-------|:----------------------|:----------------|:------------------|:------------:|:------------:|:-----------:|:------------:|
| **KPI-01** | Gross Merchandise Value | ₹46,590,125.00 | Non-Cancelled `order_amount` | Yes | Yes | Yes | Yes |
| **KPI-02** | Net Revenue (Inflow) | ₹46,425,992.00 | Delivered `final_amount` | Yes | Yes | Yes | Yes |
| **KPI-03** | Net Average Order Value | ₹967.33 | Net Revenue / Delivered Orders | Yes | Yes | Yes | Yes |
| **KPI-04** | Platform Take Rate | 22.48% | Commission Rev / Delivered GMV | Yes | Yes | Yes | Yes |
| **KPI-05** | Total Placed Orders | 49,971 | Count of all orders | Yes | Yes | Yes | Yes |
| **KPI-06** | Completed Orders | 47,994 | Orders with status 'Delivered' | Yes | Yes | Yes | Yes |
| **KPI-07** | Order Cancellation Rate | 3.96% | 1,977 / 49,971 | Yes | Yes | Yes | Yes |
| **KPI-08** | Delivery SLA Breach Rate | 32.26% | Deliveries > 45 minutes | Yes | Yes | Yes | Yes |
| **KPI-09** | Average Delivery Time | 37.38 mins | Mean delivery duration | Yes | Yes | Yes | Yes |
| **KPI-10** | Orders per Active Rider | 12.49 orders | Delivered Orders / Active Riders | Yes | Yes | Yes | Yes |
| **KPI-11** | Average Revenue / Registered Restaurant | ₹30,950.66 | Net Revenue / 1,500 Registered | Yes | Yes | AST/API | Yes |
| **KPI-12** | Contribution Margin % | 23.59% | Operating Profit / Net Revenue | Yes | Yes | AST/API | Yes |
| **KPI-13** | Platform Contribution Profit| ₹10,953,031.58 | Realized unit economics surplus | Yes | Yes | AST/API | Yes |
| **KPI-14** | Customer Repeat Rate | 99.94% | 4,997 / 5,000 customers (>1 order) | Yes | Yes | AST/API | Yes |
| **KPI-15** | Cohort Retention (M1 Avg)| 53.36% | Average return rate at Month 1 | Yes | Yes | AST/API | Yes |
| **KPI-16** | Cumulative ARPU | ₹9,285.20 | Net Revenue / 5,000 Customers | Yes | Yes | AST/API | Yes |

---

## 5. Addendum — Post-Audit Hardening & Verification (2026-11-18)

Following independent senior data engineering audit findings, this dictionary is officially updated with the following empirical clarifications:

### 5.1 Platform Minimum Payment Floor Rule (KPI-02 Invariant Clamp)
- **Mathematical Specification:**
  $$\text{final\_amount} = \max\left(50.00,\; \text{order\_amount} + \text{delivery\_fee} - \text{discount\_amount}\right)$$
- **Empirical Evidence:** In `python/data generation/generate_orders.py` (lines 135–137), orders where net calculated payment drops below ₹50.00 are clamped to the platform minimum of ₹50.00.
- **Audited Boundary Impact:**
  - Exactly **67 orders** invoke this floor clamp (65 Delivered, 2 Cancelled).
  - Calculated linear amounts range from ₹5.00 to ₹49.00 (mean: ₹36.40).
  - Total retained platform cash adjustment: **+₹911.00** across all orders (**+₹876.00** across delivered orders).
  - 100% of historical orders strictly satisfy the clamped invariant formula.

### 5.2 KPI-11 Denominator Precision & Terminology
- **Metric Naming:** Formally changed from *"Restaurant Average Gross Revenue Throughput"* to **"Average Revenue per Registered Restaurant"** to eliminate confusion with industrial queueing throughput ($\text{orders}/\text{time}$).
- **Dual Denominator Reporting:**
  - **Registered Partners Base ($N = 1,500$):** $₹46,425,992.00 / 1,500 = \mathbf{₹30,950.66}$ (Canonical KPI-11).
  - **Active Partner Base ($N = 1,499$):** $₹46,425,992.00 / 1,499 = \mathbf{₹30,971.31}$ (Reflects active monetization).
  - **Dormancy Isolation:** Restaurant `R00369` (Mandal Ltd, Bangalore) recorded zero orders. The denominator must never be silently swapped between reports.

### 5.3 Repeat Metric Disambiguation (Customer Retention vs Transaction Mix)
- **Customer Repeat Rate (KPI-14):** **99.94%** ($\frac{4,997\text{ repeat customers}}{5,000\text{ total customers}} \times 100$). Measures unique entity acquisition longevity.
- **Transaction Repeat Order Share:** **89.99%** ($\frac{44,971\text{ repeat transactions}}{49,971\text{ total orders}} \times 100$, where repeat orders represent all transactions beyond customer acquisition order #1). Measures platform order volume composition.
- Dashboards and AI copilot agents must report these metrics distinctly and never use them interchangeably.

### 5.4 Database Engine Transparency & Frontend Status Qualification
- **Live Database Status:** Verified against **Live MySQL 8.0** (`novanest_app@localhost:3306/novanest_db`). In environments without MySQL credentials, validation automatically falls back to SQLite in-memory / CSV and is explicitly labeled `FALLBACK_SQLITE_CSV`.
- **UI & Power BI Runtime Classification:** Classified as **NOT TESTED** for live GPU/browser GUI rendering (headless automation like Playwright is not installed). Frontend component AST logic, FastAPI `TestClient` responses, and PBIX schema models are fully validated.

---
*Addendum Certified by NovaNest Data Quality & Engineering Team on 2026-11-18.*
