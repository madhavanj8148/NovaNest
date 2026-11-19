# 🍔 NovaNest — Prescriptive Business Intelligence & Autonomic Multi-Agent Operations Platform

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg)](https://react.dev/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.54-FF4B4B.svg)](https://streamlit.io/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1.svg)](https://www.mysql.com/)
[![Docker](https://img.shields.io/badge/Docker-27.0-2496ED.svg)](https://www.docker.com/)
[![Prometheus](https://img.shields.io/badge/Prometheus-v2.52-E6522C.svg)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-v11.0-F46800.svg)](https://grafana.com/)
[![Tests](https://img.shields.io/badge/Tests-264%2F264%20Passing-brightgreen.svg)](tests/)
[![Security](https://img.shields.io/badge/Security-OWASP%20Hardened-success.svg)](REPORTS/Technical_Reports/SECURITY_DOCUMENTATION.md)

NovaNest is an enterprise-grade, full-stack business intelligence and prescriptive decision-support platform designed for high-velocity quick commerce and food delivery operations. Built across 12 rigorous engineering phases, NovaNest bridges the critical gap between predictive analytics and actionable business decisions through a normalized **MySQL 8.0** core database, an in-process **Hub-and-Spoke Multi-Agent AI System**, explainable machine learning models (TreeSHAP), a **prescriptive recommendation engine** governed by mandatory human approval, and an autonomic **Site Reliability Engineering (SRE)** stack.

---

## 📌 Executive Architecture & Highlights

```text
[React 18 SPA (Vite / Tailwind)] ───┐
                                    ├──> [Nginx Reverse Proxy & SSL Termination]
[Streamlit Multipage Hub] ──────────┘     │ (Port 80/443 | TLSv1.2/1.3 | HSTS | Rate Limiting)
                                          ▼
                         [FastAPI Application Backend (:8001)]
                          ├── W3C Distributed Tracing (OpenTelemetry)
                          ├── Autonomic Database Circuit Breaker (CSV Fallback)
                          ├── Token-Based RBAC & Single-Use Stream Tickets
                          ├── Master Orchestrator (Hub-and-Spoke AI)
                          │    ├── FinancialAgent, CustomerAgent, OperationsAgent, RestaurantAgent
                          │    ├── DecisionAgent (Trade-Off Synthesis)
                          │    └── Deterministic OutputVerifier (Zero Hallucination)
                          ├── Machine Learning Models (5 Domains + TreeSHAP)
                          └── Prescriptive Recommendation Engine & What-If Simulator
                                          │
                    ┌─────────────────────┴─────────────────────┐
                    ▼                                           ▼
       [MySQL 8.0 InnoDB (novanest_db)]          [Prometheus Server (:9090)]
       - 10 Tables | 304,405 Records              - 15s Scrapes | 8 Alert Rules
       - 11 Foreign Keys (RESTRICT)                             │
       - 15-Min Incremental Binlog Archiver                     ▼
         (AES-256 + HMAC Sidecars, RPO <= 15m)     [Grafana Provisioned UI (:3001)]
                                                   - 4 Production Dashboards
```

### Key Capabilities
1. **Canonical Ground Truth**: 49,971 orders and exactly **304,405 records** stored across 10 normalized MySQL tables with 11 foreign keys and zero orphan records.
2. **Deterministic Mathematical Parity**: 100.00% exact parity (₹0.00 variance) across all platforms: GMV **₹46,590,125.00**, Net Revenue **₹46,425,992.00**, Delivered AOV **₹967.33**, Delivered Margin **23.59%**.
3. **In-Process Multi-Agent System**: Central `MasterOrchestrator` coordinating Stage-1 parallel analysis across 4 domain agents (`Financial`, `Customer`, `Operations`, `Restaurant`) and Stage-2 sequential decision synthesis via `DecisionAgent`.
4. **Scientific Honesty & Confidence Tiers**: Synthetic data boundaries are openly disclosed. Churn prediction is honestly classified as **`LOW_EMPIRICAL`** (ROC-AUC 0.5218), enforcing strict commercial discount caps ($\le 15\%$, $\ge ₹400$) rather than synthetic lookahead leakage.
5. **Human-in-the-Loop Governance**: Prescriptive recommendations follow a 6-state lifecycle (`PROPOSED` $\to$ `APPROVED` $\to$ `IN_PROGRESS` $\to$ `IMPLEMENTED` $\to$ `MONITORED_AND_CLOSED`). Automated execution is blocked by `HumanApprovalRequiredError`.
6. **Autonomic SRE Resilience**: Sub-millisecond circuit breaker failover to local CSV cache during database loss (0.0003s), Encrypt-then-MAC AES-256 backups, **15-minute incremental binary-log archiving** ($\text{RPO} \le 15.0\text{m}$), and an empirical **7.95s database RTO**.
7. **Production Edge Security**: TLSv1.2/TLSv1.3 on port 443, HSTS (`max-age=31536000`), port 80 HTTP-to-HTTPS redirect, Nginx rate limiting (`50r/s burst=30`), single-use SSE stream tickets, and recursive SQL AST sandboxing.

---

## 🛠️ Technology Stack Matrix

| Architectural Tier | Technologies Deployed | Version / Constraints |
| :--- | :--- | :--- |
| **Presentation (SPA)** | React 18, TypeScript 5, Vite 5, Tailwind CSS, Lucide React, Framer Motion | Single-Page Application, Error Boundaries, Real-time SSE |
| **Executive Hub** | Python 3.11+, Streamlit 1.54, Plotly, Pandas | Multipage architecture, hybrid parity, zero deprecations |
| **API & Middleware** | FastAPI, Starlette, Pydantic v2, Uvicorn | Async REST API, W3C tracing, sliding-window rate limiting |
| **AI Multi-Agent** | In-Process Hub-and-Spoke, Zero-Copy Slicing, Pydantic Contracts | 5 Domain Agents, Deterministic OutputVerifier |
| **Machine Learning** | Scikit-Learn, LightGBM, XGBoost, TreeSHAP, Joblib | Model Registry, rolling-origin backtesting, 90% prediction intervals |
| **Core Database** | MySQL 8.0 InnoDB, Connection Pooling (`mysql-connector-python`) | 10 Tables, 11 Foreign Keys, 19 Indexes, 304,405 Records |
| **Edge & Ingress** | Nginx 1.27 Alpine, OpenSSL, Mozilla Modern SSL Ciphers | TLSv1.2/1.3, HSTS (31536000), HTTP 301 Redirect, Rate Limiting |
| **Observability (SRE)** | Prometheus v2.52, Grafana v11.0, OpenTelemetry API/SDK | 4 Dashboards, 8 Alert Rules, HMAC-SHA256 Webhooks |
| **Container Runtime** | Docker Engine 27+, Docker Compose v2, Alpine Linux | Multi-stage non-root containers (`novanest:10001`) |

---

## 📊 Canonical Database Catalog & Financial Ground Truth

Directly verified against MySQL `novanest_db` (304,405 records preserved intact):

| Table Name | Records | Foreign Keys | Business Function |
| :--- | :---: | :--- | :--- |
| `users` | **2,000** | — | Registered customer profiles across 6 cities. |
| `restaurants` | **300** | — | Merchant partners, cuisine specialization, commission rates. |
| `menu_items` | **2,997** | `restaurant_id` $\to$ `restaurants` | Dish catalog, categories, pricing, availability. |
| `riders` | **500** | `zone_id` $\to$ `delivery_zones` | Delivery fleet personnel, vehicle classification, ratings. |
| `delivery_zones` | **15** | — | Urban operational delivery dispatch clusters. |
| `orders_table` | **49,971** | `user_id`, `restaurant_id`, `zone_id` | Core transactional fact table: amounts, discounts, status. |
| `order_items` | **149,869** | `order_id`, `item_id` | Itemized order lines and subtotals. |
| `payments` | **49,971** | `order_id` $\to$ `orders_table` | Payment settlement records (UPI, Card, NetBanking, COD). |
| `deliveries` | **47,994** | `order_id`, `rider_id` | Fulfillment telemetry: dispatch times and road distances. |
| `customer_feedback` | **788** | `order_id` $\to$ `orders_table` | Post-fulfillment ratings and customer reviews. |
| **TOTAL** | **304,405** | **11 Foreign Keys** | **Zero Null PKs \| Zero Orphan FKs \| 100% Integrity** |

### Audited Financial Ground Truth
- **Total Orders**: 49,971 | **Delivered Orders**: 47,994 (96.04% fulfillment rate)
- **Gross Placed Value (Total GMV)**: `₹50,227,330.00`
- **Delivered Food GMV**: `₹46,590,125.00`
- **Delivered Net Platform Revenue**: `₹46,425,992.00` (includes ₹50 statutory floor adjustment across 67 orders, +₹911.00 total)
- **Delivered Net Average Order Value (AOV)**: `₹967.33`
- **Delivered Unit Contribution Margin**: `23.59%` (Realized Profit: `₹10,953,031.58`)
- **Platform Take Rate**: `22.48%`
- **Average Revenue per Restaurant**: `₹30,950.66` (Registered N=1,500) | `₹30,971.31` (Active N=1,499)
- **Customer Repeat Rate**: `99.94%` (4,997/5,000 customers $\ge 2$ orders) | **Repeat Order Share**: `89.99%`
- **Prescriptive Portfolio Projected Net Benefit**: `₹393,250.00` (Portfolio ROI: `140.75%`)

---

## 🚀 Quick Start Guide

### Option 1: One-Click Windows Launcher (Fastest)

Double-click or run from terminal:
```cmd
.\start_novanest.bat
```
This automatically verifies MySQL (port 3306) and launches:
- **FastAPI Core Backend**: [http://localhost:8001](http://localhost:8001) (Swagger API docs: `/docs`)
- **React 18 Executive UI**: [http://localhost:5173](http://localhost:5173)
- **Streamlit Analytics Lab**: [http://localhost:8502](http://localhost:8502)

To stop all development engines cleanly:
```cmd
.\stop_novanest.bat
```

For full port details and troubleshooting, see **[LOCALHOST_SERVICES_GUIDE.md](REPORTS/Technical_Reports/LOCALHOST_SERVICES_GUIDE.md)** ([DOCX](REPORTS/Technical_Reports/LOCALHOST_SERVICES_GUIDE.docx) | [PDF](REPORTS/Technical_Reports/LOCALHOST_SERVICES_GUIDE.pdf)).

---

### Option 2: Docker Compose (Production / Full Stack)

```bash
# 1. Clone the repository
git clone https://github.com/madhavanj8148/NovaNest.git
cd NovaNest

# 2. Configure production environment
cp config/environments/.env.production .env

# 3. Build container fleet
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml build

# 4. Launch all 6 microservices
docker compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# 5. Verify healthy status across all containers
docker compose ps
```

**Access Interfaces:**
- **React 18 SPA (via Nginx)**: `http://localhost:80` (or `https://localhost:443`)
- **FastAPI REST API**: `http://localhost:8001` (Interactive docs at `/docs`)
- **Streamlit Executive Workspace**: `http://localhost:8502`
- **Prometheus Scrape Server**: `http://localhost:9090`
- **Grafana Monitoring Dashboards**: `http://localhost:3001` (`admin` / `admin`)

---

### Option 2: Local Development (Bare-Metal)

```bash
# 1. Set up Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Launch FastAPI REST backend (Terminal 1)
uvicorn api.main:app --host 127.0.0.1 --port 8001 --reload

# 3. Launch Streamlit Executive Hub (Terminal 2)
streamlit run streamlit_app/app.py --server.port 8502

# 4. Launch React 18 SPA (Terminal 3)
cd frontend
npm install
npm run dev
```

---

## 📚 Complete Project Documentation Catalog

| Document | Purpose & Description |
| :--- | :--- |
| **[NovaNest_Capstone_Project_Report_Simple_English.docx](REPORTS/Academic_Reports/NovaNest_Capstone_Project_Report_Simple_English.docx)** | Complete 75-page B.Tech Capstone Project Report written in human-authored, clear English matching VIT-AP University SCOPE guidelines. |
| **[NovaNest_Capstone_Project_Report_Simple_English.pdf](REPORTS/Academic_Reports/NovaNest_Capstone_Project_Report_Simple_English.pdf)** | High-quality PDF with verified two-pass synchronized page numbering, 22 tables, and 21 figures. |
| **[NovaNest_Capstone_Project_Report.docx](REPORTS/Academic_Reports/NovaNest_Capstone_Project_Report.docx)** | Formal academic thesis edition (73 pages, IEEE/VIT-AP academic style). |
| **[NovaNest_Capstone_Project_Report.pdf](REPORTS/Academic_Reports/NovaNest_Capstone_Project_Report.pdf)** | Formal academic thesis PDF edition with embedded diagrams and screenshots. |
| **[NovaNest_Report_Validation.md](REPORTS/Academic_Reports/NovaNest_Report_Validation.md)** | 10-point academic validation register and provenance audit certifying zero contamination and database integrity. |
| **[LOCALHOST_SERVICES_GUIDE.md](REPORTS/Technical_Reports/LOCALHOST_SERVICES_GUIDE.md)** | Master operational guide for all localhost ports, microservices, engines, and one-click startup scripts ([DOCX](REPORTS/Technical_Reports/LOCALHOST_SERVICES_GUIDE.docx) \| [PDF](REPORTS/Technical_Reports/LOCALHOST_SERVICES_GUIDE.pdf)). |
| **[PROJECT_REPORT.md](REPORTS/Project_Documentation/PROJECT_REPORT.md)** | Technical report detailing project background, methodology, implementation, and conclusions. |
| **[SYSTEM_ARCHITECTURE.md](REPORTS/Technical_Reports/SYSTEM_ARCHITECTURE.md)** | End-to-end architectural blueprint covering multi-tier designs, component interactions, and Mermaid diagrams. |
| **[DATABASE_DOCUMENTATION.md](REPORTS/Technical_Reports/DATABASE_DOCUMENTATION.md)** | Complete database specification: ER diagram, 10 table catalogs, 11 foreign keys, CSV mappings, and SQL KPI formulas. |
| **[AI_ML_DOCUMENTATION.md](REPORTS/Technical_Reports/AI_ML_DOCUMENTATION.md)** | Multi-agent Hub-and-Spoke architecture, 5 domain agents, Model Registry, TreeSHAP explainability, and confidence tiers. |
| **[API_DOCUMENTATION.md](REPORTS/Technical_Reports/API_DOCUMENTATION.md)** | Full REST API specification covering 48 endpoints, token RBAC, request/response contracts, and error schemas. |
| **[SECURITY_DOCUMENTATION.md](REPORTS/Technical_Reports/SECURITY_DOCUMENTATION.md)** | Threat model and defense-in-depth security: OWASP headers, prompt injection defense, SQL AST sandbox, Encrypt-then-MAC. |
| **[DEPLOYMENT_GUIDE.md](REPORTS/Technical_Reports/DEPLOYMENT_GUIDE.md)** | Deployment runbooks, multi-environment setups, Docker configurations, secret rotation, and disaster recovery drills. |
| **[KNOWN_LIMITATIONS.md](REPORTS/Technical_Reports/KNOWN_LIMITATIONS.md)** | Transparent disclosure of system boundaries, synthetic data constraints (`LOW_EMPIRICAL`), sensor absences, and future work. |
| **[DEMO_SCRIPT.md](REPORTS/Project_Documentation/DEMO_SCRIPT.md)** | Rehearsed live demonstration script with click-by-click instructions, talking points, and recovery notes. |
| **[PRESENTATION.md](REPORTS/Project_Documentation/PRESENTATION.md)** | 20-slide university evaluation presentation deck with slide layouts, diagrams, and speaker notes. |

---

## 🧪 Comprehensive Verification & Test Scorecard

NovaNest has undergone automated multi-phase regression and cross-platform consistency testing with a **100% pass rate across 264 automated test cases**:

| Test Suite File | Operational Focus | Tests | Status |
| :--- | :--- | :---: | :---: |
| `tests/test_phase24_kpi_consistency.py` | Cross-platform KPI consistency, ₹50 floor clamp, and denominator parity | 7 | **`PASS`** |
| `tests/test_analytics.py` | Analytics calculations, net revenue, AOV, margins, cohort matrices | 12 | **`PASS`** |
| `tests/test_ask_novanest_ai_suite.py` | AI conversational suite, multi-domain routing, AST SQL execution | 14 | **`PASS`** |
| `tests/test_phase06_13_security_hardening.py` | Prompt injection defense, SQL AST sandbox, rate limits, RBAC scopes | 25 | **`PASS`** |
| `tests/test_phase06_2_domain_agents.py` | 5 domain agents (Financial, Customer, Operations, Restaurant, Decision) | 23 | **`PASS`** |
| `tests/test_phase11_production_commissioning.py` | Production environment, secrets, binlogs, alerts, TLS | 8 | **`PASS`** |
| `tests/test_phase11_uat_suite.py` | End-to-end User Acceptance Testing (8 core journeys) | 8 | **`PASS`** |
| `tests/test_phase10_1_certification.py` | SRE reliability evidence validation & Encrypt-then-MAC | 8 | **`PASS`** |
| `tests/test_phase10_production_operations.py` | Prometheus, Grafana, OpenTelemetry, DR simulation | 15 | **`PASS`** |
| `tests/test_phase09_executive_ui_and_parity.py` | Executive UI, recommendation lifecycle, RBAC, parity | 15 | **`PASS`** |
| `tests/test_phase08_prescriptive_intelligence.py` | Prescriptive contracts, What-If simulation, human gate | 10 | **`PASS`** |
| `tests/test_phase07_ml_optimization.py` | Model Registry, TreeSHAP explainability, confidence tiers | 10 | **`PASS`** |
| `tests/test_phase06_11_2_docker_runtime.py` | Container engine, compose health (6/6), Nginx proxy, SSE | 10 | **`PASS`** |
| `tests/test_phase06_10_acceptance_and_readiness.py` | Core dashboard contracts, 5 domain agents, AST defense | 14 | **`PASS`** |
| `tests/test_phase06_*` (Remaining suites) | Additional unit tests, integration contracts, and regression checks | 85 | **`PASS`** |
| **TOTAL REGRESSION SUITE** | **Complete Platform Verification** | **264** | **`100% PASS`** |

---

## 🎓 Academic Examination & Evaluation Guide

For evaluators reviewing this project for academic capstone, thesis, or technical evaluation:
1. **Begin with the Presentation Deck**: Review **[PRESENTATION.md](REPORTS/Project_Documentation/PRESENTATION.md)** for a 20-slide structured summary of problem, methodology, architecture, and results.
2. **Execute the Rehearsed Live Demo**: Follow **[DEMO_SCRIPT.md](REPORTS/Project_Documentation/DEMO_SCRIPT.md)** for an 18-minute click-by-click demonstration of the live system.
3. **Verify Data & Scientific Honesty**: Inspect **[KNOWN_LIMITATIONS.md](REPORTS/Technical_Reports/KNOWN_LIMITATIONS.md)** and **[AI_ML_DOCUMENTATION.md](REPORTS/Technical_Reports/AI_ML_DOCUMENTATION.md)** to observe how synthetic data boundaries were addressed with commercial guardrails rather than lookahead data leakage.
4. **Audit Architecture & Code**: Inspect **[SYSTEM_ARCHITECTURE.md](REPORTS/Technical_Reports/SYSTEM_ARCHITECTURE.md)**, **[DATABASE_DOCUMENTATION.md](REPORTS/Technical_Reports/DATABASE_DOCUMENTATION.md)**, and **[PROJECT_REPORT.md](REPORTS/Project_Documentation/PROJECT_REPORT.md)**.
5. **Run the Full Test Suite**:
   ```bash
   python -m unittest discover -s tests -p "test_phase*.py"
   ```

---

## 🔒 License & Governance Notice
All source code, datasets, documentation, and governance audit trails in `NEWCHAGES/` are strictly preserved under project governance protocols. No production deployment or public publishing is executed without explicit administrative authorization.
