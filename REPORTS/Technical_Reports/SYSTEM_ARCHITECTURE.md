# NOVANEST — SYSTEM ARCHITECTURE DOCUMENTATION
## End-to-End Architectural Blueprint, Component Design & Data Flow Specifications

**Document Version:** 2.0.0 (Production Commissioned)  
**Author:** Principal Platform Architect  
**Audience:** Technical Evaluators, System Architects, SRE Engineers, Academic Reviewers  

---

### 1. Executive System Overview

NovaNest is a full-stack, enterprise-grade business intelligence and prescriptive decision-support platform designed for high-velocity quick commerce and food delivery operations. The platform transforms fragmented transactional records into actionable, financially quantified business recommendations governed by mandatory human approval.

The system is engineered as a hardened, multi-tier distributed architecture combining a React 18 single-page application (SPA), an alternative Streamlit executive workspace, a high-throughput FastAPI REST engine, an in-process multi-agent artificial intelligence orchestrator, a relational MySQL 8.0 core database, a Docker container fleet, an Nginx edge reverse proxy with TLS/HSTS and rate limiting, and an autonomic site reliability engineering (SRE) observability stack powered by Prometheus, Grafana, and OpenTelemetry.

```mermaid
flowchart TD
    subgraph ClientLayer ["1. Presentation & Client Layer"]
        ReactSPA["React 18 SPA (TypeScript + Vite)<br/>Port 80 / 443 via Nginx"]
        StreamlitApp["Streamlit Multipage Hub<br/>Port 8502 (Container) / 8501 (Host)"]
        PowerBIApp["Power BI Desktop (.pbix)<br/>27 DAX Measures / 5 Pages"]
    end

    subgraph EdgeLayer ["2. Edge & Ingress Security Layer"]
        NginxProxy["Nginx Reverse Proxy & SSL Termination<br/>TLSv1.2/1.3 | HSTS | Port 80 Redirect<br/>Rate Limiting: 50r/s API / 10r/s AI"]
    end

    subgraph APILayer ["3. Application & Middleware Layer"]
        FastAPIApp["FastAPI REST Backend (Python 3.11+)<br/>Port 8001 (Container) / 8000 (Host)"]
        RBAC["Token-Based RBAC<br/>Scopes: viewer | operator | admin"]
        RateLimiter["Sliding-Window Rate Limiter & IP Lockout"]
        TracingMiddleware["W3C Distributed Tracing Middleware<br/>traceparent Context Injection"]
        MetricsMiddleware["Prometheus Metrics Recorder<br/>Cardinality Normalizer"]
        CircuitBreaker["Autonomic Database Circuit Breaker<br/>Closed | Open | Half-Open"]
    end

    subgraph MultiAgentLayer ["4. Intelligence & Multi-Agent Layer"]
        MasterOrch["Master Orchestrator (Hub-and-Spoke)<br/>Intent Classification & Context Propagation"]
        Stage1Exec["Stage 1: Parallel Domain Analysis<br/>(Financial, Customer, Operations, Restaurant)"]
        Stage2Exec["Stage 2: Sequential Decision Synthesis<br/>(Decision Agent & Trade-Off Matrix)"]
        OutputVerifier["Deterministic Output Verifier<br/>Fact Grounding & Leakage Guardrails"]
        ConversationalMem["Conversation Manager<br/>Caller-Scoped Memory | PII Redaction"]
    end

    subgraph DecisionLayer ["5. Machine Learning & Prescriptive Layer"]
        ModelRegistry["ML Model Registry (models/registry_index.json)<br/>SHA-256 Hashing | Confidence Tiers"]
        MLModels["5 Trained Models: Churn, ETA, Demand, Restaurant, Anomaly"]
        PrescriptiveEngine["Prescriptive Recommendation Engine<br/>Customer Retention, Unit Margin, Logistics"]
        ScenarioSim["What-If Scenario Simulator<br/>5 Business Scenarios | Projection Disclaimers"]
        LifecycleManager["Recommendation Lifecycle State Machine<br/>Human Approval Gate (HumanApprovalRequiredError)"]
    end

    subgraph PersistenceLayer ["6. Persistence & Storage Layer"]
        MySQLDB[("MySQL 8.0 InnoDB (novanest_db)<br/>10 Canonical Tables | 304,405 Records | 11 FKs")]
        CSVCache[("Authoritative CSV File Store<br/>datasets/cleaned/ (Fallback Cache)")]
        BinlogArchiver["15-Min Incremental Binlog Archiver<br/>AES-256-CBC + HMAC Sidecars (RPO <= 15m)"]
    end

    subgraph ObservabilityLayer ["7. SRE & Observability Infrastructure"]
        PrometheusServer["Prometheus Server (:9090)<br/>15s Scrapes | 8 Alert Rules"]
        GrafanaServer["Grafana Provisioned UI (:3001)<br/>4 Dashboards: App, DB, Infra, Business"]
        AlertWebhook["HMAC-SHA256 Alert Webhook Dispatcher<br/>URL Secret Masking"]
    end

    %% Ingress Connections
    ReactSPA -->|HTTP/HTTPS| NginxProxy
    NginxProxy -->|Proxy Pass /api| FastAPIApp
    StreamlitApp -->|Internal HTTP| FastAPIApp
    PowerBIApp -.->|Direct Relational Read| MySQLDB

    %% Middleware flow
    FastAPIApp --> RBAC
    RBAC --> RateLimiter
    RateLimiter --> TracingMiddleware
    TracingMiddleware --> MetricsMiddleware
    MetricsMiddleware --> CircuitBreaker

    %% App to Intelligence & DB
    CircuitBreaker -->|Active Connection| MySQLDB
    CircuitBreaker -.->|Failover on DB Loss| CSVCache
    FastAPIApp --> MasterOrch
    FastAPIApp --> DecisionLayer

    %% Multi-Agent Pipeline
    MasterOrch --> Stage1Exec
    Stage1Exec --> Stage2Exec
    Stage2Exec --> OutputVerifier
    OutputVerifier --> MasterOrch
    MasterOrch <--> ConversationalMem
    Stage1Exec --> ModelRegistry
    Stage2Exec --> PrescriptiveEngine

    %% Persistence & Backup
    MySQLDB --> BinlogArchiver
    PrometheusServer -->|Scrape /api/metrics| FastAPIApp
    GrafanaServer -->|Query PromQL| PrometheusServer
    PrometheusServer -->|Fire Alerts| AlertWebhook
```

---

### 2. Multi-Tier Architecture Breakdown

#### Tier 1: Presentation & User Experience Layer
NovaNest provides dual operational interfaces designed for distinct executive and operational workflows:
1. **React 18 Single-Page Application (`frontend/`)**:
   - **Technology Stack**: React 18, TypeScript 5, Vite, Tailwind CSS, Lucide React, Framer Motion.
   - **Key Views**:
     - *Executive Overview*: High-level financial KPIs, revenue vs gross profit, city filter bar (`All`, `Bangalore`, `Chennai`, `Coimbatore`, `Hyderabad`, `Vijayawada`).
     - *Recommendation Action Center*: Executive portfolio summary strip, multi-criteria filtering, modal approval/rejection workflows, and audited contribution margin waterfall view.
     - *Customer 360*: Detailed customer profiles, RFM segmentation, and commercial discount guardrails with transparent `LOW_EMPIRICAL` churn caveats.
     - *Restaurant 360*: Merchant operations, kitchen preparation times, and bottleneck remediation action plans.
     - *Rider Operations*: Fleet workload ratios, SLA breach tails (>45m), and live GPS telematics disclaimers.
     - *What-If Decision Lab*: Interactive scenario simulation sliders across 5 business archetypes.
     - *AI Intelligence & Chatbot*: Full-page and floating conversational interfaces with animated agent execution cards and real-time Server-Sent Events (SSE) streaming progress.
   - **Resilience**: Decoupled error boundaries (`ErrorBoundary`), empty state fallbacks (`EmptyStateCard`), and token authentication recovery states (`ApiErrorState`).

2. **Streamlit Executive Hub (`streamlit_app/`)**:
   - **Technology Stack**: Python 3.11+, Streamlit 1.54+, Plotly.
   - **Capabilities**: Multipage workspace (`01_Executive_Overview.py` through `09_Command_Center.py`), zero deprecation warnings (migrated off `use_container_width`), hybrid parity routing queries to `MasterOrchestrator`, live telemetry status rendering, and in-place contextual AI buttons.

3. **Power BI Semantic Layer (`powerbi/NovaNest.pbix`)**:
   - 5 enterprise report pages, 66 visual containers, 27 DAX measures. Verified schema compatibility with zero binary modifications.

---

#### Tier 2: Edge & Ingress Security Layer
All incoming web traffic is mediated by the edge reverse proxy:
- **Nginx Reverse Proxy (`docker/nginx.prod.conf`)**:
  - **TLS Termination**: Strict TLSv1.2 and TLSv1.3 with Mozilla modern cipher suites.
  - **Port 80 Redirect**: Unencrypted HTTP traffic on port 80 is redirected with HTTP 301 to HTTPS.
  - **HSTS Enforcement**: `Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;`.
  - **Security Headers**: `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `X-XSS-Protection: 1; mode=block`, `Referrer-Policy: strict-origin-when-cross-origin`.
  - **Rate Limiting Engine**:
    - Standard API Zone: `50 requests/second` with a burst of `30` (nodelay).
    - AI & Simulation Zone: `10 requests/second` with a burst of `5` (nodelay).
  - **Real-Time Streaming**: Bufferless SSE proxying (`proxy_buffering off; chunked_transfer_encoding off;`).

---

#### Tier 3: Application & Middleware Layer
- **FastAPI Engine (`api/main.py`)**:
  - Built with Python 3.11+ and Pydantic v2. Exposes over 35 production REST endpoints.
  - **Authentication & RBAC (`api/auth.py`)**:
    - Validates incoming Bearer tokens and `X-API-Key` headers.
    - Tiered scopes: `viewer` (read-only), `operator` (recommendation approval & lifecycle updates), `admin` (system controls, key rotation, disaster recovery).
    - Single-use stream tickets: `POST /api/ai/stream-ticket` exchanges authenticated credentials for a 60-second, single-use ticket (`st_...`), eliminating static token exposure in query parameters.
  - **W3C Distributed Tracing Middleware (`python/operations/tracing.py`)**:
    - Injects and propagates standard W3C `traceparent` headers (`00-{trace_id}-{span_id}-{flags}`).
    - Context maintained across asynchronous coroutines and worker threads via `contextvars.ContextVar`.
    - Auto-redacts sensitive secrets (`[REDACTED_SECRET]`), emails (`[REDACTED_EMAIL]`), and phone numbers (`[REDACTED_PHONE]`).
  - **Autonomic Database Circuit Breaker (`python/operations/health_circuit_breaker.py`)**:
    - Wraps all database access in a thread-safe state machine (`CLOSED` -> `OPEN` -> `HALF-OPEN`).
    - On database failure, trips to `OPEN` in 0.0003s, immediately routing read requests to the authoritative CSV file store (`datasets/cleaned/`) to guarantee 100% read availability.
    - Write requests and lifecycle mutations are explicitly suspended during database loss to prevent split-brain states and protect transactional integrity.

---

#### Tier 4: Intelligence & Multi-Agent Architecture
NovaNest features a multi-agent artificial intelligence subsystem implementing an in-process Hub-and-Spoke topology:

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Executive
    participant UI as React SPA / Streamlit
    participant API as FastAPI REST Engine
    participant MO as Master Orchestrator
    participant S1 as Stage 1 Agents (Parallel)
    participant S2 as Stage 2 Decision Agent
    participant OV as Output Verifier
    participant DB as MySQL novanest_db

    User->>UI: Submit inquiry ("Evaluate VIP churn in Bangalore")
    UI->>API: POST /api/ai/ask { query, session_id }
    API->>MO: route_and_execute(query, context)
    MO->>MO: Classify Intent & Resolve Memory
    MO->>S1: Fan-out: Financial, Customer, Operations Agents
    par Financial Agent
        S1->>DB: Query revenue, AOV, discounts
    and Customer Agent
        S1->>DB: Query RFM, LTV, churn risks
    and Operations Agent
        S1->>DB: Query delivery times, SLA breach tail
    end
    S1-->>MO: Return grounded facts & domain findings
    MO->>S2: Fan-in to Decision Agent (Context + Stage 1 Facts)
    S2->>S2: Synthesize trade-offs & recommend intervention
    S2-->>MO: Return structured Action Recommendation
    MO->>OV: Validate numbers against certified KPIs
    OV-->>MO: Grounding verified (zero hallucination)
    MO-->>API: Synthesized narrative, facts, recommendations
    API-->>UI: Return HTTP 200 JSON payload
    UI-->>User: Render verified response & recommendation card
```

1. **Master Orchestrator (`python/ai/agents/master_orchestrator.py`)**:
   - Classifies query intent across 5 functional domains.
   - Extracts active filters (city, entity ID) and retrieves conversation history from `ConversationManager`.
   - Executes zero-copy data slicing backed by pandas Copy-on-Write (14.7x speedup: 40.27ms -> 2.74ms).
2. **Stage 1: Parallel Domain Analysis**:
   - `FinancialAgent`: Analyzes GMV, net revenue, margins, and promotional subsidies.
   - `CustomerAgent`: Analyzes customer retention, RFM segments, and churn probabilities.
   - `OperationsAgent`: Analyzes rider fleet allocation, transit delays, and SLA breach tails.
   - `RestaurantAgent`: Analyzes merchant volume, kitchen delays, and commission tiers.
3. **Stage 2: Sequential Decision Synthesis**:
   - `DecisionAgent`: Ingests Stage 1 facts, balances operational trade-offs, and formulates high-impact prescriptive recommendations.
4. **Deterministic Output Verifier (`python/ai/agents/output_verifier.py`)**:
   - Parses currency figures, percentages, and order counts in agent narratives.
   - Reconciles every figure against certified canonical KPIs, rejecting hallucinations or ungrounded statistics.

---

#### Tier 5: Prescriptive Analytics & Decision Optimization
- **Prescriptive Engine (`python/decision/`)**:
  - Translates analytical findings into structured `PrescriptiveRecommendation` contracts.
  - Computes projected gross benefits, implementation costs, and net impact.
- **Controlled What-If Simulation Engine (`python/decision/scenario_simulation_engine.py`)**:
  - Simulates 5 business archetypes: *Customer Retention Boost*, *Commission Restructuring*, *Delivery SLA Compression*, *Promotional Rationalization*, and *Fleet Incentive Tuning*.
  - Every simulation response includes explicit amber projection disclaimers (`is_simulation_projection=True`), distinguishing projections from historical accounting.
- **Recommendation Lifecycle State Machine (`python/decision/recommendation_lifecycle.py`)**:
  - Enforces 6 discrete states:
    $$\text{PROPOSED} \longrightarrow \text{APPROVED} \longrightarrow \text{IN\_PROGRESS} \longrightarrow \text{IMPLEMENTED} \longrightarrow \text{MONITORED\_AND\_CLOSED}$$
    $$\text{PROPOSED} \longrightarrow \text{REJECTED}$$
  - **Human-in-the-Loop Gate**: If an automated script attempts to execute or advance an unapproved recommendation, the engine raises `HumanApprovalRequiredError`.

---

#### Tier 6: Persistence & Database Layer
- **Relational Database (`novanest_db`)**:
  - MySQL 8.0 InnoDB engine storing exactly **304,405 records** across 10 normalized tables.
  - Enforces 11 foreign key constraints with `RESTRICT` delete/update semantics, guaranteeing zero orphan rows.
  - Configured with 19 secondary B-tree indexes optimizing analytical joins and filtering.
- **Least-Privilege Security Roles**:
  - `novanest_app`: Read/Write DML (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) with zero DDL permissions.
  - `novanest_loader`: Ingestion credentials with temporary table creation.
  - `novanest_backup`: Minimal privileges (`RELOAD`, `REPLICATION CLIENT`, `LOCK TABLES`) for non-root automated backups.
- **15-Minute Incremental Binary-Log Archiver (`python/operations/binlog_archiver.py`)**:
  - Periodically executes `FLUSH BINARY LOGS;`, encrypts closed binary logs using AES-256-CBC, and computes companion HMAC-SHA256 signature sidecars (`.enc.sig`).
  - Empirically certifies an intraday Recovery Point Objective (RPO) of **$\le$ 15.0 minutes**.
  - **Fatal Safety Guardrail**: Programmatically aborts with `ValueError` if any restoration or binlog replay targets production `novanest_db`, forcing recovery drills into isolated test schemas (`novanest_restore_isolated`).

---

#### Tier 7: SRE Observability & Monitoring Layer
- **Prometheus Scrape Daemon (:9090)**:
  - Scrapes `/api/metrics` every 15 seconds using Bearer token authentication.
  - Tracks API request rates, latency histograms, database connection pool utilization, CPU, and memory.
  - 8 operational alert rules loaded in `docker/prometheus/alert_rules.yml`.
- **Grafana Provisioning (:3001)**:
  - 4 automated production dashboards loaded: *Application Health*, *Database Health*, *Infrastructure Health*, and *Business Operations*.
- **HMAC-SHA256 Alert Webhook Dispatcher (`python/operations/alert_webhook.py`)**:
  - Automatically signs webhook notification payloads with `WEBHOOK_HMAC_SECRET` and scrubs sensitive credentials from target URLs.

---

### 3. Comprehensive Data Flow Architecture

The end-to-end data processing lifecycle is structured into four distinct stages:

```mermaid
flowchart LR
    subgraph S1 ["Stage 1: Raw Ingestion"]
        RawCSV["10 Raw CSV Files<br/>(datasets/cleaned/*.csv)"]
        CleanData["clean_data.py<br/>Type Casts & Null Stripping"]
    end

    subgraph S2 ["Stage 2: Relational Ingestion"]
        LoadMySQL["load_mysql.py<br/>FK Dependency Sequence"]
        MySQLRel[("MySQL novanest_db<br/>304,405 Records / 11 FKs")]
    end

    subgraph S3 ["Stage 3: Feature & ML Engineering"]
        FeatEng["feature_engineering.py<br/>Leak-Free Windows"]
        TrainML["Model Training & Registry<br/>TreeSHAP / Metrics"]
        EngineeredCSV["Engineered Datasets<br/>(datasets/engineered/)"]
    end

    subgraph S4 ["Stage 4: Serving & Business Intelligence"]
        APIServer["FastAPI REST Backend"]
        ReactUI["React 18 SPA"]
        StreamlitUI["Streamlit Workspace"]
    end

    RawCSV --> CleanData
    CleanData --> LoadMySQL
    LoadMySQL --> MySQLRel
    MySQLRel --> FeatEng
    FeatEng --> TrainML
    TrainML --> EngineeredCSV
    MySQLRel --> APIServer
    EngineeredCSV --> APIServer
    APIServer --> ReactUI
    APIServer --> StreamlitUI
```

---

### 4. Architectural Quality Attributes & Non-Functional Verification

| Quality Attribute | Architectural Mechanism | Empirical Benchmark / Evidence |
| :--- | :--- | :--- |
| **Availability** | Multi-service Docker containers, health probes, and self-healing circuit breaker with local CSV fallback. | **100% Read Availability** during database downtime simulations (0 dropped read requests). |
| **Latency** | Nginx keepalive upstreams, in-memory route caching, pandas Copy-on-Write zero-copy data slicing. | **API Health p50: 14.44ms** | **Nginx Proxy p50: 8.93ms** | **SPA Static p50: 4.51ms**. |
| **Throughput & Protection** | Nginx rate limiting zones (`50r/s burst=30`) protecting upstream FastAPI connection pools. | **392.46 RPS handled**; volumetric flood successfully intercepted and rate-limited (HTTP 503). |
| **Durability (RPO)** | Daily Encrypt-then-MAC AES-256 snapshots combined with **15-minute incremental binary-log archiving**. | **Empirical RPO $\le$ 15.0 minutes (900s)** (certified 96x improvement over daily backups). |
| **Recoverability (RTO)** | Streamlined automated restoration engine importing verified SQL dumps into isolated schemas. | **Empirical RTO: 7.95 seconds** (0.26s decrypt + 7.51s SQL load vs $\le$ 30.0s SLA target). |
| **Security** | TLSv1.2/1.3, HSTS (31536000), fail-closed RBAC, single-use stream tickets, SQL AST validation, PII scrubbing. | **0 Plaintext Secrets Exposed**; 19/19 SQL injection vectors blocked; prompt injections neutralized. |
| **Integrity** | Deterministic OutputVerifier reconciling agent outputs against certified MySQL ground truth. | **₹0.00 Variance** across all 12 canonical financial metrics; zero hallucination permitted. |
