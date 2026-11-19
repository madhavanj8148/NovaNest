# NOVANEST — COMPLETE SYSTEM ARCHITECTURE SPECIFICATION
## Comprehensive Architectural Blueprints, Multi-Tier Engineering & 17 Formal System Diagrams

---

### Executive Architectural Summary
NovaNest is an enterprise-grade, AI-powered food delivery analytics, decision intelligence, and autonomous operational platform. The platform ingests, processes, normalizes, analyzes, and predicts across a multi-tier food delivery ecosystem comprising **304,405 canonical records** across 10 relational tables.

This document serves as the formal architectural reference manual for NovaNest, providing technical narratives, component interaction protocols, data flow specifications, and **17 comprehensive Mermaid architecture diagrams** detailing every tier of the platform.

---

## 1. Overall NovaNest System Architecture

The overall system architecture follows a decoupled, resilient, multi-tiered micro-service pattern. The core layers comprise:
1. **Edge & Ingress Tier**: Hardened Nginx reverse proxy managing SSL/TLS termination, DDoS rate limiting, HTTP security headers, and reverse proxy routing.
2. **Presentation Tier**: Dual-frontend architecture featuring a modern React 18 + Vite Single Page Application (SPA) with Tailwind CSS for operational users, alongside an interactive Streamlit Multi-Page Analytics Application with dual-resolution data fallbacks.
3. **Application & API Tier**: High-performance FastAPI asynchronous backend providing 48 endpoints, structured into modular domain routers, secured by Bearer Token Authentication and Role-Based Access Control (RBAC).
4. **Intelligence & Decision Tier**: Multi-Agent AI system powered by a Master Orchestrator and 5 specialized domain agents (Customer, Restaurant, Operations, Financial, Decision), integrated with an OutputVerifier security gate, Prescriptive Recommendation Engine, and Digital Twin Simulation Engine.
5. **Machine Learning Tier**: 5 production/experimental ML pipelines (Customer Churn, Order ETA, Hourly Demand, Restaurant Order Volume, and Anomaly Consensus Ensemble) governed by strict deployment gating.
6. **Data Storage Tier**: ACID-compliant MySQL 8.0 relational database normalized to Third Normal Form (3NF) with InnoDB engine, utf8mb4 collation, composite indexing, and transactional foreign key constraints.
7. **Observability Tier**: Prometheus metrics scraping daemon, Grafana visual telemetry dashboards, structured JSON logging, and distributed request tracing.

```mermaid
graph TB
    subgraph Client_Layer ["Client & Ingress Layer"]
        UserBrowser["Web Browser (End User / Executive)"]
        StreamlitUser["Analytics User (BI / Data Analyst)"]
        NginxIngress["Nginx Reverse Proxy & TLS Ingress (:80 / :443)"]
    end

    subgraph Presentation_Layer ["Presentation Tier"]
        ReactApp["React 18 + Vite SPA (:5173 / :80)<br/>9 Intelligence Views | Tailwind CSS | Chart.js"]
        StreamlitApp["Streamlit Analytics App (:8501)<br/>Multi-page BI | Dual Database Resolution"]
        PowerBIApp["Power BI Desktop / Embedded<br/>Executive Reporting | Injected Brand Theme"]
    end

    subgraph Backend_Layer ["Application & API Tier (FastAPI :8000)"]
        AuthMiddleware["Security & RBAC Middleware<br/>(Admin, Operator, Viewer Scopes)"]
        APIRouters["48 Modular REST Endpoints<br/>(Overview, Customer, Ops, Finance, Prescriptive, Twin)"]
        CacheLayer["Multi-Tier Cache Manager<br/>(L1 Memory LRU + L2 Redis Ready)"]
        PaginationEngine["Server-Side Pagination & Whitelist Engine"]
    end

    subgraph Intelligence_Layer ["Intelligence & Decision Tier"]
        Orchestrator["Master Multi-Agent Orchestrator"]
        subgraph Domain_Agents ["Five Domain Intelligence Agents"]
            CustAgent["Customer Agent"]
            RestAgent["Restaurant Agent"]
            OpsAgent["Operations Agent"]
            FinAgent["Financial Agent"]
            DecAgent["Decision Agent"]
        end
        OutputVerifier["OutputVerifier Security Gate<br/>(Hallucination & Jailbreak Defense)"]
        PrescriptiveEngine["Prescriptive Analytics Engine<br/>(Next-Best-Action Lifecycle)"]
        DigitalTwin["Digital Twin Simulation Engine<br/>(What-If Scenario Modeling)"]
    end

    subgraph ML_Layer ["Machine Learning Model Tier"]
        ModelRegistry["Model Registry & Metadata Store"]
        ChurnModel["Customer Churn (Random Forest)"]
        ETAModel["ETA Predictor (HistGradientBoosting)"]
        DemandModel["Demand Forecaster (HistGradientBoosting)"]
        RestModel["Restaurant Volume (Ridge Regression)"]
        AnomalyModel["Anomaly Detection (Consensus Ensemble)"]
    end

    subgraph Storage_Layer ["Data Tier (MySQL 8.0 :3306)"]
        MySQL[(MySQL 8.0 Database<br/>304,405 Rows | 10 Tables | 3NF)]
        CleanedCSVs[("Cleaned & Engineered CSV Datasets<br/>Fail-Safe Offline Mode")]
    end

    subgraph Observability_Layer ["Telemetry & Observability Tier"]
        Prometheus["Prometheus Server (:9090)"]
        Grafana["Grafana Dashboards (:3000)"]
        HealthProbes["Health Endpoints (:8000/api/health/*)"]
    end

    UserBrowser --> NginxIngress
    StreamlitUser --> NginxIngress
    NginxIngress --> ReactApp
    NginxIngress --> StreamlitApp
    ReactApp --> AuthMiddleware
    StreamlitApp --> APIRouters
    StreamlitApp -.->|Dual Resolution Fallback| MySQL
    StreamlitApp -.->|Offline Mode| CleanedCSVs
    PowerBIApp -.-> MySQL

    AuthMiddleware --> APIRouters
    APIRouters --> CacheLayer
    APIRouters --> PaginationEngine
    APIRouters --> Orchestrator
    APIRouters --> PrescriptiveEngine
    APIRouters --> DigitalTwin
    PaginationEngine --> MySQL

    Orchestrator --> CustAgent
    Orchestrator --> RestAgent
    Orchestrator --> OpsAgent
    Orchestrator --> FinAgent
    Orchestrator --> DecAgent

    Domain_Agents --> OutputVerifier
    Domain_Agents --> ModelRegistry
    ModelRegistry --> ChurnModel
    ModelRegistry --> ETAModel
    ModelRegistry --> DemandModel
    ModelRegistry --> RestModel
    ModelRegistry --> AnomalyModel

    PrescriptiveEngine --> MySQL
    DigitalTwin --> MySQL
    CustAgent --> MySQL
    RestAgent --> MySQL
    OpsAgent --> MySQL
    FinAgent --> MySQL

    APIRouters --> Prometheus
    Prometheus --> Grafana
    HealthProbes --> Prometheus
```

---

## 2. Data Ingestion & Processing Flow

The data engineering pipeline processes raw transactional data through a multi-stage validation, cleaning, and enrichment lifecycle. 

1. **Raw Ingestion**: Ingests 10 raw operational datasets containing simulated Indian food delivery transactional logs.
2. **Data Cleaning & Auditing**: Identifies and remediates missing timestamps, negative pricing anomalies, mismatched category strings, and duplicate tracking IDs.
3. **Feature Engineering**: Derives geospatial distance vectors, preparation delays, customer RFM (Recency, Frequency, Monetary) metrics, cohort matrices, and hourly demand aggregations.
4. **Relational Normalization**: Transforms flat datasets into 10 structured 3NF tables in MySQL 8.0, enforcing strict foreign key referential integrity.
5. **Analytical Dataset Generation**: Generates 9 engineered feature tables and 8 pre-computed business intelligence summary tables.

```mermaid
flowchart TD
    subgraph Raw_Stage ["Stage 1: Raw Data Sources"]
        R1["raw/customers.csv (5,000)"]
        R2["raw/restaurants.csv (1,500)"]
        R3["raw/riders.csv (4,000)"]
        R4["raw/promotions.csv (200)"]
        R5["raw/menu_items.csv (15,000)"]
        R6["raw/orders.csv (49,971)"]
        R7["raw/payments.csv (49,971)"]
        R8["raw/deliveries.csv (49,971)"]
        R9["raw/ratings_reviews.csv (28,792)"]
        R10["raw/app_events.csv (100,000)"]
    end

    subgraph Cleaning_Stage ["Stage 2: Validation & Cleansing Engine"]
        ValScript["python/data/clean_datasets.py"]
        Deduplication["Deduplication & Primary Key Verification"]
        TypeCasting["Date/Time Parsing & Decimal Standardisation"]
        NullHandling["Imputation & Missing Value Resolution"]
        IntegrityChecks["Referential Integrity & Orphan ID Purging"]
    end

    subgraph Cleaned_Stage ["Stage 3: Canonical Cleaned Datasets (304,405 Rows)"]
        C1["cleaned/customers.csv"]
        C2["cleaned/restaurants.csv"]
        C3["cleaned/riders.csv"]
        C4["cleaned/promotions.csv"]
        C5["cleaned/menu_items.csv"]
        C6["cleaned/orders.csv"]
        C7["cleaned/payments.csv"]
        C8["cleaned/deliveries.csv"]
        C9["cleaned/ratings_reviews.csv"]
        C10["cleaned/app_events.csv"]
    end

    subgraph Engineering_Stage ["Stage 4: Feature & Spatial Enrichment"]
        GeoTemporal["Geo-Temporal Distance & Velocity Engine"]
        RFMScoring["Customer RFM & Behavioral Segmentation"]
        TemporalAggs["Hourly Demand & Heatmap Aggregations"]
        AnomalyFeatures["Multivariate Anomaly Signal Construction"]
    end

    subgraph Output_Stage ["Stage 5: Production Datastores"]
        MySQLDB[("MySQL 8.0 Relational DB (304,405 rows)")]
        EngineeredCSVs[("Engineered CSVs (9 Datasets)")]
        AnalyticsCSVs[("Analytics Summary Tables (8 Datasets)")]
    end

    Raw_Stage --> ValScript
    ValScript --> Deduplication --> TypeCasting --> NullHandling --> IntegrityChecks
    IntegrityChecks --> Cleaned_Stage
    Cleaned_Stage --> Engineering_Stage
    Cleaned_Stage --> MySQLDB
    Engineering_Stage --> EngineeredCSVs
    Engineering_Stage --> AnalyticsCSVs
    Engineering_Stage --> MySQLDB
```

---

## 3. Database Entity-Relationship (ER) Architecture

The database architecture is designed in strict Third Normal Form (3NF) to eliminate data redundancy and guarantee transaction atomicity across all 10 core operational tables.

### Key Relationships
- `customers` (1) to `orders_table` (M) via `customer_id`
- `restaurants` (1) to `orders_table` (M) via `restaurant_id`
- `riders` (1) to `orders_table` (M) via `rider_id`
- `menu_items` (1) to `orders_table` (M) via `item_id`
- `restaurants` (1) to `menu_items` (M) via `restaurant_id`
- `orders_table` (1) to `payments` (1) via `order_id`
- `orders_table` (1) to `deliveries` (1) via `order_id`
- `riders` (1) to `deliveries` (M) via `rider_id`
- `orders_table` (1) to `ratings_reviews` (0..1) via `order_id`
- `customers` (1) to `ratings_reviews` (M) via `customer_id`
- `customers` (1) to `app_events` (M) via `customer_id`

```mermaid
erDiagram
    CUSTOMERS ||--o{ ORDERS_TABLE : places
    CUSTOMERS ||--o{ APP_EVENTS : triggers
    CUSTOMERS ||--o{ RATINGS_REVIEWS : writes
    RESTAURANTS ||--o{ MENU_ITEMS : offers
    RESTAURANTS ||--o{ ORDERS_TABLE : fulfills
    RIDERS ||--o{ ORDERS_TABLE : delivers
    RIDERS ||--o{ DELIVERIES : assigned
    MENU_ITEMS ||--o{ ORDERS_TABLE : ordered_in
    ORDERS_TABLE ||--|| PAYMENTS : settled_by
    ORDERS_TABLE ||--|| DELIVERIES : tracked_by
    ORDERS_TABLE ||--o| RATINGS_REVIEWS : evaluated_by

    CUSTOMERS {
        varchar(20) customer_id PK
        varchar(100) customer_name
        int age
        varchar(20) gender
        varchar(50) city
        varchar(50) persona
        varchar(100) occupation
        date signup_date
        varchar(20) subscription_type
        varchar(100) acquisition_channel
    }

    RESTAURANTS {
        varchar(20) restaurant_id PK
        varchar(100) restaurant_name
        varchar(50) city
        varchar(50) restaurant_type
        varchar(50) cuisine_type
        int opening_year
        decimal(3-1) avg_rating
        decimal(4-1) delivery_radius_km
        int commission_percentage
    }

    RIDERS {
        varchar(20) rider_id PK
        varchar(100) rider_name
        varchar(50) city
        varchar(50) vehicle_type
        int experience_years
        int joining_year
        varchar(50) shift_type
    }

    PROMOTIONS {
        varchar(20) promo_id PK
        varchar(100) promo_name
        varchar(100) promo_type
        int discount_percentage
        int campaign_budget
    }

    MENU_ITEMS {
        varchar(20) item_id PK
        varchar(20) restaurant_id FK
        varchar(50) cuisine_type
        varchar(100) item_name
        int price
        int preparation_time
    }

    ORDERS_TABLE {
        varchar(20) order_id PK
        varchar(20) customer_id FK
        varchar(20) restaurant_id FK
        varchar(20) item_id FK
        varchar(20) rider_id FK
        datetime order_datetime
        int quantity
        int order_amount
        int discount_amount
        int delivery_fee
        int final_amount
        varchar(20) order_status
    }

    PAYMENTS {
        varchar(20) payment_id PK
        varchar(20) order_id FK
        varchar(50) payment_method
        varchar(50) payment_status
    }

    DELIVERIES {
        varchar(20) delivery_id PK
        varchar(20) order_id FK
        varchar(20) rider_id FK
        decimal(4-1) distance_km
        int delivery_duration
    }

    RATINGS_REVIEWS {
        varchar(20) review_id PK
        varchar(20) order_id FK
        varchar(20) customer_id FK
        int restaurant_rating
        int delivery_rating
    }

    APP_EVENTS {
        varchar(20) event_id PK
        varchar(20) customer_id FK
        varchar(50) event_type
    }
```

---

## 4. Backend FastAPI Architecture

The FastAPI backend (`api/main.py`) serves as the central orchestration bus. It provides 48 high-performance endpoints with sub-50ms baseline latencies for cached paths.

### Component Responsibilities:
- **CORS & Compression**: Gzip compression middleware and cross-origin resource sharing configured for local and production hosts.
- **RBAC Security Gate (`api/auth.py`)**: Hierarchical API token validation enforcing `admin > operator > viewer` privilege rings.
- **Caching Layer (`api/cache.py`)**: High-throughput thread-safe L1 memory LRU cache with automatic cache busting on transactional write operations.
- **Pagination Engine (`api/pagination.py`)**: Whitelisted attribute sorting, row bounds (10–100), total record metadata calculation, and SQL-injection defense.
- **SSE Streaming Core**: Server-Sent Events implementation delivering real-time LLM token streams to React and Streamlit frontends.

```mermaid
graph TD
    ClientReq["Incoming Client HTTP/S Request"]
    
    subgraph Middleware_Pipeline ["Middleware Pipeline"]
        CORSMW["CORS Middleware"]
        GzipMW["Gzip Compression Middleware"]
        TimingMW["Request Duration & Trace Timing"]
        AuthMW["Bearer Token & Scope Resolution<br/>(viewer, operator, admin)"]
    end

    subgraph Router_Registry ["Router & Endpoint Dispatcher (48 Endpoints)"]
        HealthRouter["Health & Readiness Endpoints<br/>/api/health/*, /api/metrics"]
        OpsRouter["Operations & Telemetry<br/>/api/operations/*, /api/records/*"]
        DomainRouter["Domain Intelligence<br/>/api/customer/*, /api/restaurant/*, /api/financial/*"]
        AIRouter["Multi-Agent AI & Streaming<br/>/api/ai/ask, /api/ai/stream, /api/copilot/*"]
        PrescriptiveRouter["Prescriptive Decision Engine<br/>/api/prescriptive/*, /api/decision/*"]
        TwinRouter["Digital Twin Simulation<br/>/api/digital-twin/*"]
    end

    subgraph Service_Infrastructure ["Service Infrastructure Layer"]
        CacheMgr["Multi-Tier Cache Manager<br/>(L1 In-Memory LRU Cache)"]
        PagingMgr["Pagination & Sanitization Service"]
        DBPool["MySQL Connection Pool (aiomysql / pymysql)"]
        OrchestrationBridge["Agent Dispatch & SSE Streamer"]
    end

    subgraph Target_Backends ["Target Backends"]
        MySQLInstance[("MySQL 8.0 Engine")]
        AgentSubsystem["Multi-Agent Subsystem"]
        PrometheusRegistry["Prometheus Metrics Collector"]
    end

    ClientReq --> CORSMW --> GzipMW --> TimingMW --> AuthMW
    AuthMW --> Router_Registry
    
    HealthRouter --> PrometheusRegistry
    OpsRouter --> PagingMgr --> DBPool
    DomainRouter --> CacheMgr --> DBPool
    PrescriptiveRouter --> DBPool
    TwinRouter --> DBPool
    AIRouter --> OrchestrationBridge --> AgentSubsystem

    DBPool --> MySQLInstance
```

---

## 5. Five-Agent Multi-Agent System Architecture

The AI subsystem utilizes a specialized five-agent architecture coordinated by a Master Orchestrator. Agents communicate through typed Pydantic contracts and are isolated from untrusted LLM outputs via a strict verification gate.

### Agent Specializations:
1. **Customer Agent (`CustomerAgent`)**: Customer churn analysis, RFM segmentation, LTV prediction, order frequency, cohort retention.
2. **Restaurant Agent (`RestaurantAgent`)**: Partner performance, cuisine demand, menu pricing, kitchen preparation latency, commission yield.
3. **Operations Agent (`OperationsAgent`)**: Rider fleet utilization, dispatch efficiency, delivery delay root-cause, weather/traffic impact, zone bottlenecks.
4. **Financial Agent (`FinancialAgent`)**: GMV tracking, platform commission margin, discount expenditure, operating profit calculations, revenue leakage detection.
5. **Decision Agent (`DecisionAgent`)**: Cross-domain synthesis, trade-off evaluation, scenario prioritization, prescriptive next-best-action generation.

```mermaid
graph TB
    subgraph Orchestration_Layer ["Orchestration & Verification Core"]
        UserQuery["Executive / Analyst Natural Language Query"]
        Orchestrator["Master Multi-Agent Orchestrator"]
        ContextEngine["Context Aggregator & Session State"]
        OutputVerifier["OutputVerifier Security Guardrail<br/>(Grounding & Injection Filter)"]
        Synthesizer["Cross-Domain Executive Synthesizer"]
    end

    subgraph Domain_Agents ["Specialized Domain Intelligence Agents"]
        CA["Customer Agent<br/>(Churn, RFM, Cohorts, LTV)"]
        RA["Restaurant Agent<br/>(Preparation, Menu, Commission)"]
        OA["Operations Agent<br/>(Riders, Delays, Bottlenecks, Fleet)"]
        FA["Financial Agent<br/>(GMV, Margins, Leakage, Profits)"]
        DA["Decision Agent<br/>(Trade-offs, Simulation, Next-Best-Action)"]
    end

    subgraph Data_And_ML_Grounding ["Deterministic Data & Model Grounding"]
        SQLStore[("MySQL 8.0 Relational Data")]
        MLStore["Gated Scikit-Learn / XGBoost Models"]
        PrescriptiveRules["Prescriptive Business Logic Matrix"]
    end

    UserQuery --> Orchestrator
    Orchestrator --> ContextEngine
    ContextEngine --> CA & RA & OA & FA & DA

    CA --> SQLStore & MLStore
    RA --> SQLStore & MLStore
    OA --> SQLStore & MLStore
    FA --> SQLStore
    DA --> PrescriptiveRules & SQLStore

    CA & RA & OA & FA & DA --> Synthesizer
    Synthesizer --> OutputVerifier
    OutputVerifier --> VerifiedResponse["Verified, Factually Grounded Response"]
```

---

## 6. Master Orchestrator Workflow

The Master Orchestrator controls the full lifecycle of an AI query: parsing user intent, dispatching requests to relevant domain agents, executing parallel analyses, and validating results against canonical platform metrics.

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Dashboard
    participant API as FastAPI /api/ai/ask
    participant Orch as Master Orchestrator
    participant Router as Intent Router
    participant Agents as Domain Agents (Parallel)
    participant DB as MySQL Database
    participant Synth as Cross-Domain Synthesizer
    participant Verifier as OutputVerifier Guardrail

    User->>API: POST /api/ai/ask (Query + SessionID)
    API->>Orch: orchestrate_query(query, context)
    Orch->>Router: classify_intent(query)
    Router-->>Orch: Domain Routes [Customer, Operations]
    
    par Query Customer Domain
        Orch->>Agents: CustomerAgent.analyze(query, context)
        Agents->>DB: Query customer RFM & churn metrics
        DB-->>Agents: Customer aggregates
        Agents-->>Orch: CustomerDomainResponse
    and Query Operations Domain
        Orch->>Agents: OperationsAgent.analyze(query, context)
        Agents->>DB: Query rider fleet & delivery delays
        DB-->>Agents: Operations aggregates
        Agents-->>Orch: OperationsDomainResponse
    end

    Orch->>Synth: synthesize([CustomerResp, OpsResp], context)
    Synth-->>Orch: Draft Executive Briefing
    
    Orch->>Verifier: verify_content(draft_response, ground_truth)
    alt Content Grounded & Safe
        Verifier-->>Orch: APPROVED (Zero Hallucination / Injection)
        Orch-->>API: Verified Structured JSON / Token Stream
        API-->>User: 200 OK + AI Response
    else Anomaly / Injection Detected
        Verifier-->>Orch: REJECTED (Fallback to Deterministic Response)
        Orch-->>API: Sanitized Deterministic Business Answer
        API-->>User: 200 OK + Safe Fallback
    end
```

---

## 7. Conversational AI Lifecycle & SSE Streaming

To ensure responsive executive interactions, conversational queries support Server-Sent Events (SSE). The engine streams chunks as they are generated while maintaining trace IDs, token budgets, and security filtering.

```mermaid
stateDiagram-v2
    [*] --> Ingestion: Incoming Query via /api/ai/stream
    
    state Ingestion {
        ValidatePayload: Verify JSON & Session Token
        CheckRateLimit: Enforce Token Bucket Limits
        PromptInjectionScan: Regex & Vector Heuristic Check
    }

    state Routing {
        ClassifyIntent: Determine Primary & Secondary Domains
        ExtractEntities: Resolve City, Restaurant, Customer IDs
    }

    state Execution {
        QueryDatabase: Deterministic SQL Execution
        MLInference: Extract Model Scores & Confidence
        StreamGeneration: Generate Token Stream Chunks
    }

    state Guardrail {
        BufferChunk: Buffer Sentences for Semantic Check
        OutputVerification: Check Factual Accuracy Against SQL Results
    }

    Ingestion --> Routing: Payload Clean
    Ingestion --> [*]: 400 Bad Request / 429 Rate Exceeded
    Routing --> Execution: Dispatched to Agents
    Execution --> Guardrail: Stream Chunks
    Guardrail --> ClientStream: Emit SSE data: {...}
    ClientStream --> Guardrail: Next Chunk
    Guardrail --> Finalize: Stream EOF
    Finalize --> [*]: Log Telemetry & Close Socket
```

---

## 8. Machine Learning Pipeline Architecture

NovaNest incorporates 5 dedicated machine learning pipelines with rigorous temporal train/test splitting, automated hyperparameter optimization, and empirical deployment gating.

### Empirical Gating Standards:
- **`PRODUCTION`**: High predictive power, rigorous calibration, operational stability.
- **`LOW_EMPIRICAL`**: Retained as reference baseline or assistive signal; holdout metrics reflect synthetic boundary noise.
- **`BASELINE_ONLY`**: Benchmark heuristic model; requires production telemetry recalibration.
- **`EXPERIMENTAL`**: Unsupervised or consensus ensemble heuristic.

```mermaid
flowchart LR
    subgraph Data_Extraction ["1. Ingestion & Preprocessing"]
        SQLData[("MySQL Tables")] --> FeaturePipeline["Feature Transformation Pipeline<br/>(Scaling, One-Hot, Imputation)"]
        FeaturePipeline --> TemporalSplit["Temporal Train/Test Split<br/>(Train: 80% Early | Test: 20% Late)"]
    end

    subgraph Training_Grid ["2. Model Training & Cross-Validation"]
        TemporalSplit --> ChurnTrain["Customer Churn<br/>RandomForestClassifier"]
        TemporalSplit --> ETATrain["Delivery ETA<br/>HistGradientBoostingRegressor"]
        TemporalSplit --> DemandTrain["Hourly Demand<br/>HistGradientBoostingRegressor"]
        TemporalSplit --> RestTrain["Restaurant Volume<br/>Ridge Regressor"]
        TemporalSplit --> AnomalyTrain["Anomaly Detector<br/>Consensus Ensemble (IF + EE + LOF)"]
    end

    subgraph Model_Evaluation ["3. Evaluation & Validation"]
        ChurnTrain --> ChurnEval["ROC-AUC: 0.5062 (RF)<br/>ROC-AUC: 0.4861 (XGB)"]
        ETATrain --> ETAEval["MAE: 11.52 min<br/>90% Band: ±21.9 min"]
        DemandTrain --> DemandEval["WAPE: 17.20%<br/>MAE: 7.02 orders/hr"]
        RestTrain --> RestEval["MAE: 1.32 orders<br/>R²: 0.052"]
        AnomalyTrain --> AnomalyEval["Flagged: 628 orders<br/>Contamination: 1.26%"]
    end

    subgraph Governance_Gate ["4. Empirical Deployment Gating"]
        ChurnEval --> Gate1["LOW_EMPIRICAL (Assistive Only)"]
        ETAEval --> Gate2["LOW_EMPIRICAL (Operational Banding)"]
        DemandEval --> Gate3["BASELINE_ONLY (Benchmark Heuristic)"]
        RestEval --> Gate4["LOW_EMPIRICAL (Assistive Only)"]
        AnomalyEval --> Gate5["EXPERIMENTAL (Consensus Heuristic)"]
    end

    subgraph Deployment_Store ["5. Model Artifact Registry"]
        Gate1 & Gate2 & Gate3 & Gate4 & Gate5 --> JoblibStore["Joblib Serialization & metadata_v3.json"]
        JoblibStore --> RuntimeAPIs["FastAPI Runtime /models/*"]
    end
```

---

## 9. Business Recommendation Lifecycle (Prescriptive Analytics)

The Prescriptive Analytics engine transforms raw predictive flags into actionable, governed operational decisions through a formalized five-stage lifecycle.

```mermaid
stateDiagram-v2
    [*] --> Proposed: Rule Trigger / ML Anomaly / KPI Breach
    
    state Proposed {
        SizeOpportunity: Compute Expected Net Financial Gain (₹)
        DetermineConfidence: Assign Confidence Tier (HIGH, MED, LOW)
        ClassifyAction: Assign Domain (Customer, Restaurant, Fleet)
    }

    Proposed --> Approved: Operator / Executive Approval
    Proposed --> Rejected: Operator Dismissal / Out of Scope

    state Approved {
        AssignOwner: Allocate Operational Team Owner
        SetSLA: Establish Implementation Deadline
    }

    Approved --> In_Progress: Execution Commenced
    
    state In_Progress {
        DispatchAction: Trigger Operational / Marketing Workflow
        MonitorMetrics: Telemetry Counter Activated
    }

    In_Progress --> Implemented: Action Successfully Deployed
    
    state Implemented {
        AuditOutcome: Evaluate Actual vs Projected Revenue Delta
        RecordVariance: Store In Database for Retrospective ML Tuning
    }

    Implemented --> [*]: Archive Lifecycle Record
    Rejected --> [*]: Log Rejection Rationale
```

---

## 10. Digital Twin Simulation Workflow

The Digital Twin simulates the operational food delivery ecosystem, enabling leadership to test strategic interventions (e.g., commission fee changes, rider wage incentives, bad weather surges) without risking operational stability.

```mermaid
flowchart TD
    BaselineState[("Current System Baseline State<br/>(304,405 Canonical Records)")]
    SimParams["User Simulation Parameters<br/>• Commission Rate (+/- %)<br/>• Rider Surge Incentive (₹)<br/>• Bad Weather Delay Factor<br/>• Discount Reduction (%)"]

    subgraph Digital_Twin_Engine ["Digital Twin Core Simulation Engine"]
        TwinInit["Initialize Twin Environment"]
        SubTwinCust["Customer Twin Model<br/>(Elasticity & Churn Sensitivity)"]
        SubTwinRest["Restaurant Twin Model<br/>(Partner Margins & Menu Availability)"]
        SubTwinOps["Operations Twin Model<br/>(Rider Velocity & Fleet Backlog)"]
        SubTwinFin["Financial Twin Model<br/>(GMV, Net Inflow, Operating Margin)"]
    end

    subgraph Perturbation_Execution ["Perturbation & Impact Propagation"]
        MonteCarlo["Perturbation Propagation Loop<br/>(Simulating 49,971 Orders)"]
        CrossElasticity["Cross-Domain Elasticity Computation"]
    end

    subgraph Simulation_Outputs ["Simulation Output & Variance Matrix"]
        DeltaGMV["Projected GMV Delta (₹)"]
        DeltaDelays["Projected Delivery Time Delta (min)"]
        DeltaChurn["Projected Customer Churn Delta (%)"]
        RiskScore["Comprehensive Execution Risk Score (0-100)"]
    end

    BaselineState & SimParams --> TwinInit
    TwinInit --> SubTwinCust & SubTwinRest & SubTwinOps & SubTwinFin
    SubTwinCust & SubTwinRest & SubTwinOps & SubTwinFin --> MonteCarlo
    MonteCarlo --> CrossElasticity
    CrossElasticity --> DeltaGMV & DeltaDelays & DeltaChurn & RiskScore
    Simulation_Outputs --> UIReport["Visual Impact Report & Prescriptive Trade-off Matrix"]
```

---

## 11. React Frontend Architecture

The React frontend is built on React 18, Vite, TypeScript, and Tailwind CSS. It delivers a fast, responsive user interface styled with crisp white cards, light slate backgrounds, royal blue accents, and accessible typography.

```mermaid
graph TD
    subgraph Core_Shell ["Application Core & State Shell"]
        App["App.tsx (Root Component)"]
        ThemeCtx["ThemeContext.tsx (Brand Design Tokens)"]
        HeaderNav["HeaderNav.tsx (System Status, Global Search)"]
        Sidebar["Sidebar.tsx (Navigation & Route Switcher)"]
    end

    subgraph State_And_Services ["Services & Communication Layer"]
        APIClient["api.ts (Axios REST Service + Interceptors)"]
        AuthHandler["Auth & Token Storage Service"]
        SSEListener["SSE Stream Listener (EventSource Hook)"]
    end

    subgraph Intelligence_Views ["Nine Core Intelligence Views"]
        V1["ExecutiveOverviewView.tsx"]
        V2["CustomerIntelligenceView.tsx"]
        V3["RestaurantIntelligenceView.tsx"]
        V4["OperationsIntelligenceView.tsx"]
        V5["FinancialIntelligenceView.tsx"]
        V6["DecisionCenterView.tsx"]
        V7["DecisionSimulatorView.tsx"]
        V8["CommandCenterView.tsx (Digital Twin)"]
        V9["ExecutiveAiCopilotView.tsx"]
    end

    subgraph Shared_UI_Components ["Component Design Library"]
        KpiCard["KpiCard.tsx (Metric + Delta + Sparkline)"]
        DataTable["DataTable.tsx (Sort, Search, Paginate)"]
        SectionHeader["SectionHeader.tsx"]
        StatusBadge["StatusBadge.tsx"]
        FloatingChatbot["FloatingChatbot.tsx (AI Assistant Drawer)"]
    end

    App --> ThemeCtx
    ThemeCtx --> HeaderNav & Sidebar
    Sidebar --> Intelligence_Views
    Intelligence_Views --> Shared_UI_Components
    Intelligence_Views --> APIClient
    Intelligence_Views --> SSEListener
    APIClient --> AuthHandler
```

---

## 12. Streamlit Analytics Platform Architecture

The Streamlit application (`streamlit_app/app.py`) provides an interactive analytics environment featuring **Dual Database Resolution** that allows seamless transitions between live MySQL database querying and bundled offline CSV datasets.

```mermaid
graph TD
    UserReq["User Browser Request (:8501)"]
    
    subgraph Streamlit_Runtime ["Streamlit Multi-Page Runtime"]
        AppMain["app.py (Navigation & Global Layout)"]
        SidebarNav["Sidebar Navigation (8 Analytical Pages)"]
        CustomStyles["styles/theme.css (Official Brand Tokens)"]
    end

    subgraph Data_Connection_Layer ["Dual-Resolution Connection Engine"]
        ConnMgr["database/connection.py"]
        SecretProbe["Check st.secrets / OS Environment"]
        LiveConn["Live MySQL Connection Pool"]
        OfflineLoader["Offline CSV Loader (datasets/cleaned/)"]
    end

    subgraph Pages_Module ["Analytics Modules"]
        P1["1_Overview.py"]
        P2["2_Customer_Intelligence.py"]
        P3["3_Restaurant_Performance.py"]
        P4["4_Delivery_Operations.py"]
        P5["5_Financial_Insights.py"]
        P6["6_Prescriptive_Decisions.py"]
        P7["7_Digital_Twin.py"]
        P8["8_AI_Copilot.py"]
    end

    subgraph Visualization_Engine ["Visualization & API Layer"]
        PlotlyRenders["Plotly Express & Graph Objects Charts"]
        FastAPIBridge["FastAPI Client (Streaming AI & Copilot)"]
    end

    UserReq --> AppMain
    AppMain --> CustomStyles
    AppMain --> SidebarNav --> Pages_Module
    Pages_Module --> ConnMgr
    ConnMgr --> SecretProbe
    
    SecretProbe -->|Credentials Valid & DB Reachable| LiveConn
    SecretProbe -->|Credentials Missing or DB Down| OfflineLoader
    
    LiveConn --> MySQLDB[(MySQL 8.0 Live Database)]
    OfflineLoader --> BundledData[(10 Cleaned CSV Datasets)]

    Pages_Module --> PlotlyRenders
    Pages_Module --> FastAPIBridge
```

---

## 13. Power BI Reporting Architecture

The Power BI reporting suite provides strategic reporting for executive stakeholders. It operates on an optimized star schema and incorporates the official brand theme.

```mermaid
flowchart TD
    subgraph Source_Data ["Data Sources"]
        MySQLProd[("MySQL Database: novanest_db")]
        CleanedCSVs[("Cleaned CSV Export")]
    end

    subgraph PowerBI_Model ["Power BI Semantic Data Model"]
        DimCust["dim_customers"]
        DimRest["dim_restaurants"]
        DimRider["dim_riders"]
        DimDate["dim_calendar (DAX Generated)"]
        FactOrders["fact_orders (49,971 rows)"]
        FactDeliveries["fact_deliveries (49,971 rows)"]
        FactPayments["fact_payments (49,971 rows)"]
    end

    subgraph DAX_Measure_Layer ["DAX Enterprise Measures (16 Canonical KPIs)"]
        M1["Gross Merchandise Value (GMV) = SUM(fact_orders[final_amount])"]
        M2["Delivered Order Count = CALCULATE(COUNTROWS(), status='Delivered')"]
        M3["Platform Contribution Profit = [Total Revenue] - [Direct Delivery Costs]"]
        M4["On-Time Delivery Rate = DIVIDE([On Time Count], [Total Delivered])"]
    end

    subgraph Visual_Reports ["Visual Dashboards (NovaNest_themed.pbix)"]
        Page1["1. Executive Overview & Financial Health"]
        Page2["2. Customer LTV, Cohorts & Churn Risk"]
        Page3["3. Restaurant Partner Yield & Menus"]
        Page4["4. Rider Fleet & Last-Mile Operations"]
    end

    Source_Data --> FactOrders & FactDeliveries & FactPayments
    Source_Data --> DimCust & DimRest & DimRider & DimDate
    
    DimCust --> FactOrders
    DimRest --> FactOrders
    DimRider --> FactOrders
    DimDate --> FactOrders
    FactOrders --> FactDeliveries
    FactOrders --> FactPayments

    PowerBI_Model --> DAX_Measure_Layer
    DAX_Measure_Layer --> Visual_Reports
```

---

## 14. System Security Architecture

NovaNest adopts a defense-in-depth security approach that spans from edge proxying to runtime application controls and least-privilege database role separation.

```mermaid
graph TD
    Client["Client / External Web Traffic"]
    
    subgraph Edge_Security ["Layer 1: Edge & Network Security"]
        Nginx["Nginx Reverse Proxy"]
        TLS["Let's Encrypt TLS 1.2 / 1.3 Encryption"]
        Headers["Security Headers<br/>(HSTS, CSP, X-Frame-Options, X-Content-Type)"]
        RateLimit["Rate Limiting<br/>(10 req/s general, 5 req/s AI endpoints)"]
    end

    subgraph App_Security ["Layer 2: Application & API Security"]
        TokenAuth["Bearer Token Authentication"]
        RBAC["Role-Based Access Control (RBAC)<br/>• Admin: Read/Write/Ops/Simulate<br/>• Operator: Operational Access<br/>• Viewer: Read-Only Overview"]
        InputSanitizer["SQL Injection Defense<br/>(Whitelist-based sorting & query parameters)"]
    end

    subgraph AI_Security ["Layer 3: AI & Guardrail Defense"]
        PromptGuard["Prompt Injection Heuristics Scanner"]
        OutputVerifier["OutputVerifier Security Gate<br/>(Fact-Checking, Citation Validation)"]
    end

    subgraph Database_Security ["Layer 4: Database Least Privilege"]
        DBUserApp["novanest_app User<br/>(SELECT on all, INSERT/UPDATE on 5 tables, NO DDL)"]
        DBAdmin["novanest_root User<br/>(Schema Maintenance & Disaster Recovery Only)"]
    end

    Client --> TLS --> Headers --> RateLimit --> Nginx
    Nginx --> TokenAuth --> RBAC --> InputSanitizer
    InputSanitizer --> PromptGuard --> OutputVerifier
    InputSanitizer --> DBUserApp
    DBAdmin -.->|Restricted Maintenance| DBUserApp
```

---

## 15. Monitoring & Observability Architecture

The observability stack monitors runtime performance, database query latencies, API request rates, and multi-agent AI execution states.

```mermaid
graph LR
    subgraph Application_Sources ["Instrumentation Sources"]
        FastAPIApp["FastAPI Engine (:8000)<br/>Prometheus Middleware"]
        AgentEngine["Multi-Agent Subsystem<br/>Telemetry & Tracing Events"]
        MySQLApp["MySQL Database<br/>Slow Query Log & Connections"]
    end

    subgraph Collection_Layer ["Metrics Collection & Scraping"]
        PrometheusServer["Prometheus Server (:9090)<br/>Scrape Interval: 15s"]
        TraceLogger["Structured JSON Logger<br/>(TraceID, SessionID, Duration)"]
    end

    subgraph Visualization_And_Alerts ["Observability Dashboards"]
        GrafanaServer["Grafana Dashboards (:3000)"]
        subgraph Dashboards ["Monitored Dashboards"]
            D1["System Health & Request Latency"]
            D2["API Throughput & Error Rates (4xx, 5xx)"]
            D3["Multi-Agent Token & Execution Traces"]
            D4["Database Connection Pool Saturation"]
        end
        AlertMgr["Alert Notification Manager<br/>(Threshold Breaches & Latency Spikes)"]
    end

    FastAPIApp -->|/api/metrics| PrometheusServer
    AgentEngine --> TraceLogger
    AgentEngine --> FastAPIApp
    MySQLApp --> FastAPIApp
    PrometheusServer --> GrafanaServer
    GrafanaServer --> Dashboards
    PrometheusServer --> AlertMgr
```

---

## 16. Docker Infrastructure & Deployment Architecture

The entire platform is containerized using multi-container Docker Compose architectures for both development and production environments.

```mermaid
graph TB
    subgraph Host_Environment ["Docker Host (Linux VPS / Windows Dev)"]
        subgraph Network_Bridge ["Bridge Network: novanest-net (172.28.0.0/16)"]
            
            subgraph Web_Containers ["Ingress & Frontend Services"]
                C_Nginx["novanest_nginx<br/>Ports: 80, 443<br/>Reverse Proxy & SSL"]
                C_React["novanest_frontend<br/>Port: 5173 / 80<br/>Node.js / Nginx Alpine"]
                C_Streamlit["novanest_streamlit<br/>Port: 8501<br/>Python 3.11 Runtime"]
            end

            subgraph Backend_Containers ["Core Application Services"]
                C_FastAPI["novanest_api<br/>Port: 8000<br/>Uvicorn ASGI | 4 Workers"]
            end

            subgraph Storage_Containers ["Database & Volume Services"]
                C_MySQL["novanest_db<br/>Port: 3306<br/>MySQL 8.0 Server"]
                Vol_Data[("mysql_data Volume<br/>Persistent Storage")]
            end

            subgraph Observability_Containers ["Monitoring Services"]
                C_Prom["novanest_prometheus<br/>Port: 9090"]
                C_Graf["novanest_grafana<br/>Port: 3000"]
                C_Certbot["novanest_certbot<br/>Let's Encrypt Automation"]
            end

        end
    end

    C_Nginx --> C_React
    C_Nginx --> C_Streamlit
    C_Nginx --> C_FastAPI
    C_FastAPI --> C_MySQL
    C_Streamlit --> C_MySQL
    C_Streamlit --> C_FastAPI
    C_MySQL --- Vol_Data
    C_Prom --> C_FastAPI
    C_Graf --> C_Prom
    C_Certbot -.-> C_Nginx
```

---

## 17. Complete End-to-End Business Data Flow

This diagram illustrates the lifecycle of a single customer transaction and its downstream propagation across machine learning inference, real-time analytics, AI agent alerts, and executive decisioning.

```mermaid
sequenceDiagram
    autonumber
    actor Customer as Mobile App Customer
    participant AppEvents as App Event Collector
    participant MySQL as MySQL 8.0 DB
    participant ML as ML Inference Engine
    participant OpsAgent as Operations AI Agent
    participant Prescriptive as Prescriptive Engine
    participant Dashboard as React / Streamlit Dashboard
    actor Exec as Operations Director

    Customer->>AppEvents: Place Order (Item, Restaurant, Address)
    AppEvents->>MySQL: Insert into orders_table & payments (Status='Placed')
    
    par ML Feature Enrichment
        MySQL->>ML: Trigger Delivery ETA Model
        ML-->>MySQL: Predicted ETA: 32 min (HistGradientBoosting)
    and Anomaly Verification
        MySQL->>ML: Run Consensus Anomaly Detection
        ML-->>MySQL: Anomaly Score: 0.12 (Normal Transaction)
    end

    MySQL->>OpsAgent: Order Delayed Alert (> 45 min threshold)
    OpsAgent->>Prescriptive: Evaluate Surge in Zone & Rider Deficit
    Prescriptive->>MySQL: Generate Prescriptive Action: "Reallocate 5 Riders to Zone B"
    
    MySQL->>Dashboard: Stream Real-Time KPI Update (GMV, Active Orders)
    Dashboard->>Exec: Display Prescriptive Alert on Decision Center
    Exec->>Dashboard: Click [Approve Reallocation]
    Dashboard->>OpsAgent: Dispatch Rider Rebalance Instructions
```

---

### Architectural Verification & Conformance Sign-Off
- **Diagrams Verified**: 17 / 17 complete, rendered with Mermaid standard syntax.
- **Microservice Decoupling**: Complete separation between React SPA, Streamlit BI, FastAPI Application, AI Orchestration, and MySQL Datastore.
- **Data Parity**: 100% adherence to 304,405 canonical rows and 16 enterprise KPIs.
- **Security Posture**: Multi-tier defense covering Edge TLS, Token RBAC, SQL-injection whitelists, and AI OutputVerifier guardrails.
