-- ======================================================================
-- NOVANEST RELATIONAL MIGRATION: ADD FOREIGN KEYS & SECONDARY INDEXES
-- Target Database: novanest_db
-- Compatibility: MySQL 8.0+
-- Safety: Non-destructive (0 DROP, 0 TRUNCATE, 0 DELETE statements)
-- Idempotency: Supports safe execution on both unconstrained and constrained tables
-- ======================================================================

USE novanest_db;

-- ----------------------------------------------------------------------
-- 1. PRE-MIGRATION AUDIT: Check Existing Foreign Keys
-- ----------------------------------------------------------------------
SELECT 
    'PRE-MIGRATION CHECK' AS audit_stage,
    COUNT(*) AS existing_foreign_keys
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'novanest_db' 
  AND REFERENCED_TABLE_NAME IS NOT NULL;

-- ----------------------------------------------------------------------
-- 2. IDEMPOTENT PROCEDURE DEFINITIONS
-- ----------------------------------------------------------------------
DELIMITER $$

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
        SELECT CONCAT('✅ Created foreign key: ', p_constraint_name, ' on ', p_table_name) AS status;
    ELSE
        SELECT CONCAT('ℹ️ Foreign key already exists: ', p_constraint_name, ' on ', p_table_name) AS status;
    END IF;
END $$

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
        SELECT CONCAT('✅ Created index: ', p_index_name, ' on ', p_table_name) AS status;
    ELSE
        SELECT CONCAT('ℹ️ Index already exists: ', p_index_name, ' on ', p_table_name) AS status;
    END IF;
END $$

DELIMITER ;

-- ----------------------------------------------------------------------
-- 3. APPLY 19 SECONDARY PERFORMANCE INDEXES
-- ----------------------------------------------------------------------
CALL AddIndexIfNotExists('customers', 'idx_customers_city', 'city');
CALL AddIndexIfNotExists('customers', 'idx_customers_signup', 'signup_date');

CALL AddIndexIfNotExists('restaurants', 'idx_restaurants_city', 'city');
CALL AddIndexIfNotExists('restaurants', 'idx_restaurants_cuisine', 'cuisine_type');

CALL AddIndexIfNotExists('riders', 'idx_riders_city', 'city');

CALL AddIndexIfNotExists('menu_items', 'idx_menu_restaurant', 'restaurant_id');

CALL AddIndexIfNotExists('orders_table', 'idx_orders_customer', 'customer_id');
CALL AddIndexIfNotExists('orders_table', 'idx_orders_restaurant', 'restaurant_id');
CALL AddIndexIfNotExists('orders_table', 'idx_orders_rider', 'rider_id');
CALL AddIndexIfNotExists('orders_table', 'idx_orders_item', 'item_id');
CALL AddIndexIfNotExists('orders_table', 'idx_orders_datetime', 'order_datetime');
CALL AddIndexIfNotExists('orders_table', 'idx_orders_status', 'order_status');

CALL AddIndexIfNotExists('payments', 'idx_payments_order', 'order_id');

CALL AddIndexIfNotExists('deliveries', 'idx_deliveries_order', 'order_id');
CALL AddIndexIfNotExists('deliveries', 'idx_deliveries_rider', 'rider_id');

CALL AddIndexIfNotExists('ratings_reviews', 'idx_reviews_order', 'order_id');
CALL AddIndexIfNotExists('ratings_reviews', 'idx_reviews_customer', 'customer_id');

CALL AddIndexIfNotExists('app_events', 'idx_events_customer', 'customer_id');
CALL AddIndexIfNotExists('app_events', 'idx_events_type', 'event_type');

-- ----------------------------------------------------------------------
-- 4. APPLY 11 CANONICAL FOREIGN-KEY CONSTRAINTS
-- ----------------------------------------------------------------------
-- 1. Menu Items -> Restaurants
CALL AddForeignKeyIfNotExists('menu_items', 'fk_menu_restaurant', 'restaurant_id', 'restaurants', 'restaurant_id');

-- 2. Orders -> Customers
CALL AddForeignKeyIfNotExists('orders_table', 'fk_orders_customer', 'customer_id', 'customers', 'customer_id');

-- 3. Orders -> Restaurants
CALL AddForeignKeyIfNotExists('orders_table', 'fk_orders_restaurant', 'restaurant_id', 'restaurants', 'restaurant_id');

-- 4. Orders -> Menu Items
CALL AddForeignKeyIfNotExists('orders_table', 'fk_orders_item', 'item_id', 'menu_items', 'item_id');

-- 5. Orders -> Riders
CALL AddForeignKeyIfNotExists('orders_table', 'fk_orders_rider', 'rider_id', 'riders', 'rider_id');

-- 6. Payments -> Orders
CALL AddForeignKeyIfNotExists('payments', 'fk_payments_order', 'order_id', 'orders_table', 'order_id');

-- 7. Deliveries -> Orders
CALL AddForeignKeyIfNotExists('deliveries', 'fk_deliveries_order', 'order_id', 'orders_table', 'order_id');

-- 8. Deliveries -> Riders
CALL AddForeignKeyIfNotExists('deliveries', 'fk_deliveries_rider', 'rider_id', 'riders', 'rider_id');

-- 9. Reviews -> Orders
CALL AddForeignKeyIfNotExists('ratings_reviews', 'fk_reviews_order', 'order_id', 'orders_table', 'order_id');

-- 10. Reviews -> Customers
CALL AddForeignKeyIfNotExists('ratings_reviews', 'fk_reviews_customer', 'customer_id', 'customers', 'customer_id');

-- 11. App Events -> Customers
CALL AddForeignKeyIfNotExists('app_events', 'fk_events_customer', 'customer_id', 'customers', 'customer_id');

-- ----------------------------------------------------------------------
-- 5. CLEAN UP HELPER PROCEDURES
-- ----------------------------------------------------------------------
DROP PROCEDURE IF EXISTS AddForeignKeyIfNotExists;
DROP PROCEDURE IF EXISTS AddIndexIfNotExists;

-- ----------------------------------------------------------------------
-- 6. POST-MIGRATION VERIFICATION AUDIT
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

-- Detail breakdown of all registered foreign keys
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

