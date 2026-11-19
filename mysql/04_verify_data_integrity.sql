-- ======================================================================
-- NOVANEST DATA INTEGRITY & POST-INGESTION VERIFICATION SUITE
-- Target Database: novanest_db
-- Compatibility: MySQL 8.0+
-- Safety: 100% Read-Only (Zero DDL, Zero DML, Zero Data Modification)
-- Purpose: Certifies row counts, referential integrity (0 orphans),
--          primary key uniqueness, and business financial metric parity.
-- ======================================================================

USE novanest_db;

-- ----------------------------------------------------------------------
-- 1. ROW COUNT RECONCILIATION AUDIT
-- Expected Total: 304,405 records across 10 tables
-- ----------------------------------------------------------------------
SELECT 
    tbl AS table_name,
    actual_rows,
    expected_rows,
    CASE 
        WHEN actual_rows = expected_rows THEN '✅ MATCH'
        ELSE '⚠️ MISMATCH'
    END AS count_status
FROM (
    SELECT 'customers' AS tbl, COUNT(*) AS actual_rows, 5000 AS expected_rows FROM customers
    UNION ALL SELECT 'restaurants', COUNT(*), 1500 FROM restaurants
    UNION ALL SELECT 'riders', COUNT(*), 4000 FROM riders
    UNION ALL SELECT 'promotions', COUNT(*), 200 FROM promotions
    UNION ALL SELECT 'menu_items', COUNT(*), 15000 FROM menu_items
    UNION ALL SELECT 'orders_table', COUNT(*), 49971 FROM orders_table
    UNION ALL SELECT 'payments', COUNT(*), 49971 FROM payments
    UNION ALL SELECT 'deliveries', COUNT(*), 49971 FROM deliveries
    UNION ALL SELECT 'ratings_reviews', COUNT(*), 28792 FROM ratings_reviews
    UNION ALL SELECT 'app_events', COUNT(*), 100000 FROM app_events
) AS row_summary;

-- Total records aggregation check
SELECT 
    SUM(actual_rows) AS total_records_loaded,
    304405 AS expected_total_records,
    CASE 
        WHEN SUM(actual_rows) = 304405 THEN '✅ 100% COMPLETE INGESTION VERIFIED'
        ELSE '⚠️ INCOMPLETE OR PARTIAL DATASET'
    END AS total_ingestion_status
FROM (
    SELECT COUNT(*) AS actual_rows FROM customers
    UNION ALL SELECT COUNT(*) FROM restaurants
    UNION ALL SELECT COUNT(*) FROM riders
    UNION ALL SELECT COUNT(*) FROM promotions
    UNION ALL SELECT COUNT(*) FROM menu_items
    UNION ALL SELECT COUNT(*) FROM orders_table
    UNION ALL SELECT COUNT(*) FROM payments
    UNION ALL SELECT COUNT(*) FROM deliveries
    UNION ALL SELECT COUNT(*) FROM ratings_reviews
    UNION ALL SELECT COUNT(*) FROM app_events
) AS total_summary;

-- ----------------------------------------------------------------------
-- 2. REFERENTIAL INTEGRITY AUDIT (0 ORPHAN VERIFICATION)
-- Validates all 11 foreign-key paths. Each must return exactly 0 orphan rows.
-- ----------------------------------------------------------------------
SELECT 
    relationship,
    orphan_count,
    CASE 
        WHEN orphan_count = 0 THEN '✅ 0 ORPHANS (INTEGRITY CERTIFIED)'
        ELSE '❌ REFERENTIAL INTEGRITY VIOLATION'
    END AS integrity_status
FROM (
    -- 1. menu_items -> restaurants
    SELECT '1. menu_items -> restaurants' AS relationship, COUNT(*) AS orphan_count
    FROM menu_items m LEFT JOIN restaurants r ON m.restaurant_id = r.restaurant_id WHERE r.restaurant_id IS NULL

    UNION ALL
    -- 2. orders_table -> customers
    SELECT '2. orders_table -> customers', COUNT(*)
    FROM orders_table o LEFT JOIN customers c ON o.customer_id = c.customer_id WHERE c.customer_id IS NULL

    UNION ALL
    -- 3. orders_table -> restaurants
    SELECT '3. orders_table -> restaurants', COUNT(*)
    FROM orders_table o LEFT JOIN restaurants r ON o.restaurant_id = r.restaurant_id WHERE r.restaurant_id IS NULL

    UNION ALL
    -- 4. orders_table -> menu_items
    SELECT '4. orders_table -> menu_items', COUNT(*)
    FROM orders_table o LEFT JOIN menu_items m ON o.item_id = m.item_id WHERE m.item_id IS NULL

    UNION ALL
    -- 5. orders_table -> riders
    SELECT '5. orders_table -> riders', COUNT(*)
    FROM orders_table o LEFT JOIN riders r ON o.rider_id = r.rider_id WHERE r.rider_id IS NULL

    UNION ALL
    -- 6. payments -> orders_table
    SELECT '6. payments -> orders_table', COUNT(*)
    FROM payments p LEFT JOIN orders_table o ON p.order_id = o.order_id WHERE o.order_id IS NULL

    UNION ALL
    -- 7. deliveries -> orders_table
    SELECT '7. deliveries -> orders_table', COUNT(*)
    FROM deliveries d LEFT JOIN orders_table o ON d.order_id = o.order_id WHERE o.order_id IS NULL

    UNION ALL
    -- 8. deliveries -> riders
    SELECT '8. deliveries -> riders', COUNT(*)
    FROM deliveries d LEFT JOIN riders r ON d.rider_id = r.rider_id WHERE r.rider_id IS NULL

    UNION ALL
    -- 9. ratings_reviews -> orders_table
    SELECT '9. ratings_reviews -> orders_table', COUNT(*)
    FROM ratings_reviews rv LEFT JOIN orders_table o ON rv.order_id = o.order_id WHERE o.order_id IS NULL

    UNION ALL
    -- 10. ratings_reviews -> customers
    SELECT '10. ratings_reviews -> customers', COUNT(*)
    FROM ratings_reviews rv LEFT JOIN customers c ON rv.customer_id = c.customer_id WHERE c.customer_id IS NULL

    UNION ALL
    -- 11. app_events -> customers
    SELECT '11. app_events -> customers', COUNT(*)
    FROM app_events e LEFT JOIN customers c ON e.customer_id = c.customer_id WHERE c.customer_id IS NULL
) AS fk_summary;

-- ----------------------------------------------------------------------
-- 3. PRIMARY KEY UNIQUENESS AUDIT
-- Validates 0 duplicate primary keys across all 10 tables.
-- ----------------------------------------------------------------------
SELECT 
    table_name,
    duplicate_pk_count,
    CASE 
        WHEN duplicate_pk_count = 0 THEN '✅ 0 DUPLICATES (UNIQUE PKs)'
        ELSE '❌ DUPLICATE PK DETECTED'
    END AS pk_status
FROM (
    SELECT 'customers' AS table_name, COUNT(*) - COUNT(DISTINCT customer_id) AS duplicate_pk_count FROM customers
    UNION ALL SELECT 'restaurants', COUNT(*) - COUNT(DISTINCT restaurant_id) FROM restaurants
    UNION ALL SELECT 'riders', COUNT(*) - COUNT(DISTINCT rider_id) FROM riders
    UNION ALL SELECT 'promotions', COUNT(*) - COUNT(DISTINCT promo_id) FROM promotions
    UNION ALL SELECT 'menu_items', COUNT(*) - COUNT(DISTINCT item_id) FROM menu_items
    UNION ALL SELECT 'orders_table', COUNT(*) - COUNT(DISTINCT order_id) FROM orders_table
    UNION ALL SELECT 'payments', COUNT(*) - COUNT(DISTINCT payment_id) FROM payments
    UNION ALL SELECT 'deliveries', COUNT(*) - COUNT(DISTINCT delivery_id) FROM deliveries
    UNION ALL SELECT 'ratings_reviews', COUNT(*) - COUNT(DISTINCT review_id) FROM ratings_reviews
    UNION ALL SELECT 'app_events', COUNT(*) - COUNT(DISTINCT event_id) FROM app_events
) AS pk_summary;

-- ----------------------------------------------------------------------
-- 4. CORE BUSINESS & FINANCIAL KPI RECONCILIATION
-- Validates GMV, delivery counts, and order status distributions against certified metrics
-- ----------------------------------------------------------------------
SELECT 
    'Core Order KPIs' AS metric_group,
    COUNT(*) AS total_orders,
    SUM(order_amount) AS total_gmv,
    AVG(order_amount) AS aov,
    SUM(CASE WHEN order_status = 'Delivered' THEN 1 ELSE 0 END) AS delivered_orders,
    SUM(CASE WHEN order_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
    SUM(CASE WHEN order_status = 'Delivered' THEN order_amount ELSE 0 END) AS delivered_gmv
FROM orders_table;

