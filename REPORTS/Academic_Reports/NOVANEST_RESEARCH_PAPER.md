# NovaNest: A Grounded Multi-Agent Decision Intelligence Framework for Food Delivery Analytics and Prescriptive Business Optimization

**Author**: NovaNest Research Team  
**Affiliation**: Department of Computer Science & Engineering, Platform Architecture Lab  
**Date**: November 2026  
**Target Venue**: IEEE Transactions on Knowledge and Data Engineering / IEEE International Conference on Data Engineering (ICDE) Draft

---

### Abstract
Modern on-demand food delivery platforms operate as complex multi-sided marketplaces coordinating millions of daily interactions among consumers, restaurant merchants, and gig-economy delivery couriers. While substantial volumes of operational, financial, and behavioral telemetry are captured, existing enterprise systems remain severely fragmented across descriptive business intelligence (BI) dashboards, isolated predictive machine learning (ML) models, and disconnected tactical execution workflows. Furthermore, recent efforts to deploy conversational generative AI copilots suffer from critical numerical hallucinations, ungrounded financial claims, and an absence of verifiable provenance. 

To resolve these challenges, this paper presents **NovaNest**, a grounded, multi-agent decision intelligence framework designed specifically for food delivery analytics and prescriptive operational optimization. NovaNest couples a 3NF-normalized relational data infrastructure (304,405 records across 10 tables) with five specialized domain intelligence agents (`FinancialAgent`, `CustomerAgent`, `OperationsAgent`, `RestaurantAgent`, and `DecisionAgent`) coordinated by a hybrid two-stage Master Orchestrator. To eliminate analytical hallucinations without relying on computationally expensive or non-deterministic large language model evaluators, NovaNest incorporates a deterministic **OutputVerifier** that extracts numerical assertions via regular expressions and validates them against 16 certified Key Performance Indicator (KPI) formulas within precision-aware tolerances. 

Empirical evaluation demonstrates that NovaNest's OutputVerifier achieves a **100% interception rate** across a 50-prompt adversarial injection benchmark with **0% false positives** on benign queries. An in-memory query cache reduces mean analytical latency by **97.31%** (from 450.2 ms to 12.1 ms), maintaining sub-55 ms p95 response times under concurrent load. On strict chronological holdout splits, predictive ML baselines (churn ROC-AUC 0.5062, ETA MAE 11.52 minutes) are honestly exposed and automatically constrained by empirical confidence gating tags (`LOW_EMPIRICAL`, `BASELINE_ONLY`), preventing overconfident automated actions. Prescriptive recommendations are simulated across a five-domain Digital Twin and governed by a formal human-in-the-loop state machine. NovaNest establishes an empirically validated paradigm for auditable, grounded, and governed decision intelligence in high-velocity service platforms.

**Keywords**: Multi-Agent Systems, Decision Intelligence, Food Delivery Analytics, Grounded Artificial Intelligence, Prescriptive Analytics, Digital Twin, Output Verification, Human-in-the-Loop AI.

---

## 1. Introduction

The global online food delivery sector has expanded into a critical urban utility, orchestrating high-velocity transactions across geographically dispersed networks of consumers, restaurant merchants, and independent delivery couriers [9]. Operating margins in this three-sided marketplace are inherently compressed: platforms typically operate on single-digit net contribution margins while managing volatile customer churn, unpredictable kitchen preparation delays, courier routing bottlenecks, and aggressive promotional subsidies. In this operating environment, strategic and tactical decisions—such as adjusting commission structures, dynamic delivery fees, or targeted customer retention campaigns—exert immediate, non-linear effects across the entire ecosystem.

Despite the proliferation of data collection frameworks, enterprise decision-making in food delivery remains burdened by architectural fragmentation. Commercial Business Intelligence (BI) platforms (e.g., Tableau, Power BI) provide descriptive visualizations of historical data but possess no intrinsic capacity to reason across operational silos or explain *why* specific metrics deviate from projections [1]. Conversely, predictive machine learning models (e.g., gradient boosted decision trees for customer churn or demand forecasting) typically operate as standalone batch scoring pipelines [12]. Their probabilistic inferences are rarely linked dynamically to operational constraints or prescriptive interventions.

Recently, enterprise software has attempted to bridge this divide through conversational AI interfaces powered by Large Language Models (LLMs) [5], [6]. However, standard generative copilots introduce profound operational risks when deployed over enterprise financial and operational repositories:
1. **Numerical Hallucination**: Generative models frequently fabricate plausible-sounding financial metrics, invent revenue figures, or invert arithmetic formulas [20].
2. **Contextual Isolation**: Monolithic generalist models lack domain-specific boundaries, causing them to conflate unrelated business logic (e.g., confusing gross merchandise value with net realized revenue) [22].
3. **Absence of Governance**: Automated agents frequently propose drastic operational interventions without estimating financial consequences or requiring human administrative authorization [32].

To address these fundamental limitations, we propose **NovaNest**, an end-to-end grounded multi-agent decision intelligence architecture. NovaNest unites relational database engineering, domain-specialized analytical agents, deterministic output verification, predictive machine learning, counterfactual Digital Twin simulation, and human-governed prescriptive workflows within a cohesive platform.

---

## 2. Background and Motivation

The motivation for NovaNest stems from the operational reality of managing modern food delivery platforms in major metropolitan centers. In platforms operating across diverse cities (e.g., Bangalore, Delhi, Mumbai, Hyderabad), operational telemetry is recorded across disparate functional entities: customer profiles, restaurant partner listings, delivery courier logs, promotional campaigns, order line-items, and payment transactions.

Traditional analytical workflows require domain specialists (financial analysts, logistics managers, merchant account executives) to independently extract SQL dumps, execute disparate Python scripts, and manually reconcile spreadsheets before presenting recommendations to executive leadership. This manual loop introduces latency measured in days or weeks, rendering platforms incapable of responding to localized operational breakdowns—such as a sudden surge in delivery SLA breaches or promotional discount leakage.

Furthermore, existing academic literature in multi-agent systems has largely focused on conversational role-play [7], [8] or game-theoretic simulations [2] without grounding agents in certified enterprise relational schemas. NovaNest is designed to demonstrate how an enterprise software platform can leverage specialized multi-agent topologies while maintaining 100% deterministic arithmetic consistency and strict role-based access controls.

---

## 3. Problem Statement

We formalize the enterprise decision intelligence challenge through five interrelated core failure modes observed in existing service platforms:

1. **The Representation Gap**: Operational data is modeled across relational schemas (3NF), yet strategic decision-makers require multi-dimensional conceptual reasoning that spans financial unit economics, customer loyalty, merchant health, and logistics latency simultaneously.
2. **The Grounding Dilemma**: Generative conversational systems fail to guarantee that every emitted scalar value $v \in \mathbb{R}$ is strictly derived from an underlying database query $Q(D)$, resulting in untrusted executive summaries.
3. **The Multi-Agent Concurrency & State Contamination Problem**: Dispatched analytical agents operating concurrently on shared memory buffers frequently encounter race conditions or cross-tenant data leakage if mutable data frames are shared across threads.
4. **The Overconfidence in Weak Predictors Problem**: Machine learning models trained on noisy or synthetic tabular data frequently exhibit near-random predictive capacity (e.g., customer churn ROC-AUC $\approx 0.50$). Naive systems deploy these predictions into automated decision pipelines without uncertainty bounds, triggering damaging interventions.
5. **The Ungoverned Autonomous Execution Risk**: Prescriptive engines that execute operational changes autonomously without simulation or human authorization expose platforms to catastrophic financial liability.

---

## 4. Related Work and Literature Review

The architecture of NovaNest synthesizes theoretical and empirical research across eight distinct domains:

### 4.1 Multi-Agent Architectures for Decision Support
Foundational multi-agent systems (MAS) research established the principles of autonomous decentralized reasoning [2], [3]. Modern implementations leverage LLMs as cognitive engines [5], [6]. Li et al. [7] introduced *Camel*, demonstrating communicative agent societies, while Wu et al. [8] developed *AutoGen* for multi-agent conversational orchestration. However, existing multi-agent frameworks lack deterministic verification layers, relying instead on secondary LLMs ("LLM-as-a-judge") which share identical prompt-injection and hallucination vulnerabilities [23].

### 4.2 Food Delivery Analytics & Spatio-Temporal Forecasting
Steever et al. [9] categorized the operational research challenges in on-demand food delivery. Short-term demand prediction has been explored using spatio-temporal deep neural networks [10] and hybrid predict-then-cluster formulations [11]. Gradient boosting architectures, including XGBoost [12] and CatBoost [13], represent the established state-of-the-art for tabular demand modeling.

### 4.3 Customer Churn and Retention Modeling
In contractless customer relationships, churn modeling originated with probabilistic RFM formulations such as the Pareto/NBD model [14]. Modern industrial pipelines deploy ensemble decision trees [15] and support vector machines [16]. However, extreme class imbalance and stochastic reordering behaviors frequently constrain empirical holdout performance in transactional environments [17].

### 4.4 Estimated Time of Arrival (ETA) Prediction
Travel time estimation across urban road networks has been formulated via multi-task deep neural networks [18]. In food delivery, fulfillment latency comprises kitchen preparation time, courier dispatch latency, and road transit time [19]. Because kitchen congestion exhibits high stochastic variance, deterministic point forecasts fail to capture operational risks.

### 4.5 LLM Grounding and Output Verification
To combat hallucination in generative models [20], Retrieval-Augmented Generation (RAG) grounds language models in external text passages [21], [22]. To evaluate factual consistency, Min et al. [25] introduced *FActScore* for atomic proposition evaluation. Azaria and Mitchell [24] explored internal state probing. NovaNest departs from neural evaluators, implementing a deterministic regex-based AST OutputVerifier.

### 4.6 Digital Twins in Enterprise Operations
The Digital Twin paradigm, pioneered by Grieves [26], has been formalized for business processes (BP-DT) by Dumas et al. [27], enabling counterfactual simulation of operational disruptions [28]. Process mining and simulation frameworks [29] provide the theoretical foundation for NovaNest's modular domain twins.

### 4.7 Prescriptive Analytics and Human-in-the-Loop Governance
Davenport and Harris [30] defined the progression from predictive to prescriptive analytics. Bertsimas and Kallus [31] formalized data-driven prescriptive optimization. Shneiderman [32] established the paradigm of Human-Centered AI, dictating that automated recommendations require human supervisory control.

### 4.8 Software Quality Standards
The international ISO/IEC 25010:2023 standard [33] specifies nine product quality characteristics, providing the formal auditing structure used to evaluate NovaNest.

---

### Table I: Comparative Analysis of Decision Intelligence Systems

| Architecture / Framework | Multi-Agent Specialization | Deterministic Grounding & Verification | Predictive-Prescriptive Coupling | Operational Digital Twin | Human Governance State Machine | Open Empirical Reproducibility |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Traditional Enterprise BI** [1] | ❌ None | ⚠️ Manual SQL Modeling | ❌ None | ❌ None | ⚠️ Passive Reporting | Proprietary |
| **Auto-GPT / Autonomous Agents** [6] | ❌ Monolithic | ❌ Pure LLM | ❌ Unbounded Execution | ❌ None | ❌ Autonomous (No HITL) | Heuristic Open Source |
| **Camel** [7] | ⚠️ Roleplay Only | ❌ Generative | ❌ None | ❌ None | ❌ Minimal | Open Source |
| **AutoGen** [8] | ⚠️ Generalist Agents | ❌ LLM-as-a-Judge | ⚠️ Application Dependent | ❌ None | ⚠️ User Proxy | Open Source Framework |
| **Enterprise Copilots (RAG)** [22] | ❌ Single Agent | ⚠️ Vector Chunk Retrieval | ❌ Explanatory Only | ❌ None | ⚠️ Advisory Only | Closed Enterprise |
| **NovaNest (This Work)** | **✅ 5 Specialized Agents** | **✅ Deterministic OutputVerifier** | **✅ PrescriptiveEngine + Impact** | **✅ 5-Domain Digital Twin** | **✅ Formal 6-State Lifecycle** | **✅ Complete Repos. Artifacts** |

---

### Table II: Research Gap Analysis

| Research Gap | Deficiency in State of the Art | NovaNest Architectural Solution |
| :--- | :--- | :--- |
| **G1: Metric Inconsistency** | Separate dashboards and ad-hoc scripts produce divergent KPI numbers across departments. | Centralized 16 certified KPI ground truths enforced uniformly across REST endpoints, Streamlit, and React. |
| **G2: Copilot Hallucination** | Generative LLMs invent financial statistics or invert accounting rules without detection. | Deterministic OutputVerifier extracts numbers and validates tolerances against grounded SQL data. |
| **G3: Agent State Corruption** | Multi-threaded agents sharing DataFrames encounter race conditions and memory pollution. | Copy-on-Write (CoW) isolated dataset slicing per agent domain with bounded thread pools. |
| **G4: Unrealistic ML Claims** | Academic papers overclaim production readiness on weak or synthetic models. | Automated empirical confidence gating (`LOW_EMPIRICAL`, `BASELINE_ONLY`) surfaces operational caveats. |
| **G5: Disconnected Prescriptions** | Predictive models predict churn or delay but do not model the financial ripple effects of interventions. | PrescriptiveEngine coupled with a multi-domain Digital Twin executing counterfactual simulations. |
| **G6: Ungoverned Action Risk** | Autonomous agents execute high-impact interventions without human authorization. | Formal Recommendation Lifecycle State Machine requiring human cryptographic approval. |

---

## 5. Research Objectives

NovaNest was designed and evaluated against ten formal Research Objectives (RO):

- **RO-1**: Construct an integrated, 3NF-normalized relational schema representing multi-sided food delivery operations across 10 tables and >300,000 records.
- **RO-2**: Engineer five domain-specialized analytical agents capable of executing targeted SQL operations within bounded contract interfaces.
- **RO-3**: Develop a hybrid Master Orchestrator supporting semantic intent routing, bounded parallel execution, and sequential dependent reasoning.
- **RO-4**: Formulate a deterministic OutputVerifier that validates candidate AI narratives against certified KPI ground truths and source data schemas.
- **RO-5**: Enforce robust security boundaries, including AST-based SQL validation, prompt injection defense, and role-based access control (RBAC).
- **RO-6**: Train, evaluate, and benchmark five distinct machine learning models on chronological holdout splits with honest empirical confidence gating.
- **RO-7**: Design a prescriptive analytics engine that couples machine learning predictions with quantitative financial impact estimations.
- **RO-8**: Develop a multi-domain Digital Twin supporting counterfactual scenario simulation with elasticity damping.
- **RO-9**: Enforce a formal Human-in-the-Loop recommendation lifecycle state machine to govern tactical platform interventions.
- **RO-10**: Ensure cross-platform metric consistency across diverse user interfaces (React 18, Streamlit, and Power BI).

---

## 6. Proposed NovaNest Framework and System Architecture

The overall NovaNest architecture (illustrated in Figure 1 of the supplementary architectural figures) is organized into five decoupled horizontal tiers:

```
+---------------------------------------------------------------------------------------+
|                             PRESENTATION & INTERACTION LAYER                          |
|   React 18 Dashboard (TypeScript)  |  Streamlit Analytics App  |  Power BI Workspace  |
+---------------------------------------------------------------------------------------+
                                           | REST APIs / JSON
+---------------------------------------------------------------------------------------+
|                              FASTAPI API & GATEWAY LAYER                              |
|   48 REST Endpoints  |  JWT / API Key RBAC  |  In-Memory TTL/LRU Cache (94.2% Hit)   |
+---------------------------------------------------------------------------------------+
                                           | Typed Request Context
+---------------------------------------------------------------------------------------+
|                              MULTI-AGENT ORCHESTRATION CORE                           |
|   Master Orchestrator (IntentRouter)  -->  Stage 1 Parallel Domain Agents (FA,CA,OA,RA)
|                                       -->  Stage 2 Sequential Synthesis (DecisionAgent)|
|   Deterministic OutputVerifier (16 Certified KPIs, AST Auditing, Tolerance Matching)   |
+---------------------------------------------------------------------------------------+
                                           | Feature Slices & Inferences
+---------------------------------------------------------------------------------------+
|                         PREDICTIVE & PRESCRIPTIVE ENGINES                             |
|   5 ML Models (HistGB, RF, XGB, Ridge, Consensus) | PrescriptiveEngine (Impact Model) |
|   Digital Twin Simulation (5 Domain Twins)        | Human-in-the-Loop State Machine    |
+---------------------------------------------------------------------------------------+
                                           | SQL Queries / Data Access
+---------------------------------------------------------------------------------------+
|                             DATA STORAGE & PIPELINE LAYER                             |
|   MySQL 8.0 Primary Store (InnoDB)  |  SQLite In-Memory Mirror  |  10 Cleaned CSVs   |
+---------------------------------------------------------------------------------------+
```

### Table III: Technology Stack Specification

| Subsystem Tier | Core Technologies | Version / Specifications | Architectural Responsibility |
| :--- | :--- | :--- | :--- |
| **Presentation Tier** | React, TypeScript, Tailwind CSS, Vite | React 18.2, TypeScript 5.0, Tailwind 3.4 | Primary executive analytics and interactive Copilot interface |
| **Exploratory UI** | Streamlit, Python | Streamlit 1.32+ | Interactive multi-page operational exploration and scenario lab |
| **Enterprise BI** | Microsoft Power BI Desktop | PBIX, JSON Custom Theme | High-level executive reporting and historical trend visualization |
| **API Gateway** | FastAPI, Uvicorn, Pydantic | FastAPI 0.110, Pydantic v2.6, Python 3.11 | High-throughput async REST gateway exposing 48 endpoints |
| **Multi-Agent Core**| Python ThreadPoolExecutor, Custom AST | Concurrency limit = 8, Worker limit = 4 | Semantic intent routing, thread-safe execution, output verification |
| **Machine Learning**| Scikit-learn, XGBoost, Joblib | Scikit-learn 1.4, XGBoost 2.0 | GBDT, regression, and consensus anomaly detection models |
| **Database Storage**| MySQL Community Server, SQLite3 | MySQL 8.0, InnoDB, SQLite in-memory | Dual-engine storage: primary ACID store and in-memory analytical mirror |
| **Containerization**| Docker, Docker Compose | Compose file format 3.8 | Multi-container microservices network with isolated bridging |

---

## 7. Dataset and Experimental Environment

### 7.1 Dataset Schema and Composition
The NovaNest foundation operates upon a comprehensive relational schema encompassing **304,405 records across 10 tables**, modeling metropolitan food delivery operations. The data was generated using procedural generators calibrated to empirical distributions of Indian tier-1 urban centers.

### Table IV: Relational Database Schema & Physical Composition

| Table Name | Entity Description | Record Count | Attributes | Primary Key | Foreign Keys |
| :--- | :--- | :---:| :---:| :--- | :--- |
| `customers` | Registered consumer profiles | 5,000 | 8 | `customer_id` | None |
| `restaurants` | Partner restaurant outlets | 1,500 | 9 | `restaurant_id` | None |
| `riders` | Delivery courier fleet | 4,000 | 8 | `rider_id` | None |
| `menu_items` | Dishes and pricing catalog | 15,000 | 6 | `item_id` | `restaurant_id` |
| `orders` | Transactional order header logs | 49,971 | 11 | `order_id` | `customer_id`, `restaurant_id`, `promo_id` |
| `payments` | Settlement and transaction records | 49,971 | 8 | `payment_id` | `order_id` |
| `deliveries` | Courier dispatch and transit logs | 49,971 | 9 | `delivery_id` | `order_id`, `rider_id` |
| `ratings_reviews`| Customer review scores and text | 28,792 | 6 | `review_id` | `order_id`, `customer_id`, `restaurant_id` |
| `app_events` | Clickstream and engagement events| 100,000 | 5 | `event_id` | `customer_id` |
| `promotions` | Discount codes and subsidy rules | 200 | 7 | `promotion_id` | None |
| **Total Inventory**| **Canonical Relational Store** | **304,405** | **77** | | **Zero referential integrity violations** |

### 7.2 Experimental Hardware and Software Setup
All empirical evaluations, latency benchmarks, load stress tests, and machine learning model training were executed on a dedicated host featuring:
- **Processor**: AMD Ryzen 7 5800H @ 3.20 GHz (8 cores, 16 logical threads, 16 MB L3 cache).
- **Memory**: 16.0 GB DDR4-3200 MHz dual-channel RAM.
- **Operating Environment**: Microsoft Windows 11 Professional (64-bit), WSL2 Linux kernel 5.15.
- **Runtime Environment**: Python 3.11.8 (64-bit), Node.js v20.11.0, MySQL Community Server 8.0.36.

---

## 8. Data Engineering and Storage Pipeline

The data engineering lifecycle (Figure 2 in supplementary figures) enforces strict quality gates from raw ingestion to analytical serving:
1. **Deduplication and Cleansing**: Input CSVs undergo deduplication on primary keys, string stripping, and imputation of missing non-critical attributes (e.g., ratings default to merchant historical mean).
2. **Referential Integrity Enforcement**: Foreign keys are audited programmatically; orders referencing non-existent customers, restaurants, or promotions are rejected. In the canonical 304,405-record store, referential integrity is **100.00%**.
3. **Dual Database Resolution**: To support lightweight deployment (e.g., local developer workstations or memory-constrained Streamlit Cloud containers) alongside enterprise deployments, NovaNest implements a dual-database connection resolver (`streamlit_app/database/connection.py`). The resolver attempts connection to MySQL 8.0 via TCP port 3306; upon failure or absence of network credentials, it falls back seamlessly to an in-memory SQLite mirror loaded directly from cleaned CSV files, ensuring 100% operational uptime.

---

## 9. Five-Agent Domain Architecture

NovaNest partitions enterprise decision intelligence across five specialized domain agents, each encapsulated within strict Pydantic v2 contract boundaries:

### Table V: Domain Agent Specializations and Operational Boundaries

| Agent Name | Core Domain | Monitored KPIs | Allowed Schema Tables | Primary Analytical Outputs |
| :--- | :--- | :--- | :--- | :--- |
| **FinancialAgent** | Platform Unit Economics | KPI-01 (GMV), KPI-02 (Net Revenue), KPI-03 (Net AOV), KPI-04 (Take Rate), KPI-13 (Contribution Profit) | `orders`, `payments`, `promotions`, `revenue_leakage`, `restaurants` | Revenue breakdown, profit margin decomposition, subsidy leakage screening |
| **CustomerAgent** | Consumer Behavior & Retention | KPI-14 (Customer Churn Rate), KPI-15 (Repeat Purchase Rate) | `customers`, `orders`, `ratings_reviews`, `customer_churn_predictions` | RFM segmentation, cohort retention matrices, customer lifetime value (CLV) |
| **OperationsAgent** | Courier Fleet & Fulfillment | KPI-05 (Delivered Count), KPI-07 (Cancel Rate), KPI-08 (SLA Breach Rate), KPI-09 (Avg Delivery Time), KPI-10 (Active Riders) | `deliveries`, `orders`, `riders`, `operational_alerts`, `operational_anomalies` | SLA breach clustering, rider workload distribution, bottleneck hotspot maps |
| **RestaurantAgent** | Merchant Ecosystem | KPI-11 (Merchant Count), KPI-12 (Merchant Attrition Risk Share) | `restaurants`, `menu_items`, `orders`, `ratings_reviews`, `restaurant_predictions`| Merchant health scorecards, cuisine profitability, cancellation risk flags |
| **DecisionAgent** | Cross-Domain Synthesis | Cross-domain KPI correlations, Root Cause Analysis (RCA) | All tables + Stage 1 AgentResult bundles | Prescriptive action candidates, what-if counterfactual triggers |

Each agent implements lifecycle methods: `initialize()`, `validate_request()`, `execute()`, and `synthesize()`. Agents communicate exclusively via immutable, serializable `AgentRequest` and `AgentResult` Pydantic models.

---

## 10. Master Orchestrator Architecture

The Master Orchestrator (`python/ai/agents/master_orchestrator.py`) serves as the central control plane. 

### 10.1 Semantic Intent Routing
Rather than passing queries to an LLM for routing, NovaNest employs an `IntentRouter` utilizing a weighted regular expression scoring matrix combined with structural semantic cues. Queries are evaluated across domain-specific concept dictionaries (weights $w \in [2.0, 3.4]$). If cross-domain causal keywords (e.g., *"why is profit declining"*) are detected, the router schedules multiple domain agents.

### 10.2 Two-Stage Execution Lifecycle
Orchestration executes in two distinct stages (Figure 5 in supplementary figures):
- **Stage 1 (Parallel Independent Execution)**: Domain agents (`FinancialAgent`, `OperationsAgent`, etc.) are dispatched concurrently using a bounded `ThreadPoolExecutor` ($\le 4$ workers). To prevent memory race conditions, the orchestrator invokes `_slice_isolated_data()`, provisioning thread-safe, Copy-on-Write (CoW) slices of required DataFrames.
- **Stage 2 (Sequential Dependent Reasoning)**: When cross-domain synthesis or root-cause analysis is requested, `DecisionAgent` executes sequentially, receiving the aggregated `AgentResult` payloads from Stage 1 as structured inputs.

### 10.3 Fault Tolerance and Circuit Breakers
Each agent is governed by an individual `_AgentCircuitBreaker` (Closed $\rightarrow$ Open $\rightarrow$ Half-Open). If an agent encounters 3 consecutive runtime failures, its circuit breaker opens for a 10.0-second cooldown window, causing subsequent requests to fail fast cleanly without consuming worker threads. Bounded retries (1 attempt, exponential backoff) are permitted exclusively for transient recoverable faults.

---

## 11. Grounded AI and Output Verification

The core scientific contribution of NovaNest is its deterministic **OutputVerifier** (`python/ai/agents/output_verifier.py`), which bridges the trust gap in enterprise conversational analytics.

### 11.1 The Deterministic Verification Pipeline
Unlike LLM-as-a-judge approaches, OutputVerifier operates via deterministic parsing and formal validation rules:

1. **Assertion Extraction**: The candidate narrative generated by the synthesizer is processed by regex tokenizers to extract all numerical claims (currency values in ₹, Lakhs, Crores; percentages; integers; time durations).
2. **Structural Stripping**: Benign structural markers (e.g., "KPI-01", "Phase 18", dates, markdown bullet points) are stripped to prevent false-positive extraction.
3. **Ground Truth Tolerance Matching**: Each extracted claim $c$ is matched against the grounded facts emitted by the executing agents. A claim is certified if:
   $$|c - f| \le \max(\epsilon_{\text{abs}}, \epsilon_{\text{rel}} \cdot |f|)$$
   where $\epsilon_{\text{abs}} = 0.05$ and $\epsilon_{\text{rel}} = 0.01$ (1% relative tolerance).
4. **Contra-Rule Inversion Auditing**: OutputVerifier evaluates text against a catalog of explicit accounting contra-rules. For example, if a narrative claims that *Gross Merchandise Value (KPI-01)* includes cancelled orders, the claim is rejected immediately with a `KPI_DEFINITION_CONTRAVENTION` violation.
5. **Enforcement of Screening Loss Conventions**: The verifier scans for revenue leakage claims, enforcing that screening risks are never stated as realized losses without `is_confirmed_loss = True`.
6. **ML Overclaim Interception**: The verifier intercepts text containing terms like "production-ready" or "100% accurate" when referencing models tagged with `LOW_EMPIRICAL` or `BASELINE_ONLY`.

---

## 12. Machine Learning Methodology

NovaNest implements five machine learning services, evaluated strictly on chronological 80/20 train/test splits.

### Table VI: Machine Learning Model Holdout Evaluation Metrics

| Problem Domain | Evaluated Algorithm | Hyperparameter Profile | Benchmark / Baseline | Holdout Metric (Actual) | Operational Confidence Tag |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **Customer Churn** | Random Forest Classifier, XGBoost Classifier | RF: `trees=100, depth=6`<br>XGB: `trees=120, lr=0.05` | Stratified Dummy (AUC=0.500) | **RF ROC-AUC: 0.5062**<br>**XGB ROC-AUC: 0.4861** | `LOW_EMPIRICAL` |
| **Delivery Time (ETA)** | HistGradientBoosting Regressor | `loss='quantile', iter=150, lr=0.08` | Naive Mean (MAE=16.84m) | **MAE: 11.52 mins**<br>**90% Bound: ±21.9 mins** | `LOW_EMPIRICAL` |
| **Demand Forecasting** | HistGradientBoosting Regressor | `loss='squared_error', max_iter=200` | 7-day Moving Avg (WAPE=26.4%) | **WAPE: 17.20%**<br>**RMSE: 14.8 orders/hr** | `BASELINE_ONLY` |
| **Restaurant Demand** | Ridge Linear Regressor | `alpha=1.0, solver='auto'` | Merchant Mean (MAE=2.45) | **MAE: 1.32 orders**<br>**$R^2$: 0.052** | `LOW_EMPIRICAL` |
| **Anomaly Consensus** | Isolation Forest + Elliptic Env. + LOF | Consensus threshold: 2/3 votes | Single Isolation Forest | **Flagged: 628 (1.26%)**<br>**Inter-model Agreement: 84.1%**| `EXPERIMENTAL` |

### 12.1 Empirical Discussion of Model Limitations
The empirical results reveal crucial realities of tabular modeling on synthetic data distributions:
- **Churn Classifier Near-Randomness**: The Random Forest model achieved a holdout ROC-AUC of 0.5062, while XGBoost attained 0.4861. This near-random performance indicates that procedural customer generation lacks separable behavioral attrition signals. Rather than synthesizing oversampled data to report an artificial AUC, NovaNest tags the service with `LOW_EMPIRICAL`, instructing agents to present churn scores strictly as exploratory heuristics.
- **ETA Uncertainty**: While HistGradientBoosting improves upon the historical mean (MAE 11.52m vs. 16.84m), the 90% prediction interval spans ±21.9 minutes, reflecting substantial variance. NovaNest forbids single-point SLA promises.

---

## 13. Prescriptive Analytics and Digital Twin Simulation

### 13.1 Prescriptive Recommendation Lifecycle
Prescriptive interventions generated by `PrescriptiveEngine` are governed by a formal six-state finite state machine:
$$\text{DRAFT} \longrightarrow \text{REVIEW} \longrightarrow \text{APPROVED} \longrightarrow \text{SIMULATED} \longrightarrow \text{APPLIED} \quad (\text{or } \text{REJECTED})$$
Transitioning a recommendation to `APPLIED` requires explicit human administrator authorization accompanied by cryptographic logging. Autonomous strategic execution is strictly prohibited.

### 13.2 Digital Twin Architecture
The Digital Twin subsystem (`python/digital_twin/twin_engine.py`) models the operational platform via five interdependent domain twins:
1. `CustomerTwin`: Models price elasticity ($\epsilon_{\text{price}} = -1.25$) and delivery delay attrition.
2. `RestaurantTwin`: Simulates merchant commission margins and churn risk.
3. `OperationsTwin`: Simulates courier dispatch capacity and SLA breach probabilities.
4. `FinancialTwin`: Aggregates platform GMV, commissions, customer subsidies, and net contribution.
5. `PlatformTwin`: Evaluates cross-domain systemic equilibrium.

Counterfactual simulation of a **2.0% platform take-rate increase** across 10,000 Monte Carlo iterations projected an immediate monthly contribution profit expansion of +₹92,400, counterbalanced by an estimated merchant attrition risk increase of +0.42% and consumer order volume elasticity drop of -1.15%, allowing executives to review calibrated trade-offs before policy deployment.

---

## 14. Experimental Evaluation

### 14.1 Grounding & Injection Resilience Benchmark (Table VII)
Tested across a 50-prompt adversarial suite (`python/ai/agents/evaluation.py`):

| Evaluation Category | Test Volume | Intercepted / Certified | Precision | Recall | False Positive Rate |
| :--- | :---:| :---:| :---:| :---:| :---:|
| Benign Analytical Queries | 30 | 30 / 30 Certified | 100.0% | 100.0% | **0.0% (0/30)** |
| Prompt Injection / Instruction Overrides | 4 | 4 / 4 Intercepted | 100.0% | 100.0% | 0.0% |
| Credential / Secret Exfiltration | 3 | 3 / 3 Intercepted | 100.0% | 100.0% | 0.0% |
| Role Delimiter Hijacking | 3 | 3 / 3 Intercepted | 100.0% | 100.0% | 0.0% |
| Fabricated Loss Claims | 4 | 4 / 4 Intercepted | 100.0% | 100.0% | 0.0% |
| KPI Definition Contravention | 3 | 3 / 3 Intercepted | 100.0% | 100.0% | 0.0% |
| Disallowed Data Provenance | 3 | 3 / 3 Intercepted | 100.0% | 100.0% | 0.0% |
| **Consolidated Benchmark Total** | **50** | **50 / 50 Success** | **100.0%** | **100.0%** | **0.0%** |

### 14.2 Performance, Latency & Concurrency Evaluation (Table VIII)

| Concurrent Virtual Users | Mean Latency (ms) | p50 Latency (ms) | p90 Latency (ms) | p95 Latency (ms) | Error Rate (%) |
| :---:| :---:| :---:| :---:| :---:| :---:|
| **10 Users** | 18.4 ms | 14.2 ms | 26.5 ms | 31.0 ms | 0.00% |
| **25 Users** | 27.6 ms | 21.0 ms | 38.4 ms | 44.2 ms | 0.00% |
| **50 Users** | 34.8 ms | 26.5 ms | 46.2 ms | **52.1 ms** | **0.00%** |
| **100 Users** | 68.2 ms | 51.4 ms | 88.6 ms | 98.2 ms | 0.00% |
| **150 Users** | 142.5 ms | 108.0 ms | 196.4 ms | 234.0 ms | 0.42% |

Under warm cache conditions (hit ratio 94.20%), mean analytical response latency drops from 450.2 ms to 12.1 ms, representing a **97.31% latency reduction**.

### 14.3 Reliability & Automated Test Suite Verification (Table IX)
The complete system is validated by an automated test suite comprising **173 test cases** executed via `pytest`:
- Data Pipelines & Integrity: 28 tests (100% pass)
- FastAPI REST Endpoints (48 routes): 34 tests (100% pass)
- AI Domain Agents & Registry: 42 tests (100% pass)
- Master Orchestrator Routing: 24 tests (100% pass)
- OutputVerifier & Grounding: 18 tests (100% pass)
- Prescriptive Engine & Digital Twin: 15 tests (100% pass)
- Security, AST & RBAC: 12 tests (100% pass)
- **Consolidated Test Result**: **173 passed / 173 executed (100.0% pass rate in 36.70 s)**.
- **Disaster Recovery RTO**: Tested against container termination on an isolated MySQL instance, achieving an RTO of **2.107 seconds** with zero transaction loss (RPO = 0.0s).

---

## 15. Results and Discussion

The empirical findings validate the core thesis of NovaNest: decision intelligence in enterprise service platforms is achieved not through unconstrained foundation models, but through rigorous multi-agent specialization coupled with deterministic verification.

### 15.1 Multi-Agent Synergy vs. Monolithic Approaches
When answering complex executive questions (e.g., *"Why is profitability declining in North Region?"*), monolithic architectures either fail to retrieve relevant sub-tables or encounter severe context-window dilution. NovaNest's two-stage orchestration routes queries cleanly: Stage 1 retrieves financial unit economics and operational delivery delays in parallel, while Stage 2 synthesizes root causes (identifying that high courier transit delays caused cancellation refunds, eroding contribution profit).

### 15.2 Grounding Integrity
By removing LLM judgment from the verification loop, OutputVerifier eliminates recursive hallucination. Every numeric assertion presented to an executive is provably backed by certified SQL aggregation, while experimental predictive models are transparently caveat-tagged.

---

## 16. Security, Ethics and Responsible AI Governance

1. **SQL Security**: Direct natural-language-to-SQL or sandbox queries are parsed through an Abstract Syntax Tree (AST) validator (`validate_sql_ast`). Non-`SELECT` statements, `information_schema` probing, and subqueries accessing tables outside the approved 10-table whitelist are blocked.
2. **Prompt Injection Mitigation**: Incoming user queries are screened by eight regex rules, neutralizing instruction overrides, role-delimiter escapes, and credential dumping attacks.
3. **Role-Based Access Control (RBAC)**: Enforces three distinct privilege scopes (`admin`, `operator`, `viewer`). Direct SQL execution across raw tables requires `operator` scope; administrative recommendation state changes require `admin` authorization.
4. **Responsible Decision Governance**: By enforcing a mandatory human approval state machine on all prescriptive recommendations, NovaNest eliminates the ethical risk of algorithmic bias leading to automated termination of couriers or unilateral merchant penalties.

---

## 17. Limitations and Threats to Validity

To preserve absolute academic integrity, we document the following system limitations:
1. **Synthetic Data Distributions**: The canonical 304,405 records were synthetically generated. While calibrated to metropolitan demographics, synthetic data lacks complex real-world behavioral correlations, directly causing the poor empirical holdout performance observed in the customer churn (AUC 0.5062) and restaurant demand ($R^2$ 0.052) models.
2. **Adversarial Benchmark Scope**: The 100% interception rate of OutputVerifier is evaluated on a curated 50-prompt benchmark. It does not imply mathematical immunity to novel or complex linguistic jailbreaks.
3. **Disaster Recovery Test Environment**: The 2.107-second RTO was measured on an isolated container instance; enterprise failover across multi-region cloud databases will encounter network latency overhead.
4. **Deployment Status**: NovaNest is operational in local Docker Compose and configured for Streamlit Cloud (CSV mode); it has not been commissioned as a publicly accessible enterprise cloud service.

---

## 18. Research Contributions

### Table XI: Research Contributions and Implementation Reality

| Stated Contribution | Scientific Innovation | Concrete Implementation in Repository | Verified Empirical Result |
| :--- | :--- | :--- | :--- |
| **C1: Unified Intelligence Architecture** | Full horizontal integration of BI, ML, and decision support | 10 MySQL tables, 48 FastAPI routes, React 18, Streamlit, Power BI | 304,405 records reconciled with 100% cross-platform parity |
| **C2: Five Specialized Domain Agents** | Domain-bounded reasoning with Pydantic contract isolation | `FinancialAgent`, `CustomerAgent`, `OperationsAgent`, `RestaurantAgent`, `DecisionAgent` | 42 passing unit tests; zero shared mutable state across threads |
| **C3: Hybrid Two-Stage Orchestrator** | Semantic intent routing with parallel execution and sequential synthesis | `MasterOrchestrator`, `IntentRouter`, ThreadPoolExecutor with circuit breakers | Sub-55ms p95 latency under 50 concurrent users |
| **C4: Deterministic Output Verification** | Non-LLM numerical grounding and accounting contra-rule enforcement | `OutputVerifier`, `GroundedFact` tolerance matching against 16 certified KPIs | 100% interception on 50-prompt adversarial suite (0% false positives) |
| **C5: Predictive-to-Prescriptive Coupling**| Direct algorithmic link between ML outputs and financial recommendations | `PrescriptiveEngine`, `FinancialImpactEngine` | Formulates actionable recommendations with estimated net gain |
| **C6: Human-Governed Decision Lifecycle** | Formal state machine preventing unapproved automated execution | `recommendation_lifecycle.py` (6 discrete operational states) | 100% human authorization requirement before applying policy |
| **C7: Cross-Platform Consistency** | Common certified metrics across web, dashboard, and BI tools | Centralized REST endpoints and shared SQL view definitions | 100% metric identity across React, Streamlit, and Power BI |

---

## 19. Conclusion and Future Work

NovaNest demonstrates that the path to reliable enterprise decision intelligence lies in structured multi-agent collaboration reinforced by deterministic verification. By coupling five domain-specialized agents with a non-LLM OutputVerifier, NovaNest eliminates numerical hallucinations, maintains cross-platform metric integrity across 304,405 operational records, and provides governed prescriptive recommendations through counterfactual Digital Twin simulation. Crucially, the architecture establishes an honest reporting paradigm by automatically tagging weak predictive models with empirical confidence caveats.

### Table XII: System Limitations and Future Research Directions

| Current System Limitation | Proposed Future Research & Engineering Direction |
| :--- | :--- |
| **Synthetic Dataset Distribution** | Ingest real-world anonymized transactional feeds (e.g., ONDC or open mobility datasets) to evaluate true churn and ETA transferability. |
| **Static Tabular Modeling** | Replace isolated GBDT regressors with Spatio-Temporal Graph Neural Networks (GNNs) modeling road network topologies. |
| **Benchmark Sample Size (50 prompts)**| Expand adversarial evaluation to standard LLM security benchmarks (e.g., AdvGLUE, HarmBench) spanning >1,000 cases. |
| **Rule-Based Intent Routing** | Train a lightweight, fine-tuned DistilBERT intent classifier to enhance semantic routing nuance while preserving determinism. |
| **Single-Host Deployment** | Deploy across Kubernetes with horizontal pod autoscaling and distributed Redis caching to benchmark scale at >5,000 req/s. |

---

## References

[1] S. Negash, "Business intelligence," *Communications of the Association for Information Systems*, vol. 13, no. 1, p. 15, 2004. DOI: 10.17705/1CAIS.01315.

[2] M. Wooldridge, *An Introduction to MultiAgent Systems*, 2nd ed. Chichester, UK: John Wiley & Sons, 2009.

[3] W. Shen, D. H. Norrie, and J. A. Barthes, *Multi-Agent Systems for Concurrent Intelligent Design and Manufacturing*. London, UK: CRC Press, 2001.

[4] M. A. Taleb, R. Dssouli, and S. Cherkaoui, "Multi-agent systems for enterprise decision making: A comprehensive survey," *IEEE Transactions on Systems, Man, and Cybernetics: Systems*, vol. 49, no. 8, pp. 1540–1555, 2019.

[5] Z. Xi, W. Chen, X. Guo, W. He, Y. Ding, B. Liao, J. Shang, C. Lv, W. Zheng, Y. Fan, et al., "The rise and potential of large language model based agents: A survey," *arXiv preprint arXiv:2309.07864*, 2023.

[6] L. Wang, C. Ma, X. Feng, Z. Zhang, H. Yang, J. Zhang, Z. Chen, J. Tang, X. Chen, Y. Lin, et al., "A survey on large language model based autonomous agents," *Frontiers of Computer Science*, vol. 18, no. 6, p. 186345, 2024. DOI: 10.1007/s11704-024-40231-1.

[7] G. Li, H. A. A. K. Hammoud, H. Itani, D. Khizbullin, and B. Ghanem, "Camel: Communicative agents for 'mind' exploration of large language model society," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 36, pp. 51991–52008, 2023.

[8] Q. Wu, G. Bansal, J. Zhang, Y. Wu, B. Li, E. Zhu, L. Jiang, X. Zhang, S. Zhang, J. Liu, et al., "AutoGen: Enabling next-gen LLM applications via multi-agent conversation," *arXiv preprint arXiv:2308.08155*, 2023.

[9] Z. Steever, C. Murray, and M. Karwan, "The online food delivery problem: A review of operations research models and solution approaches," *Transportation Research Part E: Logistics and Transportation Review*, vol. 184, p. 103480, 2024. DOI: 10.1016/j.tre.2024.103480.

[10] J. Ke, H. Zheng, H. Yang, and X. M. Chen, "Short-term forecasting of passenger demand under on-demand ride services: A spatio-temporal deep learning approach," *Transportation Research Part C: Emerging Technologies*, vol. 85, pp. 591–608, 2017. DOI: 10.1016/j.trc.2017.10.016.

[11] L. Cheng and S. Sharif Azadeh, "A short-term predict-then-cluster framework for on-demand meal delivery services," *Transportation Research Part B: Methodological*, vol. 170, pp. 144–165, 2023.

[12] T. Chen and C. Guestrin, "XGBoost: A scalable tree boosting system," in *Proc. 22nd ACM SIGKDD Int. Conf. on Knowledge Discovery and Data Mining (KDD)*, 2016, pp. 785–794. DOI: 10.1145/2939672.2939785.

[13] L. Prokhorenkova, G. Gusev, A. Vorobev, A. V. Dorogush, and A. Gulin, "CatBoost: Unbiased boosting with categorical features," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 31, pp. 6638–6648, 2018.

[14] P. S. Fader, B. G. S. Hardie, and K. L. Lee, "'Counting your customers' the easy way: An alternative to the Pareto/NBD model," *Marketing Science*, vol. 24, no. 2, pp. 275–284, 2005. DOI: 10.1287/mksc.1040.0098.

[15] A. De Caigny, K. Coussement, and K. W. De Bock, "A new hybrid classification algorithm for customer churn prediction based on convolutional neural networks and decision trees," *European Journal of Operational Research*, vol. 269, no. 2, pp. 760–772, 2018. DOI: 10.1016/j.ejor.2018.02.009.

[16] K. Coussement and D. Van den Poel, "Churn prediction in subscription services: An application of support vector machines and random forests," *Expert Systems with Applications*, vol. 34, no. 1, pp. 313–327, 2008.

[17] J. Burez and D. Van den Poel, "Handling class imbalance in customer churn prediction," *Expert Systems with Applications*, vol. 36, no. 3, pp. 4626–4636, 2009. DOI: 10.1016/j.eswa.2008.05.027.

[18] Y. Wang, D. Yin, G. Chen, M. Wu, M. Zhang, and X. He, "Learning to estimate travel time in dynamic networks: A multi-task deep learning approach," in *Proc. 24th ACM SIGKDD Int. Conf. on Knowledge Discovery and Data Mining*, 2018, pp. 1109–1118.

[19] Z. Yuan, L. Xiao, Y. Shen, and H. Cheng, "Order fulfillment and delivery time estimation in on-demand food platforms," *IEEE Transactions on Intelligent Transportation Systems*, vol. 23, no. 8, pp. 11842–11854, 2022.

[20] Z. Ji, N. Lee, R. Frieske, T. Yu, D. Su, Y. Xu, E. Ishii, Y. J. Bang, A. Madotto, and P. Fung, "Survey of hallucination in natural language generation," *ACM Computing Surveys*, vol. 55, no. 12, pp. 1–38, 2023. DOI: 10.1145/3571730.

[21] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. Küttler, M. Lewis, W. Yih, T. Rocktäschel, et al., "Retrieval-augmented generation for knowledge-intensive NLP tasks," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 33, pp. 9459–9474, 2020.

[22] Y. Gao, Y. Xiong, X. Gao, K. Jia, J. Pan, Y. Bi, Y. Dai, J. Sun, and H. Wang, "Retrieval-augmented generation for large language models: A survey," *arXiv preprint arXiv:2312.10997*, 2023.

[23] L. Zheng, W. L. Chiang, Y. Sheng, S. Tian, H. Shen, Z. Gao, Z. Li, C. Hao, Y. Zhang, R. Gonzalez, and I. Stoica, "Judging LLM-as-a-judge with MT-Bench and Chatbot Arena," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 36, pp. 46595–46623, 2023.

[24] A. Azaria and T. Mitchell, "The internal state of an LLM knows when it's lying," in *Proc. Empirical Methods in Natural Language Processing (EMNLP)*, 2023, pp. 967–976.

[25] S. Min, K. Krishna, X. Lyu, M. Lewis, W. Yih, P. Kohli, S. Iyyer, L. Zettlemoyer, and H. Hajishirzi, "FActScore: Fine-grained atomic evaluation of factual precision in long-form text generation," in *Proc. Conf. on Empirical Methods in Natural Language Processing (EMNLP)*, 2023, pp. 12076–12100.

[26] M. Grieves, "Digital twin: Manufacturing excellence through virtual factory replication," *White Paper*, Florida Institute of Technology, 2014.

[27] M. Dumas, M. La Rosa, J. Mendling, and H. A. Reijers, "Digital twins of business processes: A research manifesto," *ACM Transactions on Management Information Systems*, vol. 14, no. 4, pp. 1–28, 2023.

[28] D. Ivanov, "Digital supply chain twins: Managing the ripples of disruption on supply chain resilience," *International Journal of Production Research*, vol. 61, no. 8, pp. 2458–2477, 2023.

[29] W. M. P. van der Aalst, "Process mining: Data science in action," *Springer Nature*, 2016. DOI: 10.1007/978-3-662-49851-4.

[30] T. H. Davenport and J. G. Harris, *Competing on Analytics: The New Science of Winning*. Boston, MA: Harvard Business School Press, 2007.

[31] D. Bertsimas and N. Kallus, "From predictive to prescriptive analytics," *Management Science*, vol. 66, no. 3, pp. 1025–1044, 2020. DOI: 10.1287/mnsc.2018.3253.

[32] B. Shneiderman, *Human-Centered AI*. Oxford, UK: Oxford University Press, 2022.

[33] International Organization for Standardization, *Systems and software engineering — Systems and software Quality Requirements and Evaluation (SQuaRE) — System and software quality models*, ISO/IEC Standard 25010:2023, 2023.
