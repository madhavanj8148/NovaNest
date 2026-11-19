-- ======================================================================
-- NOVANEST RELATIONAL MIGRATION: DIRECT ALTER TABLE STATEMENTS
-- Target Database: novanest_db
-- Compatibility: Standard MySQL 8.0 DDL (Executes directly in MySQL Workbench)
-- Safety: Non-destructive (0 DROP, 0 TRUNCATE, 0 DELETE statements)
-- ======================================================================

USE novanest_db;

-- ----------------------------------------------------------------------
-- 1. APPLY 19 SECONDARY INDEXES
-- ----------------------------------------------------------------------
ALTER TABLE customers ADD INDEX idx_customers_city (city);
ALTER TABLE customers ADD INDEX idx_customers_signup (signup_date);

ALTER TABLE restaurants ADD INDEX idx_restaurants_city (city);
ALTER TABLE restaurants ADD INDEX idx_restaurants_cuisine (cuisine_type);

ALTER TABLE riders ADD INDEX idx_riders_city (city);

ALTER TABLE menu_items ADD INDEX idx_menu_restaurant (restaurant_id);

ALTER TABLE orders_table ADD INDEX idx_orders_customer (customer_id);
ALTER TABLE orders_table ADD INDEX idx_orders_restaurant (restaurant_id);
ALTER TABLE orders_table ADD INDEX idx_orders_rider (rider_id);
ALTER TABLE orders_table ADD INDEX idx_orders_item (item_id);
ALTER TABLE orders_table ADD INDEX idx_orders_datetime (order_datetime);
ALTER TABLE orders_table ADD INDEX idx_orders_status (order_status);

ALTER TABLE payments ADD INDEX idx_payments_order (order_id);

ALTER TABLE deliveries ADD INDEX idx_deliveries_order (order_id);
ALTER TABLE deliveries ADD INDEX idx_deliveries_rider (rider_id);

ALTER TABLE ratings_reviews ADD INDEX idx_reviews_order (order_id);
ALTER TABLE ratings_reviews ADD INDEX idx_reviews_customer (customer_id);

ALTER TABLE app_events ADD INDEX idx_events_customer (customer_id);
ALTER TABLE app_events ADD INDEX idx_events_type (event_type);

-- ----------------------------------------------------------------------
-- 2. APPLY 11 CANONICAL FOREIGN-KEY CONSTRAINTS
-- ----------------------------------------------------------------------
ALTER TABLE menu_items 
    ADD CONSTRAINT fk_menu_restaurant 
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id) 
    ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE orders_table 
    ADD CONSTRAINT fk_orders_customer 
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) 
    ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE orders_table 
    ADD CONSTRAINT fk_orders_restaurant 
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id) 
    ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE orders_table 
    ADD CONSTRAINT fk_orders_item 
    FOREIGN KEY (item_id) REFERENCES menu_items(item_id) 
    ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE orders_table 
    ADD CONSTRAINT fk_orders_rider 
    FOREIGN KEY (rider_id) REFERENCES riders(rider_id) 
    ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE payments 
    ADD CONSTRAINT fk_payments_order 
    FOREIGN KEY (order_id) REFERENCES orders_table(order_id) 
    ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE deliveries 
    ADD CONSTRAINT fk_deliveries_order 
    FOREIGN KEY (order_id) REFERENCES orders_table(order_id) 
    ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE deliveries 
    ADD CONSTRAINT fk_deliveries_rider 
    FOREIGN KEY (rider_id) REFERENCES riders(rider_id) 
    ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE ratings_reviews 
    ADD CONSTRAINT fk_reviews_order 
    FOREIGN KEY (order_id) REFERENCES orders_table(order_id) 
    ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE ratings_reviews 
    ADD CONSTRAINT fk_reviews_customer 
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) 
    ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE app_events 
    ADD CONSTRAINT fk_events_customer 
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) 
    ON DELETE RESTRICT ON UPDATE CASCADE;

-- ----------------------------------------------------------------------
-- 3. POST-MIGRATION VERIFICATION
-- ----------------------------------------------------------------------
SELECT 
    'POST-MIGRATION VERIFICATION' AS audit_stage,
    COUNT(*) AS registered_foreign_keys,
    CASE 
        WHEN COUNT(*) = 11 THEN '✅ ALL 11 CONSTRAINTS VERIFIED'
        ELSE '⚠️ MISMATCH DETECTED'
    END AS status
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'novanest_db' 
  AND REFERENCED_TABLE_NAME IS NOT NULL;

SELECT 
    TABLE_NAME AS child_table,
    COLUMN_NAME AS child_column,
    CONSTRAINT_NAME,
    REFERENCED_TABLE_NAME AS parent_table,
    REFERENCED_COLUMN_NAME AS parent_column
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'novanest_db' 
  AND REFERENCED_TABLE_NAME IS NOT NULL
ORDER BY child_table, CONSTRAINT_NAME;

