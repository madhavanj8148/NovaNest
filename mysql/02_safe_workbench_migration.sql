-- ======================================================================
-- NOVANEST CANONICAL RELATIONAL MIGRATION FOR MYSQL WORKBENCH
-- Target Database: novanest_db
-- Storage Engine: InnoDB (Strictly Required for Foreign Keys)
-- Execution Mode: Multi-Stage, Fully Idempotent, Safe for Repeat & Partial Runs
-- Safety: Non-destructive (0 DROP TABLE, 0 TRUNCATE, 0 DELETE statements)
-- Integrity: Enforces 11 Foreign Keys and 19 Secondary Performance Indexes
-- ======================================================================

USE novanest_db;

-- ======================================================================
-- STAGE 1: PRE-MIGRATION HEALTH, ENGINE & CONSTRAINT AUDIT
-- (Can be executed independently to inspect current database state)
-- ======================================================================

-- 1.1 Verify all 10 tables exist and all use the InnoDB storage engine
SELECT 
    TABLE_NAME,
    ENGINE,
    TABLE_ROWS,
    TABLE_COLLATION
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'novanest_db'
ORDER BY TABLE_NAME;

-- 1.2 Verify table count and InnoDB engine compliance
SELECT 
    COUNT(*) AS total_tables_found,
    SUM(CASE WHEN ENGINE = 'InnoDB' THEN 1 ELSE 0 END) AS innodb_tables_count,
    CASE 
        WHEN COUNT(*) = 10 AND SUM(CASE WHEN ENGINE = 'InnoDB' THEN 1 ELSE 0 END) = 10 
        THEN '✅ ALL 10 TABLES INNODB COMPLIANT — SAFE TO PROCEED'
        ELSE '⚠️ TABLE COUNT OR ENGINE MISMATCH DETECTED'
    END AS pre_migration_engine_status
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'novanest_db';

-- 1.3 Audit existing foreign keys prior to migration
SELECT 
    'PRE-MIGRATION FOREIGN KEY AUDIT' AS audit_stage,
    COUNT(*) AS registered_foreign_keys
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'novanest_db' 
  AND REFERENCED_TABLE_NAME IS NOT NULL;


-- ======================================================================
-- STAGE 2: IDEMPOTENT DDL PROCEDURES INITIALIZATION
-- (Handles conditional execution to prevent Duplicate Key / Duplicate Constraint errors)
-- ======================================================================

DELIMITER $$

DROP PROCEDURE IF EXISTS AddIndexIfNotExists $$
CREATE PROCEDURE AddIndexIfNotExists(
    IN p_table_name VARCHAR(64),
    IN p_index_name VARCHAR(64),
    IN p_columns VARCHAR(255)
)
BEGIN
    DECLARE v_exists INT DEFAULT 0;
    
    SELECT COUNT(*) INTO v_exists
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = 'novanest_db'
      AND TABLE_NAME = p_table_name
      AND INDEX_NAME = p_index_name;

    IF v_exists = 0 THEN
        SET @sql = CONCAT('ALTER TABLE `novanest_db`.`', p_table_name, '` ADD INDEX `', p_index_name, '` (', p_columns, ');');
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
        SELECT CONCAT('✅ Created index: ', p_index_name, ' on table ', p_table_name) AS operation_status;
    ELSE
        SELECT CONCAT('ℹ️ Index already exists (skipped): ', p_index_name, ' on table ', p_table_name) AS operation_status;
    END IF;
END $$

DROP PROCEDURE IF EXISTS AddForeignKeyIfNotExists $$
CREATE PROCEDURE AddForeignKeyIfNotExists(
    IN p_table_name VARCHAR(64),
    IN p_constraint_name VARCHAR(64),
    IN p_child_col VARCHAR(64),
    IN p_parent_table VARCHAR(64),
    IN p_parent_col VARCHAR(64)
)
BEGIN
    DECLARE v_exists INT DEFAULT 0;
    
    SELECT COUNT(*) INTO v_exists
    FROM information_schema.TABLE_CONSTRAINTS
    WHERE CONSTRAINT_SCHEMA = 'novanest_db'
      AND TABLE_NAME = p_table_name
      AND CONSTRAINT_NAME = p_constraint_name
      AND CONSTRAINT_TYPE = 'FOREIGN KEY';

    IF v_exists = 0 THEN
        SET @sql = CONCAT(
            'ALTER TABLE `novanest_db`.`', p_table_name, '` ',
            'ADD CONSTRAINT `', p_constraint_name, '` ',
            'FOREIGN KEY (`', p_child_col, '`) ',
            'REFERENCES `novanest_db`.`', p_parent_table, '` (`', p_parent_col, '`) ',
            'ON DELETE RESTRICT ON UPDATE CASCADE;'
        );
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
        SELECT CONCAT('✅ Created foreign key: ', p_constraint_name, ' on table ', p_table_name) AS operation_status;
    ELSE
        SELECT CONCAT('ℹ️ Foreign key already exists (skipped): ', p_constraint_name, ' on table ', p_table_name) AS operation_status;
    END IF;
END $$

DELIMITER ;


-- ======================================================================
-- STAGE 3: APPLY 19 SECONDARY PERFORMANCE INDEXES
-- (Executed before foreign keys so MySQL binds FK constraints directly to named indexes)
-- ======================================================================

-- 3.1 Dimension Table Indexes
CALL AddIndexIfNotExists('customers', 'idx_customers_city', 'city');
CALL AddIndexIfNotExists('customers', 'idx_customers_signup', 'signup_date');

CALL AddIndexIfNotExists('restaurants', 'idx_restaurants_city', 'city');
CALL AddIndexIfNotExists('restaurants', 'idx_restaurants_cuisine', 'cuisine_type');

CALL AddIndexIfNotExists('riders', 'idx_riders_city', 'city');

-- 3.2 Menu Items Indexes
CALL AddIndexIfNotExists('menu_items', 'idx_menu_restaurant', 'restaurant_id');

-- 3.3 Orders Transaction Table Indexes
CALL AddIndexIfNotExists('orders_table', 'idx_orders_customer', 'customer_id');
CALL AddIndexIfNotExists('orders_table', 'idx_orders_restaurant', 'restaurant_id');
CALL AddIndexIfNotExists('orders_table', 'idx_orders_rider', 'rider_id');
CALL AddIndexIfNotExists('orders_table', 'idx_orders_item', 'item_id');
CALL AddIndexIfNotExists('orders_table', 'idx_orders_datetime', 'order_datetime');
CALL AddIndexIfNotExists('orders_table', 'idx_orders_status', 'order_status');

-- 3.4 Payments Table Indexes
CALL AddIndexIfNotExists('payments', 'idx_payments_order', 'order_id');

-- 3.5 Deliveries Table Indexes
CALL AddIndexIfNotExists('deliveries', 'idx_deliveries_order', 'order_id');
CALL AddIndexIfNotExists('deliveries', 'idx_deliveries_rider', 'rider_id');

-- 3.6 Ratings Reviews Table Indexes
CALL AddIndexIfNotExists('ratings_reviews', 'idx_reviews_order', 'order_id');
CALL AddIndexIfNotExists('ratings_reviews', 'idx_reviews_customer', 'customer_id');

-- 3.7 App Events Table Indexes
CALL AddIndexIfNotExists('app_events', 'idx_events_customer', 'customer_id');
CALL AddIndexIfNotExists('app_events', 'idx_events_type', 'event_type');


-- ======================================================================
-- STAGE 4: APPLY 11 CANONICAL FOREIGN-KEY CONSTRAINTS
-- (All referential actions use ON DELETE RESTRICT ON UPDATE CASCADE)
-- ======================================================================

-- 4.1 Menu Items -> Restaurants (1:N)
CALL AddForeignKeyIfNotExists('menu_items', 'fk_menu_restaurant', 'restaurant_id', 'restaurants', 'restaurant_id');

-- 4.2 Orders -> Customers (1:N)
CALL AddForeignKeyIfNotExists('orders_table', 'fk_orders_customer', 'customer_id', 'customers', 'customer_id');

-- 4.3 Orders -> Restaurants (1:N)
CALL AddForeignKeyIfNotExists('orders_table', 'fk_orders_restaurant', 'restaurant_id', 'restaurants', 'restaurant_id');

-- 4.4 Orders -> Menu Items (1:N)
CALL AddForeignKeyIfNotExists('orders_table', 'fk_orders_item', 'item_id', 'menu_items', 'item_id');

-- 4.5 Orders -> Riders (1:N)
CALL AddForeignKeyIfNotExists('orders_table', 'fk_orders_rider', 'rider_id', 'riders', 'rider_id');

-- 4.6 Payments -> Orders (1:1 / 1:N)
CALL AddForeignKeyIfNotExists('payments', 'fk_payments_order', 'order_id', 'orders_table', 'order_id');

-- 4.7 Deliveries -> Orders (1:1)
CALL AddForeignKeyIfNotExists('deliveries', 'fk_deliveries_order', 'order_id', 'orders_table', 'order_id');

-- 4.8 Deliveries -> Riders (1:N)
CALL AddForeignKeyIfNotExists('deliveries', 'fk_deliveries_rider', 'rider_id', 'riders', 'rider_id');

-- 4.9 Reviews -> Orders (1:1)
CALL AddForeignKeyIfNotExists('ratings_reviews', 'fk_reviews_order', 'order_id', 'orders_table', 'order_id');

-- 4.10 Reviews -> Customers (1:N)
CALL AddForeignKeyIfNotExists('ratings_reviews', 'fk_reviews_customer', 'customer_id', 'customers', 'customer_id');

-- 4.11 App Events -> Customers (1:N)
CALL AddForeignKeyIfNotExists('app_events', 'fk_events_customer', 'customer_id', 'customers', 'customer_id');


-- ======================================================================
-- STAGE 5: TEMPORARY PROCEDURE CLEANUP
-- (Removes transient helper routines so novanest_db remains strictly clean)
-- ======================================================================

DROP PROCEDURE IF EXISTS AddForeignKeyIfNotExists;
DROP PROCEDURE IF EXISTS AddIndexIfNotExists;


-- ======================================================================
-- STAGE 6: POST-MIGRATION CERTIFICATION & DETAILED VERIFICATION
-- (Run to certify that all 11 foreign keys and 19 secondary indexes are registered)
-- ======================================================================

-- 6.1 Foreign Key Certification Summary
SELECT 
    'POST-MIGRATION CERTIFICATION' AS audit_stage,
    COUNT(*) AS registered_foreign_keys,
    CASE 
        WHEN COUNT(*) = 11 THEN '✅ ALL 11 CANONICAL FOREIGN KEYS VERIFIED (SUCCESS)'
        ELSE '⚠️ FOREIGN KEY COUNT MISMATCH — INSPECT DETAILED BREAKDOWN BELOW'
    END AS certification_status
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'novanest_db' 
  AND REFERENCED_TABLE_NAME IS NOT NULL;

-- 6.2 Secondary Indexes Certification Summary
SELECT 
    'POST-MIGRATION INDEXES AUDIT' AS audit_stage,
    COUNT(DISTINCT INDEX_NAME) AS total_named_indexes,
    CASE 
        WHEN COUNT(DISTINCT INDEX_NAME) >= 20 THEN '✅ ALL SECONDARY INDEXES VERIFIED (SUCCESS)'
        ELSE '⚠️ INDEX COUNT MISMATCH'
    END AS index_status
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'novanest_db';

-- 6.3 Complete Mapping of All 11 Registered Foreign Keys
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

