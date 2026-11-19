# NOVANEST — COMPLETE TECHNICAL REFERENCE MANUAL
## Comprehensive System Specifications, Schemas, API Catalogs, Agent Definitions, ML Model Cards & Operations

---

### Executive Overview & Purpose
This technical reference manual provides the definitive engineering specification for the NovaNest platform. It documents:
- **Database Schema**: All 10 relational tables in 3NF, data types, keys, constraints, and indexes.
- **API Catalog**: All 48 REST endpoints, HTTP methods, paths, RBAC scopes, payloads, and response contracts.
- **AI Agent Specifications**: Complete architectural profiles, prompt boundaries, tools, and contracts for all 5 domain agents and orchestrators.
- **Machine Learning Model Cards**: Model architectures, features, hyperparameters, empirical holdout evaluations, calibration, and gating classifications.
- **Frontend & UI Component Catalog**: React 18 component structure, design tokens, and Streamlit page architecture.
- **Configuration & Environment Reference**: Exhaustive reference of environment variables, secrets, and connection strings.
- **Container Architecture**: Docker services, network topologies, volume persistence, and health probes.
- **CLI & Automation Script Guide**: Operational, backup, migration, and maintenance shell and Python utilities.

---

## 1. Database Schema Reference (MySQL 8.0 / 3NF)

The database schema (`novanest_db`) is normalized to Third Normal Form (3NF), guaranteeing data integrity across **304,405 records**.

### 1.1 Summary of Relational Tables

| Table Name | Entity Classification | Primary Key | Foreign Keys | Row Count | Primary Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `customers` | Master Dimension | `customer_id` | None | 5,000 | Customer demographic, persona, and subscription profiles |
| `restaurants` | Master Dimension | `restaurant_id` | None | 1,500 | Restaurant partner attributes, commission rates, and cuisines |
| `riders` | Master Dimension | `rider_id` | None | 4,000 | Delivery fleet profiles, vehicle types, and shift schedules |
| `promotions` | Reference Dimension | `promo_id` | None | 200 | Marketing campaigns, discount percentages, and budgets |
| `menu_items` | Master Dimension | `item_id` | `restaurant_id` | 15,000 | Dish catalog, preparation times, and retail pricing |
| `orders_table` | Core Transaction Fact | `order_id` | `customer_id`, `restaurant_id`, `item_id`, `rider_id` | 49,971 | Core order transactional log and financial totals |
| `payments` | Dependent Transaction | `payment_id` | `order_id` | 49,971 | Payment settlement methods, transaction IDs, and statuses |
| `deliveries` | Dependent Transaction | `delivery_id` | `order_id`, `rider_id` | 49,971 | Last-mile delivery tracking, distance, and duration |
| `ratings_reviews`| Dependent Dimension | `review_id` | `order_id`, `customer_id` | 28,792 | Customer satisfaction ratings for food and delivery |
| `app_events` | Behavioral Fact | `event_id` | `customer_id` | 100,000 | Mobile clickstream telemetry and engagement events |
| **Total** | **10 Tables** | — | — | **304,405** | **Complete Relational Ecosystem** |

*Note: A canonical backward-compatibility view `orders` is maintained over `orders_table`.*

---

### 1.2 Table Specifications

#### Table: `customers` (5,000 Rows)
- **Engine**: InnoDB | **Charset**: utf8mb4 | **Collation**: utf8mb4_unicode_ci
- **Columns**:
  - `customer_id` (VARCHAR(20), PRIMARY KEY): Unique customer identifier (e.g., `CUST_00001`).
  - `customer_name` (VARCHAR(100), NOT NULL): Full legal name of the user.
  - `age` (INT): Customer age (range 18–70).
  - `gender` (VARCHAR(20)): User gender classification (`Male`, `Female`, `Non-Binary`).
  - `city` (VARCHAR(50), NOT NULL): Metropolitan operational city (e.g., `Mumbai`, `Delhi`, `Bangalore`).
  - `persona` (VARCHAR(50)): Behavioral demographic segment (e.g., `College Student`, `Working Professional`).
  - `occupation` (VARCHAR(100)): Professional employment domain.
  - `signup_date` (DATE, NOT NULL): Date of user account registration.
  - `subscription_type` (VARCHAR(20)): Loyalty membership tier (`None`, `Gold`, `Platinum`).
  - `acquisition_channel` (VARCHAR(100)): Marketing attribution source (e.g., `Organic`, `Instagram Ads`).
- **Indexes**: `PRIMARY (customer_id)`, `idx_customers_city (city)`, `idx_customers_signup (signup_date)`.

#### Table: `restaurants` (1,500 Rows)
- **Engine**: InnoDB | **Charset**: utf8mb4 | **Collation**: utf8mb4_unicode_ci
- **Columns**:
  - `restaurant_id` (VARCHAR(20), PRIMARY KEY): Unique partner identifier (e.g., `REST_0001`).
  - `restaurant_name` (VARCHAR(100), NOT NULL): Commercial business name.
  - `city` (VARCHAR(50), NOT NULL): Operating metropolitan market.
  - `restaurant_type` (VARCHAR(50)): Establishment tier (`Casual Dining`, `QSR`, `Fine Dining`, `Cloud Kitchen`).
  - `cuisine_type` (VARCHAR(50)): Primary culinary category (`North Indian`, `Chinese`, `South Indian`, `Continental`, `Biryani`).
  - `opening_year` (INT): Commercial inception year (2010–2023).
  - `avg_rating` (DECIMAL(3,1)): Historical aggregate customer rating (1.0 to 5.0).
  - `delivery_radius_km` (DECIMAL(4,1)): Service coverage radius in kilometers (3.0 to 15.0 km).
  - `commission_percentage` (INT): Contractual platform take rate percentage (range 15% to 30%).
- **Indexes**: `PRIMARY (restaurant_id)`, `idx_restaurants_city (city)`, `idx_restaurants_cuisine (cuisine_type)`.

#### Table: `riders` (4,000 Rows)
- **Engine**: InnoDB | **Charset**: utf8mb4 | **Collation**: utf8mb4_unicode_ci
- **Columns**:
  - `rider_id` (VARCHAR(20), PRIMARY KEY): Unique delivery partner identifier (e.g., `RIDER_0001`).
  - `rider_name` (VARCHAR(100), NOT NULL): Full delivery partner name.
  - `city` (VARCHAR(50), NOT NULL): Operational delivery zone/city.
  - `vehicle_type` (VARCHAR(50)): Transportation mode (`Motorcycle`, `Electric Scooter`, `Bicycle`).
  - `experience_years` (INT): Professional delivery experience in years.
  - `joining_year` (INT): Year onboarded to platform.
  - `shift_type` (VARCHAR(50)): Primary duty schedule (`Morning`, `Evening`, `Night`, `Full-Time`).
- **Indexes**: `PRIMARY (rider_id)`, `idx_riders_city (city)`.

#### Table: `promotions` (200 Rows)
- **Engine**: InnoDB | **Charset**: utf8mb4 | **Collation**: utf8mb4_unicode_ci
- **Columns**:
  - `promo_id` (VARCHAR(20), PRIMARY KEY): Unique marketing campaign code.
  - `promo_name` (VARCHAR(100), NOT NULL): Descriptive campaign title.
  - `promo_type` (VARCHAR(100)): Structure (`Flat Discount`, `Percentage Off`, `Free Delivery`).
  - `discount_percentage` (INT): Nominal discount rate applied (10% to 50%).
  - `campaign_budget` (INT): Approved marketing expenditure limit (₹).
- **Indexes**: `PRIMARY (promo_id)`.

#### Table: `menu_items` (15,000 Rows)
- **Engine**: InnoDB | **Charset**: utf8mb4 | **Collation**: utf8mb4_unicode_ci
- **Columns**:
  - `item_id` (VARCHAR(20), PRIMARY KEY): Unique dish catalog identifier.
  - `restaurant_id` (VARCHAR(20), NOT NULL, FK): Reference to `restaurants.restaurant_id`.
  - `cuisine_type` (VARCHAR(50)): Cuisine category of item.
  - `item_name` (VARCHAR(100), NOT NULL): Commercial dish title.
  - `price` (INT, NOT NULL): Base retail list price (₹).
  - `preparation_time` (INT): Standard kitchen preparation duration in minutes (10 to 45 min).
- **Indexes**: `PRIMARY (item_id)`, `idx_menu_restaurant (restaurant_id)`.
- **Foreign Key**: `fk_menu_restaurant` -> `restaurants(restaurant_id)` ON UPDATE CASCADE ON DELETE RESTRICT.

#### Table: `orders_table` (49,971 Rows)
- **Engine**: InnoDB | **Charset**: utf8mb4 | **Collation**: utf8mb4_unicode_ci
- **Columns**:
  - `order_id` (VARCHAR(20), PRIMARY KEY): Unique order transaction identifier (e.g., `ORD_000001`).
  - `customer_id` (VARCHAR(20), NOT NULL, FK): Reference to `customers.customer_id`.
  - `restaurant_id` (VARCHAR(20), NOT NULL, FK): Reference to `restaurants.restaurant_id`.
  - `item_id` (VARCHAR(20), NOT NULL, FK): Reference to `menu_items.item_id`.
  - `rider_id` (VARCHAR(20), NOT NULL, FK): Reference to `riders.rider_id`.
  - `order_datetime` (DATETIME, NOT NULL): UTC/IST timestamp of order placement.
  - `quantity` (INT, NOT NULL): Number of units ordered (1 to 8).
  - `order_amount` (INT, NOT NULL): Gross item value prior to discounts (₹).
  - `discount_amount` (INT, NOT NULL, DEFAULT 0): Promotional discount deducted (₹).
  - `delivery_fee` (INT, NOT NULL, DEFAULT 0): Consumer delivery surcharge (₹).
  - `final_amount` (INT, NOT NULL): Net transaction billing amount to customer (₹).
  - `order_status` (VARCHAR(20), NOT NULL): Order fulfillment state (`Delivered` [47,994], `Cancelled` [1,977]).
- **Indexes**: `PRIMARY (order_id)`, `idx_orders_customer`, `idx_orders_restaurant`, `idx_orders_rider`, `idx_orders_item`, `idx_orders_datetime`, `idx_orders_status`.
- **Foreign Keys**: Cascading constraints linking customer, restaurant, menu item, and rider.

#### Table: `payments` (49,971 Rows)
- **Engine**: InnoDB | **Charset**: utf8mb4 | **Collation**: utf8mb4_unicode_ci
- **Columns**:
  - `payment_id` (VARCHAR(20), PRIMARY KEY): Unique payment transaction receipt ID.
  - `order_id` (VARCHAR(20), NOT NULL, FK): Reference to `orders_table.order_id`.
  - `payment_method` (VARCHAR(50), NOT NULL): Instrument (`UPI`, `Credit Card`, `Debit Card`, `Cash on Delivery`, `Digital Wallet`).
  - `payment_status` (VARCHAR(50), NOT NULL): Gateway settlement outcome (`Successful`, `Failed`, `Refunded`).
- **Indexes**: `PRIMARY (payment_id)`, `idx_payments_order (order_id)`.

#### Table: `deliveries` (49,971 Rows)
- **Engine**: InnoDB | **Charset**: utf8mb4 | **Collation**: utf8mb4_unicode_ci
- **Columns**:
  - `delivery_id` (VARCHAR(20), PRIMARY KEY): Delivery tracking record ID.
  - `order_id` (VARCHAR(20), NOT NULL, FK): Reference to `orders_table.order_id`.
  - `rider_id` (VARCHAR(20), NOT NULL, FK): Reference to `riders.rider_id`.
  - `distance_km` (DECIMAL(4,1)): Geospatial delivery distance (1.0 to 18.5 km).
  - `delivery_duration` (INT): Total transit duration from restaurant dispatch to customer handover in minutes (12 to 85 min).
- **Indexes**: `PRIMARY (delivery_id)`, `idx_deliveries_order (order_id)`, `idx_deliveries_rider (rider_id)`.

#### Table: `ratings_reviews` (28,792 Rows)
- **Engine**: InnoDB | **Charset**: utf8mb4 | **Collation**: utf8mb4_unicode_ci
- **Columns**:
  - `review_id` (VARCHAR(20), PRIMARY KEY): Feedback tracking identifier.
  - `order_id` (VARCHAR(20), NOT NULL, FK): Associated order transaction.
  - `customer_id` (VARCHAR(20), NOT NULL, FK): Submitting customer.
  - `restaurant_rating` (INT, NOT NULL): Culinary rating (integer scale 1 to 5).
  - `delivery_rating` (INT, NOT NULL): Courier rating (integer scale 1 to 5).
- **Indexes**: `PRIMARY (review_id)`, `idx_reviews_order (order_id)`, `idx_reviews_customer (customer_id)`.

#### Table: `app_events` (100,000 Rows)
- **Engine**: InnoDB | **Charset**: utf8mb4 | **Collation**: utf8mb4_unicode_ci
- **Columns**:
  - `event_id` (VARCHAR(20), PRIMARY KEY): Telemetry event identifier.
  - `customer_id` (VARCHAR(20), NOT NULL, FK): Active session customer.
  - `event_type` (VARCHAR(50), NOT NULL): Behavioral event name (`app_open`, `search_restaurant`, `view_item`, `add_to_cart`, `checkout_start`, `payment_success`, `order_cancel`).
- **Indexes**: `PRIMARY (event_id)`, `idx_events_customer (customer_id)`, `idx_events_type (event_type)`.

---

## 2. API Route Reference (48 Endpoints)

The FastAPI server provides 48 REST and streaming endpoints organized into modular functional groups.

### 2.1 Security & Role Scopes
- **`public`**: Unauthenticated endpoints (Health probes).
- **`read` / `viewer`**: Read-only business data access.
- **`operator`**: Operational execution, simulations, and sensitive pagination.
- **`admin`**: Administrative control, backup execution, cache flushing, and model retraining.

### 2.2 Endpoint Directory

| # | HTTP Method | Endpoint Path | RBAC Scope | Request Query / Body | Response Contract | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `GET` | `/api/health` | Public | None | `{"status": "ok", "app": "novanest"}` | General application liveness probe |
| 2 | `GET` | `/api/health/live` | Public | None | `{"status": "healthy"}` | Kubernetes liveness probe |
| 3 | `GET` | `/api/health/ready` | Public | None | `{"ready": true, "db": "connected"}` | Container readiness probe |
| 4 | `GET` | `/api/health/db` | Public | None | `{"database": "novanest_db", "status": "up"}` | Direct MySQL connection probe |
| 5 | `GET` | `/api/health/containers` | Public | None | `{"containers": [...]}` | Docker container inspection status |
| 6 | `GET` | `/api/metrics` | Public | None | Plaintext Prometheus metrics | Prometheus metrics exposition format |
| 7 | `GET` | `/api/diagnostics/data-source` | `read` | None | `{"source": "mysql", "rows": 304405}` | Runtime active datasource audit |
| 8 | `GET` | `/api/overview` | `read` | `period: Optional[str]` | `ExecutiveOverviewResponse` | High-level business overview and top KPIs |
| 9 | `GET` | `/api/customer/overview` | `read` | `city: Optional[str]` | `CustomerOverviewResponse` | Customer counts, RFM, and retention |
| 10 | `GET` | `/api/customer/list` | `operator` | `page: int, limit: int` | `PaginatedCustomerList` | Paged customer list with persona filters |
| 11 | `GET` | `/api/customer/360/{id}` | `operator` | Path `customer_id` | `Customer360Profile` | Deep 360-degree customer profile |
| 12 | `GET` | `/api/restaurant/overview`| `read` | `cuisine: Optional[str]` | `RestaurantOverviewResponse` | Restaurant partner performance metrics |
| 13 | `GET` | `/api/operations/overview`| `read` | None | `OperationsOverviewResponse` | Delivery operations, fleet and delay data |
| 14 | `GET` | `/api/operations/traces` | `operator` | `limit: int = 50` | `List[TelemetryTrace]` | Recent system latency & execution traces |
| 15 | `GET` | `/api/operations/alerts` | `operator` | `severity: Optional[str]` | `List[OperationalAlert]` | Active system and operational alerts |
| 16 | `POST`| `/api/operations/alerts/test`| `operator` | `{"severity": "INFO"}` | `{"status": "emitted"}` | Diagnostic alert emission endpoint |
| 17 | `POST`| `/api/operations/backup` | `operator` | None | `{"status": "success", "file": "..."}` | Manual Encrypt-then-MAC DB backup |
| 18 | `POST`| `/api/operations/restore-test`| `operator` | None | `{"status": "verified", "rto_sec": 2.1}` | Automated non-destructive restore audit |
| 19 | `GET` | `/api/operations/performance` | `operator`| None | `PerformanceMetricsResponse` | Hardware, CPU, memory, and cache telemetry |
| 20 | `GET` | `/api/operations/disaster-recovery` | `operator` | None | `DisasterRecoveryAuditResponse` | Backup logs, RTO/RPO SLAs, test history |
| 21 | `GET` | `/api/financial/overview` | `read` | None | `FinancialOverviewResponse` | GMV, Net Inflow, and Contribution Profit |
| 22 | `POST`| `/api/ai/ask` | Public/Auth | `{"query": str, "session_id": str}` | `AgentResponseContract` | Natural language multi-agent AI query |
| 23 | `POST`| `/api/ai/ask/stream` | Public/Auth | `{"query": str, "session_id": str}` | `text/event-stream` | SSE token streaming for AI queries |
| 24 | `POST`| `/api/ai/stream` | Public/Auth | `{"prompt": str}` | `text/event-stream` | Standard SSE AI streaming interface |
| 25 | `POST`| `/api/ai/stream-ticket` | Public/Auth | `{"query": str}` | `{"ticket": str, "url": str}` | Streaming ticket generator for browser |
| 26 | `GET` | `/api/ai/ask/stream` | Public/Auth | `ticket: str` | `text/event-stream` | Ticket-authenticated SSE stream |
| 27 | `GET` | `/api/ai/stream` | Public/Auth | `ticket: str` | `text/event-stream` | Direct browser GET SSE listener |
| 28 | `GET` | `/api/ai/agents/status` | Public | None | `{"agents": [{"name": "...", "status": "UP"}]}` | Multi-agent registry status probe |
| 29 | `GET` | `/api/ai/traces/{request_id}` | Public | Path `request_id` | `AgentTraceDetails` | Inspect reasoning trace for specific query |
| 30 | `POST`| `/api/ai/reset` | `admin` | `{"session_id": str}` | `{"status": "session_cleared"}` | Purge conversation context & session |
| 31 | `GET` | `/api/prescriptive/recommendations` | `read` | `domain: Optional[str]` | `List[PrescriptiveRecommendation]` | Active prescriptive business recommendations |
| 32 | `GET` | `/api/prescriptive/summary` | `read` | None | `PrescriptiveSummaryResponse` | Quantified revenue upside and action counts |
| 33 | `GET` | `/api/prescriptive/recommendations/{id}` | `read` | Path `rec_id` | `PrescriptiveRecommendation` | Deep-dive into specific recommendation |
| 34 | `POST`| `/api/prescriptive/recommendations/{id}/approve` | `operator` | Path `rec_id` | `LifecycleTransitionResponse` | Move recommendation to APPROVED |
| 35 | `POST`| `/api/prescriptive/recommendations/{id}/reject` | `operator` | Path `rec_id` | `LifecycleTransitionResponse` | Move recommendation to REJECTED |
| 36 | `POST`| `/api/prescriptive/recommendations/{id}/start-progress` | `operator` | Path `rec_id` | `LifecycleTransitionResponse` | Move recommendation to IN_PROGRESS |
| 37 | `POST`| `/api/prescriptive/recommendations/{id}/mark-implemented` | `operator` | Path `rec_id` | `LifecycleTransitionResponse` | Move recommendation to IMPLEMENTED |
| 38 | `POST`| `/api/prescriptive/recommendations/{id}/record-outcome` | `operator` | Path `rec_id`, `{"actual_gain": float}` | `OutcomeRecordResponse` | Record actual financial gain vs projected |
| 39 | `POST`| `/api/prescriptive/simulate` | `operator` | `SimulationParametersPayload` | `SimulationResultsResponse` | Run what-if prescriptive scenario |
| 40 | `GET` | `/api/prescriptive/customer-profile/{id}` | `read` | Path `customer_id` | `CustomerPrescriptiveProfile` | Prescriptive retention action for user |
| 41 | `GET` | `/api/prescriptive/restaurant-profile/{id}` | `read` | Path `restaurant_id` | `RestaurantPrescriptiveProfile`| Prescriptive margin & menu suggestions |
| 42 | `GET` | `/api/prescriptive/rider-fleet-workload` | `read` | None | `FleetWorkloadResponse` | Prescriptive fleet rebalancing suggestions |
| 43 | `GET` | `/api/prescriptive/financial-charts` | `read` | None | `FinancialChartsResponse` | Waterfall & margin analytics charts |
| 44 | `GET` | `/api/decision/actions` | `read` | None | `DecisionActionsResponse` | Next-best-action executive priority list |
| 45 | `POST`| `/api/decision/simulate` | `operator` | `DecisionSimulationPayload` | `DecisionSimulationResponse` | Prescriptive trade-off simulation engine |
| 46 | `GET` | `/api/digital-twin/state` | `read` | None | `DigitalTwinStateResponse` | Current operational Digital Twin state |
| 47 | `POST`| `/api/copilot/query` | Public/Auth | `{"query": str}` | `CopilotQueryResponse` | Executive AI Copilot multi-step analysis |
| 48 | `GET` | `/api/records/{entity}` | `operator` | Path `entity`, `page`, `sort_by` | `PaginatedRecordResponse` | Whitelisted server-side entity pagination |

---

## 3. Multi-Agent AI System Specification

The AI subsystem operates on a collaborative, typed multi-agent architecture.

### 3.1 Base Architecture & Shared Contracts
All agents inherit from `BaseAgent` (`python/ai/agents/base.py`) and communicate using Pydantic contracts (`python/ai/agents/contracts.py`).
- **Input Contract (`AgentQueryContext`)**:
  - `query: str`: Raw user prompt.
  - `session_id: str`: Session correlation UUID.
  - `domain_intent: List[str]`: Identified target domains.
  - `temporal_context: Dict[str, Any]`: Active date ranges and filters.
  - `user_role: str`: RBAC privilege scope.
- **Output Contract (`DomainAgentResponse`)**:
  - `agent_name: str`: Identifying name of the responding agent.
  - `confidence_score: float`: Calibrated confidence (0.0 to 1.0).
  - `factual_grounding: Dict[str, Any]`: Canonical SQL and ML values used.
  - `insights: List[str]`: Domain-specific bullet points.
  - `recommendations: List[str]`: Prescriptive action candidates.
  - `citations: List[str]`: Exact database tables and model artifacts queried.

### 3.2 Five Domain Intelligence Agents

#### 1. Customer Intelligence Agent (`CustomerAgent`)
- **Domain Focus**: Churn probability, RFM segmentation, LTV prediction, order frequency, cohort retention.
- **Data Grounding**: `customers`, `orders_table`, `app_events`, `models/customer_churn/model_artifact_v3.joblib`.
- **System Prompt Guardrail**: "You are NovaNest's Customer Intelligence Specialist. You provide rigorous, fact-based customer behavior analysis. You MUST cite canonical churn holdout metrics (Random Forest ROC-AUC 0.5062, Gated: LOW_EMPIRICAL) and never fabricate customer sentiment."

#### 2. Restaurant Performance Agent (`RestaurantAgent`)
- **Domain Focus**: Partner profitability, preparation latency, cuisine demand elasticity, commission yield, menu pricing.
- **Data Grounding**: `restaurants`, `menu_items`, `orders_table`, `models/restaurant_prediction/model_artifact_v3.joblib`.
- **System Prompt Guardrail**: "You are NovaNest's Restaurant Optimization Analyst. You evaluate partner commission structures (15-30%) and kitchen bottlenecks. Ground all volume projections on the Ridge model (MAE 1.32 orders, Gated: LOW_EMPIRICAL)."

#### 3. Operations & Logistics Agent (`OperationsAgent`)
- **Domain Focus**: Rider utilization, delivery velocity, weather/traffic bottlenecks, dispatch delays, fleet deficit.
- **Data Grounding**: `riders`, `deliveries`, `orders_table`, `models/eta_prediction/model_artifact_v3.joblib`.
- **System Prompt Guardrail**: "You are NovaNest's Fleet & Delivery Logistics Director. Analyze last-mile delivery performance. Explicitly state the ETA model holdout performance (MAE 11.52 min, 90% confidence interval +/- 21.9 min, Gated: LOW_EMPIRICAL)."

#### 4. Financial & Revenue Agent (`FinancialAgent`)
- **Domain Focus**: Gross Merchandise Value (GMV), net platform inflow, discount burn, driver payout overhead, platform contribution profit, revenue leakage.
- **Data Grounding**: `orders_table`, `payments`, `promotions`, `datasets/engineered/revenue_leakage.csv`.
- **System Prompt Guardrail**: "You are NovaNest's Chief Financial Intelligence Officer. You govern financial precision. Always cite exact canonical numbers: GMV ₹46,590,125.00, Net Inflow ₹46,425,992.00, Net AOV ₹967.33, and Platform Contribution Profit ₹10,953,031.58. Never refer to contribution profit as net profit."

#### 5. Decision & Strategy Agent (`DecisionAgent`)
- **Domain Focus**: Cross-domain synthesis, trade-off optimization, opportunity sizing, Next-Best-Action generation.
- **Data Grounding**: Prescriptive rule matrix, output responses of the four domain agents, Digital Twin simulation hooks.
- **System Prompt Guardrail**: "You are NovaNest's Strategic Decision Orchestrator. Synthesize cross-functional trade-offs between customer retention and driver profitability. Formulate actionable prescriptive recommendations with quantified upside."

### 3.3 Security Guardrail: `OutputVerifier`
- **Location**: `python/ai/agents/output_verifier.py`
- **Benchmark Evaluation**: Evaluated against a rigorous 50-prompt test suite (30 legitimate queries, 10 prompt injection attacks, 10 prompt extraction/jailbreak attempts).
- **Interception Rate**: **100% on tested benchmark (20/20 attacks blocked)**.
- **False Positive Rate**: **0.0% (0/30 legitimate business queries blocked)**.
- **Verification Logic**:
  1. Detects system prompt override sequences (`"ignore previous instructions"`, `"reveal system prompt"`).
  2. Compares numerical claims in generated text against `factual_grounding` metadata to prevent hallucination.
  3. Replaces unverified responses with deterministic SQL-grounded business answers.

---

## 4. Machine Learning Model Cards

NovaNest maintains 5 machine learning pipelines trained on temporal splits (80% early training / 20% late holdout).

### Model Card 1: Customer Churn Predictor
- **Architecture**: `RandomForestClassifier` (Pipeline: `StandardScaler` + `OneHotEncoder`).
- **Target Variable**: `is_churned` (Binary: Inactive for >= 60 days).
- **Features (14)**: `recency_days`, `frequency_total`, `monetary_total`, `avg_order_value`, `customer_age`, `gender_enc`, `city_enc`, `subscription_enc`, `channel_enc`, `days_since_signup`, `refund_count`, `complaint_count`, `delivery_delay_rate`, `discount_dependency_ratio`.
- **Holdout Evaluation**:
  - **Random Forest**: ROC-AUC = **0.5062**, Accuracy = **54.20%**, F1 = **0.5180**.
  - **XGBoost Comparison**: ROC-AUC = **0.4861**, Accuracy = **52.10%**, F1 = **0.4950**.
- **Calibration**: Brier Score = **0.2504**.
- **Deployment Gating**: **`LOW_EMPIRICAL`** (Assistive feature only; near-random discrimination on synthetic holdout; not permitted to execute autonomous customer de-provisioning).

### Model Card 2: Delivery ETA Predictor
- **Architecture**: `HistGradientBoostingRegressor`.
- **Target Variable**: `delivery_duration` (Minutes: kitchen dispatch to door).
- **Features (11)**: `distance_km`, `rider_experience_years`, `rider_vehicle_type`, `preparation_time`, `order_hour`, `day_of_week`, `is_weekend`, `traffic_congestion_factor`, `weather_severity_index`, `active_orders_in_zone`, `restaurant_city`.
- **Holdout Evaluation**:
  - MAE = **11.52 minutes**.
  - RMSE = **14.88 minutes**.
  - 90% Prediction Interval Band: **+/- 21.90 minutes**.
- **Deployment Gating**: **`LOW_EMPIRICAL`** (Operational display uses wide +/- 22 min interval banding; requires real GPS telemetry for tight SLA routing).

### Model Card 3: Hourly Delivery Demand Forecaster
- **Architecture**: `HistGradientBoostingRegressor`.
- **Target Variable**: `hourly_order_volume` (Orders per hour per metropolitan zone).
- **Features (9)**: `hour_of_day`, `day_of_week`, `is_holiday`, `rolling_lag_1h`, `rolling_lag_24h`, `rolling_lag_7d`, `zone_id`, `temperature_celsius`, `precipitation_mm`.
- **Holdout Evaluation**:
  - WAPE (Weighted Absolute Percentage Error) = **17.20%**.
  - MAE = **7.02 orders/hour**.
  - RMSE = **9.81 orders/hour**.
- **Deployment Gating**: **`BASELINE_ONLY`** (Benchmark baseline for shift scheduling; requires real-time holiday calendar synchronization).

### Model Card 4: Restaurant Daily Order Volume Predictor
- **Architecture**: `Ridge` Regressor ($lpha = 1.0$).
- **Target Variable**: `daily_restaurant_orders`.
- **Features (8)**: `avg_rating`, `price_level`, `cuisine_type`, `delivery_radius_km`, `city`, `menu_item_count`, `historical_avg_orders`, `promotional_campaign_active`.
- **Holdout Evaluation**:
  - MAE = **1.32 orders/day**.
  - RMSE = **1.89 orders/day**.
  - $R^2$ = **0.052** (Synthetic variance limit).
- **Deployment Gating**: **`LOW_EMPIRICAL`** (Used for macro restaurant tiering; partner inventory planning requires point-of-sale data integration).

### Model Card 5: Operational Anomaly Consensus Detector
- **Architecture**: Tri-Model Consensus Voting (`IsolationForest` + `EllipticEnvelope` + `LocalOutlierFactor`).
- **Target Variable**: Multidimensional operational outlier flag.
- **Features (7)**: `order_amount`, `delivery_duration`, `distance_km`, `discount_amount`, `preparation_time`, `rider_experience`, `rating_spread`.
- **Holdout Evaluation**:
  - Consensus Threshold: Unanimous agreement (\ge 2 models voting anomaly).
  - Flagged Records: **628 orders out of 49,971 (1.26% anomaly prevalence)**.
- **Deployment Gating**: **`EXPERIMENTAL`** (Heuristic triage for manual review queue; high-dollar outliers dispatched to fraud audit).

---

## 5. Frontend & UI Component Catalog

### 5.1 React 18 SPA Architecture (`frontend/src/`)
- **Theme Standard**: Enterprise Light Theme (`theme-light-novanest`). Pure white surfaces (`#FFFFFF`), light slate canvases (`#F8FAFC`), deep slate typography (`#0F172A`), royal blue brand primary (`#2563EB`), and amber/orange accents (`#F59E0B`).
- **Key Modules**:
  1. `ExecutiveOverviewView.tsx`: High-level executive dashboard, financial KPIs, real-time pulse.
  2. `CustomerIntelligenceView.tsx`: RFM segments, cohort retention grids, customer 360 viewer.
  3. `RestaurantIntelligenceView.tsx`: Partner margin matrix, menu pricing curves, rating distributions.
  4. `OperationsIntelligenceView.tsx`: Delivery duration heatmaps, fleet utilization, bottleneck zones.
  5. `FinancialIntelligenceView.tsx`: Revenue waterfall, platform take rates, discount burn, leakages.
  6. `DecisionCenterView.tsx`: Prescriptive recommendations, approval buttons, lifecycle status cards.
  7. `DecisionSimulatorView.tsx`: Interactive trade-off sliders, elasticity modeling, sensitivity charts.
  8. `CommandCenterView.tsx`: Digital Twin operational status, ecosystem health, live alerts.
  9. `ExecutiveAiCopilotView.tsx`: Natural language multi-agent chat interface with live token streaming.
- **Core Components**:
  - `KpiCard.tsx`: Metric card with primary number, period-over-period delta badge, and embedded micro-sparkline.
  - `DataTable.tsx`: Accessible table with column sorting, live substring filtering, and server-side pagination.
  - `GlobalFilterBar.tsx`: Metropolitan city and date-range pickers with local storage persistence.
  - `FloatingChatbot.tsx`: Collapsible bottom-right AI assistant drawer for instant query access.

### 5.2 Streamlit Analytics Platform (`streamlit_app/`)
- **Multi-Page Layout**: 8 modular analytical pages mirroring React view logic.
- **Dual Database Resolution (`database/connection.py`)**: Automatic discovery of MySQL via `st.secrets` or environment variables, with immediate graceful failover to bundled offline CSVs (`datasets/cleaned/`).
- **Visuals**: Dynamic Plotly charts (`plotly.graph_objects`, `plotly.express`) adhering to light theme tokens.

---

## 6. Configuration & Environment Reference

### 6.1 Environment Variables (`.env`)

| Variable Name | Required | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `MYSQL_HOST` | Yes | `localhost` (or `db` in Docker) | Hostname for MySQL server |
| `MYSQL_PORT` | Yes | `3306` | Port for MySQL database |
| `MYSQL_DATABASE` | Yes | `novanest_db` | Target database catalog |
| `MYSQL_USER` | Yes | `novanest_app` | Least-privilege runtime application user |
| `MYSQL_PASSWORD` | Yes | `novanest_secure_pass_2026` | Application database user password |
| `MYSQL_ROOT_PASSWORD`| Yes | `novanest_root_super_secret_2026` | Administrative root user password |
| `API_HOST` | No | `0.0.0.0` | FastAPI binding host |
| `API_PORT` | No | `8000` | FastAPI binding port |
| `API_SECRET_KEY` | Yes | `32-byte-hex-random-token` | Secret for HMAC signing & sessions |
| `API_TOKEN_ADMIN` | Yes | `token-admin-phase18-2026` | Bearer token for `admin` role |
| `API_TOKEN_OPERATOR`| Yes | `token-operator-phase18-2026`| Bearer token for `operator` role |
| `API_TOKEN_VIEWER` | Yes | `token-viewer-phase18-2026` | Bearer token for `viewer` role |
| `GEMINI_API_KEY` | Optional| None | External LLM API key (Mock fallback active) |
| `PROMETHEUS_PORT` | No | `9090` | Prometheus scraping daemon port |
| `GRAFANA_PORT` | No | `3000` | Grafana telemetry UI port |

---

## 7. Container & Infrastructure Reference

### 7.1 Multi-Container Services (`docker-compose.yml`)

1. **`db` (`novanest_db`)**:
   - Image: `mysql:8.0`
   - Ports: `3306:3306`
   - Volume: `mysql_data:/var/lib/mysql`, `./docker/mysql/init:/docker-entrypoint-initdb.d`
   - Healthcheck: `mysqladmin ping -h localhost -u root -p${MYSQL_ROOT_PASSWORD}` (Interval: 10s, Timeout: 5s, Retries: 5).
2. **`api` (`novanest_api`)**:
   - Build: Dockerfile (Python 3.11-slim)
   - Ports: `8000:8000`
   - Depends On: `db` (healthy)
   - Healthcheck: `curl -f http://localhost:8000/api/health || exit 1`.
3. **`frontend` (`novanest_frontend`)**:
   - Build: Dockerfile (Multi-stage Node.js build -> Nginx Alpine)
   - Ports: `5173:80` (or `80:80` in production)
   - Depends On: `api` (healthy).
4. **`streamlit` (`novanest_streamlit`)**:
   - Build: Dockerfile (Python 3.11-slim)
   - Ports: `8501:8501`
   - Depends On: `db` (healthy), `api` (healthy).
5. **`prometheus` (`novanest_prometheus`)**:
   - Image: `prom/prometheus:v2.45.0`
   - Ports: `9090:9090`
   - Config: `./docker/prometheus/prometheus.yml`.
6. **`grafana` (`novanest_grafana`)**:
   - Image: `grafana/grafana:10.0.0`
   - Ports: `3000:3000`
   - Volumes: `./docker/grafana/dashboards`, `./docker/grafana/provisioning`.

---

## 8. CLI & Maintenance Scripts Reference

All management scripts reside in `scripts/` and have verified automated execution.

| Script Name | Language | Purpose & Operation | Key Flags / Inputs |
| :--- | :--- | :--- | :--- |
| `deploy_production.sh` | Bash | Validates host requirements, builds containers, executes migrations, starts detached stack | None |
| `backup_production.sh` | Bash | Generates AES-256-CBC encrypted, HMAC-SHA256 authenticated database backup | Output: `backup/novanest_YYYYMMDD.sql.enc` |
| `restore_production.sh`| Bash | Verifies HMAC signature, decrypts backup, restores into target MySQL instance | `--file <path>` |
| `init_ssl.sh` | Bash | Acquires initial Let's Encrypt certificates using Certbot standalone webroot | `--domain <domain> --email <email>` |
| `renew_ssl.sh` | Bash | Tests certificate expiry and triggers automated zero-downtime Nginx reload | Designed for crontab execution |
| `migrate_database_to_cloud.sh`| Bash | Exports local MySQL database, encrypts payload, and prepares secure upload package | None |
| `load_test_phase17.py` | Python | Simulates 10, 25, and 50 concurrent users benchmarking p50, p95, and p99 latencies | `--users 50 --duration 60` |
| `clean_datasets.py` | Python | Cleans, validates, and normalizes raw CSVs into canonical cleaned datasets | None |
| `train_models_v3.py` | Python | Retrains all 5 machine learning models, executes calibration, generates metadata | None |
