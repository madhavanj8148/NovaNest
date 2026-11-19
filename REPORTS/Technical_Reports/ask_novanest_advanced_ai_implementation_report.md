# Ask NovaNest AI — Advanced Business Analyst Implementation Report

**Project:** NovaNest — AI-Powered Food Delivery Business Analytics, Intelligence and Decision Platform  
**System:** Conversational Business Intelligence & Advanced AI Business Analyst  
**Environment:** Localhost (`http://127.0.0.1:8000` REST API, `http://localhost:5173` React Frontend)  
**Date:** 2026-10-11  

---

## Executive Summary

The Ask NovaNest conversational system has been upgraded from a basic query placeholder into an enterprise **Data-Grounded Business Intelligence AI and Advanced AI Business Analyst**.

Rather than relying on free-form generative LLM guessing or hallucinated metrics, Ask NovaNest anchors every response in actual project datasets (MySQL when configured, with seamless CSV fallback), validated analytical modules (CLV, RFM, Churn, Merchant Health, Unit Economics), strict SQL safety guardrails, an empirical Root-Cause Analysis (RCA) engine, and the multi-variable Decision Simulator.

When `GEMINI_API_KEY` is not present, the system operates deterministically using grounded telemetry, exact calculations, and provenance tracking, clearly declaring its status as `unconfigured` or `mock` rather than faking live generative responses. When credentials are supplied, it enriches these verified findings using Google Gemini (`gemini-2.5-flash`).

---

## 1. Existing Architecture Discovered

Before writing new code, an audit was performed across the codebase:
- **Data Access & Storage:** [api/loader.py](file:///c:/Users/madha/OneDrive/Documents/03.CAPSTONE/NovaNest/NovaNest/api/loader.py) loads 10 relational tables (orders, customers, restaurants, deliveries, riders, promotions, etc.) with automatic fallback from MySQL to preprocessed CSVs in `datasets/cleaned/` and `datasets/engineered/`.
- **FastAPI REST API:** [api/main.py](file:///c:/Users/madha/OneDrive/Documents/03.CAPSTONE/NovaNest/NovaNest/api/main.py) serves endpoints on port 8000 for overview KPIs, customer intelligence, restaurant health, logistics dispatch, unit economics, digital twin state, and what-if simulation.
- **Analytical & Simulation Engines:**
  - `python/intelligence/customer/`: CLV, RFM, Cohort retention matrix, Customer 360.
  - `python/intelligence/restaurant/`: Health score, early warning risk detection, peer benchmarking.
  - `python/decision_simulation/`: `scenario_engine.py` coordinating financial, customer, restaurant, and operations impact.
  - `python/digital_twin/`: Twin state and cross-domain impact ripple propagation.
- **Frontend Stack:** React 19 + TypeScript + Vite + TailwindCSS + Lucide Icons + Recharts for charts.

---

## 2. Files Created and Modified

### Created Modules
1. [python/ai/provider/base.py](file:///c:/Users/madha/OneDrive/Documents/03.CAPSTONE/NovaNest/NovaNest/python/ai/provider/base.py): Base class `BaseAIProvider`, `AIProviderResult`, and `ProviderStatus` (`READY`, `UNCONFIGURED`, `MOCK`, `ERROR`).
2. [python/ai/provider/gemini_provider.py](file:///c:/Users/madha/OneDrive/Documents/03.CAPSTONE/NovaNest/NovaNest/python/ai/provider/gemini_provider.py): REST-based Google Gemini provider calling `v1beta/models/gemini-2.5-flash:generateContent`. Handles timeouts (15s), auth errors, rate limits (429), and unconfigured fallback.
3. [python/ai/provider/mock_provider.py](file:///c:/Users/madha/OneDrive/Documents/03.CAPSTONE/NovaNest/NovaNest/python/ai/provider/mock_provider.py): Deterministic offline test provider ensuring zero paid API calls occur during test executions.
4. [python/ai/provider/factory.py](file:///c:/Users/madha/OneDrive/Documents/03.CAPSTONE/NovaNest/NovaNest/python/ai/provider/factory.py): Centralized provider factory with environment detection.
5. [python/ai/provider/__init__.py](file:///c:/Users/madha/OneDrive/Documents/03.CAPSTONE/NovaNest/NovaNest/python/ai/provider/__init__.py): Provider module interface.
6. [python/ai/analyst/data_grounding.py](file:///c:/Users/madha/OneDrive/Documents/03.CAPSTONE/NovaNest/NovaNest/python/ai/analyst/data_grounding.py): Extracts grounded business context, verified KPI cards, and provenance across revenue, cancellations, churn, merchants, operations, and leakage.
7. [python/ai/analyst/sql_agent.py](file:///c:/Users/madha/OneDrive/Documents/03.CAPSTONE/NovaNest/NovaNest/python/ai/analyst/sql_agent.py): Strict SQL validator enforcing read-only `SELECT`/`WITH` queries, table whitelist (`orders`, `customers`, `restaurants`, `deliveries`, `riders`, `promotions`), query length limits, multi-statement blocking, and auto-appended `LIMIT 25`.
8. [python/ai/analyst/root_cause.py](file:///c:/Users/madha/OneDrive/Documents/03.CAPSTONE/NovaNest/NovaNest/python/ai/analyst/root_cause.py): Empirical RCA engine investigating cancellations, delivery delays, margin leakage, and customer churn. Categorizes output into observed empirical facts, contributing factors with correlation ratings, stated uncertainties, and actionable next steps.
9. [python/ai/analyst/simulation_agent.py](file:///c:/Users/madha/OneDrive/Documents/03.CAPSTONE/NovaNest/NovaNest/python/ai/analyst/simulation_agent.py): Translates conversational what-if scenarios into validated simulation parameters, runs `decision_simulation.scenario_engine.run_scenario`, and generates baseline vs simulated delta comparisons.
10. [python/ai/analyst/conversation_manager.py](file:///c:/Users/madha/OneDrive/Documents/03.CAPSTONE/NovaNest/NovaNest/python/ai/analyst/conversation_manager.py): Session-isolated turn memory, sliding-window retention, and follow-up query resolver (e.g., resolving "Which region is the worst?" in context of cancellation rates).
11. [python/ai/analyst/orchestrator.py](file:///c:/Users/madha/OneDrive/Documents/03.CAPSTONE/NovaNest/NovaNest/python/ai/analyst/orchestrator.py): Central orchestration pipeline uniting query routing, context grounding, SQL security, RCA, simulations, recommendations, provider synthesis, and suggestion generation.
12. [python/ai/analyst/__init__.py](file:///c:/Users/madha/OneDrive/Documents/03.CAPSTONE/NovaNest/NovaNest/python/ai/analyst/__init__.py): Analyst package interface.
13. [tests/test_ask_novanest_ai_suite.py](file:///c:/Users/madha/OneDrive/Documents/03.CAPSTONE/NovaNest/NovaNest/tests/test_ask_novanest_ai_suite.py): 14-point automated test suite covering all functional, security, grounding, simulation, and conversational requirements.

### Modified Files
1. [api/main.py](file:///c:/Users/madha/OneDrive/Documents/03.CAPSTONE/NovaNest/NovaNest/api/main.py):
   - Integrated `analyze_business_inquiry` into `POST /api/ai/ask`.
   - Added `POST /api/ai/reset` for explicit context reset.
   - Maintained full backwards compatibility with legacy `sql_query`, `sql_valid`, `validation_message`, `insights`, and `route` keys.
2. [frontend/src/services/api.ts](file:///c:/Users/madha/OneDrive/Documents/03.CAPSTONE/NovaNest/NovaNest/frontend/src/services/api.ts):
   - Extended `ChatResponse` interface with `verified_metrics`, `suggested_chart`, `root_cause_analysis`, `simulation_results`, `recommendations`, `follow_up_suggestions`, `provenance`, and `provider_status`.
   - Updated `askAi(question, session_id)` to transmit session tokens.
   - Added `resetAiSession(session_id)`.
3. [frontend/src/views/AiIntelligenceView.tsx](file:///c:/Users/madha/OneDrive/Documents/03.CAPSTONE/NovaNest/NovaNest/frontend/src/views/AiIntelligenceView.tsx):
   - Redesigned interface into an interactive multi-turn conversation thread.
   - Added "New Chat" session reset button.
   - Integrated dynamic Recharts visualization rendering (Bar, Line, Pie).
   - Added Verified Metrics KPI cards row with provenance badges.
   - Added structured Root-Cause Analysis cards (Confirmed Facts, Contributing Factors, Stated Uncertainties).
   - Added Decision Simulator scenario comparison cards (Baseline vs Simulated metrics).
   - Added SQL Security Audit card and verified dataset result tables.
   - Added clickable context-aware follow-up suggestion chips.

---

## 3. AI Provider Abstraction

The AI provider abstraction is located in `python/ai/provider/`:
- **Current Model:** Google Gemini `gemini-2.5-flash` via the official Google Generative Language v1beta REST API endpoint (`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent`).
- **Isolation & Security:** Credentials (`GEMINI_API_KEY`) remain strictly server-side in backend environment variables. React frontend never receives credentials.
- **Failure Resilience:**
  - `Timeout Handling`: 15-second request timeout guards against hanging upstream requests.
  - `Rate Limiting (429)`: Catches HTTP 429 and returns `ProviderStatus.ERROR` with retry notifications.
  - `Unconfigured State`: When `GEMINI_API_KEY` is not found, the provider returns `ProviderStatus.UNCONFIGURED` without throwing unhandled exceptions.
  - `Extensibility`: `BaseAIProvider` allows adding OpenAI GPT-4o or Claude providers in the future without redesigning Ask NovaNest.

---

## 4. Business Data Grounding & Provenance

When responding to an inquiry, the system executes a 6-step grounding pipeline:
1. **Intent & Topic Routing:** Detects whether the query targets revenue, cancellations, customers/churn, restaurant health, operations/dispatch, promotions, or simulations.
2. **Deterministic Metric Extraction:** Retrieves raw tables from the project data access layer (`orders`, `customers`, `restaurants`, `deliveries`, `churn_predictions`, `revenue_leakage`).
3. **Verified Calculations:** Executes deterministic functions (e.g., exact cancellation percentage, gross merchandise value in Crores, take-rate margin, at-risk customer count, average delivery ETA).
4. **Structured Context Injection:** Supplies only verified figures to the prompt context.
5. **Generative Synthesis (Optional):** If Gemini is configured, it summarizes the verified facts. If unconfigured, the deterministic context summary is returned directly.
6. **Provenance Tracking:** Every response includes the data source name (`MySQL Database` or `CSV File Store`), the calculation period, and the record count.

---

## 5. SQL Safety & Guardrail Architecture

The natural-language-to-SQL functionality in `python/ai/analyst/sql_agent.py` enforces enterprise-grade security:
- **Strict Read-Only:** Queries must begin with `SELECT` or `WITH`.
- **Mutating Command Blocker:** Rejects `DROP`, `DELETE`, `INSERT`, `UPDATE`, `ALTER`, `TRUNCATE`, `REPLACE`, `CREATE`, `EXEC`, `GRANT`, `REVOKE`.
- **Multi-Statement Blocker:** Rejects semicolons and multi-statement batching.
- **Schema Whitelist:** Queries can only access approved platform tables: `orders`, `customers`, `restaurants`, `deliveries`, `riders`, `promotions`. Inquiries attempting to access unauthorized tables (e.g. `passwords`, `users`, system catalogs) are blocked before execution.
- **Resource Constraints:** Automatically appends `LIMIT 25` if not present.
- **Sandboxed Execution:** Queries execute against SQLite/MySQL in read-only transaction wrappers.

---

## 6. Root-Cause Analysis (RCA) Engine

For diagnostic questions (e.g., *"Why did cancellations increase?"*, *"Why are delivery times higher?"*), the system uses `python/ai/analyst/root_cause.py`:
1. **Confirmed Empirical Facts:** Computes exact figures from historical records (e.g., *4.16% overall cancellation rate, 2,082 cancelled orders*).
2. **Contributing Factors & Evidence:** Examines correlated dimensions such as peak dispatch bottlenecks, kitchen preparation delays, or bad weather surges with correlation ratings (*High*, *Medium*, *Moderate*).
3. **Stated Uncertainties:** Explicitly highlights data that is unobserved or missing (e.g., *customer-side cancellation reasons, weather telemetry, kitchen prep timestamps*), avoiding claiming correlation as proven causality.
4. **Actionable Recommendations:** Recommends concrete operational actions (e.g., *dynamic buffer dispatching, kitchen SLA audits*).

---

## 7. Decision Simulator Integration

Ask NovaNest parses natural-language scenario parameters and executes the existing Decision Simulator:
- **Parameter Extraction:** Identifies percentage changes in commission rate, delivery fees, discount subsidies, customer churn reduction, and demand elasticity.
- **Scenario Execution:** Calls `decision_simulation.scenario_engine.run_scenario()` with active baseline datasets.
- **Structured Delta Output:**
  - Baseline vs Simulated Platform Revenue.
  - Baseline vs Simulated Take-Rate Margins.
  - Preserved Customer Accounts.
  - Delivery SLA impact.
- **Visual Presentation:** Renders a side-by-side comparison chart and strategic recommendation in the UI.

---

## 8. Multi-Turn Context & Session Management

- **Isolated Sessions:** Conversations are partitioned by `session_id`. Different users or browser sessions never share state.
- **Sliding-Window Memory:** Retains recent conversation turns to resolve ambiguous follow-up inquiries.
- **Context Expansion:**
  - *Turn 1:* User asks: *"What is our cancellation rate?"* -> Assistant answers with 4.16% cancellation rate.
  - *Turn 2:* User asks: *"Which region is the worst?"* -> Context manager detects the active topic (`cancellations`) and resolves the query to: *"Which city or region has the highest cancellation rate?"*
- **Explicit Reset:** `POST /api/ai/reset` purges the conversation history for a given session.

---

## 9. Test Execution & Verification

### Automated Unit & Integration Tests (`tests/test_ask_novanest_ai_suite.py`)
```text
Ran 14 tests in 5.857s
OK
```
1. `test_01_normal_business_inquiry`: PASSED (Status 200, verified metrics, answer, provenance)
2. `test_02_actual_data_grounding`: PASSED (Domain grounding, cancellation metrics verified)
3. `test_03_provider_unconfigured_fallback`: PASSED (Graceful unconfigured state when API key is missing)
4. `test_04_mock_ai_provider`: PASSED (Offline test provider with zero external network calls)
5. `test_05_sql_injection_mutating_rejection`: PASSED (DROP, DELETE, UPDATE, INSERT, TRUNCATE, ALTER blocked)
6. `test_06_sql_injection_multi_statement`: PASSED (Multi-statement query injection blocked)
7. `test_07_sql_schema_whitelist_rejection`: PASSED (Unauthorized table access blocked)
8. `test_08_valid_read_only_sql`: PASSED (Safe SELECT with auto-LIMIT 25 approved)
9. `test_09_root_cause_analysis_engine`: PASSED (Empirical facts, contributing factors, uncertainties present)
10. `test_10_visualization_generation`: PASSED (Interactive chart specifications with valid keys and data)
11. `test_11_decision_simulator_integration`: PASSED (Conversational what-if scenario executed and compared)
12. `test_12_follow_up_conversation_context`: PASSED (Turn 2 contextual expansion verified)
13. `test_13_conversation_reset`: PASSED (Session reset endpoint returns success)
14. `test_14_platform_endpoints_regression`: PASSED (All 8 core platform endpoints verified)

### Regression Test Suite (`tests/test_platform_full_suite.py`)
```text
ALL VERIFICATION CHECKS PASSED: PLATFORM HEALTHY & READY
```
- All FastAPI endpoints healthy.
- React frontend production bundle builds cleanly (`tsc -b && vite build` in 771ms).
- Streamlit application healthy on port 8501.
- MySQL/CSV datasets verified (10 tables cleaned, 10 tables engineered).
- Protected Power BI asset (`powerbi/NovaNest.pbix`) preserved intact (5,638,573 bytes).

### End-to-End Browser Verification
- Tested locally on `http://localhost:5173/` using automated browser subagent.
- Navigated to "Ask NovaNest AI" module.
- Successfully executed query: *"What are the top 5 restaurants by revenue?"*.
- Verified visual rendering of:
  - KPI cards with provenance badges.
  - Recharts interactive Bar Chart with merchant revenue bars.
  - SQL Security Audit showing safe read-only SELECT validation.
  - Data table with 5 merchant records.
  - Interactive Decision Simulator scenario levers.

---

## 10. Configuration & Environment Settings

To enable live Google Gemini generative synthesis:
1. Add `GEMINI_API_KEY` to `.env`:
   ```bash
   GEMINI_API_KEY=your_google_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   ```
2. Restart the FastAPI backend.
3. If `GEMINI_API_KEY` is not provided, the platform automatically runs on the **Grounded Analytics Engine**, returning exact calculations, charts, RCA breakdowns, and simulations without errors.

---

## 11. Known Limitations & Boundaries

1. **Read-Only Enforced:** Users cannot mutate database records through natural language. All mutating DDL/DML statements are permanently blocked.
2. **Simulation Bounds:** Decision Simulator parameters are capped within realistic operational bounds (commission changes between -10% and +15%, demand shifts between -30% and +50%) to prevent mathematical divergence.
3. **Session Storage:** Conversation context is currently stored in memory on the backend per `session_id`. Server restarts will clear active turn memory.

---

## Conclusion

Ask NovaNest AI has transitioned from an ungrounded conversational prototype into a hardened, data-grounded Business Intelligence AI and AI Business Analyst. The upgrade delivers safe NL-to-SQL, verified KPI calculations, root-cause investigations, interactive visualizations, and conversational what-if simulations while preserving the existing UI design, styling, and codebase architecture.
