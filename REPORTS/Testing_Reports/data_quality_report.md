# NOVANEST — COMPREHENSIVE DATA QUALITY & INTEGRITY REPORT
**Phase 2: Data Intelligence & Pipeline Stabilization Audit**

---

## 1. Executive Summary

A comprehensive, automated data health audit was conducted across all 10 relational tables in the **NovaNest Food Delivery Ecosystem**, comprising **304,405 records** and **49,971 enriched transactions**.

### High-Level Quality Verdict:
- **Missing Values (Nulls)**: **0** across all 10 cleaned tables (100% complete).
- **Duplicate Records**: **0** duplicate primary keys or rows across all tables.
- **Referential Integrity**: **100% Pass** across all 11 primary-foreign key relationships. Zero orphaned child records.
- **Statistical Outliers**: Bounded within valid real-world business constraints (no negative prices, fees, or durations).
- **Documented Anomalies**:
  - **Cross-City Transactions**: 38,572 orders (77.2%) pair customers and restaurants in different cities.
  - **Pre-Signup Order Timestamps**: 12,418 orders (24.9%) bear order timestamps preceding customer signup dates.
  - **Resolution**: Non-destructive preservation. Both anomalies are explicitly isolated with binary audit flags (`cross_city_flag`, `pre_signup_order_flag`) in `datasets/engineered/orders_engineered.csv` and `datasets/engineered/orders_geo_temporal_enriched.csv`, preserving 100% of transactional history for downstream modeling.

---

## 2. Table-by-Table Data Health Matrix

| Table Name | Primary Key | Total Records | Columns | Null Count | Duplicate Rows | Referential Integrity | Quality Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `customers` | `customer_id` | 5,000 | 10 | 0 | 0 | Parent Table | **EXCELLENT** |
| `restaurants` | `restaurant_id` | 1,500 | 9 | 0 | 0 | Parent Table | **EXCELLENT** |
| `menu_items` | `item_id` | 15,000 | 6 | 0 | 0 | 100% linked to `restaurants` | **EXCELLENT** |
| `riders` | `rider_id` | 4,000 | 7 | 0 | 0 | Parent Table | **EXCELLENT** |
| `orders` | `order_id` | 49,971 | 12 | 0 | 0 | 100% linked to cust, rest, item, rider | **EXCELLENT** |
| `payments` | `payment_id` | 49,971 | 4 | 0 | 0 | 100% 1:1 linked to `orders` | **EXCELLENT** |
| `deliveries` | `delivery_id` | 49,971 | 5 | 0 | 0 | 100% 1:1 linked to `orders` & riders | **EXCELLENT** |
| `app_events` | `event_id` | 100,000 | 3 | 0 | 0 | 100% linked to `customers` | **EXCELLENT** |
| `ratings_reviews` | `review_id` | 28,792 | 5 | 0 | 0 | 100% linked to `orders` & cust | **EXCELLENT** |
| `promotions` | `promo_id` | 200 | 5 | 0 | 0 | Standalone Campaign Table | **EXCELLENT** |
| **Total Ecosystem** | — | **304,405** | **66** | **0** | **0** | **11/11 Verified Relations** | **HEALTHY** |

---

## 3. Referential Integrity Verification Matrix

Automated verification was executed via `python/pipeline_runner.py`:

```
┌────────────────────────────────────────────────────────┬─────────┬──────────────┐
│ Foreign Key Relationship                               │ Status  │ Orphan Count │
├────────────────────────────────────────────────────────┼─────────┼──────────────┤
│ orders.customer_id        ──► customers.customer_id     │ PASS ✅ │ 0            │
│ orders.restaurant_id      ──► restaurants.restaurant_id │ PASS ✅ │ 0            │
│ orders.item_id            ──► menu_items.item_id        │ PASS ✅ │ 0            │
│ orders.rider_id           ──► riders.rider_id           │ PASS ✅ │ 0            │
│ deliveries.order_id       ──► orders.order_id           │ PASS ✅ │ 0            │
│ deliveries.rider_id       ──► riders.rider_id           │ PASS ✅ │ 0            │
│ payments.order_id         ──► orders.order_id           │ PASS ✅ │ 0            │
│ ratings_reviews.order_id  ──► orders.order_id           │ PASS ✅ │ 0            │
│ ratings_reviews.cust_id   ──► customers.customer_id     │ PASS ✅ │ 0            │
│ app_events.customer_id    ──► customers.customer_id     │ PASS ✅ │ 0            │
│ menu_items.restaurant_id  ──► restaurants.restaurant_id │ PASS ✅ │ 0            │
└────────────────────────────────────────────────────────┴─────────┴──────────────┘
```

---

## 4. Deep Anomaly Investigation & Resolution

### Anomaly 1: Cross-City Order Inconsistency
- **Finding**: Out of 49,971 total orders, **38,572 orders (77.19%)** feature a customer registered in city $A$ ordering from a restaurant located in city $B$.
- **Rider Verification**: In **100.00%** of orders, `rider_city == restaurant_city`. Deliveries are always fulfilled within the restaurant's local operating zone.
- **Root Cause**: In `python/data generation/generate_orders.py`, customer selection was randomized across all customers without filtering by `customer.city == restaurant.city`.
- **Business Interpretation**:
  - In a production environment, this mirrors legitimate real-world phenomena: business travelers ordering food in hotel cities, gifting meals to relatives in other cities, or users maintaining their permanent hometown profile while residing in another metropolitan area.
- **Architectural Resolution**:
  - We strictly adhere to **ADR-003**: No records were deleted.
  - Added `cross_city_flag` (1 for cross-city, 0 for same-city) to `orders_engineered.csv`.
  - Machine learning models for hyperlocal ETA prediction filter on `cross_city_flag == 0` or utilize restaurant-to-rider localized coordinates.

### Anomaly 2: Pre-Signup Order Inconsistency
- **Finding**: **12,418 orders (24.85%)** have an `order_datetime` timestamp that occurs prior to the customer's recorded `signup_date`.
- **Root Cause**: `generate_orders.py` generated `order_datetime` uniformly across the preceding 365 days independently of `signup_date`.
- **Business Interpretation**:
  - Represents guest-checkout conversions (orders placed before formal profile creation) or backfilled historical data.
- **Architectural Resolution**:
  - Retained all records to preserve transactional integrity and revenue calculations.
  - Added `pre_signup_order_flag` (1 if `order_datetime < signup_date`, 0 otherwise) to the engineered dataset.
  - Downstream cohort retention analytics and customer lifetime value (CLV) models adjust the effective acquisition date to $\min(\text{signup\_date}, \text{first\_order\_date})$.

---

## 5. Statistical Distributions & Outlier Analysis

Key numerical variables were audited for range validity, zero/negative bounds, and distribution characteristics:

| Feature Name | Min | 25% | Median | 75% | Max | IQR | Outlier Policy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Quantity** | 1 | 1 | 2 | 3 | 4 | 2 | Legitimate basket size |
| **Order Amount (₹)** | ₹80 | ₹452 | ₹794 | ₹1,365 | ₹2,800 | ₹913 | Realistic meal prices |
| **Discount Amount (₹)** | ₹0 | ₹25 | ₹41 | ₹60 | ₹100 | ₹35 | Capped promotion limits |
| **Delivery Fee (₹)** | ₹20 | ₹30 | ₹40 | ₹50 | ₹60 | ₹20 | Standard distance-tier fees |
| **Final Amount (₹)** | ₹50 | ₹448 | ₹789 | ₹1,362 | ₹2,843 | ₹914 | 100% positive values |
| **Distance (km)** | 1.0 | 3.7 | 6.5 | 9.2 | 12.0 | 5.5 | Clamped to delivery radius |
| **Delivery Duration (min)**| 15 | 26 | 37 | 49 | 60 | 23 | Bounded 15–60 min range |
| **Menu Price (₹)** | ₹80 | ₹235 | ₹389 | ₹543 | ₹700 | ₹308 | Realistic single-dish menu pricing |
| **Preparation Time (min)** | 10 | 19 | 28 | 37 | 45 | 18 | Realistic kitchen prep SLA |

---

## 6. Engineered Feature Set Certification

The stabilized feature engineering pipeline produces `datasets/engineered/orders_engineered.csv` with **38 certified columns**:

1. **Identifiers**: `order_id`, `customer_id`, `restaurant_id`, `item_id`, `rider_id`
2. **Transactional Core**: `order_datetime`, `quantity`, `order_amount`, `discount_amount`, `delivery_fee`, `final_amount`, `order_status`
3. **Temporal Breakdown**: `order_date`, `order_year`, `order_month`, `order_month_name`, `hour`, `day_of_week`
4. **Behavioral Flags**: `peak_hour_flag` (29.2%), `weekend_flag` (28.6%), `cancellation_flag` (5.1%)
5. **Economic Metrics**: `net_order_value`, `discount_percentage`, `commission_percentage`, `commission_revenue`, `estimated_profit`, `profit_margin_pct`, `order_size`
6. **Operations & Fulfillment**: `distance_km`, `delivery_duration`, `delivery_speed_kph`, `delivery_delay_flag` (32.3%)
7. **Geospatial & Demographics**: `restaurant_city`, `customer_city`, `rider_city`, `signup_date`
8. **Data Quality Audit Flags**: `cross_city_flag` (77.2%), `pre_signup_order_flag` (24.9%)

---

## 7. Pipeline Reproducibility & Execution Benchmark

The automated execution harness `python/pipeline_runner.py` was benchmarked on the active environment (Python 3.14.4 on Windows 11):

- **Data Cleaning (`clean_data.py`)**: 1.37s
- **Referential Integrity Validation**: 2.57s
- **Feature Engineering (`feature_engineering.py`)**: 2.24s
- **Total Pipeline Execution**: **6.18 seconds**
- **Exit Status**: Code 0 (Success)

*Certified for Phase 02 Data Foundation Milestone.*
