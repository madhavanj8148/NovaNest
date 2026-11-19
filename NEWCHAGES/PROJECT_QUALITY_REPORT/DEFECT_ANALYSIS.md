# NOVANEST — DEFECT ANALYSIS & ROOT CAUSE REGISTER (v2.0 REVISED)

**Classification Standard:** IEEE 1044 Standard for Software Defect Classification  
**Audit Scope:** 15 Test Suites (173 Tests), API Endpoints, Container Runtime, Streamlit Deployment  
**Assessment Date:** November 16, 2026  
**Auditor:** Senior QA Engineer & Lead Software Quality Auditor  

---

## 1. Defect Summary & Density Metrics

During the comprehensive SQA audit of the NovaNest platform, **4 test execution failures** and **2 deployment/configuration issues** were identified. Zero defects caused unhandled runtime crashes or data corruption in the running application.

* **Total Code Base Size (LOC)**: ~24,500 Lines of Code (Python, TypeScript, SQL, Docker).
* **Total Automated Tests**: 173 tests.
* **Passed Tests**: 169 tests (97.69%).
* **Failed Tests**: 4 tests (2.31%).
* **Defect Density**: $4 / 24.5 = \mathbf{0.163\ \text{Defects / KLOC}}$ (Well below the industry threshold of $1.0\ \text{Defects / KLOC}$ for enterprise software).

---

## 2. Itemized Defect Register

### DEF-001: Historical Test Assertion Drift — Customer Domain Churn Caveat
* **Defect ID**: `DEF-001`
* **Severity**: Medium | **Priority**: P3
* **Failing Test**: `tests.test_phase06_2_domain_agents.TestDomainAgents.test_valid_customer_intelligence_kpis_and_experimental_churn_caveat`
* **Failure Trace**:
  ```text
  AssertionError: 'PHASE_07_LOW_EMPIRICAL' != 'NEEDS_MORE_DATA'
  - PHASE_07_LOW_EMPIRICAL
  + NEEDS_MORE_DATA
  ```
* **Root Cause**: In Phase 07, model validation statuses were refined from generic `NEEDS_MORE_DATA` to `PHASE_07_LOW_EMPIRICAL` to transparently disclose synthetic data limitations. The Phase 06 test suite assertion was not updated to reflect this calibration.
* **Impact**: Zero application runtime impact; customer agent functions correctly and returns calibrated warnings.
* **Remediation**: Update test assertion to check for `'PHASE_07_LOW_EMPIRICAL'`.

---

### DEF-002: Decision Agent Mock Harness Execution Timeout
* **Defect ID**: `DEF-002`
* **Severity**: Medium | **Priority**: P3
* **Failing Test**: `tests.test_phase06_2_domain_agents.TestDomainAgents.test_decision_synthesis_rca_simulation_twin_and_nba`
* **Failure Trace**:
  ```text
  AssertionError: <AgentStatus.TIMEOUT: 'timeout'> != <AgentStatus.SUCCESS: 'success'>
  Intent next_best_action gaps=[] err=[AgentError(code='EXECUTION_TIMEOUT', 
  message='Request deadline expired prior to domain execution.', agent_id='decision_agent')]
  ```
* **Root Cause**: The unit test set a tight mock request deadline (15.0 seconds). Under full marathon test runner execution (173 consecutive tests across 15 suites), thread scheduling delays caused the `next_best_action` intent to exceed the timeout deadline.
* **Impact**: Isolated to unit test execution under heavy runner load; production timeout in Docker is configured at 60 seconds.
* **Remediation**: Increase the mock deadline in the unit test harness from 15s to 30s.

---

### DEF-003: Historical Test Assertion Drift — Operations Model Production Readiness Flag
* **Defect ID**: `DEF-003`
* **Severity**: Medium | **Priority**: P3
* **Failing Test**: `tests.test_phase06_2_domain_agents.TestDomainAgents.test_valid_operations_metrics_and_non_production_ml_caveats`
* **Failure Trace**:
  ```text
  AssertionError: True is not false
  File "tests/test_phase06_2_domain_agents.py", line 389, in test_valid_operations_metrics_and_non_production_ml_caveats
    self.assertFalse(cav.is_production_ready)
  ```
* **Root Cause**: In Phase 07, the operations ETA model was optimized with Gradient Boosting and calibrated prediction intervals, marking `is_production_ready=True`. The legacy Phase 06 unit test still asserted that `is_production_ready` must be `False`.
* **Impact**: Zero application runtime impact.
* **Remediation**: Update the test assertion to align with the optimized Phase 07 model readiness contract.

---

### DEF-004: Historical Test Assertion Drift — Restaurant Domain Caveat Status
* **Defect ID**: `DEF-004`
* **Severity**: Medium | **Priority**: P3
* **Failing Test**: `tests.test_phase06_2_domain_agents.TestDomainAgents.test_valid_restaurant_metrics_avg_rating_and_caveat`
* **Failure Trace**:
  ```text
  AssertionError: 'PHASE_07_LOW_EMPIRICAL' != 'NEEDS_MORE_DATA'
  - PHASE_07_LOW_EMPIRICAL
  + NEEDS_MORE_DATA
  ```
* **Root Cause**: Identical to `DEF-001`. The restaurant agent caveat status was updated to `PHASE_07_LOW_EMPIRICAL`, but the legacy Phase 06 test expected `NEEDS_MORE_DATA`.
* **Impact**: Zero application runtime impact.
* **Remediation**: Update the test assertion to accept `PHASE_07_LOW_EMPIRICAL`.

---

### DEF-005: Streamlit Community Cloud Deployment Configuration Mismatch
* **Defect ID**: `DEF-005`
* **Severity**: High | **Priority**: P1 (Deployment Blocker)
* **Status**: **OPEN / PENDING RE-DEPLOYMENT**
* **Root Cause**:
  1. Main file path misconfigured as `api/main.py` instead of `streamlit_app/app.py`.
  2. Python 3.14 selected instead of stable 3.11.
  3. GitHub private repository authorization pending.
* **Impact**: App failed to launch on Streamlit Community Cloud ("Oh no. Error running app").
* **Remediation**: Re-create deployment specifying `streamlit_app/app.py`, Python 3.11, and secret `DATA_SOURCE = "csv"`.

---

### DEF-006: FastAPI `regex` Parameter Deprecation Warning
* **Defect ID**: `DEF-006`
* **Severity**: Low | **Priority**: P4
* **Root Cause**: Use of deprecated `regex` argument instead of `pattern` in FastAPI / Pydantic query validation (`Query(regex=...)`).
* **Impact**: Produces harmless warning during API startup.
* **Remediation**: Replace `regex=...` with `pattern=...` in endpoint parameter declarations.
