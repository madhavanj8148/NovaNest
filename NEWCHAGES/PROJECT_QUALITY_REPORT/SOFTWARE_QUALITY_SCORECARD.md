# NOVANEST — ISO/IEC 25010 SOFTWARE QUALITY SCORECARD (v2.0 REVISED)

**Evaluation Framework:** ISO/IEC 25010:2023 Systems and Software Quality Requirements and Evaluation (SQuaRE)  
**Evaluation Type:** Internal Automated Software Quality Assurance Audit  
**Assessment Date:** November 16, 2026  
**Auditor:** Senior QA Engineer & Lead Software Quality Auditor  

---

## 1. Quality Scoring Rubric & Methodology

Quality scores are evaluated using an evidence-based, transparent point allocation model across 9 quality characteristics.
Each characteristic begins at a theoretical baseline of 100 points, from which deductions are strictly applied based on:
- Test failures / assertion mismatches ($-2$ to $-5$ pts per defect category).
- Performance bottlenecks / latency tails under load ($-3$ to $-7$ pts).
- Deployment incompleteness / unprovisioned cloud targets ($-10$ to $-35$ pts).
- Synthetic or low-confidence ML model realities ($-5$ to $-10$ pts).
- Lack of third-party external certification (marked explicitly as **NOT ASSESSED** where evidence is absent).

$$\text{Composite Score} = \sum_{i=1}^{9} \left( \text{Dimension Weight}_i \times \text{Dimension Score}_i \right)$$

---

## 2. ISO/IEC 25010 Dimension Breakdown

| Dimension | Standard Characteristic | Weight | Assessed Score | Deductions & Evidence Rationale | Audited Quality Status |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **1. Functional Suitability** | Completeness, Correctness, Appropriateness | 15% | **96.0 / 100** | $-4$ pts: 4 unit test assertion drift failures in domain agent suite (`DEF-001` to `DEF-004`). 16/16 core KPIs 100% reconciled across Python, MySQL, and DAX. | **EXCELLENT** |
| **2. Performance Efficiency** | Time Behaviour, Resource Utilization, Capacity | 12% | **92.0 / 100** | $-8$ pts: Uncached analytical scans take 370–1399ms; p95 latency under 50 concurrent users reaches 845ms. Fast in-memory cache hit (18.4ms) and lightweight RAM footprint (< 1.6 GB across 6 containers). | **VERY GOOD** |
| **3. Reliability & Fault Tolerance**| Fault Tolerance, Recoverability, Availability | 12% | **88.0 / 100** | $-12$ pts: Decision Agent hit execution timeout in multi-agent marathon test (`DEF-002`); live cloud database disaster recovery drill is unperformed (script syntax verified). Circuit breaker and CSV failover verified in 0.04s. | **GOOD (Conditional)** |
| **4. Cybersecurity & Integrity** | Confidentiality, Integrity, Non-repudiation, Authenticity | 15% | **95.0 / 100** | $-5$ pts: External SOC2/ISO 27001 audit NOT ASSESSED. Internal security verification 15/15 passed: fail-closed RBAC, constant-time HMAC tokens, 19/19 parameterized SQL queries, zero hardcoded credentials. | **VERY GOOD (Internal)** |
| **5. Usability / Interaction** | Operability, User Error Protection, Aesthetics | 10% | **95.0 / 100** | $-5$ pts: React dark/light switch pending SSE telemetry integration. Unified Electric Sapphire & Slate palette across React and Streamlit; 9 specialized domain pages; contextual AI assistant. | **VERY GOOD** |
| **6. Maintainability** | Modularity, Reusability, Analyzability, Modifiability | 10% | **94.0 / 100** | $-6$ pts: Test assertions require synchronizing with Phase 07 model calibrated statuses; deprecation warning on FastAPI `Query(regex=...)`. Clean layered architecture; high type annotation coverage. | **VERY GOOD** |
| **7. Portability & Containerization**| Adaptability, Installability, Replaceability | 8% | **91.0 / 100** | $-9$ pts: Docker containerization verified across 6 containers locally; cross-platform OS paths require POSIX-compliant script execution on Windows hosts. Multi-stage Dockerfiles and environment abstraction verified. | **GOOD** |
| **8. Data Quality & Governance** | Accuracy, Completeness, Consistency, Traceability | 10% | **99.0 / 100** | $-1$ pt: Synthetic origin of data requires explicit boundary disclosure. 304,405 records preserved across 10 canonical tables; 0 foreign key orphans; single-source failover consistency. | **EXCELLENT** |
| **9. Cloud Deployment & Operations**| Cloud Provisioning, Remote Availability, Edge Security | 8% | **65.0 / 100** | $-35$ pts: Streamlit Community Cloud is **NOT DEPLOYED** (entry-point and version setup mismatch); Public Cloud VPS deployment is **PENDING LIVE PROVISIONING** (scripts and compose ready, infrastructure unpurchased). | **INCOMPLETE (Action Required)** |
| **COMPOSITE SQA SCORE** | **Weighted Multi-Factor SQA Assessment** | **100%** | **90.22 / 100** | **Grade: A (Highly Competent, Conditional on Deployment & Test Synchronization)** | **VALIDATED** |

---

## 3. Academic Grading Scale

$$\begin{array}{|c|c|l|}
\hline
\textbf{Score Range} & \textbf{Grade} & \textbf{Classification} \\
\hline
95.0 - 100.0 & \text{A+} & \text{Exceptional — Fully Certified, Cloud Commissioned, Zero Outstanding Defects} \\
\mathbf{90.0 - 94.9} & \mathbf{A} & \mathbf{\text{Highly Competent — Sound Architecture, High Test Coverage, Deployment Pending}} \\
85.0 - 89.9 & \text{B+} & \text{Proficient — Functional Core, Minor Architecture or Data Gaps} \\
80.0 - 84.9 & \text{B} & \text{Satisfactory — Adequate Prototype, Multiple Unresolved Defects} \\
< 80.0 & \text{C / F} & \text{Deficient — Major Architectural, Security, or Data Inconsistencies} \\
\hline
\end{array}$$

* **Final Score Calculation**:
  $$\begin{aligned}
  \text{Score} &= (0.15 \times 96.0) + (0.12 \times 92.0) + (0.12 \times 88.0) + (0.15 \times 95.0) \\
  &\quad + (0.10 \times 95.0) + (0.10 \times 94.0) + (0.08 \times 91.0) + (0.10 \times 99.0) + (0.08 \times 65.0) \\
  &= 14.40 + 11.04 + 10.56 + 14.25 + 9.50 + 9.40 + 7.28 + 9.90 + 5.20 \\
  &= \mathbf{90.22 / 100} \quad (\mathbf{Grade\ A})
  \end{aligned}$$

---

## 4. Specific Unsupported Claims Formally Retracted

To maintain absolute academic transparency, the following claims from draft v1 are explicitly retracted and corrected:
1. ~~"Independent Audit Certification"~~ &rarr; **Corrected**: This is an internal automated quality audit conducted via test runners and diagnostic tooling, not an external accredited third-party certification.
2. ~~"Enterprise Commissioning"~~ &rarr; **Corrected**: The platform is commissioned in a local containerized staging runtime; live enterprise cloud deployment is pending.
3. ~~"Streamlit Community Cloud Certified"~~ &rarr; **Corrected**: Streamlit Cloud status is **NOT DEPLOYED** due to configuration mismatches.
4. ~~"100% Security Compliance"~~ &rarr; **Corrected**: Internal unit security test suites (15/15) passed; external regulatory compliance (SOC2/PCI-DSS) is **NOT ASSESSED**.
5. ~~"34,980 Delivered Orders"~~ &rarr; **Corrected**: Verified canonical database contains **47,994 Delivered Orders** (96.04%) and **1,977 Cancelled Orders** (3.96%).
