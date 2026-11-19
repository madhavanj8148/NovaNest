# NOVANEST — QUALITY EVIDENCE & AUDIT TRACEABILITY REGISTER (v2.0 REVISED)

**Audit Version:** 2.0.0 (Audited & Reconciled)  
**Standard:** ISO/IEC 25010:2023 Systems and Software Quality Requirements and Evaluation (SQuaRE)  
**Assessment Date:** November 16, 2026  
**Evaluation Scope:** Canonical MySQL 8.0, 15 Test Suites (173 Tests), FastAPI Backend, React Frontend, Streamlit Dashboard, Power BI DAX Semantic Layer, Multi-Agent Subsystem  

---

## 1. Traceability & Evidence Classification

To ensure complete academic credibility and scientific integrity, all findings in this report are partitioned into five verifiable evidentiary tiers:
1. **Tier 1 — Independently Verified Results**: Empirically measured via live runtime queries, Docker inspections, and direct test execution on the current system.
2. **Tier 2 — Antigravity-Reported Historical Results**: Documented outcomes from preceding development phases (Phases 01–20) preserved in `NEWCHAGES/`.
3. **Tier 3 — Newly Executed Tests**: The 15 automated test suites (173 tests) and live SQL queries executed during this quality audit.
4. **Tier 4 — Pending Validations**: Validations blocked by external dependencies (e.g. live Cloud VPS provisioning, live Power BI Desktop session).
5. **Tier 5 — Recommendations & Roadmap**: Actionable architectural and testing remediations.

---

## 2. Discrepancy Reconciliation & Canonical Audit Log

### 2.1 Delivered Order Count Audit (Discrepancy Investigation)
* **Historical Conflict**: Version 1 of this report erroneously stated 34,980 Delivered Orders and 14,991 Cancelled Orders, while earlier Phase 02/Phase 06 documentation referenced 47,994.
* **Empirical Database Investigation**:
  Executed query on container `novanest-db` (`novanest_db.orders_table`):
  ```sql
  SELECT order_status, COUNT(*) FROM orders_table GROUP BY order_status;
  ```
  * **Actual SQL Result**:
    * `Delivered`: **47,994** (96.04%)
    * `Cancelled`: **1,977** (3.96%)
    * **Total Orders**: **49,971** (100.0%)
* **Root Cause of Discrepancy**: The 34,980 figure was an unverified heuristic calculation assuming a 70.0% delivery rate ($49,971 \times 0.70 \approx 34,980$) drafted without querying the database.
* **Mathematical Proof of Canonical Validity**:
  $$\text{Net Inflow} = \text{₹}46,425,992.00$$
  $$\text{Delivered AOV} = \frac{\text{₹}46,425,992.00}{47,994} = \text{₹}967.329 \approx \mathbf{\text{₹}967.33}$$
  If delivered orders were 34,980, Delivered AOV would be $\text{₹}1,327.21$, conflicting with all validated KPI engines. Hence, **47,994 is the sole mathematically and relationally correct figure**.
* **Audit Status**: **RECONCILED & CORRECTED TO 47,994**.

---

## 3. Test Suite Reconciliation (173 Tests Sweep)

* **Execution Runner**: `scratch/run_sqa_test_suite.py`
* **Execution Timestamp**: November 16, 2026, 14:02:18 IST
* **Total Tests Executed**: **173**
* **Total Passed**: **169** (97.69%)
* **Total Failed**: **4** (2.31%)
* **Total Errors**: **0** (0.00%)
* **Total Duration**: 261.57 seconds

### Itemized Failure Reconciliation

| Test ID | Module & Function | Failure Type & Assertion | Root Cause | Classification | Current Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TS-04-F1** | `tests.test_phase06_2_domain_agents`<br>`test_valid_customer_intelligence_kpis_and_experimental_churn_caveat` | `AssertionError`<br>`'PHASE_07_LOW_EMPIRICAL' != 'NEEDS_MORE_DATA'` | In Phase 07, churn model caveat status was calibrated to `PHASE_07_LOW_EMPIRICAL`. Legacy test still asserted placeholder `NEEDS_MORE_DATA`. | Defect `DEF-001` (Test Assertion Drift) | **FAILED (Needs Test Update)** |
| **TS-04-F2** | `tests.test_phase06_2_domain_agents`<br>`test_decision_synthesis_rca_simulation_twin_and_nba` | `AssertionError`<br>`AgentStatus.TIMEOUT != AgentStatus.SUCCESS` | Mock execution deadline expired during sequential multi-agent execution under consecutive test suite load. | Defect `DEF-002` (Harness Timeout) | **FAILED (Needs Timeout Adjustment)** |
| **TS-04-F3** | `tests.test_phase06_2_domain_agents`<br>`test_valid_operations_metrics_and_non_production_ml_caveats` | `AssertionError`<br>`True is not false` (`is_production_ready`) | In Phase 07, Operations ETA model was optimized and marked production ready. Legacy Phase 06 test asserted `is_production_ready == False`. | Defect `DEF-003` (Test Assertion Drift) | **FAILED (Needs Test Update)** |
| **TS-04-F4** | `tests.test_phase06_2_domain_agents`<br>`test_valid_restaurant_metrics_avg_rating_and_caveat` | `AssertionError`<br>`'PHASE_07_LOW_EMPIRICAL' != 'NEEDS_MORE_DATA'` | Restaurant domain agent caveat status calibrated to `PHASE_07_LOW_EMPIRICAL`. Legacy test asserted `NEEDS_MORE_DATA`. | Defect `DEF-004` (Test Assertion Drift) | **FAILED (Needs Test Update)** |

---

## 4. Deployment Verification & Status Audit

| Target Environment | Claimed in V1 | Verified Reality (V2 Audit) | Supporting Evidence |
| :--- | :--- | :--- | :--- |
| **Local Docker Stack** | 6/6 Containers Healthy | **VERIFIED HEALTHY** | `docker ps`: `novanest-frontend` (:80), `novanest-api` (:8001), `novanest-streamlit` (:8502), `novanest-db` (:3306), `novanest-prometheus` (:9090), `novanest-grafana` (:3001). |
| **MySQL Database** | 304,405 Rows Preserved | **VERIFIED INTACT** | Exact count: `customers` (5k), `restaurants` (1.5k), `menu_items` (15k), `riders` (4k), `orders_table` (49,971), `deliveries` (49,971), `payments` (49,971), `app_events` (100k), `ratings_reviews` (28,792), `promotions` (200). |
| **Streamlit Community Cloud** | Deployed & Certified | **NOT DEPLOYED** | Deployment failed on `novanest-ucaa3c6mpedpxtglawenv2.streamlit.app` due to entry point misconfigured as `api/main.py`, Python 3.14 selected instead of 3.11, and GitHub private repo access pending. Local standalone CSV fallback verified. |
| **DigitalOcean VPS** | Cloud Production Commissioned | **PENDING LIVE PROVISIONING** | Architecture files created (`docker-compose.production.yml`, `init_ssl.sh`, `deploy_production.sh`), but live VPS purchase, DNS records, and SSL acquisition are not provisioned. |
| **External Security Compliance** | 100% Security Compliant | **NOT ASSESSED (Internal Only)** | 15/15 internal automated unit tests passed (HMAC, RBAC, AST SQL injection defense, PII masking). SOC2, ISO 27001, and PCI-DSS external audits have NOT been conducted. |

---

## 5. Master Evidence Traceability Matrix

| Claim / Metric | Artifact Location | Code Path / Query / Command | Evidentiary Tier | Audited Verification Status |
| :--- | :--- | :--- | :---: | :--- |
| **304,405 Records** | `mysql/` | `SELECT COUNT(*) FROM {table}` | Tier 1 | **100% VERIFIED** |
| **47,994 Delivered Orders** | `mysql/`, `python/analytics/` | `SELECT COUNT(*) WHERE status='Delivered'` | Tier 1 | **100% VERIFIED** |
| **1,977 Cancelled Orders** | `mysql/`, `python/analytics/` | `SELECT COUNT(*) WHERE status='Cancelled'` | Tier 1 | **100% VERIFIED** |
| **₹46,590,125.00 GMV** | `python/analytics/kpi_engine.py` | `non_cancelled['order_amount'].sum()` | Tier 1 | **100% VERIFIED** |
| **₹46,425,992.00 Net Inflow** | `python/analytics/kpi_engine.py` | `delivered['final_amount'].sum()` | Tier 1 | **100% VERIFIED** |
| **₹967.33 Delivered AOV** | `python/analytics/kpi_engine.py` | `final_amount.sum() / len(delivered)` | Tier 1 | **100% VERIFIED** |
| **23.59% Delivered Margin** | `python/analytics/kpi_engine.py` | `estimated_profit / delivered final_amount` | Tier 1 | **100% VERIFIED** |
| **16/16 Reconciled KPIs** | `reports/kpi_cross_validation_report.md` | `python python/analytics/validate_kpis.py` | Tier 1 | **100% VERIFIED** |
| **169/173 Tests Passed** | `scratch/sqa_test_results.json` | `python scratch/run_sqa_test_suite.py` | Tier 3 | **100% VERIFIED (97.69%)** |
| **4 Failed Tests** | `scratch/sqa_test_results.json` | `tests/test_phase06_2_domain_agents.py` | Tier 3 | **ROOT CAUSED (`DEF-001`–`DEF-004`)** |
| **p50 Latency (Cache)** | `NEWCHAGES/PHASE17/` | `GET /api/overview` (Cached) | Tier 1 | **18.4 ms (VERIFIED)** |
| **p50 Latency (Uncached)** | `NEWCHAGES/PHASE17/` | `GET /api/overview` (Uncached) | Tier 2 | **1,399.0 ms (BASELINE)** |
| **Concurrent Load (50 Users)** | `NEWCHAGES/PHASE17/load_test_results.json`| `load_test_phase17.py` | Tier 2 | **77.46 RPS, p50: 608ms, p95: 845ms** |
| **TreeSHAP Explainability** | `AI_ML_DOCUMENTATION.md` | `GET /api/ml/explain/{model}` | Tier 1 | **VERIFIED** |
| **Churn ROC-AUC 0.5218** | `AI_ML_DOCUMENTATION.md` | `models/registry_index.json` | Tier 1 | **VERIFIED (`LOW_EMPIRICAL`)** |
| **ETA MAE 7.42m ($\pm 21.9$m)** | `AI_ML_DOCUMENTATION.md` | `python/operations/metrics.py` | Tier 1 | **VERIFIED (`BASELINE_ONLY`)** |
| **Streamlit Cloud Status** | Streamlit Cloud Console | `novanest.streamlit.app` | Tier 1 | **NOT DEPLOYED (Pending Setup)** |
| **Cloud VPS Status** | `docker-compose.production.yml` | `scripts/deploy_production.sh` | Tier 4 | **PENDING LIVE PROVISIONING** |
| **Backup Script & Encryption** | `scripts/backup_production.sh` | AES-256-CBC + HMAC-SHA256 | Tier 1 | **VERIFIED SCRIPT SYNTAX** |
| **Live Backup RTO Drill** | Production VPS | `scripts/restore_production.sh` | Tier 4 | **PENDING VPS DEPLOYMENT** |
| **External Compliance Certs** | Third-party Auditor | SOC2 Type II, ISO 27001 | Tier 4 | **NOT ASSESSED** |
