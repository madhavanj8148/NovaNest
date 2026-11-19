# NovaNest Platform Architecture & Enterprise Operational Guide

**NovaNest** is an AI-powered, enterprise-grade food delivery business analytics, intelligence, and decision platform. It transforms raw multi-tier delivery operations data into strategic business intelligence through advanced data engineering, predictive machine learning, decision simulation, an analytical digital twin, and a unified executive command center.

---

## 1. System Ecosystem & Dual Frontend Architecture

NovaNest features a unified, dual-interface architecture designed for both executive C-suite decision-making and exploratory business intelligence:

```
                                  ┌────────────────────────────────────────┐
                                  │       RAW & ENGINEERED DATASETS        │
                                  │   (Cleaned CSVs & MySQL Relational DB) │
                                  └───────────────────┬────────────────────┘
                                                      │
                       ┌──────────────────────────────┴──────────────────────────────┐
                       ▼                                                             ▼
        ┌─────────────────────────────┐                               ┌─────────────────────────────┐
        │       FASTAPI BACKEND       │                               │   STREAMLIT ANALYTICS HUB   │
        │      (http://127.0.0.1:8000)│                               │    (http://localhost:8501)  │
        │  • 12 JSON REST Endpoints   │                               │  • 9 Multi-Page Modules     │
        │  • In-Memory SQLite Mirror  │                               │  • Direct Python Integration│
        │  • SQL Guardrails & NL2SQL  │                               │  • Plotly Visualizations    │
        │  • Simulation & Twin Engine │                               │  • Exploratory Data Tooling │
        └──────────────┬──────────────┘                               └─────────────────────────────┘
                       │ (REST / JSON over CORS)
                       ▼
        ┌─────────────────────────────┐
        │   STANDALONE REACT SUITE    │
        │    (http://localhost:5173)  │
        │  • React 18 + Vite + TS     │
        │  • Tailwind CSS Design Sys  │
        │  • 9 Modular Views          │
        │  • Recharts & Lucide Icons  │
        │  • What-If Simulation Lab   │
        │  • Customer 360 Drawer      │
        │  • Digital Twin Matrix      │
        └─────────────────────────────┘
```

---

## 2. Platform Intelligence Modules

NovaNest is structured into 9 interconnected business intelligence modules:

### 1. Executive Overview
- **Core Purpose**: High-level platform telemetry for C-suite leadership.
- **Key Metrics**: Gross Merchandise Value (GMV), Total Orders, Active Customers, Restaurant Network Size, Average Order Value (AOV), Delivery Fulfillment Rate, and Net Platform Revenue.
- **Visual Storytelling**: 30-Day Revenue Velocity area chart, geographic territory distribution, and top restaurant partner rankings.

### 2. Customer Intelligence
- **Core Purpose**: Comprehensive retention, RFM segmentation, and lifetime value analytics.
- **RFM Segmentation**: 9 distinct customer segments (`Champions`, `Loyal Customers`, `Potential Loyalists`, `At Risk`, `Hibernating`, etc.) computed via quantile scoring.
- **Customer Lifetime Value (CLV)**: 12-month predictive CLV modeling with segment aggregations.
- **Cohort Retention**: Monthly customer cohort matrix tracking retention decay across Month 0 to Month 5.
- **Interactive Customer 360**: Searchable and filterable directory with slide-out drawer displaying profile details, Digital Twin behavioral indices, recent order trajectory, and AI hybrid recommendations.

### 3. Restaurant Intelligence
- **Core Purpose**: Partner performance evaluation, portfolio health scoring, and early warning risk detection.
- **Composite Health Score (0–100)**: Multi-factor formula weighting order throughput, gross volume, partner rating, and cancellation rate.
- **Performance Matrix Scatter**: Quadrant bubble chart comparing order volume against revenue across top restaurant partners.
- **Early Warning System**: Automated risk detection alerting operations teams to sudden drops in ratings, elevated cancellation spikes, or kitchen delays.
- **Cuisine Benchmarks**: Industry baseline comparisons across North Indian, Chinese, Continental, Desserts, and Fast Food.

### 4. Operations Intelligence
- **Core Purpose**: Delivery efficiency, demand forecasting, and logistics anomaly detection.
- **14-Day Demand Forecast**: Time-series predictive modeling complete with upper and lower 95% confidence intervals.
- **Geographic Demand Heatmaps**: Cross-tabulation of order density across metropolitan territories and peak hour windows (Lunch vs Dinner).
- **Smart Fleet Allocation**: Dynamic rider deficit calculation comparing active riders against recommended allocation.
- **Logistics Anomalies**: Statistical outlier detection capturing delivery duration spikes and transit bottlenecks.

### 5. Financial Intelligence
- **Core Purpose**: P&L economics, margin integrity, platform monetization, and revenue leakage detection.
- **Revenue Inflows & Outflows**: Dynamic tracking of Commission Take-Rate (18–22%), Delivery Fee secondary revenues, and Promo Discount subsidies.
- **Unit Economics**: Contribution margin per delivered order.
- **Revenue Leakage Audit**: Automated scanner pinpointing margin erosion from excessive coupon subsidies, uncollected cancellation penalties, and rider surge bonuses.
- **Promotion ROI Analysis**: Tracking redemption volume, gross merchandise value driven, and ROI multiplier per promo code.

### 6. AI Intelligence (Ask NovaNest)
- **Core Purpose**: Natural language querying and automated business insights.
- **Conversational Analytics**: Supports queries like *"What are the top 5 restaurants by revenue?"*, *"Which cities generate the highest volume?"*, and *"Which customers are at high churn risk?"*.
- **NL-to-SQL Pipeline**: Natural language intent parsing → dynamic SQL generation → strict AST & regex security validation (rejecting destructive commands like `DROP`, `DELETE`, `INSERT`, `UPDATE`, `ALTER`) → read-only execution against an in-memory SQLite mirror → conversational interpretation.
- **System Insights**: Automated rule-based executive findings extracted from historical order velocities and customer segments.

### 7. Decision Intelligence
- **Core Purpose**: Next Best Action (NBA) queue translating analytics into prioritized operational decisions.
- **Cross-Domain Recommendations**: Synthesizes customer churn signals, merchant kitchen bottlenecks, and logistics capacity deficits.
- **Action Verification**: Interactive 1-click authorization system tracking action execution state in real time.

### 8. Decision Simulator (What-If Scenario Lab)
- **Core Purpose**: Multi-variable strategy simulation before live deployment.
- **Interactive Levers**:
  - Commission Take Rate adjustment (-5.0% to +5.0%)
  - Delivery Fee shift (-₹15 to +₹25)
  - Discount Subsidy burn (-10.0% to +10.0%)
  - Demand Elasticity velocity (-20.0% to +30.0%)
  - Churn Reduction target (0.0% to 10.0%)
- **Preconfigured Strategies**: *Aggressive Market Expansion*, *Profit Maximization*, *Merchant Retention Protocol*, and *Balanced Growth*.
- **Live Output Comparison**: Real-time recalculation of projected GMV, net platform revenue delta, margin shifts, and strategic executive recommendations.

### 9. NovaNest Command Center (Digital Twin)
- **Core Purpose**: Integrated holistic view connecting all operational dimensions.
- **Platform Systemic Vitality Index (0–100)**: Real-time health pulse combining Customer, Restaurant, Operations, and Financial states.
- **4-Pillar Digital Twin Matrix**:
  - *Customer Twin*: Active user base, churn exposure, CLV capital, engagement index.
  - *Restaurant Twin*: Active merchant network, critical risk partners, network health, network cancellation rate.
  - *Operations Twin*: Active rider fleet, average ETA, dispatch fulfillment, active bottlenecks.
  - *Financial Twin*: Gross merchandise volume, net revenue, margin rate, leakage exposure.
- **Cross-Domain Causal Ripple Chains**: Visualizes how an operational disruption (e.g. delivery delay spike) cascades into merchant cancellations, negative reviews, customer churn, and platform margin contraction.

---

## 3. REST API Specification

The FastAPI backend runs on `http://127.0.0.1:8000` and serves the following endpoints:

| Endpoint | Method | Description | Key Response Fields |
| :--- | :---: | :--- | :--- |
| `/api/health` | `GET` | Health check & data source status | `status`, `data_source`, `datasets`, `timestamp` |
| `/api/overview` | `GET` | Executive KPIs and macro charts | `kpis`, `revenue_trend`, `city_breakdown`, `top_restaurants` |
| `/api/customer/overview` | `GET` | RFM, CLV, Churn & Cohort retention | `kpis`, `rfm_segments`, `clv_tiers`, `churn_distribution`, `cohort_retention` |
| `/api/customer/list` | `GET` | Paginated customer directory | Array of `{ customer_id, name, city, order_count, total_spend, churn_risk }` |
| `/api/customer/360/{id}` | `GET` | Comprehensive Customer 360 profile | `profile`, `digital_twin`, `order_history`, `recommendations` |
| `/api/restaurant/overview`| `GET` | Merchant metrics, scatter & early warnings | `kpis`, `health_distribution`, `risk_distribution`, `performance_matrix`, `early_warnings` |
| `/api/operations/overview`| `GET` | 14-day forecast, fleet & anomalies | `kpis`, `demand_forecast`, `rider_allocation`, `anomalies` |
| `/api/financial/overview` | `GET` | P&L economics, unit breakdown & leakage | `kpis`, `unit_economics`, `revenue_leakage`, `promotions` |
| `/api/ai/ask` | `POST`| Natural language to SQL query engine | `question`, `route`, `sql_query`, `sql_valid`, `data_rows`, `answer`, `insights` |
| `/api/decision/actions` | `GET` | Prioritized Next Best Action queue | Array of `{ id, domain, title, severity, target, evidence, reason, confidence_pct }` |
| `/api/decision/simulate`| `POST`| Multi-variable What-If simulation | `scenario_name`, `projected_revenue`, `projected_net_margin`, `projected_orders`, `roi_multiple` |
| `/api/digital-twin/state`| `GET` | 4-pillar digital twin state & ripple chains| `vitality_index`, `pillars`, `systemic_alerts`, `impact_ripple_chains` |

---

## 4. Local Setup & Execution Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- Git

### 1. Backend REST API
```bash
# From repository root
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation (Swagger UI) is accessible at `http://127.0.0.1:8000/docs`.

### 2. Standalone React Frontend
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` to access the primary NovaNest interface.

To build for production:
```bash
npm run build
```

### 3. Streamlit Analytics Hub (Alternative Interface)
```bash
# From repository root
streamlit run streamlit_app/app.py --server.port 8501
```
Open `http://localhost:8501` to access the multi-page exploratory analytics hub.

### 4. Running the Complete Verification Test Suite
```bash
python tests/test_platform_full_suite.py
```
This script verifies:
1. All 12 FastAPI REST API endpoints
2. Frontend dev server and production build files
3. Streamlit hub availability
4. Dataset files and Power BI asset preservation

---

## 5. Security & Data Integrity Guarantees

1. **SQL Injection Prevention**: All queries generated by the AI Natural Language interface pass through an AST validator ensuring only safe `SELECT` operations are executed against a mirrored, in-memory read-only SQLite database.
2. **Deterministic Calculations**: No synthetic numbers are hardcoded into views. All metrics, charts, and forecasts derive directly from the data engineering pipelines and ML models in `datasets/cleaned/` and `datasets/engineered/`.
3. **Data Fallback Safety**: If MySQL database credentials are absent, the platform automatically falls back to curated CSV data caches with identical schemas.
4. **Protected Assets**: Binary assets like `powerbi/NovaNest.pbix` are protected and preserved.
