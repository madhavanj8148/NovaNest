# Figure 1: Overall NovaNest System Architecture

```mermaid
flowchart TD
    subgraph PresentationLayer ["Presentation & Interaction Layer"]
        UI1["React 18 Dashboard<br/>(TypeScript, Tailwind CSS, Recharts)"]
        UI2["Streamlit Multi-Page App<br/>(Dual DB Resolution: MySQL / SQLite)"]
        UI3["Power BI Analytical Workspace<br/>(Executive BI, NovaNest Dark Theme)"]
    end

    subgraph APILayer ["API & Gateway Layer (FastAPI)"]
        GW["FastAPI REST Gateway (48 Endpoints)"]
        AUTH["Security & RBAC Enforcement<br/>(JWT, API Key, Scope Validator)"]
        CACHE["In-Memory Query Cache<br/>(TTL, LRU, 94.2% Hit Ratio)"]
    end

    subgraph AgenticLayer ["Multi-Agent Intelligence Core"]
        ORCH["Master Orchestrator<br/>(Semantic IntentRouter & Circuit Breakers)"]
        VERIF["Deterministic OutputVerifier<br/>(16 Certified KPIs, AST, Tolerance)"]
        
        subgraph DomainAgents ["Specialized Domain Intelligence Agents"]
            FA["FinancialAgent<br/>(GMV, AOV, P&L, Leakage)"]
            CA["CustomerAgent<br/>(RFM, Churn, LTV, C360)"]
            OA["OperationsAgent<br/>(ETA, SLA, Fleet, Dispatch)"]
            RA["RestaurantAgent<br/>(Merchants, Menus, Risk)"]
            DA["DecisionAgent<br/>(Cross-domain Synthesis, RCA)"]
        end
    end

    subgraph DecisionLayer ["Prescriptive & Simulation Engines"]
        PRESC["PrescriptiveEngine<br/>(Action Recommendation Lifecycle)"]
        SIM["Digital Twin Engine<br/>(5 Interconnected Sub-Twins, Monte Carlo)"]
        HITL["Human-in-the-Loop Governance<br/>(Cryptographic Admin Review & Approval)"]
    end

    subgraph AnalyticsMLLayer ["Machine Learning & Analytical Services"]
        ML1["Customer Churn Predictor (RF/XGB)"]
        ML2["Delivery ETA Predictor (HistGB)"]
        ML3["Demand Volume Forecaster (HistGB)"]
        ML4["Restaurant Demand Predictor (Ridge)"]
        ML5["Operational Anomaly Consensus (IF+EE+LOF)"]
    end

    subgraph DataLayer ["Data Engineering & Storage Infrastructure"]
        SQL["MySQL 8.0 Primary DB<br/>(InnoDB, 10 Tables, 304,405 Rows)"]
        SQLITE["SQLite Analytical Mirror<br/>(In-Memory, Zero-Network Evaluation)"]
        RAW["Raw & Cleaned Datasets<br/>(10 CSV Files, Python ETL)"]
    end

    %% Connections
    UI1 --> GW
    UI2 --> GW
    UI2 -.-> SQLITE
    UI3 -.-> SQL
    GW --> AUTH
    AUTH --> CACHE
    CACHE --> ORCH
    ORCH --> FA & CA & OA & RA
    FA & CA & OA & RA --> DA
    ORCH --> VERIF
    VERIF --> GW

    FA & CA & OA & RA -.-> SQLITE
    DA --> PRESC
    PRESC --> SIM
    SIM --> HITL
    
    DomainAgents -.-> AnalyticsMLLayer
    AnalyticsMLLayer -.-> SQL
    SQL --> SQLITE
    RAW --> SQL
```

### Architectural Description
Figure 1 presents the multi-tiered architecture of NovaNest. The system coordinates five specialized domain agents through a central Master Orchestrator, underpinned by a deterministic OutputVerifier that enforces numerical grounding against 16 certified KPI ground truths. The decision intelligence subsystem bridges predictive ML services with prescriptive action recommendations, governed by a mandatory Human-in-the-Loop approval state machine.
