-- ======================================================================
-- NOVANEST LEAST-PRIVILEGE APPLICATION DATABASE USERS SETUP
-- Target Database: novanest_db
-- Compatibility: MySQL 8.0+
-- Security Policy: Role-Separated Least Privilege (0 Global / 0 Root Grants)
-- Execution: Run manually as 'root'@'localhost' in MySQL Workbench
-- ======================================================================

USE novanest_db;

-- ======================================================================
-- STAGE 1: CREATE LEAST-PRIVILEGE USERS SAFELY (IF NOT EXISTS)
-- ======================================================================

-- 1. Ingestion ETL User: Used strictly by python/load_mysql.py
-- Replace 'REPLACE_WITH_INGESTION_PASSWORD' with your secure password before execution
CREATE USER IF NOT EXISTS 'novanest_loader'@'localhost' 
    IDENTIFIED BY 'Chinnu@2311';

-- 2. Application Runtime User: Used strictly by FastAPI (api/) and Streamlit (streamlit_app/)
-- Replace 'REPLACE_WITH_APP_PASSWORD' with your secure password before execution
CREATE USER IF NOT EXISTS 'novanest_app'@'localhost' 
    IDENTIFIED BY 'Chinnu_2311';


-- ======================================================================
-- STAGE 2: GRANT STRICTLY SCOPED PERMISSIONS ON novanest_db
-- ======================================================================

-- 2.1 Ingestion ETL User Permissions:
-- Permitted: SELECT (check existing row counts), INSERT (bulk ingestion), UPDATE (status updates)
-- Denied: DROP, ALTER, CREATE, DELETE, TRUNCATE, GRANT OPTION, SUPER, FILE
GRANT SELECT, INSERT, UPDATE ON `novanest_db`.* TO 'novanest_loader'@'localhost';

-- 2.2 Application Runtime User Permissions:
-- Permitted: SELECT across all 10 tables for real-time analytics and KPI dashboards
-- Denied: All DDL statements, administrative grants, and master table writes
GRANT SELECT ON `novanest_db`.* TO 'novanest_app'@'localhost';

-- Optional: If the application needs to accept customer order placement or events:
GRANT INSERT, UPDATE ON `novanest_db`.`orders_table` TO 'novanest_app'@'localhost';
GRANT INSERT, UPDATE ON `novanest_db`.`payments` TO 'novanest_app'@'localhost';
GRANT INSERT, UPDATE ON `novanest_db`.`deliveries` TO 'novanest_app'@'localhost';
GRANT INSERT, UPDATE ON `novanest_db`.`ratings_reviews` TO 'novanest_app'@'localhost';
GRANT INSERT, UPDATE ON `novanest_db`.`app_events` TO 'novanest_app'@'localhost';

-- Apply updated privilege tables
FLUSH PRIVILEGES;


-- ======================================================================
-- STAGE 3: VERIFICATION QUERIES (RUN TO CONFIRM SETUP)
-- ======================================================================

-- 3.1 Confirm both users exist in mysql.user
SELECT 
    user, 
    host, 
    plugin, 
    account_locked, 
    password_expired 
FROM mysql.user 
WHERE user IN ('novanest_loader', 'novanest_app') 
ORDER BY user;

-- 3.2 Verify Grants for Ingestion User
SHOW GRANTS FOR 'novanest_loader'@'localhost';

-- 3.3 Verify Grants for Application Runtime User
SHOW GRANTS FOR 'novanest_app'@'localhost';
