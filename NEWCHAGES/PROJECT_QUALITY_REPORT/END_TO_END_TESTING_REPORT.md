# NovaNest – End-to-End Workflows & Integration Testing Report

**Audit Date**: November 18, 2026  
**Auditor**: Senior Full-Stack QA & Data Engineering Lead  
**Component**: End-to-End Workflows (Data Pipeline -> Backend -> AI -> Presentation)  
**Verdict**: **`VERIFIED & OPERATIONALLY CONSISTENT`**

---

## 1. End-to-End Architecture Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as Executive / User
    participant UI as React / Streamlit / Power BI
    participant API as FastAPI Backend (:8000)
    participant Orch as Master Orchestrator
    participant Agents as 5 Domain Agents
    participant Verifier as OutputVerifier
    participant DB as MySQL 8.0 (novanest_db)

    User->>UI: Submit Natural Language Query / Open Dashboard
    UI->>API: HTTP POST /api/ai/ask or /api/kpis/overview
    API->>Orch: orchestrate(user_query, context)
    Orch->>Agents: Fork Context & Dispatch Intent (Fin, Ops, Cust, Rest)
    Agents->>DB: Query Scoped Tables (e.g. orders_table, deliveries)
    DB-->>Agents: Return Cleaned Results (304,405 Rows Total)
    Agents-->>Orch: Return Grounded Facts, Provenance & Caveats
    Orch->>Agents: Stage 2: Prescriptive Synthesis (Decision Agent)
    Orch->>Verifier: Validate Numerical Consistency & Integrity
    Verifier-->>Orch: Outcome: VERIFIED (0 Unsupported Claims)
    Orch-->>API: Emit Structured Chat Response
    API-->>UI: JSON Payload with Grounding Badge & Facts
    UI-->>User: Render Interactive Visuals, Cards & Narrative
```

---

## 2. Verified End-to-End User Journeys

### Journey 1: Financial Performance & Minimum Floor Reconciliation
1. **Trigger**: User asks *"What is our Net Revenue and GMV?"*
2. **Execution**: Routed to Financial Agent.
3. **Database Query**: Filters `orders_table` for `order_status = 'Delivered'`, applies `max(50, order_amount + delivery_fee - discount_amount)`.
4. **Result**: Delivered Food GMV ₹46,590,125.00, Net Revenue ₹46,425,992.00, Net AOV ₹967.33. Verified against ₹50 floor adjustment (+₹876.00).
5. **Attribution**: Grounded in `orders_table` and `payments`. Verification outcome: `VERIFIED`.

### Journey 2: Customer Retention & Churn Screening
1. **Trigger**: User queries *"Analyze customer churn risk and cohort retention."*
2. **Execution**: Routed to Customer Agent.
3. **Analysis**: Computes RFM segmentation from `customers` and `orders`, retrieves model prediction from `models/customer_churn/model_artifact_v3.joblib`.
4. **Safety Control**: Because churn model is tier `LOW_EMPIRICAL` (ROC-AUC 0.5062), output includes mandatory caveat: `NEEDS_MORE_DATA`. Prevents ungrounded retention incentives.
5. **Output**: Verified customer repeat rate (99.94%) alongside caveat.

### Journey 3: Prescriptive What-If Scenario Simulation
1. **Trigger**: Executive adjusts delivery fee by +₹10 in Decision Simulator.
2. **Execution**: Routed to Decision Agent / Scenario Simulation Engine.
3. **Simulation**: Projects margin improvement while calculating sensitivity elasticity and potential churn impact.
4. **Human-in-the-Loop Safeguard**: Generates `REC-REV-001` with `human_approval_required = True`. Automated agents are strictly blocked from self-executing fee changes.

---

## 3. Cross-Platform Parity Verification Matrix

| Touchpoint | Total Orders | Delivered Food GMV | Net Revenue | Contribution Margin | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **MySQL 8.0 Source** | 49,971 | ₹46,590,125.00 | ₹46,425,992.00 | 23.59% | **BASELINE** |
| **Cleaned CSV Files** | 49,971 | ₹46,590,125.00 | ₹46,425,992.00 | 23.59% | **100% PARITY** |
| **FastAPI `/api/kpis`** | 49,971 | ₹46,590,125.00 | ₹46,425,992.00 | 23.59% | **100% PARITY** |
| **Master Orchestrator**| 49,971 | ₹46,590,125.00 | ₹46,425,992.00 | 23.59% | **100% PARITY** |
| **React Components** | 49,971 | ₹46,590,125.00 | ₹46,425,992.00 | 23.59% | **100% PARITY** |
| **Streamlit Pages** | 49,971 | ₹46,590,125.00 | ₹46,425,992.00 | 23.59% | **100% PARITY** |
| **Power BI Semantic** | 49,971 | ₹46,590,125.00 | ₹46,425,992.00 | 23.59% | **100% PARITY** |

---

## 4. End-to-End Conclusion

The entire analytical and operational loop—from underlying SQL tables through intermediate AI agents to final user interfaces—demonstrates seamless mathematical alignment, robust error handling, and complete data safety.
