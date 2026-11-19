# Figure 6: Deterministic OutputVerifier Architecture & Flow

```mermaid
flowchart TD
    subgraph InputStage ["Input Verification Artifacts"]
        TXT["Candidate Narrative Prose"]
        FACTS["GroundedFact[] Array<br/>(Emitted by Agents)"]
        REQS["Approved KPI Catalog<br/>(16 Formal Definitions)"]
    end

    subgraph RegexParser ["1. Extraction & Parsing Subsystem"]
        P1["Strip Benign Structural Tokens<br/>(KPI IDs, Dates, Bullets, Version Tags)"]
        P2["Normalize Currency & Numbers<br/>(INR, Lakhs, Crores, %, Scalars)"]
        P3["Build ExtractedClaim[] List"]
    end

    subgraph ValidationGates ["2. Deterministic Verification Gates"]
        G1["Tolerance Matching Gate<br/>(|claim - fact| <= max(abs_tol, rel_tol * fact))"]
        G2["KPI Inversion Audit<br/>(Detect contra-rules, e.g. GMV with cancelled)"]
        G3["Inter-Agent Metric Conflict Check<br/>(Flag divergent values across agents)"]
        G4["Provenance Source Audit<br/>(Validate against approved 10-table schema)"]
        G5["Confirmed Loss Enforcement<br/>(Ensure is_confirmed_loss=False on screening)"]
        G6["ML Overclaim Interception<br/>(Ensure LOW_EMPIRICAL / BASELINE caveat present)"]
    end

    subgraph OutcomeStage ["3. Verification Report Generation"]
        REP["VerificationReport<br/>• outcome: VERIFIED / PARTIAL / REJECTED<br/>• checked_claims: ExtractedClaim[]<br/>• violations: VerificationViolation[]<br/>• conflicts: ConflictDetail[]"]
    end

    TXT --> P1 --> P2 --> P3
    FACTS --> G1
    REQS --> G2
    P3 --> G1 --> G2 --> G3 --> G4 --> G5 --> G6
    G6 --> REP
```

---

# Figure 7: Machine Learning Training, Validation & Confidence Gating Pipeline

```mermaid
flowchart TD
    subgraph DataSplit ["Temporal Train/Test Split (80/20)"]
        DATA["Canonical 304,405 Records"] --> SPLIT["Chronological Temporal Split<br/>(Train: 80% | Holdout: 20%)"]
    end

    subgraph Models ["Five Machine Learning Problem Areas"]
        M1["Customer Churn<br/>(Random Forest / XGBoost)"]
        M2["Delivery ETA<br/>(HistGradientBoosting)"]
        M3["Demand Volume<br/>(HistGradientBoosting)"]
        M4["Restaurant Demand<br/>(Ridge Linear Regressor)"]
        M5["Operational Anomaly<br/>(IsolationForest + EE + LOF)"]
    end

    subgraph HoldoutEval ["Holdout Evaluation & Metrics"]
        E1["RF AUC: 0.5062<br/>XGB AUC: 0.4861"]
        E2["MAE: 11.52 mins<br/>90% Bound: ±21.9 mins"]
        E3["WAPE: 17.20%<br/>RMSE: 14.8/hr"]
        E4["MAE: 1.32 orders<br/>R²: 0.052"]
        E5["628 Flagged (1.26%)<br/>Consensus: 84.1%"]
    end

    subgraph ConfidenceGating ["Automated Confidence Gating System"]
        G1["Tag: LOW_EMPIRICAL<br/>(Exploratory Heuristic)"]
        G2["Tag: LOW_EMPIRICAL<br/>(Uncertainty Interval Mandate)"]
        G3["Tag: BASELINE_ONLY<br/>(Directional Indicator)"]
        G4["Tag: LOW_EMPIRICAL<br/>(Screening Baseline)"]
        G5["Tag: EXPERIMENTAL<br/>(Human Queue Mandatory)"]
    end

    SPLIT --> M1 & M2 & M3 & M4 & M5
    M1 --> E1 --> G1
    M2 --> E2 --> G2
    M3 --> E3 --> G3
    M4 --> E4 --> G4
    M5 --> E5 --> G5
```

---

# Figure 8: Prescriptive Analytics & Digital Twin Simulation Workflow

```mermaid
flowchart LR
    subgraph TriggerStage ["Insight Trigger"]
        DIAG["Diagnostic Insight<br/>(e.g., SLA Breach Surge in City X)"]
    end

    subgraph EngineStage ["Prescriptive Engine & Impact Estimation"]
        PE["PrescriptiveEngine<br/>(Generate Action Candidates)"]
        FE["FinancialImpactEngine<br/>(Estimate Net Gain / Cost)"]
    end

    subgraph TwinStage ["Digital Twin Simulation"]
        DT["DigitalTwinEngine<br/>(5 Interconnected Sub-Twins)"]
        MC["Monte Carlo Simulation<br/>(Elasticity Damped Ripple Analysis)"]
    end

    subgraph GovernanceStage ["Human-in-the-Loop Lifecycle"]
        STATE["Lifecycle State Machine<br/>DRAFT ➔ REVIEW ➔ APPROVED ➔ SIMULATED ➔ APPLIED"]
        ADMIN["Cryptographic Admin Authorization<br/>(Zero Autonomous Strategic Action)"]
    end

    DIAG --> PE --> FE
    FE --> DT --> MC
    MC --> STATE
    STATE --> ADMIN
```

---

# Figure 9: Complete User Query Lifecycle

```mermaid
flowchart TD
    Q[User Natural Language Query] --> SAN[contracts.sanitize_user_query]
    SAN -->|Pure Attack| BLK[Immediate 403 Forbidden Block]
    SAN -->|Sanitized Query| IR[IntentRouter Semantic Scoring]
    IR -->|Mode Selection| PLAN[RoutingPlan Generated]
    
    PLAN -->|Direct SQL| AST[sql_ast.validate_sql_ast]
    AST -->|Safe SELECT| SQL_RUN[Execute Read-Only SQLite Engine]
    
    PLAN -->|Domain Analysis| PAR[Stage 1 Parallel ThreadPool]
    PAR -->|Isolated Copy-on-Write Slices| AGENTS[Domain Agents Execute]
    AGENTS -->|Results| SEQ[Stage 2 DecisionAgent Traversal]
    
    SEQ --> SYN[synthesizer.synthesize_agent_results]
    SQL_RUN --> SYN
    SYN --> VER[output_verifier.verify]
    
    VER -->|Pass| OUT[OrchestrationOutcome 200 OK]
    VER -->|Violation| REDACT[Redact Unsupported Claims & Caveat]
    REDACT --> OUT
    OUT --> UI[Render React / Streamlit Metric Cards & Charts]
```

---

# Figure 10: Docker Infrastructure & Deployment Topology

```mermaid
flowchart TD
    subgraph DockerHost ["Docker Compose Virtual Network (Isolated Bridge)"]
        subgraph DataTier ["Data Tier Container"]
            MYSQL_C["mysql:8.0 Container<br/>Port 3306 (Internal)<br/>Volume: mysql_data"]
        end

        subgraph BackendTier ["Backend API Container"]
            API_C["fastapi-backend Container<br/>Python 3.11, Uvicorn, 4 Workers<br/>Port 8000<br/>Healthcheck: /api/health"]
        end

        subgraph FrontendTier ["Frontend Applications Containers"]
            REACT_C["react-frontend Container<br/>Vite / Nginx Static Server<br/>Port 3000 / 80"]
            STREAM_C["streamlit-app Container<br/>Streamlit Server<br/>Port 8501"]
        end
    end

    subgraph ExternalAccess ["Host / User Browser Access"]
        BROWSER["Web Browser / Client<br/>• http://localhost:3000 (React UI)<br/>• http://localhost:8501 (Streamlit)<br/>• http://localhost:8000/docs (FastAPI)"]
    end

    MYSQL_C <-->|Internal TCP 3306| API_C
    API_C <-->|REST / JSON| REACT_C
    API_C <-->|REST / JSON| STREAM_C
    STREAM_C -.->|Direct Read-Only DB| MYSQL_C
    
    BROWSER --> REACT_C
    BROWSER --> STREAM_C
    BROWSER --> API_C
```
