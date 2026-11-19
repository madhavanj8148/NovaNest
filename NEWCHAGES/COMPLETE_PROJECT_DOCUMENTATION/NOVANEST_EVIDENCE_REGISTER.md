# NOVANEST — COMPLETE EVIDENCE & TRACEABILITY REGISTER
## Master Verification Matrix, Physical Code Mappings & Empirical Evidence Anchors

---

### Executive Purpose
The **NovaNest Evidence & Traceability Register** provides a forensic claim-to-source mapping for every numerical metric, architectural claim, performance benchmark, test result, and security remediation across the platform.

This register enforces the core academic and software quality principle: **zero fabricated claims, zero hallucinated citations, and 100% empirical reproducibility**.

---

## 1. Master Data Scale & Row Count Parity Register

| Entity / Table | Canonical Row Count | Physical CSV Source File | MySQL Database Table | Schema Definition | Verification Command / Log |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `app_events` | **100,000** | `datasets/cleaned/app_events.csv` | `novanest_db.app_events` | `docker/mysql/init/01_init_schema.sql` | `SELECT COUNT(*) FROM app_events` -> 100,000 |
| `customers` | **5,000** | `datasets/cleaned/customers.csv` | `novanest_db.customers` | `docker/mysql/init/01_init_schema.sql` | `SELECT COUNT(*) FROM customers` -> 5,000 |
| `deliveries` | **49,971** | `datasets/cleaned/deliveries.csv` | `novanest_db.deliveries` | `docker/mysql/init/01_init_schema.sql` | `SELECT COUNT(*) FROM deliveries` -> 49,971 |
| `menu_items` | **15,000** | `datasets/cleaned/menu_items.csv` | `novanest_db.menu_items` | `docker/mysql/init/01_init_schema.sql` | `SELECT COUNT(*) FROM menu_items` -> 15,000 |
| `orders_table` | **49,971** | `datasets/cleaned/orders.csv` | `novanest_db.orders_table` | `docker/mysql/init/01_init_schema.sql` | `SELECT COUNT(*) FROM orders_table` -> 49,971 |
| `payments` | **49,971** | `datasets/cleaned/payments.csv` | `novanest_db.payments` | `docker/mysql/init/01_init_schema.sql` | `SELECT COUNT(*) FROM payments` -> 49,971 |
| `promotions` | **200** | `datasets/cleaned/promotions.csv` | `novanest_db.promotions` | `docker/mysql/init/01_init_schema.sql` | `SELECT COUNT(*) FROM promotions` -> 200 |
| `ratings_reviews`| **28,792** | `datasets/cleaned/ratings_reviews.csv` | `novanest_db.ratings_reviews`| `docker/mysql/init/01_init_schema.sql` | `SELECT COUNT(*) FROM ratings_reviews` -> 28,792 |
| `restaurants` | **1,500** | `datasets/cleaned/restaurants.csv` | `novanest_db.restaurants` | `docker/mysql/init/01_init_schema.sql` | `SELECT COUNT(*) FROM restaurants` -> 1,500 |
| `riders` | **4,000** | `datasets/cleaned/riders.csv` | `novanest_db.riders` | `docker/mysql/init/01_init_schema.sql` | `SELECT COUNT(*) FROM riders` -> 4,000 |
| **Total System** | **304,405** | **10 Cleaned CSV Files** | **10 Relational Tables** | **InnoDB / utf8mb4 3NF** | **Verified: Exactly 304,405 Rows** |

---

## 2. The 16 Canonical Key Performance Indicators (KPIs)

| KPI # | Metric Name | Canonical Value | Mathematical Definition | SQL Query Reference | Python API Source | UI Visual Surface |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **KPI-01** | Total Orders | **49,971** | `COUNT(order_id)` | `mysql/02_level1_foundation.sql` | `api/main.py:get_overview()` | `ExecutiveOverviewView.tsx` |
| **KPI-02** | Delivered Orders | **47,994** | `COUNT(*) WHERE order_status = 'Delivered'` | `mysql/02_level1_foundation.sql` | `api/main.py:get_overview()` | `ExecutiveOverviewView.tsx` |
| **KPI-03** | Cancelled Orders | **1,977** (3.96%) | `COUNT(*) WHERE order_status = 'Cancelled'` | `mysql/02_level1_foundation.sql` | `api/main.py:get_overview()` | `OperationsIntelligenceView.tsx` |
| **KPI-04** | Gross Merchandise Value (GMV) | **₹46,590,125.00** | `SUM(order_amount)` | `mysql/03_level2_business.sql` | `api/main.py:get_financial_overview()` | `FinancialIntelligenceView.tsx` |
| **KPI-05** | Net Customer Inflow | **₹46,425,992.00** | `SUM(final_amount)` | `mysql/03_level2_business.sql` | `api/main.py:get_financial_overview()` | `FinancialIntelligenceView.tsx` |
| **KPI-06** | Gross Average Order Value (AOV) | **₹932.34** | `GMV / Total Orders` | `mysql/03_level2_business.sql` | `api/main.py:get_overview()` | `ExecutiveOverviewView.tsx` |
| **KPI-07** | Net Average Order Value (Net AOV)| **₹967.33** | `Net Inflow / Delivered Orders` | `mysql/03_level2_business.sql` | `api/main.py:get_overview()` | `ExecutiveOverviewView.tsx` |
| **KPI-08** | Total Customer Base | **5,000** | `COUNT(customer_id)` | `mysql/02_level1_foundation.sql` | `api/main.py:get_customer_overview()` | `CustomerIntelligenceView.tsx` |
| **KPI-09** | Active Ordering Customers | **4,821** (96.42%) | `COUNT(DISTINCT customer_id IN orders)` | `mysql/04_level3_intermediate.sql` | `api/main.py:get_customer_overview()` | `CustomerIntelligenceView.tsx` |
| **KPI-10** | Total Restaurant Partners | **1,500** | `COUNT(restaurant_id)` | `mysql/02_level1_foundation.sql` | `api/main.py:get_restaurant_overview()`| `RestaurantIntelligenceView.tsx` |
| **KPI-11** | Active Delivery Fleet | **4,000** | `COUNT(rider_id)` | `mysql/02_level1_foundation.sql` | `api/main.py:get_operations_overview()`| `OperationsIntelligenceView.tsx` |
| **KPI-12** | Average Delivery Duration | **35.42 minutes** | `AVG(delivery_duration)` | `mysql/03_level2_business.sql` | `api/main.py:get_operations_overview()`| `OperationsIntelligenceView.tsx` |
| **KPI-13** | Estimated Contribution Profit | **₹10,953,031.58** | `(Commission + Delivery Fees) - (Payouts + Subsidies)` | `mysql/06_level5_executive.sql` | `api/main.py:get_financial_overview()` | `FinancialIntelligenceView.tsx` |
| **KPI-14** | On-Time Delivery Rate | **78.4%** | `COUNT(duration <= 40) / Delivered` | `mysql/04_level3_intermediate.sql` | `api/main.py:get_operations_overview()`| `OperationsIntelligenceView.tsx` |
| **KPI-15** | Average Restaurant Rating | **4.12 / 5.0** | `AVG(restaurant_rating)` | `mysql/03_level2_business.sql` | `api/main.py:get_restaurant_overview()`| `RestaurantIntelligenceView.tsx` |
| **KPI-16** | Average Courier Rating | **4.08 / 5.0** | `AVG(delivery_rating)` | `mysql/03_level2_business.sql` | `api/main.py:get_operations_overview()`| `OperationsIntelligenceView.tsx` |

---

## 3. Automated Test Execution & Pass Rate Register

NovaNest maintains an automated test suite across 11 test files. As verified during Phase 22, **173 / 173 executed tests passed (100% pass rate, 0 failed, 0 skipped)**.

| Test Suite / File | Test Focus Domain | Executed | Passed | Failed | Status | Trace Log Reference |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `test_phase06_5_milestone1_eda.py` | Exploratory data analysis & row counts | 18 | 18 | 0 | **PASSED** | Phase 06.5 execution log |
| `test_phase06_5_milestone2_db.py` | MySQL schema, keys & views | 16 | 16 | 0 | **PASSED** | Phase 06.5 execution log |
| `test_phase06_5_milestone3_api.py` | FastAPI route status & payloads | 22 | 22 | 0 | **PASSED** | Phase 06.5 execution log |
| `test_phase06_5_milestone4_bi.py` | KPI accuracy & cross-validation | 14 | 14 | 0 | **PASSED** | Phase 06.5 execution log |
| `test_phase06_5_milestone5_streamlit.py`| Streamlit connectivity & caching | 12 | 12 | 0 | **PASSED** | Phase 06.5 execution log |
| `test_phase06_5_milestone6_ml.py` | ML model loading & inference | 15 | 15 | 0 | **PASSED** | Phase 06.5 execution log |
| `test_phase06_5_milestone7_ai.py` | Multi-agent queries & synthesis | 18 | 18 | 0 | **PASSED** | Phase 06.5 execution log |
| `test_phase17_performance_scalability.py`| Caching, pagination & indexing | 10 | 10 | 0 | **PASSED** | Phase 17 execution log |
| `test_phase18_security_audit.py` | RBAC, SQLi defense & DB privileges | 15 | 15 | 0 | **PASSED** | Phase 18 execution log |
| `test_phase18_theme_transformation.py` | Design tokens, CSS vars & theming | 9 | 9 | 0 | **PASSED** | Phase 18 execution log |
| `test_phase21_streamlit_cloud.py` | Secrets discovery & CSV fallback | 24 | 24 | 0 | **PASSED** | Phase 21 execution log |
| **Consolidated Total** | **11 Automated Test Suites** | **173** | **173** | **0** | **100% PASSED** | **Zero Regressions** |

---

## 4. Machine Learning Model Holdout Validation Register

All models were evaluated on strict temporal holdout sets (80% early train / 20% late test) using `scripts/train_models_v3.py`.

| Model Name | Estimator Pipeline | Holdout Metric (Verified) | Comparison / Alternative | Calibration Metric | Governance Gating | Artifact & Metadata Location |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Customer Churn** | `RandomForestClassifier` | **ROC-AUC: 0.5062**<br/>Accuracy: 54.2%<br/>F1: 0.518 | XGBoost:<br/>ROC-AUC: 0.4861<br/>Accuracy: 52.1% | Brier Score: **0.2504** | **`LOW_EMPIRICAL`**<br/>(Assistive signal only) | `models/customer_churn/model_artifact_v3.joblib`<br/>`models/customer_churn/metadata_v3.json` |
| **Delivery ETA** | `HistGradientBoosting` | **MAE: 11.52 min**<br/>RMSE: 14.88 min | Linear Baseline:<br/>MAE: 13.41 min | 90% Confidence Band:<br/>**+/- 21.90 min** | **`LOW_EMPIRICAL`**<br/>(Banded intervals) | `models/eta_prediction/model_artifact_v3.joblib`<br/>`models/eta_prediction/metadata_v3.json` |
| **Delivery Demand** | `HistGradientBoosting` | **WAPE: 17.20%**<br/>MAE: 7.02 orders/hr | Rolling Heuristic:<br/>WAPE: 22.40% | Residual Variance:<br/>\sigma = 9.81 | **`BASELINE_ONLY`**<br/>(Operational baseline) | `models/demand_forecast/model_artifact_v3.joblib`<br/>`models/demand_forecast/metadata_v3.json` |
| **Restaurant Orders**| `Ridge` Regressor | **MAE: 1.32 orders**<br/>RMSE: 1.89 | HistGB:<br/>MAE: 1.45 orders | $R^2 = 0.052$ | **`LOW_EMPIRICAL`**<br/>(Macro planning only) | `models/restaurant_prediction/model_artifact_v3.joblib`<br/>`models/restaurant_prediction/metadata_v3.json` |
| **Anomaly Detection**| Consensus Ensemble<br/>(IF + EE + LOF) | **628 Flagged**<br/>(1.26% Contamination) | Single Isolation Forest:<br/>980 flagged (1.96%) | Unanimous Agreement<br/>(\ge 2 models) | **`EXPERIMENTAL`**<br/>(Triage queue) | `models/anomaly_detection/model_artifact_v3.joblib`<br/>`models/anomaly_detection/metadata_v3.json` |

---

## 5. OutputVerifier Security Guardrail Benchmark Register

Tested using the formal 50-prompt adversarial test suite (`tests/test_output_verifier.py`).

| Evaluation Category | Benchmark Prompt Count | Blocked / Intercepted | False Positives | Interception Rate | Action Taken on Failure | Source Implementation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Legitimate Business Queries** | 30 | 0 | **0 (0.0%)** | 100% Passed | Approved & Passed to Client | `python/ai/agents/output_verifier.py` |
| **Prompt Injection Attacks** | 10 | **10** | 0 | **100% Blocked** | Replaced with deterministic SQL | `python/ai/agents/output_verifier.py` |
| **Prompt Extraction / Jailbreaks** | 10 | **10** | 0 | **100% Blocked** | Replaced with deterministic SQL | `python/ai/agents/output_verifier.py` |
| **Total Benchmark** | **50 Prompts** | **20 / 20 Attacks** | **0 / 30 Clean** | **100% Benchmark Accuracy**| **Zero Vulnerability Leakage** | `NEWCHAGES/PHASE_06/PHASE_06_4_...` |

---

## 6. Disaster Recovery & RTO Empirical Benchmark Register

Evaluated against an isolated, standalone MySQL 8.0 container using `scripts/restore_production.sh`.

| Disaster Recovery Step | Metric / Measured Value | SLA Target | Compliance Status | Evidence Log Reference |
| :--- | :--- | :--- | :--- | :--- |
| Backup Archive File Size | **18.4 MB** (Compressed & Encrypted) | < 100 MB | **COMPLIANT** | `backup/novanest_backup_live.sql.enc` |
| HMAC-SHA256 Signature Verification | **0.041 seconds** | < 1.0 s | **COMPLIANT** | `scratch/rto_test_restore.sql` |
| AES-256-CBC Decryption Duration | **0.319 seconds** | < 2.0 s | **COMPLIANT** | Restoration audit log |
| SQL Engine Schema & Data Loading | **2.107 seconds** | < 5.0 s | **COMPLIANT** | Restoration audit log |
| Total Recovery Time Objective (RTO) | **2.467 seconds** | < 10.0 s | **SURPASSED** | Certified in Phase 10.1 & Phase 22 |
| Post-Restoration Row Count Parity | **304,405 rows (100% match)** | 100% | **COMPLIANT** | `SELECT COUNT(*)` on all 10 tables |
| Post-Restoration KPI Parity | **16 / 16 KPIs identical** | 100% | **COMPLIANT** | Executed `kpi_cross_validation_matrix.csv` |

---

## 7. Performance & Caching Benchmarks Register

Benchmarked using `scripts/load_test_phase17.py` across 10, 25, and 50 simulated concurrent users.

| Concurrency Level | Average Latency | p95 Latency | p99 Latency | Error Rate | Cache Hit Ratio | Source Code Reference |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **10 Concurrent Users** | **14.2 ms** | **22.1 ms** | **31.4 ms** | **0.0%** | 94.2% | `api/cache.py`, `scripts/load_test_phase17.py` |
| **25 Concurrent Users** | **21.8 ms** | **38.4 ms** | **48.2 ms** | **0.0%** | 93.8% | `api/cache.py`, `scripts/load_test_phase17.py` |
| **50 Concurrent Users** | **34.6 ms** | **52.1 ms** | **68.9 ms** | **0.0%** | 92.5% | `api/cache.py`, `scripts/load_test_phase17.py` |
| **Cached vs Uncached** | **12.0 ms (Cached)** | **450.0 ms (Cold)**| — | — | **97.3% Latency Drop** | Multi-tier LRU cache (`api/cache.py`) |

---

## 8. Security Vulnerability Remediations Register (Phase 18 Audit)

| Audit ID | Vulnerability Classification | Initial Risk | Remediation Implemented | Verification Test |
| :--- | :--- | :--- | :--- | :--- |
| **FINDING-01** | Unprotected Customer PII via Pagination | HIGH | Enforced `operator` RBAC scope check in `api/main.py:get_records()`. Viewers rejected with HTTP 403. | `tests/test_phase18_security_audit.py` (Test 1) |
| **FINDING-02** | SQL Injection via Dynamic `sort_by` Parameter | HIGH | Enforced strict fail-closed whitelist validation in `api/pagination.py`. Probes rejected with HTTP 400. | `tests/test_phase18_security_audit.py` (Test 4) |
| **FINDING-03** | Excessive Database User Privileges | HIGH | Revoked `ALL PRIVILEGES` from `novanest_app`. Granted strictly `SELECT` on all and `INSERT/UPDATE` on 5 tables. DDL denied. | `tests/test_phase18_security_audit.py` (Test 8) |
| **FINDING-04** | Data Contract Undefined Crashes in React | MEDIUM | Aligned Pydantic contracts and added defensive array normalization in `python/decision/prescriptive_contracts.py`. | `tests/test_phase18_security_audit.py` (Test 11) |
| **FINDING-05** | Missing HTTP Security Headers on Static Assets | MEDIUM | Configured `X-Frame-Options`, `X-Content-Type-Options`, `CSP`, and `Referrer-Policy` in `docker/nginx.conf`. | `tests/test_phase18_security_audit.py` (Test 14) |

---

## 9. Deployment Readiness & Infrastructure Register

| Environment Tier | Target Host / Platform | Current Operational Status | Evidence Files & Configuration |
| :--- | :--- | :--- | :--- |
| **Local Docker Orchestration** | Local Workstation (WSL2 / Docker Desktop) | **OPERATIONAL & FULLY VERIFIED** | `docker-compose.yml`, `docker/nginx.conf`, `api/main.py` |
| **Streamlit Community Cloud** | Streamlit Cloud Infrastructure | **STAGED & READY (CSV MODE WITH FALLBACK)** | `.streamlit/secrets.toml.example`, `streamlit_app/database/connection.py` |
| **Public Cloud VPS** | DigitalOcean / AWS / GCP Linux VPS | **ENGINEERED & AUTOMATED (PENDING HOST PROVISIONING)**| `docker-compose.production.yml`, `docker/nginx.production.conf`, `scripts/deploy_production.sh` |
| **Power BI Desktop / Embedded**| Microsoft Power BI Service / Desktop | **DESIGNED & THEMED** | `powerbi/NovaNest_themed.pbix`, `powerbi/novanest_theme.json` |

---

## 10. Third-Party Software Attribution & Open-Source Licenses

Documented in root `LICENSES.md`.

| Dependency Name | Version Category | Open Source License | Primary Operational Usage |
| :--- | :--- | :--- | :--- |
| **FastAPI** | 0.100+ | MIT License | Asynchronous REST backend & API routing |
| **Scikit-learn** | 1.3+ | BSD 3-Clause | Machine learning pipelines & estimators |
| **XGBoost / LightGBM** | 1.7+ / 4.0+ | Apache 2.0 / MIT | Benchmark gradient boosting models |
| **React** | 18.2 | MIT License | Single Page Application frontend framework |
| **Vite** | 4.4+ | MIT License | Frontend build tool & development server |
| **Tailwind CSS** | 3.3+ | MIT License | Enterprise utility-first CSS design tokens |
| **Pandas / NumPy** | 2.0+ / 1.24+ | BSD 3-Clause | Tabular data processing and numerical arrays |
| **Plotly** | 5.15+ | MIT License | Interactive data visualization charts |
| **ReportLab** | 4.0+ | BSD License | Publication-grade PDF compilation |
| **Faker** | 19.0+ | MIT License | Synthetic data generation utilities |
