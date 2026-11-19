# NOVANEST — ACADEMIC INTEGRITY & ORIGINALITY AUDIT
## MODULE 5: POTENTIAL ISSUES REGISTER & TRACEABILITY AUDIT

```
====================================================================================================
PROJECT:               NovaNest Enterprise Food Delivery Analytics & Decision Intelligence
DOCUMENT:              Potential Issues, Similarity Concerns & Attribution Audit Register
STANDARDS:             IEEE / ACM Publication Ethics Guidelines & Academic Integrity Criteria
TOTAL FINDINGS:        8 Identified Observations (0 Critical, 0 High, 4 Medium, 4 Low/Info)
AUDIT STATUS:          Actionable Registry Prepared for Faculty Review & Dissertation Finalization
====================================================================================================
```

---

### 1. SUMMARY OF AUDIT FINDINGS

The audit conducted across the NovaNest codebase, technical documentation, and academic reports identified **8 specific findings**. None of the findings involve intentional plagiarism, uncredited verbatim external text copying, or code theft. The findings are primarily related to **internal text repetition across modular reports**, **missing classical literature citations**, and **open-source licensing attribution hygiene**.

```
+----------------------------------------------------------------------------------------------------+
|                                      FINDINGS SEVERITY SUMMARY                                     |
+----------------------------------------------------------------------------------------------------+
| CRITICAL      (Verbatim External Plagiarism / Code Theft)        : 0 Findings                      |
| HIGH          (Fabricated Citations / Uncredited External Work)  : 0 Findings                      |
| MEDIUM        (Missing Classical Citations / License Hygiene)    : 4 Findings                      |
| LOW / INFO    (Internal Documentation Repetition across Phases)  : 4 Findings                      |
+----------------------------------------------------------------------------------------------------+
```

---

### 2. DETAILED AUDIT FINDINGS REGISTER

---

#### Finding ID: `ISS-CIT-001`
- **Severity**: **MEDIUM**
- **Document / File Path**: `NEWCHAGES/PROJECT_RESULTS_AND_NOVELTY/BUSINESS_IMPACT_ANALYSIS.md` & `NOVELTY_ASSESSMENT_REPORT.md`
- **Section / Target Area**: Module 4 (Section 3: Digital Twin & What-If Simulation Engine)
- **Original Passage**:
  > *"The NovaNest Digital Twin models the complex feedback loops between the four marketplace actors... translating physical digital twin principles into digital multi-sided platform economics."*
- **Similarity / Attribution Concern**: The concept of the "Digital Twin" is utilized extensively without citing the foundational academic originators of the paradigm (Michael Grieves and John Vickers).
- **Identified Source**: Grieves, M., & Vickers, J. (2014): *Digital Twin: Mitigating Unpredictable, Undesirable Emergent Behavior in Complex Systems.*
- **Recommended Correction**: Insert a formal scholarly citation to Grieves & Vickers (2014) in the introduction to the Digital Twin chapter.

---

#### Finding ID: `ISS-CIT-002`
- **Severity**: **MEDIUM**
- **Document / File Path**: `NEWCHAGES/PROJECT_RESULTS_AND_NOVELTY/PROJECT_RESULTS_REPORT.md`
- **Section / Target Area**: Module 1 (Section 3.2: Advanced Segmentation & Analytical Insights)
- **Original Passage**:
  > *"RFM Segmentation (Recency, Frequency, Monetary): Evaluated across all 5,000 customers using k-means and quantile scoring..."*
- **Similarity / Attribution Concern**: The RFM framework is an established database marketing methodology originated by Arthur Hughes (1994). While considered standard industry knowledge, academic dissertations should cite foundational literature.
- **Identified Source**: Hughes, A. M. (1994): *Strategic Database Marketing.* Probus Publishing Co.
- **Recommended Correction**: Add an academic citation to Arthur Hughes when defining the RFM scoring rubric.

---

#### Finding ID: `ISS-CIT-003`
- **Severity**: **MEDIUM**
- **Document / File Path**: `NEWCHAGES/PROJECT_RESULTS_AND_NOVELTY/BUSINESS_IMPACT_ANALYSIS.md`
- **Section / Target Area**: Module 4 (Section 1: The NovaNest Analytical Maturity Continuum)
- **Original Passage**:
  > *"Moving from Descriptive to Diagnostic, Predictive, and Prescriptive Analytics..."*
- **Similarity / Attribution Concern**: The four-stage analytical maturity hierarchy (Descriptive $\rightarrow$ Diagnostic $\rightarrow$ Predictive $\rightarrow$ Prescriptive) mirrors the widely recognized Gartner Analytics Maturity Model without explicit attribution.
- **Identified Source**: Gartner Research (2013): *Gartner IT Glossary: Analytics Maturity Model.*
- **Recommended Correction**: Add an attribution note: *(Adapted from the Gartner Analytics Maturity Framework)*.

---

#### Finding ID: `ISS-LIC-004`
- **Severity**: **MEDIUM**
- **Document / File Path**: Repository Root (`c:/Users/madha/OneDrive/Documents/NovaNest-main/`)
- **Section / Target Area**: Project Root Directory & Documentation
- **Original Condition**: The project imports and depends upon 16+ third-party open-source libraries (`FastAPI`, `Scikit-learn`, `LightGBM`, `XGBoost`, `React`, `Lucide`, `Recharts`, `Faker`) declared in `requirements.txt` and `package.json`, but lacks a consolidated `LICENSES.md` file acknowledging third-party copyright holders.
- **Similarity / Attribution Concern**: Open-source license attribution hygiene (BSD, MIT, and Apache-2.0 require preservation of copyright notices).
- **Identified Source**: Open Source Initiative (OSI) standard licensing terms.
- **Recommended Correction**: Create a standardized `LICENSES.md` file in the root repository compiling the MIT, BSD, and Apache licenses of all imported libraries.

---

#### Finding ID: `ISS-REP-005`
- **Severity**: **LOW**
- **Document / File Path**: `NEWCHAGES/PROJECT_RESULTS_AND_NOVELTY/` & `NEWCHAGES/PROJECT_QUALITY_REPORT/`
- **Section / Target Area**: Executive Summaries (`EXECUTIVE_SUMMARY.md` in both folders)
- **Original Passage**:
  > *"Modern online food delivery platforms (such as Swiggy, Zomato, DoorDash, and UberEats) operate as complex, highly volatile four-sided marketplaces consisting of: 1. Consumers... 2. Merchant Restaurants... 3. Delivery Fleets... 4. Platform Operators..."*
- **Similarity / Attribution Concern**: High near-verbatim textual overlap between the executive summaries of the Quality Assurance Report and the Results/Novelty Report.
- **Identified Source**: Internal self-repetition across project deliverables.
- **Recommended Correction**: Acceptable for independent standalone executive reports. For a unified master thesis submission, consolidate this background into Chapter 1 (Introduction) and cross-reference subsequently.

---

#### Finding ID: `ISS-REP-006`
- **Severity**: **LOW**
- **Document / File Path**: Multiple Phase Documentation Folders (`NEWCHAGES/PHASE18/`, `NEWCHAGES/PHASE18_THEME/`, `NEWCHAGES/PHASE15/`)
- **Section / Target Area**: Phase Metadata Banners
- **Original Passage**:
  > Standardized template: `**Phase**: XX`, `**Title**: ...`, `**Lead Agent**: ...`, `**Status**: ...`
- **Similarity / Attribution Concern**: Repetitive structural boilerplate across 30+ phase markdown files.
- **Identified Source**: Internal documentation scaffolding.
- **Recommended Correction**: None required; this represents legitimate operational documentation modularity.

---

#### Finding ID: `ISS-DAT-007`
- **Severity**: **INFORMATIONAL**
- **Document / File Path**: `python/data_generation/` & `datasets/`
- **Section / Target Area**: Data Engineering Pipeline
- **Original Passage**:
  > *"The underlying data was synthesized using Faker and domain-specific probability distributions..."*
- **Similarity / Attribution Concern**: Usage of the third-party open-source `Faker` library (by Daniele Faraglia) should be explicitly acknowledged with version number and license in the methodology section.
- **Identified Source**: Python `Faker` library (MIT License).
- **Recommended Correction**: Include full bibliographical credit to the `Faker` open-source library in the data engineering chapter.

---

#### Finding ID: `ISS-DIS-008`
- **Severity**: **INFORMATIONAL**
- **Document / File Path**: `NovaNest_Project_Results_and_Novelty_Report_Final.pdf` & `EVIDENCE_REGISTER.md`
- **Section / Target Area**: Cloud Deployment Status
- **Original Passage**:
  > *"Cloud Deployment: Local Docker productionized; Streamlit Cloud CSV configured... Status: STAGED_READY."*
- **Similarity / Attribution Concern**: Potential ambiguity regarding whether "STAGED_READY" implies active live public cloud hosting.
- **Identified Source**: Internal project status labeling.
- **Recommended Correction**: Reconciled in Final Edition: explicitly confirmed as Local Docker Operational / Streamlit Community Cloud Configured / Public VPS Deployment Pending.

---

### 3. AUDIT SUMMARY TABLE

| Finding ID | Severity | Category | Target File / Area | Summary of Finding | Remediation Complexity |
| :--- | :---: | :---: | :--- | :--- | :---: |
| `ISS-CIT-001` | **MEDIUM** | Citation Gap | `BUSINESS_IMPACT_ANALYSIS.md` | Add Grieves & Vickers (2014) Digital Twin reference | Low (1 Citation) |
| `ISS-CIT-002` | **MEDIUM** | Citation Gap | `PROJECT_RESULTS_REPORT.md` | Add Hughes (1994) RFM Marketing reference | Low (1 Citation) |
| `ISS-CIT-003` | **MEDIUM** | Attribution | `BUSINESS_IMPACT_ANALYSIS.md` | Attribute Gartner Analytics Maturity framework | Low (1 Note) |
| `ISS-LIC-004` | **MEDIUM** | Licensing | Repository Root | Create centralized `LICENSES.md` file | Moderate (Template) |
| `ISS-REP-005` | **LOW** | Repetition | Multiple Executive Summaries | Consolidate background into single Thesis chapter | Low (Dissertation) |
| `ISS-REP-006` | **LOW** | Boilerplate | Phase Markdown Banners | Operational documentation modularity (No change) | Informational |
| `ISS-DAT-007` | **INFO** | Attribution | Data Generation Docs | Attribute Python `Faker` library formally | Low (1 Citation) |
| `ISS-DIS-008` | **INFO** | Clarity | Report Deployment Tables | Deployment status already clarified in Final PDF | Complete |
