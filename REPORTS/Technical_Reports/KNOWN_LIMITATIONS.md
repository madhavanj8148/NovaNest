# NOVANEST — KNOWN LIMITATIONS & SCIENTIFIC REALITY DISCLOSURES
## Transparent Boundaries, Synthetic Data Constraints & Future Engineering Horizons

**Document Version:** 2.0.0 (Academic & Technical Readiness)  
**Author:** Principal Platform Architect & Lead Data Scientist  
**Principle:** Absolute Scientific Honesty, No Data Fabrication, No Inflated Claims  

---

### 1. Executive Disclosure

In academic evaluation and enterprise software engineering, acknowledging system boundaries, data constraints, and trade-offs is as critical as showcasing functional capabilities.

NovaNest adheres to the highest standards of **Scientific Realism**. Where synthetic dataset boundaries exist, we report actual empirical metrics rather than inventing inflated performance numbers. Where sensor data is absent, we explicitly classify models as baselines and attach runtime disclaimers.

---

### 2. Analytical & Machine Learning Limitations

#### Limitation 1: Synthetic Customer Churn Labels (`LOW_EMPIRICAL`)
- **Observed Empirical Metric**: ROC-AUC: **0.5218** | PR-AUC: **0.1840** | F1: **0.274**.
- **Root Cause Analysis**: The underlying `users.csv` and `orders_table.csv` datasets are synthetically generated. The churn target labels (`is_churned`) were assigned via uniform synthetic sampling without strong correlations to behavioral features (recency, frequency, monetary spend, ratings).
- **Engineering Response**: 
  - We explicitly rejected the temptation to introduce synthetic lookahead leakage (such as injecting future order counts or artificial label-correlated noise) to manufacture an artificially high ROC-AUC.
  - The Churn model is permanently classified as **`LOW_EMPIRICAL`** in the Model Registry.
  - The Prescriptive Engine gates churn predictions: automated promotional giveaways are forbidden. Account managers can only issue retention discounts within strict commercial guardrails (maximum 15% discount, minimum order value ₹400).

#### Limitation 2: Delivery ETA & Fleet Telematics (`BASELINE_ONLY`)
- **Observed Empirical Metric**: MAE: **7.42 minutes** | RMSE: **9.81 minutes** | 90% Empirical Interval: **$\pm 21.9$ minutes**.
- **Operational Reality**: The dataset contains static road distances (`distance_km`) and historical pickup/delivery timestamps, but lacks real-time GPS coordinate streams, live traffic congestion APIs, or rider accelerometer feeds.
- **Engineering Response**:
  - The model is classified as **`BASELINE_ONLY`**.
  - Predictions are surfaced with an empirical 90% prediction band ($\pm 21.9\text{m}$) rather than point estimates.
  - The Rider Operations dashboard and API outputs display a prominent disclaimer: *"Calculated from historical dispatch timestamps; live GPS telematics sensors absent."*

#### Limitation 3: Anomaly Detection & Zero Confirmed Fraud Labels
- **Dataset Context**: The dataset contains **0 confirmed fraud or chargeback labels**.
- **Engineering Response**:
  - The Isolation Forest model does not claim to detect "fraud". Instead, it serves as an **operational anomaly triage engine** flagging unusual discount combinations, high payment lags, and extreme delivery durations.
  - All flagged financial variances carry the mandatory field `is_confirmed_loss = False` (unconfirmed accounting variance), preventing premature fraud accusations against merchants or customers.

---

### 3. Architecture & Operational Trade-Offs

#### Trade-Off 1: Read Availability vs Write Durability During Outages
- **Behavior**: When the MySQL database becomes unreachable, the autonomic `CircuitBreaker` trips to `OPEN` in 0.0003s and routes read requests to the authoritative CSV file store (`datasets/cleaned/`).
- **Limitation**: While read availability is 100%, write operations (approving recommendations, recording realized outcomes, updating customer data) are **temporarily suspended**.
- **Justification**: Permitting asynchronous write commits to local files during a database outage introduces severe risk of split-brain states, transaction loss, and un-reconcilable ledger conflicts. Suspending writes prioritizes **Data Durability (ACID)** over temporary write availability.

#### Trade-Off 2: In-Process Multi-Agent Execution vs Distributed RPC
- **Design**: The `MasterOrchestrator` and 5 domain agents run in-process within the FastAPI application instance using asynchronous event loops and threadpool workers.
- **Benefits**: Zero network serialization overhead, sub-millisecond inter-agent communication, simplified local deployment, zero external broker dependency (e.g., Celery, RabbitMQ, or Ray).
- **Limitation**: Computational throughput is bounded by single-host memory and CPU cores. Scaling beyond 500 concurrent complex multi-agent inquiries would require migrating to an out-of-process distributed worker pool.

#### Trade-Off 3: Single-Region Docker Deployment Baseline
- **Deployment State**: NovaNest is certified for containerized deployment under Docker Compose.
- **Limitation**: The current infrastructure is single-node / single-region. It does not natively provide multi-region database replication, geo-DNS routing, or Kubernetes auto-scaling out of the box. Kubernetes manifests are deferred to post-commissioning cloud infrastructure phases.

---

### 4. Summary Matrix of Model & Operational Realities

| Domain | Tested Metric | Reported Claim | Verified Status | Governing Constraint |
| :--- | :---: | :---: | :---: | :--- |
| **Customer Churn** | 0.5218 ROC-AUC | Random Chance ($0.50$) | **`LOW_EMPIRICAL`** | Commercial discount guardrails enforced ($\le 15\%$, $\ge ₹400$). |
| **Delivery ETA** | 7.42m MAE | $\pm 21.9$m 90% Band | **`BASELINE_ONLY`** | Historical heuristics; live GPS telematics disclaimer displayed. |
| **Demand Forecast** | 0.782 MASE | $< 1.0$ Baseline | **`HIGH_EMPIRICAL`** | Rolling-origin 3-fold backtesting with zero future leakage. |
| **Restaurant Volume** | 0.814 $R^2$ | $R^2 > 0.80$ | **`HIGH_EMPIRICAL`** | Multi-target regressor with pre-order dispatch boundaries. |
| **Database Recovery (RTO)** | 7.95s End-to-End | $< 30.0$s SLA | **`PASS`** | Decrypt (0.26s) + SQL import (7.51s) in isolated test DB. |
| **Data Preservation (RPO)** | 15.0m Binlogs | $\le 15.0$m SLA | **`PASS`** | 15-minute AES-256 encrypted incremental binary log archiver. |
| **Canonical Parity** | ₹0.00 Variance | 100.0% Exact Parity | **`PASS`** | All 49,971 orders and ₹46.59M GMV match MySQL ground truth. |
