-- ==============================================================================
-- NovaNest Database Schema Initialization (Docker Entrypoint)
-- Target Database: novanest_db
-- Character Set: utf8mb4 | Collation: utf8mb4_unicode_ci
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS novanest_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE novanest_db;

-- 1. Dimension Tables
CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    age INT,
    gender VARCHAR(20),
    city VARCHAR(50) NOT NULL,
    persona VARCHAR(50),
    occupation VARCHAR(100),
    signup_date DATE NOT NULL,
    subscription_type VARCHAR(20),
    acquisition_channel VARCHAR(100),
    INDEX idx_customers_city (city),
    INDEX idx_customers_signup (signup_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS restaurants (
    restaurant_id VARCHAR(20) PRIMARY KEY,
    restaurant_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    restaurant_type VARCHAR(50),
    cuisine_type VARCHAR(50),
    opening_year INT,
    avg_rating DECIMAL(3,1),
    delivery_radius_km DECIMAL(4,1),
    commission_percentage INT,
    INDEX idx_restaurants_city (city),
    INDEX idx_restaurants_cuisine (cuisine_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS riders (
    rider_id VARCHAR(20) PRIMARY KEY,
    rider_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    vehicle_type VARCHAR(50),
    experience_years INT,
    joining_year INT,
    shift_type VARCHAR(50),
    INDEX idx_riders_city (city)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS promotions (
    promo_id VARCHAR(20) PRIMARY KEY,
    promo_name VARCHAR(100) NOT NULL,
    promo_type VARCHAR(100),
    discount_percentage INT,
    campaign_budget INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Menu Items
CREATE TABLE IF NOT EXISTS menu_items (
    item_id VARCHAR(20) PRIMARY KEY,
    restaurant_id VARCHAR(20) NOT NULL,
    cuisine_type VARCHAR(50),
    item_name VARCHAR(100) NOT NULL,
    price INT NOT NULL,
    preparation_time INT,
    INDEX idx_menu_restaurant (restaurant_id),
    CONSTRAINT fk_menu_restaurant 
        FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Orders Core Transaction Table
CREATE TABLE IF NOT EXISTS orders_table (
    order_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    restaurant_id VARCHAR(20) NOT NULL,
    item_id VARCHAR(20) NOT NULL,
    rider_id VARCHAR(20) NOT NULL,
    order_datetime DATETIME NOT NULL,
    quantity INT NOT NULL,
    order_amount INT NOT NULL,
    discount_amount INT NOT NULL DEFAULT 0,
    delivery_fee INT NOT NULL DEFAULT 0,
    final_amount INT NOT NULL,
    order_status VARCHAR(20) NOT NULL,
    INDEX idx_orders_customer (customer_id),
    INDEX idx_orders_restaurant (restaurant_id),
    INDEX idx_orders_rider (rider_id),
    INDEX idx_orders_item (item_id),
    INDEX idx_orders_datetime (order_datetime),
    INDEX idx_orders_status (order_status),
    CONSTRAINT fk_orders_customer 
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_orders_restaurant 
        FOREIGN KEY (restaurant_id) REFERENCES restaurants(restaurant_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_orders_item 
        FOREIGN KEY (item_id) REFERENCES menu_items(item_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_orders_rider 
        FOREIGN KEY (rider_id) REFERENCES riders(rider_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Dependent Tables
CREATE TABLE IF NOT EXISTS payments (
    payment_id VARCHAR(20) PRIMARY KEY,
    order_id VARCHAR(20) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    payment_status VARCHAR(50) NOT NULL,
    INDEX idx_payments_order (order_id),
    CONSTRAINT fk_payments_order 
        FOREIGN KEY (order_id) REFERENCES orders_table(order_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS deliveries (
    delivery_id VARCHAR(20) PRIMARY KEY,
    order_id VARCHAR(20) NOT NULL,
    rider_id VARCHAR(20) NOT NULL,
    distance_km DECIMAL(4,1),
    delivery_duration INT,
    INDEX idx_deliveries_order (order_id),
    INDEX idx_deliveries_rider (rider_id),
    CONSTRAINT fk_deliveries_order 
        FOREIGN KEY (order_id) REFERENCES orders_table(order_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_deliveries_rider 
        FOREIGN KEY (rider_id) REFERENCES riders(rider_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS ratings_reviews (
    review_id VARCHAR(20) PRIMARY KEY,
    order_id VARCHAR(20) NOT NULL,
    customer_id VARCHAR(20) NOT NULL,
    restaurant_rating INT NOT NULL,
    delivery_rating INT NOT NULL,
    INDEX idx_reviews_order (order_id),
    INDEX idx_reviews_customer (customer_id),
    CONSTRAINT fk_reviews_order 
        FOREIGN KEY (order_id) REFERENCES orders_table(order_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_reviews_customer 
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS app_events (
    event_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    INDEX idx_events_customer (customer_id),
    INDEX idx_events_type (event_type),
    CONSTRAINT fk_events_customer 
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Canonical Backward Compatibility View
CREATE OR REPLACE VIEW orders AS 
SELECT * FROM orders_table;
