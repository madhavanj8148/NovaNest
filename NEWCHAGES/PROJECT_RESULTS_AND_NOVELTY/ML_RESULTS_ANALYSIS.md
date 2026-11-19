# NOVANEST — PROJECT RESULTS AND NOVELTY REPORT (FINAL AUDITED EDITION)
## MODULE 2: MACHINE LEARNING & PREDICTIVE ANALYTICS RESULTS

```
====================================================================================================
PROJECT:               NovaNest Enterprise Food Delivery Analytics & Decision Intelligence
DOCUMENT:              Machine Learning Results & Empirical Benchmark Reconciliation
AUDIT METHODOLOGY:     Strict Reconciliation Against Phase 07 Reproducible Logs & Model Registry
EPISTEMIC POSTURE:     Strictly Grounded in Actual Empirical Validation — Zero Unsupported Metrics
STATUS:                CALIBRATED — GOVERNED WITH HONEST CONFIDENCE GATING
====================================================================================================
```

---

### 1. OVERVIEW & RECONCILIATION SUMMARY

A critical requirement of academic and software engineering integrity is the absolute fidelity of machine learning reporting to reproducible empirical logs. In early exploratory drafts, preliminary uncalibrated benchmark targets were inadvertently reported. This document presents the **fully reconciled, verified machine learning results** derived directly from the Phase 07 empirical audit suite (`tests/test_phase07_ml_optimization.py` and `NEWCHAGES/PHASE_07/TEST_RESULTS.md`).

The NovaNest predictive subsystem comprises five specialized models managed under the active Model Registry (`models/registry_index.json`). Every model was audited for data leakage, evaluated on monotonic temporal holdout sets, and governed by **honest confidence gating**:

```
+----------------------------------------------------------------------------------------------------+
|                                RECONCILED EMPIRICAL MODEL REGISTRY                                 |
+----------------------------------------------------------------------------------------------------+
| 1. Customer Churn Risk       | Random Forest / XGBoost (Holdout N=4,999) | ROC-AUC: 0.5062 (Gated) |
| 2. Delivery ETA Estimation   | HistGradientBoosting (Holdout N=9,995)   | MAE: 11.52 min (Gated)  |
| 3. Metro Demand Forecasting  | HistGradientBoosting (3-Fold Backtest)    | WAPE: 17.20% (Baseline) |
| 4. Restaurant Multi-Target   | Ridge / HistGradientBoosting (N=1,500)   | MAE: 1.32 orders/month  |
| 5. Operational Anomaly Detect| Unsupervised Consensus Ensemble (N=49,971)| 628 Flagged (1.26%)     |
+----------------------------------------------------------------------------------------------------+
```

---

### 2. DETAILED EMPIRICAL EVALUATION ACROSS ALL FIVE MODELS

---

#### 2.1 Model 1: Customer Churn Prediction (Holdout N = 4,999 Customers)
- **Problem Formulation**: Binary classification predicting whether an active customer places zero orders in the 90 days following the observation cutoff date.
- **Dataset & Base Rate**: 4,999 customer behavioral profiles; natural churn base rate is **8.54%** (427 churned out of 4,999).
- **Leakage Audit**: **PASSED**. All post-cutoff orders, reviews, and cumulative full-timeline recency features were strictly eliminated from the feature matrix.
- **Empirical Benchmark Results**:

| Candidate Algorithm | ROC-AUC | PR-AUC | Accuracy | Precision | Recall | F1-Score | Brier Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Heuristic Baseline (Recency > 90d)** | 0.5015 | 0.0869 | 84.32% | 0.0858 | 0.0867 | 0.0862 | 0.1299 |
| **Logistic Regression (L2)** | 0.4887 | 0.0842 | 91.46% | 0.0000 | 0.0000 | 0.0000 | 0.0782 |
| **Random Forest (Calibrated)** | **0.5062** | **0.0950** | 91.46% | 0.0000 | 0.0000 | 0.0000 | **0.0781** |
| **HistGradientBoosting (Calibrated)** | 0.4911 | 0.0825 | 91.46% | 0.0000 | 0.0000 | 0.0000 | 0.0782 |
| **LightGBM (Calibrated)** | 0.4775 | 0.0806 | 91.46% | 0.0000 | 0.0000 | 0.0000 | 0.0782 |
| **XGBoost (Calibrated)** | 0.4861 | 0.0832 | 91.46% | 0.0000 | 0.0000 | 0.0000 | 0.0781 |

- **Root Cause Analysis & Epistemic Finding**:
  When temporal leakage is strictly eliminated, the synthetic customer arrival process (generated via uniform Poisson arrival rates) yields near-chance discriminative power ($\text{ROC-AUC} \approx 0.50\text{--}0.51$).
- **Operational Governance & Confidence Gating**:
  Assigned confidence tier: **`LOW_EMPIRICAL`**. The platform automatically suppresses numerical certainty (`confidence_pct: None`) in the API and Decision Center, mandating that customer re-engagement campaigns rely on deterministic RFM rules rather than treating ML churn probabilities as ground truth.

---

#### 2.2 Model 2: Delivery ETA Prediction (Holdout N = 9,995 Trips)
- **Problem Formulation**: Continuous regression predicting total `delivery_duration` (minutes) at the moment of order dispatch.
- **Target Distribution**: Mean = **37.33 minutes**, Standard Deviation = **13.31 minutes**.
- **Leakage Audit**: **PASSED**. All post-dispatch features (actual arrival timestamps, delivery delay status, customer star ratings) were excluded.
- **Empirical Benchmark Results**:

| Candidate Algorithm | MAE (min) | Median AE (min) | RMSE (min) | $R^2$ Score | MAPE (%) | Mean Bias (min) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline Global Mean** | **11.5123** | **11.0000** | 13.3186 | -0.0006 | 38.50% | -0.3325 |
| **Ridge Regression (L2)** | 11.5208 | 11.4596 | 13.3196 | -0.0008 | 38.93% | 0.0544 |
| **Random Forest** | 11.5254 | 11.4614 | 13.3245 | -0.0015 | 38.93% | 0.0435 |
| **HistGradientBoosting** | **11.5158** | 11.4930 | **13.3159** | **-0.0002** | 38.89% | **0.0365** |
| **LightGBM** | 11.5281 | 11.4743 | 13.3346 | -0.0030 | 38.95% | 0.0640 |
| **XGBoost** | 11.5222 | 11.4743 | 13.3314 | -0.0025 | 38.94% | 0.0695 |

- **Stratified Error Breakdown**:
  - *By City*: Bangalore (MAE 11.75m), Chennai (MAE 11.47m), Coimbatore (MAE 11.41m), Hyderabad (MAE 11.53m), Vijayawada (MAE 11.18m).
  - *By Distance Tier*: 0–3 km (MAE 11.35m), 3–7 km (MAE 11.49m), 7–15 km (MAE 11.61m).
  - *By Fleet Vehicle*: Motorcycle (MAE 11.55m), Scooter (MAE 11.48m).
- **Operational Governance & Uncertainty Bounds**:
  Assigned confidence tier: **`LOW_EMPIRICAL`**. The 90% empirical prediction interval is established at **$\text{predicted} \pm 21.9\text{ minutes}$**, attaching transparent safety buffers to dispatch SLAs.

---

#### 2.3 Model 3: City Demand Forecasting (Holdout N = 70 City-Days)
- **Problem Formulation**: Multi-step daily order volume forecasting per city across a contiguous calendar grid.
- **Validation Methodology**: 3-fold rolling-origin backtesting using 14-day evaluation windows.
- **Empirical Benchmark Results**:

| Candidate Model / Benchmark | MAE (orders) | Median AE | RMSE | Pooled $R^2$ | WAPE (%) | MASE | Operational Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Seasonal Naive ($lag_7$)** | 7.1714 | 6.0000 | 8.5973 | 0.3730 | 26.31% | 1.000 | Naive Baseline |
| **Rolling Mean (7-Day)** | 5.0735 | 4.2857 | 6.2318 | 0.6705 | 18.61% | 0.707 | Rolling Baseline |
| **Ridge Regression (L2)** | 4.6943 | 4.4243 | **5.7168** | **0.7227** | 17.22% | 0.655 | Regularized OLS |
| **HistGradientBoosting** | **4.6878** | **4.1245** | 6.1350 | 0.6807 | **17.20%** | **0.654** | **Selected Best Model** |
| **LightGBM** | 4.7447 | 4.3969 | 6.2085 | 0.6730 | 17.41% | 0.662 | Tree Ensemble |
| **XGBoost** | 4.8654 | 4.7444 | 6.2687 | 0.6666 | 17.85% | 0.678 | Tree Ensemble |

- **Backtest Performance Improvement**:
  HistGradientBoosting achieves a **34.6% relative error reduction** over the Seasonal Naive baseline (WAPE drops from 26.31% to **17.20%**; MASE = **0.654**).
- **Operational Governance**:
  Assigned confidence tier: **`BASELINE_ONLY`**. Accurately models day-of-week seasonality, but is caveated against unmodeled exogenous weather or civic disruptions.

---

#### 2.4 Model 4: Restaurant Performance Multi-Target Regression (Holdout N = 1,500 Partners)
- **Problem Formulation**: Multi-target regression simultaneously predicting Next-Month Orders, Next-Month Revenue, and Partner Rating.
- **Target 1 (Monthly Orders)**: Mean = 2.92 orders/month, Std = 1.68 orders.
- **Empirical Benchmark Results**:

| Model / Baseline | Target Dimension | MAE | Median AE | RMSE | $R^2$ Score |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Baseline Prev-Month** | Next-Month Orders | 1.8067 | 1.5000 | 2.3321 | -0.9256 |
| **Baseline Global Mean** | Next-Month Orders | 1.3351 | 1.2560 | 1.6894 | -0.0106 |
| **Ridge Regression (L2)** | **Next-Month Orders** | **1.3248** | **1.1069** | **1.6829** | **-0.0027** |
| **HistGradientBoosting** | Next-Month Orders | 1.3326 | 1.1467 | 1.6870 | -0.0076 |
| **XGBoost** | Next-Month Orders | 1.3305 | 1.1211 | 1.6890 | -0.0101 |
| **Baseline Mean Revenue** | Next-Month Revenue | ₹1,552.02 | ₹1,302.89 | ₹2,005.00 | -0.0071 |
| **Ridge Regression (L2)** | **Next-Month Revenue** | **₹1,546.93** | **₹1,302.86** | **₹1,983.65** | **0.0142** |

- **Operational Governance**:
  Assigned confidence tier: **`LOW_EMPIRICAL`**. Provides indicative merchant capacity planning without automated store tier demotions.

---

#### 2.5 Model 5: Operational Anomaly & Risk Detection (N = 49,971 Audited Orders)
- **Problem Formulation**: Unsupervised anomaly detection identifying operational outliers across delivery durations, speed violations, and fee leakage.
- **Enterprise Policy Compliance**: **Zero confirmed fraud labels** are asserted, reflecting strict compliance with risk governance (no synthetic fraud labels fabricated).
- **Empirical Audited Detection Rates**:

| Detection Architecture | Flagged Orders | Outlier Rate | Risk Category Assigned | Audited Exposure Value |
| :--- | :---: | :---: | :--- | :---: |
| **Dual Z-Score / Tukey IQR** | 945 | 1.89% | `STATISTICAL_OUTLIER` | ₹918,204.00 |
| **Isolation Forest (Contamination=3%)** | 1,500 | 3.00% | `STATISTICAL_OUTLIER` | ₹1,453,558.00 |
| **Local Outlier Factor (Subsample 10k)** | 300 | 3.00% | `STATISTICAL_OUTLIER` | Subsample check |
| **Consensus Ensemble (Agreement $\ge$ 2)** | **628** | **1.26%** | `SUSPECTED_OPERATIONAL_RISK` | **₹519,596.00** |

- **Operational Governance**:
  Assigned confidence tier: **`EXPERIMENTAL`**. Anomaly flags generate supervisory review tickets; no automatic rider deactivation or partner penalization occurs without manual operator confirmation.

---

### 3. ACADEMIC SIGNIFICANCE OF HONEST CONFIDENCE GATING

The true engineering achievement demonstrated by NovaNest is **not the fabrication of artificially inflated 99% accuracy figures**, but rather the implementation of **production-grade epistemic honesty**:
1. When temporal leakage was eradicated, the platform transparently recognized the limits of synthetic tabular distributions.
2. The AI agents and API actively communicate these boundaries to executive users through metadata caveats (`PHASE_07_LOW_EMPIRICAL`, `BASELINE_ONLY`).
3. This prevents dangerous automated over-reliance on statistical models and establishes a rigorous benchmark for trustworthy applied machine learning.
