# NovaNest – Manual Verification & Professor Evaluation Guide

**Target Audience**: College Evaluator, Viva Examiner, Project Student  
**Project**: NovaNest – AI-Powered Food Delivery Analytics and Decision Intelligence Platform  
**Preparation Time**: ~5 Minutes  

---

## 1. Environment Pre-Flight Check

Open PowerShell in the project root (`NovaNest-main/`) and run:
```powershell
# 1. Verify MySQL 8.0 is running locally
Test-NetConnection -ComputerName localhost -Port 3306

# 2. Verify Python environment
python --version
```
*Expected: Port 3306 responds `TcpTestSucceeded: True`. Python 3.10+ is available.*

---

## 2. Step-by-Step System Launch Protocol

### Step 1: Start the FastAPI Backend
Open **Terminal 1**:
```powershell
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```
- Open browser to: `http://localhost:8000/docs`
- Verify OpenAPI documentation loads. Test endpoint `GET /api/kpis/overview`.
- Confirm response contains `delivered_food_gmv: 46590125.0` and `net_revenue: 46425992.0`.

### Step 2: Launch the Modern React SPA
Open **Terminal 2**:
```powershell
cd frontend
npm install
npm run dev
```
- Open browser to: `http://localhost:5173`
- Check Executive Overview: Verify 16 KPI cards render with proper formatting (₹4.66 Cr GMV, 23.59% Margin).
- Open **Ask NovaNest AI Copilot**:
  - Type: *"What is our total revenue and cancellation rate?"*
  - Confirm response displays:
    - Net Revenue: ₹46,425,992.00
    - Cancellation Rate: 3.96%
    - Verified Grounding shield badge.

### Step 3: Launch the Streamlit Analytics Workstation
Open **Terminal 3**:
```powershell
streamlit run streamlit_app/app.py
```
- Open browser to: `http://localhost:8501`
- Navigate to **08_Decision_Simulator**:
  - Drag the Commission Rate slider by +2%.
  - Verify projected revenue and sensitivity elasticity charts update instantly.

### Step 4: Open Power BI Desktop
1. Open Microsoft Power BI Desktop.
2. Load `powerbi/novanest_intelligence.pbix`.
3. Verify Star Schema relationships in Model View.
4. Click on the Executive Dashboard report page and verify KPI card values align 100% with the React and Streamlit apps.

---

## 3. Recommended Viva / Q&A Talking Points

1. **How do you ensure AI domain agents don't hallucinate numbers?**
   - *Answer*: NovaNest uses a dedicated `OutputVerifier` that extracts numbers via regex from the LLM narrative and cross-checks them against a certified fact registry and SQL provenance. Any ungrounded claim is immediately rejected (`UNSUPPORTED_NUMERIC_CLAIM`).
2. **What is the ₹50 minimum order floor?**
   - *Answer*: Orders have a floor: `final_amount = max(50, order_amount + delivery_fee - discount_amount)`. Exactly 67 orders were clamped, contributing a ₹911.00 calculated adjustment without mutating original customer transaction amounts.
3. **Why is the Churn ML model tagged LOW_EMPIRICAL?**
   - *Answer*: In food delivery, transactional data has high class imbalance (8.54% churn rate). Rather than fabricating 99% accuracy, NovaNest honestly assigns ROC-AUC 0.5062 with a mandatory caveat, requiring RFM behavioral confirmation before spending retention budgets.
