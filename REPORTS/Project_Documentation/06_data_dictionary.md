# NOVANEST — MASTER DATA DICTIONARY
**Complete Schema Documentation for all 10 Relational Entities**

---

### 1. Customers (`customers.csv` / `customers` table)
| Column Name | Data Type | Nullable | Primary/Foreign Key | Description & Examples |
| :--- | :--- | :--- | :--- | :--- |
| `customer_id` | VARCHAR(20) | NO | Primary Key | Unique customer ID (e.g., `C000001`) |
| `customer_name` | VARCHAR(100) | NO | None | Full customer name (generated via Faker India) |
| `age` | INT | NO | None | Customer age in years (18 to 65) |
| `gender` | VARCHAR(20) | NO | None | Male / Female |
| `city` | VARCHAR(50) | NO | None | Operating city (Chennai, Bangalore, Hyderabad, Coimbatore, Vijayawada) |
| `persona` | VARCHAR(50) | NO | None | Customer lifestyle persona (`Student`, `Working Professional`, `Family`) |
| `occupation` | VARCHAR(100) | NO | None | Job title / student status |
| `signup_date` | DATE | NO | None | Registration timestamp (`YYYY-MM-DD`) |
| `subscription_type`| VARCHAR(20)| NO | None | Platform tier (`Free` or `Premium`) |
| `acquisition_channel`| VARCHAR(100)| NO | None | Marketing source (`Instagram`, `Google`, `YouTube`, `Campus Campaign`, `Referral`) |

---

### 2. Restaurants (`restaurants.csv` / `restaurants` table)
| Column Name | Data Type | Nullable | Primary/Foreign Key | Description & Examples |
| :--- | :--- | :--- | :--- | :--- |
| `restaurant_id` | VARCHAR(20) | NO | Primary Key | Unique restaurant ID (e.g., `R00001`) |
| `restaurant_name` | VARCHAR(100) | NO | None | Restaurant business name |
| `city` | VARCHAR(50) | NO | None | Operating city location |
| `restaurant_type` | VARCHAR(50) | NO | None | Outlet category (`Cloud Kitchen`, `Premium Restaurant`, `Budget Restaurant`, `Cafe`, `Fast Food Chain`) |
| `cuisine_type` | VARCHAR(50) | NO | None | Primary cuisine (e.g., `Biryani`, `South Indian`, `Pizza`, `Chinese`) |
| `opening_year` | INT | NO | None | Year established (2015 to 2024) |
| `avg_rating` | DECIMAL(3,1)| NO | None | Historical average customer rating (1.0 to 5.0) |
| `delivery_radius_km`| DECIMAL(4,1)| NO | None | Serviceable delivery radius in kilometers (3.0 to 12.0) |
| `commission_percentage`| INT | NO | None | Contracted platform take rate commission (15% to 30%) |

---

### 3. Menu Items (`menu_items.csv` / `menu_items` table)
| Column Name | Data Type | Nullable | Primary/Foreign Key | Description & Examples |
| :--- | :--- | :--- | :--- | :--- |
| `item_id` | VARCHAR(20) | NO | Primary Key | Unique food item ID (e.g., `M000001`) |
| `restaurant_id` | VARCHAR(20) | NO | Foreign Key | References `restaurants.restaurant_id` |
| `cuisine_type` | VARCHAR(50) | NO | None | Cuisine classification |
| `item_name` | VARCHAR(100) | NO | None | Name of dish / beverage |
| `price` | INT | NO | None | Base menu item price in Indian Rupees (₹) |
| `preparation_time` | INT | NO | None | Average kitchen prep time in minutes (10 to 45 mins) |

---

### 4. Riders (`riders.csv` / `riders` table)
| Column Name | Data Type | Nullable | Primary/Foreign Key | Description & Examples |
| :--- | :--- | :--- | :--- | :--- |
| `rider_id` | VARCHAR(20) | NO | Primary Key | Unique delivery partner ID (e.g., `RD0001`) |
| `rider_name` | VARCHAR(100) | NO | None | Delivery partner full name |
| `city` | VARCHAR(50) | NO | None | Base operating city |
| `vehicle_type` | VARCHAR(50) | NO | None | Mode of transit (`Bike`, `Scooter`) |
| `experience_years` | INT | NO | None | Total delivery fleet experience (1 to 8 years) |
| `joining_year` | INT | NO | None | Year rider onboarded onto NovaNest |
| `shift_type` | VARCHAR(50) | NO | None | Working shift (`Day`, `Night`, `Peak Hours Only`) |

---

### 5. Orders (`orders.csv` / `orders_table`)
| Column Name | Data Type | Nullable | Primary/Foreign Key | Description & Examples |
| :--- | :--- | :--- | :--- | :--- |
| `order_id` | VARCHAR(20) | NO | Primary Key | Unique order transaction ID (e.g., `O0000001`) |
| `customer_id` | VARCHAR(20) | NO | Foreign Key | References `customers.customer_id` |
| `restaurant_id` | VARCHAR(20) | NO | Foreign Key | References `restaurants.restaurant_id` |
| `item_id` | VARCHAR(20) | NO | Foreign Key | References `menu_items.item_id` |
| `rider_id` | VARCHAR(20) | NO | Foreign Key | References `riders.rider_id` |
| `order_datetime` | DATETIME | NO | None | Timestamp when order was placed (`YYYY-MM-DD HH:MM:SS`) |
| `quantity` | INT | NO | None | Number of units ordered (1 to 5) |
| `order_amount` | INT | NO | None | Subtotal (`quantity * item_price`) in ₹ |
| `discount_amount`| INT | NO | None | Promotional discount deducted in ₹ |
| `delivery_fee` | INT | NO | None | Delivery surcharge charged to customer (₹20 to ₹60) |
| `final_amount` | INT | NO | None | Total amount paid (`order_amount - discount + delivery_fee`, min ₹50) |
| `order_status` | VARCHAR(20) | NO | None | Final fulfillment state (`Delivered`, `Cancelled`) |

---

### 6. Payments (`payments.csv` / `payments` table)
| Column Name | Data Type | Nullable | Primary/Foreign Key | Description & Examples |
| :--- | :--- | :--- | :--- | :--- |
| `payment_id` | VARCHAR(20) | NO | Primary Key | Unique transaction receipt ID (e.g., `P0000001`) |
| `order_id` | VARCHAR(20) | NO | Foreign Key | References `orders.order_id` |
| `payment_method` | VARCHAR(50) | NO | None | Channel (`UPI`, `Credit Card`, `Debit Card`, `Cash on Delivery`, `Net Banking`) |
| `payment_status` | VARCHAR(50) | NO | None | Gateway outcome (`Successful`, `Refunded`, `Failed`) |

---

### 7. Deliveries (`deliveries.csv` / `deliveries` table)
| Column Name | Data Type | Nullable | Primary/Foreign Key | Description & Examples |
| :--- | :--- | :--- | :--- | :--- |
| `delivery_id` | VARCHAR(20) | NO | Primary Key | Unique delivery leg ID (e.g., `D0000001`) |
| `order_id` | VARCHAR(20) | NO | Foreign Key | References `orders.order_id` |
| `rider_id` | VARCHAR(20) | NO | Foreign Key | References `riders.rider_id` |
| `distance_km` | DECIMAL(4,1)| NO | None | Transit distance from restaurant to customer in kilometers (1.0 to 15.0) |
| `delivery_duration`| INT | NO | None | Total elapsed fulfillment duration in minutes (15 to 65 mins) |

---

### 8. Ratings & Reviews (`ratings_reviews.csv` / `ratings_reviews` table)
| Column Name | Data Type | Nullable | Primary/Foreign Key | Description & Examples |
| :--- | :--- | :--- | :--- | :--- |
| `review_id` | VARCHAR(20) | NO | Primary Key | Unique customer feedback record ID |
| `order_id` | VARCHAR(20) | NO | Foreign Key | References `orders.order_id` |
| `customer_id` | VARCHAR(20) | NO | Foreign Key | References `customers.customer_id` |
| `restaurant_rating`| INT | NO | None | Food quality rating (1 to 5 stars) |
| `delivery_rating` | INT | NO | None | Rider service rating (1 to 5 stars) |

---

### 9. Promotions (`promotions.csv` / `promotions` table)
| Column Name | Data Type | Nullable | Primary/Foreign Key | Description & Examples |
| :--- | :--- | :--- | :--- | :--- |
| `promo_id` | VARCHAR(20) | NO | Primary Key | Unique discount campaign code (e.g., `PR0001`) |
| `promo_name` | VARCHAR(100) | NO | None | Campaign title |
| `promo_type` | VARCHAR(100) | NO | None | Mechanic (`Flat Discount`, `Percentage Discount`, `Free Delivery`, `Cashback`) |
| `discount_percentage`| INT | NO | None | Discount magnitude (5% to 40%) |
| `campaign_budget`| INT | NO | None | Marketing expenditure budget in ₹ (₹10,000 to ₹100,000) |

---

### 10. App Events (`app_events.csv` / `app_events` table)
| Column Name | Data Type | Nullable | Primary/Foreign Key | Description & Examples |
| :--- | :--- | :--- | :--- | :--- |
| `event_id` | VARCHAR(20) | NO | Primary Key | Unique clickstream session event ID (e.g., `E0000001`) |
| `customer_id` | VARCHAR(20) | NO | Foreign Key | References `customers.customer_id` |
| `event_type` | VARCHAR(50) | NO | None | Funnel stage (`App Open`, `Restaurant View`, `Menu View`, `Add To Cart`, `Checkout`, `Payment`, `Order Complete`) |
