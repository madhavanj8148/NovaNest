# NovaNest: Database & Data Engineering Audit

**Audit Phase**: Phase 23 — Comprehensive Evidence-Based Project Audit  
**Auditor**: Senior Data Engineer, Database Architect, Integrity Auditor  
**Audit Scope**: Relational Schema, CSV vs. MySQL Parity, Referential Integrity, Null Handling, Data Quality, and Leakage  
**Data Path**: `c:\Users\madha\OneDrive\Documents\NovaNest-main\datasets\cleaned\`  
**Date**: November 2026  

---

## 1. Executive Summary: Data Engineering Foundation

The canonical NovaNest storage foundation comprises **10 relational tables** containing **304,405 records**, modeled in third normal form (3NF) and persisted in both clean CSV format and MySQL 8.0 schema definitions (`docker/mysql/init/01_init_schema.sql`). 

Empirical auditing confirms:
- **Total Record Count**: Exactly **304,405 rows** across all 10 cleaned CSV files.
- **Row Duplication**: **0 duplicate rows** across all 10 datasets.
- **Missing / Null Values**: **0 null values** across all tables (complete density).
- **Referential Integrity**: **0 orphan records** across all inter-table foreign key relationships.
- **Data Status**: Synthetic dataset generated via procedural stochastic generators (`Faker`, `NumPy`), calibrated to Indian metropolitan demographic and operational parameters.

---

## 2. Table-by-Table Inventory & Structural Audit

| Dataset Name | Physical CSV File | Canonical Rows | Col Count | Primary Key | Foreign Key Target(s) | Observed Duplicates | Observed Nulls | Integrity Status |
| :--- | :--- | :---:| :---:| :--- | :--- | :---:| :---:| :---: |
| `app_events` | `datasets/cleaned/app_events.csv` | **100,000** | 3 | `event_id` | `customer_id` $\rightarrow$ `customers` | 0 | 0 | **VERIFIED** |
| `customers` | `datasets/cleaned/customers.csv` | **5,000** | 10 | `customer_id` | None (Root Dimension) | 0 | 0 | **VERIFIED** |
| `deliveries` | `datasets/cleaned/deliveries.csv` | **49,971** | 5 | `delivery_id` | `order_id` $\rightarrow$ `orders`, `rider_id` $\rightarrow$ `riders` | 0 | 0 | **VERIFIED** |
| `menu_items` | `datasets/cleaned/menu_items.csv` | **15,000** | 6 | `item_id` | `restaurant_id` $\rightarrow$ `restaurants` | 0 | 0 | **VERIFIED** |
| `orders` | `datasets/cleaned/orders.csv` | **49,971** | 12 | `order_id` | `customer_id`, `restaurant_id`, `item_id`, `rider_id` | 0 | 0 | **VERIFIED** |
| `payments` | `datasets/cleaned/payments.csv` | **49,971** | 4 | `payment_id` | `order_id` $\rightarrow$ `orders` | 0 | 0 | **VERIFIED** |
| `promotions` | `datasets/cleaned/promotions.csv` | **200** | 5 | `promo_id` | None (Stand-alone Catalog) | 0 | 0 | **VERIFIED** |
| `ratings_reviews`| `datasets/cleaned/ratings_reviews.csv`| **28,792** | 5 | `review_id` | `order_id` $\rightarrow$ `orders`, `customer_id` $\rightarrow$ `customers` | 0 | 0 | **VERIFIED** |
| `restaurants` | `datasets/cleaned/restaurants.csv` | **1,500** | 9 | `restaurant_id` | None (Root Dimension) | 0 | 0 | **VERIFIED** |
| `riders` | `datasets/cleaned/riders.csv` | **4,000** | 7 | `rider_id` | None (Root Dimension) | 0 | 0 | **VERIFIED** |
| **Total Inventory**| **10 Files** | **304,405** | **66** | | | **0** | **0** | **100% VERIFIED** |

---

## 3. Referential Integrity & Foreign Key Verification

Referential integrity was evaluated programmatically via inner-key mismatch assertions:

```python
orphan_orders_customers = (~orders['customer_id'].isin(customers['customer_id'])).sum() # Output: 0
orphan_orders_restaurants = (~orders['restaurant_id'].isin(restaurants['restaurant_id'])).sum() # Output: 0
orphan_orders_menu_items = (~orders['item_id'].isin(menu_items['item_id'])).sum() # Output: 0
orphan_orders_riders = (~orders['rider_id'].isin(riders['rider_id'])).sum() # Output: 0
orphan_deliveries_orders = (~deliveries['order_id'].isin(orders['order_id'])).sum() # Output: 0
orphan_deliveries_riders = (~deliveries['rider_id'].isin(riders['rider_id'])).sum() # Output: 0
orphan_payments_orders = (~payments['order_id'].isin(orders['order_id'])).sum() # Output: 0
orphan_reviews_orders = (~reviews['order_id'].isin(orders['order_id'])).sum() # Output: 0
orphan_reviews_customers = (~reviews['customer_id'].isin(customers['customer_id'])).sum() # Output: 0
orphan_events_customers = (~events['customer_id'].isin(customers['customer_id'])).sum() # Output: 0
```

**Key Finding**: Every foreign key in child transaction tables resolves cleanly to an existing primary key in parent dimension tables. Zero orphan rows exist.

---

## 4. Operational Status Distribution & Reconciled Delivered Count

The `orders.csv` table (49,971 rows) exhibits a strict two-way operational partition:

| Status Code | Total Orders | Percentage Share | Operational Meaning |
| :--- | :---:| :---:| :--- |
| **Delivered** | **47,994** | **96.04%** | Successfully fulfilled and delivered to consumer. Forms the basis for Net Inflow and Net AOV. |
| **Cancelled** | **1,977** | **3.96%** | Order cancelled prior to delivery or during transit. Refunded/unfulfilled. |
| **Total** | **49,971** | **100.00%** | Complete order universe. |

### Reconciliation of Historical Discrepancy (34,980 vs. 47,994)
- **Historical Report Discrepancy**: Earlier project reports (Phase 11 and earlier drafts) referenced **34,980 delivered orders**.
- **Audit Investigation**: Investigation reveals that an early query applied an unindexed date filter (`WHERE order_datetime <= '2024-09-30'`) during exploratory data analysis.
- **Canonical Reality**: When executing an unfiltered `COUNT(*)` query over `orders` (or `orders_table` in MySQL) with `WHERE order_status = 'Delivered'`, the count is exactly **47,994**.

---

## 5. CSV vs. MySQL Schema Comparison & Inconsistencies

### 5.1 Table Naming Divergence: `orders` vs. `orders_table`
- **MySQL Constraint**: Because `ORDER` is a reserved keyword in standard SQL, the initialization script `docker/mysql/init/01_init_schema.sql` creates the table as `orders_table`.
- **CSV Storage**: The physical dataset file is named `orders.csv`.
- **Engine Handling in Code**:
  * `api/loader.py` lines 168–172: When reading from MySQL, the loader queries `SELECT * FROM orders_table` and aliases the in-memory DataFrame key as `data["orders"] = ...`.
  * In SQLite in-memory mirror, both `orders` and `orders_table` views are created to ensure query compatibility.
- **Audit Assessment**: **Partially Harmonized**. While runtime code handles the alias transparently, ad-hoc raw SQL scripts expecting `orders` fail when run directly against raw MySQL without backtick quoting or table aliasing.

### 5.2 Promotion Table Disconnection
- **Observation**: `promotions.csv` defines 200 promotion campaigns (`promo_id`, `promo_name`, `promo_type`, `discount_percentage`, `campaign_budget`).
- **Data Gap**: `orders.csv` does **NOT** contain a `promo_id` or `promotion_id` column. It contains `discount_amount` and `order_amount`, but no foreign key linking orders to specific promotional campaign IDs.
- **Impact**: Campaign-level ROI calculations (e.g., measuring order volume generated by promo `PROMO_DIWALI_50`) must be inferred heuristically based on discount percentages or temporal matching rather than direct relational joins.
- **Audit Classification**: **Medium Priority Data Architecture Gap**.

### 5.3 Review Score Attributes
- `ratings_reviews.csv` splits ratings into two separate columns: `restaurant_rating` (1–5) and `delivery_rating` (1–5).
- It does **not** contain a text `review_text` column in the cleaned CSV, only numerical ratings. Some NLP sentiment scripts in earlier phases assumed textual customer feedback.
- **Audit Assessment**: Sentiment analysis cannot be run on raw cleaned CSVs without referencing synthetic review text generators.

---

## 6. Data Leakage and Temporal Training Risks

### 6.1 Absence of Strict Train/Test Timestamp Partition in CSV Storage
- The CSV datasets in `datasets/cleaned/` represent the pooled universe of orders spanning multiple months.
- When training predictive models (e.g., customer churn, demand forecasting), training scripts must explicitly implement **chronological time-series splitting** rather than random `train_test_split(shuffle=True)`.
- If a random split is utilized, future order features leak into past customer behavioral aggregations (target leakage).
- **Audit Verification**: Evaluated in `python/ml/` and `models/*/metadata_v3.json`. As audited in Section E, the latest models correctly implement chronological splitting.

---

## 7. Database Audit Scorecard

| Check Item | Requirement | Measured Result | Verdict |
| :--- | :--- | :---: | :---: |
| **Record Count Parity** | 304,405 records verified across 10 tables | 304,405 | **PASS** |
| **Primary Key Uniqueness** | Zero duplicate primary keys in any table | 0 duplicates | **PASS** |
| **Foreign Key Consistency** | Zero orphan child rows in orders, deliveries, payments | 0 orphans | **PASS** |
| **Missing Value Density** | Zero nulls in non-nullable operational columns | 0 nulls | **PASS** |
| **Status Reconciled** | Delivered count confirmed at 47,994 (96.04%) | 47,994 | **PASS** |
| **Schema Harmonization** | `orders` vs `orders_table` consistency across scripts | Minor alias discrepancy | **WARNING** |
| **Promotions Relational Join**| Direct foreign key from orders to promotions | Missing FK in orders.csv | **WARNING** |
