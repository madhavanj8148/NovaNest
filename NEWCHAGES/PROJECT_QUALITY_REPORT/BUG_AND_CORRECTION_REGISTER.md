# NovaNest – Bug & Correction Register

**Audit Date**: November 18, 2026  
**Auditor**: Lead Software Architect & Debugging Specialist  
**Governance**: Non-destructive fixes only; zero schema changes; zero data modifications.

---

## 1. Summary of Identified Defects

During the final quality validation, five verifiable code, configuration, and test defects were identified, analyzed, and successfully resolved:

| Defect ID | Category | Severity | Affected File | Resolution |
| :---: | :--- | :---: | :--- | :---: |
| **DEF-001** | AI Governance | High | `python/ai/agents/base.py` | Fixed `is_production_ready` tier condition for operational models |
| **DEF-002** | Output Verification | High | `python/ai/agents/output_verifier.py` | Added caveat warning metrics to numerical evidence extraction |
| **DEF-003** | Test Harness | Medium | `tests/test_ask_novanest_ai_suite.py` | Added in-process `fastapi.testclient.TestClient` fallback |
| **DEF-004** | Security Test | Medium | `tests/test_phase06_13_security_hardening.py`| Synchronized sliding window test with configured 1,200 req/min limit |
| **DEF-005** | Frontend Dev Server | Critical | `frontend/vite.config.ts` | Configured Vite dev server proxy forwarding `/api` to backend port 8001 |

---

## 2. Detailed Defect Analysis & Fixes

### 2.1 DEF-001: Incorrect `is_production_ready` Tagging for `OPERATIONAL_GATED` Models
- **Symptom**: In `tests/test_phase06_3_orchestrator.py`, tests failed with `AssertionError: False is not true` on `chat["grounding_verified"]`, with rejection notice `[EXPERIMENTAL_ML_OVERCLAIM]`.
- **Root Cause**: In `python/ai/agents/base.py` line 130, `is_production_ready=(tier in ("HIGH", "OPERATIONAL_GATED"))` erroneously marked `OPERATIONAL_GATED` models (such as `anomaly_detection`) as production-ready. The synthesizer emitted `production-ready=True`, triggering `OutputVerifier`'s regex rejection `_ML_OVERCLAIM_RE`.
- **Correction Applied**:
  ```python
  # File: python/ai/agents/base.py (Line 130)
  is_production_ready=(tier == "HIGH"),
  ```
- **Verification Evidence**: `tests/test_phase06_3_orchestrator.py` runs **15 / 15 PASSED** (100% Green).

---

### 2.2 DEF-002: Evidence Extraction Omitted Caveat Warnings
- **Symptom**: `OutputVerifier` rejected legitimate model metadata text, flagging `[UNSUPPORTED_NUMERIC_CLAIM] '0.0000'` for baseline R² scores cited in model caveats.
- **Root Cause**: In `python/ai/agents/output_verifier.py` line 448, the scanner inspected only `caveat.metric_summary`, ignoring numbers appearing in `caveat.warning` (e.g. `baseline R²=0.0000`).
- **Correction Applied**:
  ```python
  # File: python/ai/agents/output_verifier.py (Line 448)
  for caveat in res.caveats:
      evidence.update(self._extract_numbers(f"{caveat.metric_summary} {caveat.warning}"))
  ```
- **Verification Evidence**: All legitimate caveats now ground properly without triggering unsupported claim false positives.

---

### 2.3 DEF-003: Hardcoded Live HTTP Server Assumption in Test Runner
- **Symptom**: `tests/test_ask_novanest_ai_suite.py` crashed on startup with:
  `requests.exceptions.ConnectionError: [WinError 10061] No connection could be made because target machine actively refused it (127.0.0.1:8000)`
- **Root Cause**: `setUpClass` unconditionally dispatched live HTTP requests to `http://127.0.0.1:8000`, failing when run offline without an active uvicorn background process.
- **Correction Applied**:
  ```python
  # File: tests/test_ask_novanest_ai_suite.py
  @classmethod
  def setUpClass(cls):
      try:
          import urllib.request
          with urllib.request.urlopen("http://127.0.0.1:8000/docs", timeout=0.3):
              cls.use_live = True
      except Exception:
          from fastapi.testclient import TestClient
          from api.main import app
          cls.use_live = False
          cls.client = TestClient(app)
  ```
- **Verification Evidence**: `tests/test_ask_novanest_ai_suite.py` now passes **14 / 14 tests** in-process.

---

### 2.4 DEF-004: Rate Limiter Test Assumption Mismatch
- **Symptom**: `tests/test_phase06_13_security_hardening.py` failed `test_sliding_window_rate_limiting`.
- **Root Cause**: Test hardcoded a 300 requests/min assumption, but production `_general_limit` is set to 1,200 requests/min to accommodate multi-tab enterprise dashboards.
- **Correction Applied**:
  Updated test to consume `limit = rate_limiter._general_limit` requests, verifying that the `(limit + 1)`-th request is blocked.
- **Verification Evidence**: `tests/test_phase06_13_security_hardening.py` now passes **25 / 25 tests** (100% Green).

---

### 2.5 DEF-005: Missing Dev Server Proxy Caused JSON Parsing Exception
- **Symptom**: In the React frontend browser session, API calls failed with the error:
  `SyntaxError: Unexpected token '<', "<!doctype..." is not valid JSON.`
- **Root Cause**: `frontend/vite.config.ts` had no proxy configuration. When the React app requested `/api/...`, Vite dev server treated the path as a single-page app route and returned `index.html` (which starts with `<!doctype html>`). When `res.json()` parsed this HTML string, it crashed.
- **Correction Applied**:
  ```typescript
  // File: frontend/vite.config.ts
  server: {
    port: 5173,
    host: '127.0.0.1',
    proxy: {
      '/api': {
        target: process.env.VITE_BACKEND_URL || 'http://127.0.0.1:8001',
        changeOrigin: true,
      },
    },
  },
  ```
- **Verification Evidence**:
  - `curl.exe -s http://localhost:5173/api/health` now returns verified JSON (`{"status":"healthy", ...}`).
  - `curl.exe -s -H "X-API-Key: test-operator-key-phase06-8" http://localhost:5173/api/overview` returns complete 16-KPI payload.
  - Automated headless Chrome captures of `http://localhost:5173` successfully render all 9 tabs with live data.
