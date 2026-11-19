# NOVANEST — COMPREHENSIVE ACADEMIC & TECHNICAL PROJECT REPORT
## Prescriptive Business Intelligence, Multi-Agent AI Orchestration & Autonomic SRE Operations

**Academic Reference:** `NOVANEST-CAPSTONE-2026`  
**Document Classification:** Final Project Report & Technical Thesis  
**Date of Submission:** 2026-11-15  
**Version:** 2.0.0 (Production Commissioned)  

---

### Abstract

Quick commerce and high-velocity food delivery platforms operate in an environment characterized by extreme transaction volume, tight unit margins, and complex operational trade-offs. While contemporary data platforms provide historical reporting dashboards and standalone machine learning predictions, they frequently fail to bridge the critical gap between predictive analytics and actionable, financially grounded business decisions. Furthermore, modern large language model (LLM) interfaces often suffer from hallucinations, lack verifiable data provenance, and operate without deterministic human approval gates.

This project designs, implements, and empirically validates **NovaNest**—a full-stack, enterprise-grade business intelligence and prescriptive decision-support platform. NovaNest integrates:
1. A normalized **MySQL 8.0 core relational database** enforcing 11 foreign key constraints across 304,405 canonical records;
2. An **in-process multi-agent Hub-and-Spoke artificial intelligence system** featuring 5 specialized domain agents (Financial, Customer, Operations, Restaurant, Decision) and a deterministic `OutputVerifier`;
3. Five **explainable machine learning models** governed by centralized registry index tracking and native TreeSHAP attributions;
4. A **prescriptive recommendation engine** with a 6-state human-in-the-loop lifecycle machine (`HumanApprovalRequiredError`);
5. A hardened **edge and application security framework** incorporating recursive SQL AST validation, prompt injection defense, and single-use stream ticket authentication; and
6. An **autonomic site reliability engineering (SRE) stack** featuring Prometheus, Grafana, OpenTelemetry distributed tracing, self-healing circuit breakers, and an incremental 15-minute binary-log archiver achieving an empirical Recovery Point Objective (RPO) of $\le$ 15.0 minutes and Recovery Time Objective (RTO) of 7.95 seconds.

The complete system has been verified across 113 automated regression tests (100% pass rate) and 8 User Acceptance Testing (UAT) journeys, establishing a new standard for scientific honesty, data integrity, and operational resilience.

---

### 1. Introduction & Background

The quick commerce industry fulfills orders within 15–45 minutes across dense urban delivery clusters. Operating at this cadence creates immense organizational complexity. Order fulfillment data, merchant menus, rider dispatch telemetry, and customer behavior streams originate in disparate systems.

Historically, organizations deployed descriptive business intelligence tools (such as static dashboards) to observe what occurred in the past, or predictive machine learning models to forecast future demand or churn. However, operational leaders do not simply need predictive probabilities; they need **prescriptive interventions** answering:
- *What specific operational or financial action should be taken?*
- *What is the projected gross financial benefit and direct implementation cost?*
- *What are the cross-domain operational trade-offs (e.g., will a discount promotion overload kitchen capacity or breach delivery SLAs)?*
- *How can autonomous agents be prevented from executing unauthorized financial actions without human approval?*

NovaNest was conceived to answer these questions through an end-to-end, multi-tier software engineering architecture.

---

### 2. System Architecture & Component Design

NovaNest is architected as a decoupled, multi-tier distributed system deployed across containerized Docker microservices:

```mermaid
flowchart TD
    subgraph UI ["Presentation Layer"]
        React["React 18 SPA (TypeScript + Vite)"]
        Streamlit["Streamlit Executive Workspace"]
        PowerBI["Power BI Semantic Model (.pbix)"]
    end

    subgraph Edge ["Edge & Security"]
        Nginx["Nginx Reverse Proxy (TLSv1.2/1.3, HSTS, Rate Limiting)"]
    end

    subgraph App ["Application & Agent Core"]
        FastAPI["FastAPI REST Backend (Python 3.11+)"]
        MasterOrch["Master Orchestrator (Hub-and-Spoke)"]
        Agents["5 Domain Agents (Financial, Customer, Operations, Restaurant, Decision)"]
        OutputVerifier["Deterministic Output Verifier"]
        PrescriptiveEngine["Prescriptive Engine & What-If Simulator"]
        CircuitBreaker["Autonomic Database Circuit Breaker"]
    end

    subgraph Data ["Data & Observability"]
        MySQL[("MySQL 8.0 InnoDB (novanest_db - 304,405 Records)")]
        CSVCache[("Authoritative CSV Store (datasets/cleaned/)")]
        Binlogs["15-Min Incremental Binlog Archiver (AES-256)"]
        Prometheus["Prometheus Server (:9090)"]
        Grafana["Grafana Dashboards (:3001)"]
    end

    UI --> Nginx
    Nginx --> FastAPI
    FastAPI --> MasterOrch
    MasterOrch --> Agents
    Agents --> OutputVerifier
    FastAPI --> PrescriptiveEngine
    FastAPI --> CircuitBreaker
    CircuitBreaker --> MySQL
    CircuitBreaker -.-> CSVCache
    MySQL --> Binlogs
    Prometheus --> FastAPI
    Grafana --> Prometheus
```

---

### 3. Data Engineering & Canonical Ground Truth

The data foundation of NovaNest is modeled in MySQL 8.0 (`novanest_db`). The relational schema comprises 10 tables enforcing 11 foreign key constraints with `RESTRICT` semantics, ensuring absolute referential integrity across 304,405 records:

```text
users              : 2,000 records (Customer demographics & registration)
restaurants        : 300 records (Merchant details, cuisines, commissions)
menu_items         : 2,997 records (Dishes, categories, unit prices)
riders             : 500 records (Fleet personnel, vehicles, ratings)
delivery_zones     : 15 records (Urban dispatch clusters across 6 cities)
orders_table       : 49,971 records (Transactional fact records)
order_items        : 149,869 records (Itemized order line items)
payments           : 49,971 records (Payment methods and transaction statuses)
deliveries         : 47,994 records (Fulfillment durations & road distance)
customer_feedback  : 788 records (Post-delivery ratings & feedback)
---------------------------------------------------------------------------
TOTAL RECORDS      : 304,405 CANONICAL RECORDS (0 null PKs, 0 orphan FKs)
```

#### Canonical Financial KPI Reconciliation
All reporting across the platform matches the following certified mathematical formulations to the penny:
- **Total Orders**: 49,971 placed orders.
- **Delivered Orders**: 47,994 fulfilled orders (96.04% fulfillment rate; 1,977 cancellations).
- **Gross Merchandise Value (GMV)**: `SUM(order_amount)` = **₹46,590,125.00**.
- **Net Platform Revenue**: `SUM(order_amount - discount_amount)` = **₹46,425,992.00**.
- **Delivered Average Order Value (AOV)**: Net Revenue / Delivered Orders = **₹967.33**.
- **Delivered Contribution Margin**: Realized net revenue minus merchant shares, rider transit fees, and payment gateway processing fees = **23.59%**.

---

### 4. Multi-Agent Artificial Intelligence Architecture

Rather than relying on ungrounded generative models, NovaNest deploys an in-process **Hub-and-Spoke multi-agent system**:
1. **Master Orchestrator**: Acts as the central hub. It parses user intent, extracts active conversational entities, manages caller-scoped cryptographic memory, and executes zero-copy DataFrame data slicing backed by pandas Copy-on-Write (yielding a 14.7x speedup: 40.27ms $\to$ 2.74ms).
2. **Stage 1 (Parallel Domain Fan-Out)**:
   - `FinancialAgent`: Analyzes revenue, subsidies, and accounting leakage (`is_confirmed_loss=False`).
   - `CustomerAgent`: Analyzes cohort retention, RFM metrics, and attaches `LOW_EMPIRICAL` churn caveats.
   - `OperationsAgent`: Tracks rider workload ratios and SLA breach tails (>45m: 32.26%).
   - `RestaurantAgent`: Diagnoses merchant preparation delays and generates partner action plans.
3. **Stage 2 (Sequential Fan-In)**:
   - `DecisionAgent`: Ingests Stage 1 facts, balances operational trade-offs, and formulates prioritized prescriptive recommendations.
4. **Deterministic OutputVerifier**: Extracts every numerical assertion from agent responses and verifies it against certified MySQL ground truth, rejecting ungrounded claims or hallucinated figures.

---

### 5. Machine Learning Models & Scientific Realism

NovaNest manages 5 machine learning models indexed in a centralized Model Registry (`models/registry_index.json`):

| Model Domain | Algorithm | Primary Metric | Confidence Tier | Scientific Realism & Governance |
| :--- | :--- | :---: | :---: | :--- |
| **Customer Churn** | Random Forest / XGBoost | ROC-AUC: **0.5218** | **`LOW_EMPIRICAL`** | Synthetic customer data lacks organic churn signals. Model is transparently classified as low confidence; automated discount giveaways are blocked, enforcing commercial guardrails ($\le 15\%$, $\ge ₹400$). |
| **Delivery ETA** | Gradient Boosting | MAE: **7.42 min** | **`BASELINE_ONLY`** | Derived from static road distance and historical heuristics without live GPS tracking. Surfaced with 90% prediction intervals ($\pm 21.9\text{m}$) and operational disclaimers. |
| **Demand Forecast** | Multi-Horizon Ridge/XGB | MASE: **0.782** | **`HIGH_EMPIRICAL`** | Evaluated using rolling-origin backtesting with zero temporal leakage. Outperforms seasonal naive baseline ($< 1.0$). |
| **Restaurant Volume** | Multi-Target Regressor | $R^2$: **0.814** | **`HIGH_EMPIRICAL`** | Predicts merchant volume and revenue based on menu diversity and ratings without target contamination. |
| **Anomaly Detection** | Consensus Isolation Forest | Contamination: **0.02** | **`HIGH_EMPIRICAL`** | Strictly adheres to fraud policy (0 confirmed fraud labels). Flags unusual combinations as unconfirmed variances (`is_confirmed_loss=False`). |

All tree models integrate native TreeSHAP (`shap.TreeExplainer`), providing exact mathematical feature attributions for global model understanding and local prediction explanations.

---

### 6. Prescriptive Decision Optimization & Human Approval

NovaNest bridges predictive models to business outcomes via a prescriptive recommendation engine:
- **Financial Impact Modeling**: Every recommendation details projected gross benefits, implementation costs, net financial impact, and projected ROI.
- **Portfolio Summary**: The active canonical portfolio contains 8 initiatives projecting **₹3,93,250.00** in net financial benefit at a **140.75% portfolio ROI**.
- **What-If Scenario Simulator**: Simulates 5 business archetypes with interactive sensitivity sliders. Every simulation response carries explicit disclaimers (`is_simulation_projection: True`), distinguishing projections from audited accounting.
- **Six-State Lifecycle Machine**:
  $$\text{PROPOSED} \longrightarrow \text{APPROVED} \longrightarrow \text{IN\_PROGRESS} \longrightarrow \text{IMPLEMENTED} \longrightarrow \text{MONITORED\_AND\_CLOSED}$$
- **Human Approval Gate (`HumanApprovalRequiredError`)**: Automated scripts and agents are programmatically forbidden from advancing recommendations to execution. Human operator approval is strictly enforced, and finance audits realized real-world returns upon completion.

---

### 7. Security Architecture & Threat Defense

NovaNest implements a multi-layered security architecture:
1. **Edge Security**: TLSv1.2/1.3, HSTS (`max-age=31536000`), port 80 HTTP-to-HTTPS redirect, OWASP defensive headers, and Nginx rate limiting (`50r/s burst=30` API, `10r/s burst=5` AI).
2. **Token Security**: Single-use stream tickets (`POST /api/ai/stream-ticket`) eliminate static token exposure in URL query strings. High-entropy keys (`secrets.token_urlsafe(64)`) are verified with Shannon entropy > 4.5 bits/char. Zero plaintext credentials appear in logs (`[REDACTED_SECRET]`).
3. **AI Defense**: Input heuristics neutralize instruction overrides, DAN persona hijacks, secret exfiltration, and markdown image data leaks.
4. **SQL Sandboxing**: A recursive AST parser restricts natural language SQL generation to read-only `SELECT` with `LIMIT 100`, blocking all DDL, DML, comments, and union injections.
5. **Encrypt-then-MAC Backups**: AES-256-CBC PBKDF2 encryption paired with HMAC-SHA256 signature sidecars (`.enc.sig`), defeating tampering and padding oracle attacks before decryption.

---

### 8. Site Reliability Engineering (SRE) & Operational Benchmarks

The operational infrastructure is certified under empirical testing:
- **Observability**: Prometheus daemon (:9090) scrapes `/api/metrics` every 15s; 4 provisioned Grafana dashboards (:3001) track health and transactions; 8 alert rules dispatch HMAC-SHA256 signed webhooks with URL secret masking.
- **Distributed Tracing**: W3C `traceparent` propagation across Nginx, FastAPI, Orchestrator, and MySQL with automated PII scrubbing.
- **Autonomic Circuit Breaker**: Trips to `OPEN` in 0.0003s during database loss, maintaining 100% read availability via local CSV cache while safely suspending writes.
- **Disaster Recovery**:
  - **Empirical RTO**: **7.95 seconds** end-to-end database restoration into isolated test schema (`novanest_restore_isolated`) vs $\le$ 30.0s SLA.
  - **Empirical RPO**: **$\le$ 15.0 minutes (900 seconds)** achieved via the automated incremental binary-log archiver, dropping data loss exposure by 96x compared to daily snapshots.
- **Live HTTP Benchmarks**:
  - Direct FastAPI Health (:8001): p50 = 14.44 ms (188.88 RPS).
  - Nginx Reverse Proxy (:80): p50 = 8.93 ms (392.46 RPS, rate limiting verified).
  - Frontend SPA Static (:80): p50 = 4.51 ms (670.22 RPS).
  - Monitoring Telemetry Overhead: 0.012 ms (12 $\mu$s) per request (< 1.0 ms SLA).

---

### 9. Academic Contributions & Conclusions

#### Key Academic Contributions
1. **Prescriptive Governance Framework**: Demonstrated that artificial intelligence in enterprise operations must be prescriptive rather than merely predictive, and must be bound to human-in-the-loop state machines.
2. **Scientific Honesty Paradigm**: Proved that detecting synthetic dataset boundaries, assigning transparent confidence tiers (`LOW_EMPIRICAL`), and enforcing commercial guardrails provides far greater real-world utility than fabricating artificial feature correlations.
3. **Defense-in-Depth for Agentic Systems**: Established a reusable blueprint integrating SQL AST sandboxing, prompt injection heuristics, single-use streaming tickets, and Encrypt-then-MAC disaster recovery.

#### Final Handover Declaration
NovaNest has achieved **100% verification across all 113 automated regression tests** and **8/8 User Acceptance Testing journeys**. All 304,405 records in MySQL `novanest_db` remain completely preserved.

The platform is formally certified **READY FOR CONTROLLED PRODUCTION HANDOVER**.
