-- ==============================================================================
-- NovaNest Least-Privilege Users Initialization (Docker Entrypoint)
-- Note: User passwords are automatically managed by MySQL entrypoint environment
-- variables (MYSQL_USER, MYSQL_PASSWORD). This script enforces least privilege grants.
-- ==============================================================================

USE novanest_db;

-- 1. Ingestion ETL User (Least-privilege: SELECT, INSERT, UPDATE)
CREATE USER IF NOT EXISTS 'novanest_loader'@'%' IDENTIFIED BY 'REPLACE_WITH_INGESTION_PASSWORD';
CREATE USER IF NOT EXISTS 'novanest_loader'@'localhost' IDENTIFIED BY 'REPLACE_WITH_INGESTION_PASSWORD';
GRANT SELECT, INSERT, UPDATE ON `novanest_db`.* TO 'novanest_loader'@'%';
GRANT SELECT, INSERT, UPDATE ON `novanest_db`.* TO 'novanest_loader'@'localhost';

-- 2. Application Runtime User (FastAPI & Streamlit: Read-only SELECT + Operational event writes)
CREATE USER IF NOT EXISTS 'novanest_app'@'%' IDENTIFIED BY 'REPLACE_WITH_APP_PASSWORD';
CREATE USER IF NOT EXISTS 'novanest_app'@'localhost' IDENTIFIED BY 'REPLACE_WITH_APP_PASSWORD';
GRANT SELECT ON `novanest_db`.* TO 'novanest_app'@'%';
GRANT SELECT ON `novanest_db`.* TO 'novanest_app'@'localhost';

-- Table-level write permissions for transaction processing
GRANT INSERT, UPDATE ON `novanest_db`.`orders_table` TO 'novanest_app'@'%';
GRANT INSERT, UPDATE ON `novanest_db`.`orders_table` TO 'novanest_app'@'localhost';
GRANT INSERT, UPDATE ON `novanest_db`.`payments` TO 'novanest_app'@'%';
GRANT INSERT, UPDATE ON `novanest_db`.`payments` TO 'novanest_app'@'localhost';
GRANT INSERT, UPDATE ON `novanest_db`.`deliveries` TO 'novanest_app'@'%';
GRANT INSERT, UPDATE ON `novanest_db`.`deliveries` TO 'novanest_app'@'localhost';
GRANT INSERT, UPDATE ON `novanest_db`.`ratings_reviews` TO 'novanest_app'@'%';
GRANT INSERT, UPDATE ON `novanest_db`.`ratings_reviews` TO 'novanest_app'@'localhost';
GRANT INSERT, UPDATE ON `novanest_db`.`app_events` TO 'novanest_app'@'%';
GRANT INSERT, UPDATE ON `novanest_db`.`app_events` TO 'novanest_app'@'localhost';

-- Apply privilege tables
FLUSH PRIVILEGES;
