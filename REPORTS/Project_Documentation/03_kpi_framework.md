# NOVANEST — MASTER KPI FRAMEWORK & MATHEMATICAL DICTIONARY
**Standardized Definitions Across SQL, Python, DAX & Machine Learning**

---

## 1. Executive Summary & KPI Architecture

The NovaNest Platform aligns operational, financial, and customer intelligence metrics into an integrated KPI hierarchy:

```
                          ┌────────────────────────┐
                          │   NET PLATFORM PROFIT  │
                          └───────────┬────────────┘
                                      │
          ┌───────────────────────────┴───────────────────────────┐
          │                                                       │
┌─────────▼─────────┐                                   ┌─────────▼─────────┐
│   TOTAL REVENUE   │                                   │    TOTAL COSTS    │
│  (Take Rate * GMV)│                                   │  (Delivery+CAC+OP)│
└─────────┬─────────┘                                   └─────────┬─────────┘
          │                                                       │
   ┌──────┴──────┐                                         ┌──────┴──────┐
   │             │                                         │             │
┌──▼───┐     ┌───▼────┐                              ┌─────▼────┐   ┌────▼────┐
│ AOV  │     │ Orders │                              │ Rider Pay│   │Discounts│
└──────┘     └───┬────┘                              └──────────┘   └─────────┘
                 │
        ┌────────┴────────┐
        │                 │
  ┌─────▼─────┐     ┌─────▼─────┐
  │ Active Cust│    │ Order Freq│
  └───────────┘     └───────────┘
```

---

## 2. Core Platform KPI Matrix

### 1. Gross Merchandise Value (GMV)
- **Business Definition**: Total gross transaction value of all food orders placed through the NovaNest platform before discounts and delivery charges.
- **Mathematical Formula**:
  $$\text{GMV} = \sum (\text{quantity} \times \text{item\_price}) = \sum \text{order\_amount}$$
- **SQL Implementation**:
  ```sql
  SELECT SUM(order_amount) AS gmv FROM orders_table WHERE order_status != 'Cancelled';
  ```
- **Python Validation**:
  ```python
  gmv = orders[orders["order_status"] != "Cancelled"]["order_amount"].sum()
  ```
- **DAX Implementation**:
  ```dax
  GMV = CALCULATE(SUM(orders[order_amount]), orders[order_status] <> "Cancelled")
  ```
- **Business Interpretation**: Primary scale metric reflecting platform gross throughput.

---

### 2. Net Revenue (Platform Inflow)
- **Business Definition**: Actual gross inflow to the platform, comprising restaurant commissions, delivery fees collected from customers, and surge charges minus customer discounts.
- **Mathematical Formula**:
  $$\text{Net Revenue} = \sum (\text{order\_amount} - \text{discount\_amount} + \text{delivery\_fee}) = \sum \text{final\_amount}$$
- **SQL Implementation**:
  ```sql
  SELECT SUM(final_amount) AS net_revenue FROM orders_table WHERE order_status = 'Delivered';
  ```
- **Python Validation**:
  ```python
  net_revenue = orders[orders["order_status"] == "Delivered"]["final_amount"].sum()
  ```
- **DAX Implementation**:
  ```dax
  Net Revenue = CALCULATE(SUM(orders[final_amount]), orders[order_status] = "Delivered")
  ```
- **Business Interpretation**: The true monetary collection realized from completed customer transactions.

---

### 3. Platform Take Rate (%)
- **Business Definition**: Percentage of GMV retained by the platform as commission from restaurant partners.
- **Mathematical Formula**:
  $$\text{Take Rate} = \left( \frac{\text{Total Commission Revenue}}{\text{GMV}} \right) \times 100$$
- **SQL Implementation**:
  ```sql
  SELECT ROUND(100.0 * SUM(o.order_amount * (r.commission_percentage / 100.0)) / SUM(o.order_amount), 2) AS take_rate
  FROM orders_table o
  JOIN restaurants r ON o.restaurant_id = r.restaurant_id;
  ```
- **Python Validation**:
  ```python
  take_rate = round((orders["commission_revenue"].sum() / orders["order_amount"].sum()) * 100, 2)
  ```
- **DAX Implementation**:
  ```dax
  Take Rate = DIVIDE([Total Commission Revenue], [GMV], 0) * 100
  ```
- **Business Interpretation**: Monetization efficiency of the platform. Higher take rate increases margin but risks restaurant attrition.

---

### 4. Average Order Value (AOV)
- **Business Definition**: The average monetary amount spent by a customer per placed order.
- **Mathematical Formula**:
  $$\text{AOV} = \frac{\sum \text{final\_amount}}{\text{Total Orders}}$$
- **SQL Implementation**:
  ```sql
  SELECT ROUND(AVG(final_amount), 2) AS average_order_value FROM orders_table;
  ```
- **Python Validation**:
  ```python
  aov = round(orders["final_amount"].mean(), 2)
  ```
- **DAX Implementation**:
  ```dax
  Average Order Value = DIVIDE([Total Revenue], [Total Orders], 0)
  ```
- **Business Interpretation**: Higher AOV improves unit economics because delivery fixed costs are amortized over larger order baskets.

---

### 5. Repeat Customer Rate (%) & Customer Retention
- **Business Definition**: Percentage of unique customers who placed two or more orders.
- **Mathematical Formula**:
  $$\text{Repeat Customer Rate} = \left( \frac{\text{Count of Customers with Orders} \ge 2}{\text{Total Unique Ordering Customers}} \right) \times 100$$
- **SQL Implementation**:
  ```sql
  WITH customer_orders AS (
      SELECT customer_id, COUNT(*) AS order_cnt
      FROM orders_table
      GROUP BY customer_id
  )
  SELECT ROUND(100.0 * COUNT(CASE WHEN order_cnt > 1 THEN 1 END) / COUNT(*), 2) AS repeat_customer_rate
  FROM customer_orders;
  ```
- **Python Validation**:
  ```python
  order_counts = orders.groupby("customer_id")["order_id"].count()
  repeat_rate = round(((order_counts > 1).sum() / len(order_counts)) * 100, 2)
  ```
- **DAX Implementation**:
  ```dax
  Repeat Customer Rate = 
  VAR CustomersWithMultipleOrders = COUNTROWS(FILTER(VALUES(orders[customer_id]), CALCULATE(COUNT(orders[order_id])) > 1))
  RETURN DIVIDE(CustomersWithMultipleOrders, DISTINCTCOUNT(orders[customer_id]), 0) * 100
  ```
- **Business Interpretation**: Core loyalty metric. Sustained repeat rates indicate product-market fit and lower CAC reliance.

---

### 6. Customer Churn Rate (%)
- **Business Definition**: Percentage of customers who have only ordered once and never returned within a designated observation window (or > 60 days inactivity).
- **Mathematical Formula**:
  $$\text{Churn Rate} = 100 - \text{Repeat Customer Rate}$$
- **SQL Implementation**:
  ```sql
  WITH customer_counts AS (
      SELECT customer_id, COUNT(*) AS order_cnt
      FROM orders_table
      GROUP BY customer_id
  )
  SELECT ROUND(100.0 * COUNT(CASE WHEN order_cnt = 1 THEN 1 END) / COUNT(*), 2) AS churn_rate
  FROM customer_counts;
  ```
- **Python Validation**:
  ```python
  churn_rate = round(((order_counts == 1).sum() / len(order_counts)) * 100, 2)
  ```
- **Business Interpretation**: Identifies customer attrition; informs re-engagement and win-back voucher strategy.

---

### 7. Customer Lifetime Value (CLV / LTV)
- **Business Definition**: Total projected net profit attributable to the entire future relationship with a customer.
- **Mathematical Formula**:
  $$\text{CLV} = \text{AOV} \times \text{Purchase Frequency} \times \text{Gross Margin \%} \times \text{Average Customer Lifespan}$$
- **SQL Implementation**:
  ```sql
  SELECT 
      c.customer_id,
      COUNT(o.order_id) AS total_orders,
      SUM(o.final_amount) AS historical_value,
      ROUND(AVG(o.final_amount), 2) AS aov,
      ROUND(SUM(o.final_amount) * 0.20, 2) AS estimated_historical_ltv
  FROM customers c
  JOIN orders_table o ON c.customer_id = o.customer_id
  GROUP BY c.customer_id;
  ```
- **Business Interpretation**: Guides maximum allowable Customer Acquisition Cost (Target CAC $\le \frac{1}{3} \text{CLV}$).

---

### 8. Delivery SLA Breach Percentage (%)
- **Business Definition**: Percentage of deliveries taking longer than 45 minutes from dispatch to doorstep.
- **Mathematical Formula**:
  $$\text{SLA Breach Rate} = \left( \frac{\text{Deliveries with Duration} > 45 \text{ mins}}{\text{Total Deliveries}} \right) \times 100$$
- **SQL Implementation**:
  ```sql
  SELECT ROUND(100.0 * COUNT(CASE WHEN delivery_duration > 45 THEN 1 END) / COUNT(*), 2) AS sla_breach_rate
  FROM deliveries;
  ```
- **Python Validation**:
  ```python
  sla_breach = round((deliveries["delivery_duration"] > 45).mean() * 100, 2)
  ```
- **DAX Implementation**:
  ```dax
  SLA Breach % = DIVIDE(CALCULATE(COUNTROWS(deliveries), deliveries[delivery_duration] > 45), COUNTROWS(deliveries), 0) * 100
  ```
- **Business Interpretation**: Operational efficiency indicator. High breach rates directly correlate with bad customer ratings and cancellation churn.

---

### 9. Delivery Success Rate (%) & Cancellation Rate (%)
- **Business Definition**:
  - Delivery Success Rate: Proportion of orders successfully completed.
  - Cancellation Rate: Proportion of orders cancelled prior to or during fulfillment.
- **Mathematical Formula**:
  $$\text{Success Rate} = \left( \frac{\text{Delivered Orders}}{\text{Total Orders}} \right) \times 100, \quad \text{Cancellation Rate} = \left( \frac{\text{Cancelled Orders}}{\text{Total Orders}} \right) \times 100$$
- **SQL Implementation**:
  ```sql
  SELECT 
      ROUND(100.0 * COUNT(CASE WHEN order_status = 'Delivered' THEN 1 END) / COUNT(*), 2) AS success_rate,
      ROUND(100.0 * COUNT(CASE WHEN order_status = 'Cancelled' THEN 1 END) / COUNT(*), 2) AS cancellation_rate
  FROM orders_table;
  ```
- **Business Interpretation**: Benchmarked at $> 95\%$ success and $< 5\%$ cancellation in healthy food delivery operations.

---

### 10. Estimated Profit & Contribution Margin per Order
- **Business Definition**: Net contribution profit generated per order after restaurant commission, delivery fees collected, and estimated rider fulfillment payouts.
- **Mathematical Formula**:
  $$\text{Order Profit} = \text{Commission Revenue} + \text{Delivery Fee} - \text{Rider Delivery Subsidy (₹30)}$$
- **SQL Implementation**:
  ```sql
  SELECT 
      ROUND(AVG((order_amount * 0.22) + delivery_fee - 30.0), 2) AS avg_contribution_margin
  FROM orders_table
  WHERE order_status = 'Delivered';
  ```
- **Business Interpretation**: Determines bottom-line viability of platform unit economics.
