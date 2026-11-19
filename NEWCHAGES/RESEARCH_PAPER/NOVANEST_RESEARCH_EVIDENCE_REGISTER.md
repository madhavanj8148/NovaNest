# NovaNest: Research Evidence Register & Claim-to-Code Mapping

**Document Purpose**: Comprehensive evidence audit trail establishing empirical traceability between every technical claim, numerical metric, architectural pattern, and benchmark result in the research paper titled:  
*"NovaNest: A Grounded Multi-Agent Decision Intelligence Framework for Food Delivery Analytics and Prescriptive Business Optimization"*  
and its corresponding physical source code, test artifact, or data file in the NovaNest repository.

---

## 1. Traceability Matrix

| Claim ID | Paper Claim / Assertion | Exact Value / Stated Result | Canonical Source File in Repository | Specific Function / Section / Code Anchor | Verification Status & Notes |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **CLM-01** | Total dataset record volume | 304,405 records across 10 tables | `datasets/cleaned/*.csv`, `docker/mysql/init/01_init_schema.sql` | Line count summation across 10 cleaned CSV files | **Verified**: Exactly matches physical line count and MySQL row counts. |
| **CLM-02** | Total orders and operational split | 49,971 total (47,994 delivered, 1,977 cancelled) | `datasets/cleaned/orders.csv`, `python/analytics/validate_kpis.py` | `validate_kpis.py:orders_status_check` | **Verified**: Reconciled historical 34,980 count against canonical SQL `COUNT(*)`. |
| **CLM-03** | Gross Merchandise Value (KPI-01) | ₹46,590,125.00 | `python/ai/agents/financial_agent.py`, `python/analytics/validate_kpis.py` | `compute_financial_kpis()` | **Verified**: Excludes cancelled orders; sums `order_amount`. |
| **CLM-04** | Net Inflow / Revenue (KPI-02) | ₹46,425,992.00 | `python/ai/agents/financial_agent.py`, `python/analytics/validate_kpis.py` | `compute_financial_kpis()` | **Verified**: Sum of `final_amount` for delivered orders. |
| **CLM-05** | Net Average Order Value (KPI-03) | ₹967.33 | `python/ai/agents/financial_agent.py` | `compute_financial_kpis()` | **Verified**: ₹46,425,992.00 / 47,994 delivered orders. |
| **CLM-06** | Platform Contribution Profit (KPI-13)| ₹10,953,031.58 | `python/ai/agents/financial_agent.py`, `python/decision/financial_impact_engine.py` | `calculate_contribution_profit()` | **Verified**: Formally labeled as Estimated Platform Contribution Profit (not Operating Profit). |
| **CLM-07** | Churn Model Holdout Metrics | RF ROC-AUC: 0.5062, XGB: 0.4861 | `models/customer_churn/metadata_v3.json`, `models/customer_churn/customer_churn_metrics_v3.json` | JSON keys: `evaluation_metrics.holdout_roc_auc` | **Verified**: Evaluated on temporal 80/20 split; tagged with `LOW_EMPIRICAL`. |
| **CLM-08** | Delivery ETA Model Holdout Metric | MAE: 11.52 mins (90% bound: ±21.9m) | `models/delivery_time/metadata_v3.json`, `models/delivery_time/delivery_time_metrics_v3.json` | JSON keys: `evaluation_metrics.holdout_mae` | **Verified**: HistGradientBoostingRegressor on chronological test set. |
| **CLM-09** | Demand Forecasting Holdout Metric | WAPE: 17.20%, RMSE: 14.8 orders/hr | `models/demand_forecasting/metadata_v3.json` | JSON keys: `evaluation_metrics.holdout_wape` | **Verified**: Tagged with `BASELINE_ONLY`. |
| **CLM-10** | Restaurant Demand Holdout Metric | MAE: 1.32 orders, $R^2$: 0.052 | `models/restaurant_demand/metadata_v3.json` | JSON keys: `evaluation_metrics.holdout_r2` | **Verified**: Ridge regression; tagged with `LOW_EMPIRICAL`. |
| **CLM-11** | Anomaly Consensus Model | 628 / 49,971 flagged (1.26%) | `models/anomaly_detection/metadata_v3.json` | `ConsensusEnsemble.predict()` | **Verified**: 2/3 agreement across Isolation Forest, Elliptic Envelope, LOF. |
| **CLM-12** | OutputVerifier Attack Interception | 100% (20/20 attacks blocked) | `python/ai/agents/evaluation.py`, `python/ai/agents/output_verifier.py` | `run_eval_suite()`, `test_injection_defense()` | **Verified**: Evaluated on 50-prompt adversarial test suite; 0 false positives on 30 benign queries. |
| **CLM-13** | Two-Stage Master Orchestrator | Stage 1 parallel + Stage 2 sequential | `python/ai/agents/master_orchestrator.py` | `_execute_stage1_parallel()`, `_execute_stage2_sequential()` | **Verified**: Multi-threaded ThreadPoolExecutor with per-agent circuit breakers. |
| **CLM-14** | Data Slicing & Isolation | Copy-on-Write / shallow copying | `python/ai/agents/master_orchestrator.py` | `_slice_isolated_data()` | **Verified**: Slices isolated datasets by agent domain to prevent thread mutation. |
| **CLM-15** | SQL AST Security Validator | Read-only whitelist across 10 tables | `python/ai/analyst/sql_ast.py` | `validate_sql_ast()` | **Verified**: Blocks non-SELECT queries, pragma, and system catalog access. |
| **CLM-16** | Prompt Injection Sanitization | 8 regex pattern categories | `python/ai/agents/contracts.py` | `_INJECTION_RULES`, `sanitize_user_query()` | **Verified**: Detects instruction override, role delimiter, and secret exfiltration. |
| **CLM-17** | Query Cache Performance Gain | 450.2 ms to 12.1 ms (97.31% reduction) | `api/cache.py`, `tests/test_performance.py` | `QueryCache.get()`, `test_cache_latency()` | **Verified**: Measured on warm memory cache with 94.20% hit ratio. |
| **CLM-18** | Concurrency p95 Latency | 52.1 ms under 50 concurrent users | `tests/test_load.py`, `NEWCHAGES/PHASE19_END_TO_END_VALIDATION/` | `benchmark_concurrency_load()` | **Verified**: Executed via concurrent client threads with 0.00% error rate. |
| **CLM-19** | Disaster Recovery RTO | 2.107 seconds on isolated MySQL | `tests/test_failover.py`, `NEWCHAGES/SOFTWARE_QUALITY_IMPROVEMENT/` | `test_container_failover_recovery()` | **Verified**: RTO measured against isolated Docker daemon recovery. |
| **CLM-20** | Automated Test Suite Pass Rate | 173 passed / 173 executed (100%) | `tests/` directory (`pytest`) | `pytest --verbose` execution run | **Verified**: All 173 tests pass cleanly. |
| **CLM-21** | Recommendation State Machine | Formal 6-state lifecycle | `python/decision/recommendation_lifecycle.py` | `RecommendationStatus` Enum, `transition()` | **Verified**: Requires human cryptographic approval before execution. |
| **CLM-22** | Digital Twin Simulation Engine | 5 interconnected domain sub-twins | `python/digital_twin/twin_engine.py` | `DigitalTwinEngine.simulate_scenario()` | **Verified**: Monte Carlo elasticity damping across customer, rider, and restaurant twins. |
| **CLM-23** | Cross-Platform Analytical Parity | Reconciled across React, Streamlit, PBI | `api/main.py`, `streamlit_app/app.py`, `powerbi/NovaNest_themed.pbix` | Centralized REST endpoints and shared SQL definitions | **Verified**: Identical GMV, Revenue, AOV, and cancellation rates across all three UIs. |
| **CLM-24** | Internal ISO/IEC 25010 Quality Score | 95.65 / 100 (Grade A+) | `NEWCHAGES/SOFTWARE_QUALITY_IMPROVEMENT/NOVANEST_SOFTWARE_QUALITY_EXCELLENCE_REPORT_FINAL.md` | Weighted scoring model across 9 quality characteristics | **Verified**: Internal audit aligned with ISO/IEC 25010:2023 criteria. |

---

## 2. Integrity and Non-Fabrication Confirmation

The authoring environment confirms that:
1. No unverified claim of production readiness has been attributed to `customer_churn` (ROC-AUC 0.5062) or `restaurant_demand` ($R^2$ 0.052).
2. The term "Estimated Platform Contribution Profit" has replaced all prior instances of "net operating profit."
3. OutputVerifier's 100% defense claim is strictly scoped to the 50-prompt test suite.
4. Disaster recovery timings are explicitly marked as tested on an isolated container instance.
