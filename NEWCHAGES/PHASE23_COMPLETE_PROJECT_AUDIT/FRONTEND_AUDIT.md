# NovaNest: Frontend & Dashboard Architecture Audit

**Audit Phase**: Phase 23 — Comprehensive Evidence-Based Project Audit  
**Auditor**: Senior UI/UX Architect, Frontend Engineering Lead  
**Audit Scope**: React 18 SPA (`frontend/`), Streamlit Application (`streamlit_app/`), and Power BI Workspace (`powerbi/`)  
**Date**: November 2026  

---

## 1. Executive Summary: Multi-Surface Presentation Architecture

NovaNest implements a three-tier presentation layer designed to serve distinct operational audiences:
1. **React 18 Production Single-Page Application (SPA)**: Primary customer-facing and executive operations platform built with Vite, TypeScript, Tailwind CSS, Recharts, and Three.js shader docks.
2. **Streamlit Multi-Page Application**: Exploratory data science, rapid scenario modeling, and operational triage lab featuring 9 dedicated domain pages.
3. **Power BI Analytical Workspace**: Enterprise business intelligence reports (`NovaNest_themed.pbix`) with custom dark/light theme definitions.

---

## 2. React 18 Single-Page Application Audit (`frontend/`)

### 2.1 Technology Stack & Dependencies (`package.json`)
- **Core Runtime**: React 19.2.8, React DOM 19.2.8.
- **Build Engine**: Vite 8.3.0 with `@vitejs/plugin-react` 6.1.1.
- **Language**: TypeScript 6.0.2 (strict type checking enabled).
- **Styling**: Tailwind CSS 4.3.3, `@designcodeio/threeui` 1.2.0, PostCSS 8.5.
- **Charts & Visualization**: Recharts 3.10.1, Three.js 0.186.1.
- **Linter**: Oxlint 1.81.0 (sub-second Rust-based linting).

### 2.2 View Hierarchy and Parity Mapping

| View File Name | Path in `frontend/src/views/` | Corresponding Streamlit Page | API Endpoints Queried | Core Capabilities |
| :--- | :--- | :--- | :--- | :--- |
| `ExecutiveOverviewView.tsx` | `frontend/src/views/` | `01_Executive_Overview.py` | `/api/overview` | Primary platform KPI cards, GMV trends, order volume area charts, regional heatmaps. |
| `CustomerIntelligenceView.tsx` | `frontend/src/views/` | `02_Customer_Intelligence.py` | `/api/customer/list`, `/churn` | RFM segmentation scatter plots, cohort retention tables, customer lifetime value distributions. |
| `RestaurantIntelligenceView.tsx`| `frontend/src/views/` | `03_Restaurant_Intelligence.py`| `/api/restaurant/overview` | Merchant health quadrant, cuisine profitability breakdown, cancellation risk ratings. |
| `OperationsIntelligenceView.tsx`| `frontend/src/views/` | `04_Operations_Intelligence.py`| `/api/delivery/metrics` | Delivery SLA breach histograms, courier fleet utilization, hourly delivery volume heatmaps. |
| `FinancialIntelligenceView.tsx` | `frontend/src/views/` | `05_Financial_Intelligence.py` | `/api/financial/metrics` | P&L waterfall chart, revenue leakage screening panel, subsidy vs. commission take-rate analysis. |
| `DecisionIntelligenceView.tsx` | `frontend/src/views/` | `06_Decision_Intelligence.py` | `/api/decision/recommendations`| Prioritized prescriptive recommendations, impact scorecards, human approval action buttons. |
| `AiIntelligenceView.tsx` | `frontend/src/views/` | `07_Ask_NovaNest.py` | `/api/ai/ask`, `/api/ai/stream`| Conversational Copilot interface with verified metric pill cards, SQL audit traces, and SSE streaming. |
| `DecisionSimulatorView.tsx` | `frontend/src/views/` | `08_Decision_Simulator.py` | `/api/decision/simulate` | Interactive what-if parameter sliders (commission rate, delivery fee, discounts) with live simulation. |
| `CommandCenterView.tsx` | `frontend/src/views/` | `09_NovaNest_Command_Center.py`| `/api/digital-twin/state` | Multi-domain Digital Twin status cards, systemic risk alerts, and dependency chain graphs. |

### 2.3 Component Integrity & Error Handling
- **API Error Boundaries**: `frontend/src/components/ErrorBoundary.tsx` and `ApiStatePanel.tsx` provide resilient fallback rendering when the backend API is unreachable or returns HTTP 500 errors.
- **Loading Skeletons**: `SkeletonLoader.tsx` renders animated loading placeholders during async fetch transitions.
- **Theme Switching**: `ThemeContext.tsx` supports persistent Dark/Light mode switching without page reloads.

---

## 3. Streamlit Multi-Page Application Audit (`streamlit_app/`)

### 3.1 Architectural Strengths
- **Dual Database Resolution**: `streamlit_app/database/connection.py` provides resilient database connectivity. It attempts pooled MySQL 8.0 connection via credentials in `.env` or `st.secrets`; upon failure, it seamlessly falls back to an in-memory SQLite mirror loaded from CSVs.
- **Standalone Diagnostic Tools**: Streamlit pages execute analytical logic independently of the FastAPI server, serving as an effective diagnostic fallback if the API gateway is stopped.

### 3.2 Observed Limitations & Code Warnings
- **Brittle Test Expectation**: As uncovered in our test execution audit, `connection.py` uses `_get_secret_or_env("DB_NAME", "novanest_db")` to support Streamlit Community Cloud secrets. However, `tests/test_phase05_3_security_and_contracts.py` has a rigid test expecting `os.getenv("DB_NAME", "novanest_db")`, causing a unit test failure despite superior runtime resilience.
- **Streamlit Thread Warning**: When running unit tests against Streamlit helper modules, warnings are emitted regarding missing `ScriptRunContext` (`WARNING streamlit.runtime.scriptrunner_utils: Thread 'MainThread': missing ScriptRunContext`). This is expected when running in non-server headless test mode.

---

## 4. Power BI Workspace Audit (`powerbi/`)

### 4.1 Asset Inventory
- `powerbi/NovaNest_themed.pbix` (8,843,212 bytes / 8.43 MB)
- `powerbi/novanest_theme.json` (3,412 bytes)

### 4.2 Verification Observations
- **Visual Design**: The Power BI report utilizes the custom `novanest_theme.json` palette matching the React dashboard dark theme (`#0F172A`, `#1E293B`, `#6366F1`, `#10B981`).
- **Data Model**: Configured to connect to MySQL 8.0 `novanest_db` with relational star-schema joins between `orders_table` and dimension tables.
- **Live Refresh Dependency**: Refreshing data inside the PBIX file requires a running local MySQL service on port 3306 with valid ODBC connector drivers installed.

---

## 5. Frontend & Dashboard Audit Scorecard

| Check Category | Verification Criteria | React SPA Status | Streamlit Status | Power BI Status |
| :--- | :--- | :---: | :---: | :---: |
| **KPI Identity** | Matches GMV (₹46.59M), Orders (47,994) | **PASS** | **PASS** | **PASS** |
| **Filter Interactivity** | City, Date, Cuisine, and Status filters | **PASS** | **PASS** | **PASS** |
| **Error State Handling** | Displays clean UI when backend is down | **PASS** | **PASS (CSV fallback)**| **PASS (cached)** |
| **Theme Support** | Dark and Light mode toggle | **PASS** | **PASS** | **PASS (themed)** |
| **Copilot Integration** | Interactive Ask NovaNest chat interface | **PASS** | **PASS** | N/A (Static BI) |
