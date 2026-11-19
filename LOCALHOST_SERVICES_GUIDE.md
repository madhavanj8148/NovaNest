# NOVANEST – COMPLETE LOCALHOST SERVICES & ENGINE STARTUP GUIDE

This document serves as the master operational guide for all **Localhost Ports, Microservices, and Engines** powering the NovaNest platform. It contains exact port assignments, URLs, startup sequences, health verification commands, and troubleshooting instructions.

---

## 1. MASTER LOCALHOST PORT DIRECTORY

| Port | Service Name | Protocol | Localhost URL | Process / Framework | Purpose |
|---|---|---|---|---|---|
| **3306** | **MySQL Database** | TCP / MySQL | `mysql://localhost:3306/novanest_db` | MySQL Server 8.0 | Canonical Data Warehouse (304,405 records across 10 relational tables) |
| **8001** | **FastAPI Backend** | HTTP / REST | [http://localhost:8001](http://localhost:8001)<br>Swagger: [http://localhost:8001/docs](http://localhost:8001/docs) | Python 3.11 / Uvicorn | Analytics Engine, L1 LRU Caching, 5 Multi-Agent AI Domains & ML Registry |
| **5173** | **React Frontend** | HTTP | [http://localhost:5173](http://localhost:5173) | Node.js / Vite / React 18 | Executive Dashboard (10 Analytical Views, Tailwind CSS, Recharts) |
| **8502** | **Streamlit Lab** | HTTP | [http://localhost:8502](http://localhost:8502) | Python 3.11 / Streamlit | Operations Intelligence & Exploratory Data Science Lab |
| **3001** | **Grafana** | HTTP | [http://localhost:3001](http://localhost:3001) | Docker / Grafana | System Observability, API Latency & Metrics Dashboards |
| **9090** | **Prometheus** | HTTP | [http://localhost:9090](http://localhost:9090) | Docker / Prometheus | Time-Series Metrics Scraper & System Health Monitoring |
| **80** | **Nginx Edge Proxy** | HTTP | [http://localhost](http://localhost) | Docker / Nginx 1.27 | Production Edge Ingress Proxy, SSL Termination & Rate Limiting |

---

## 2. SYSTEM ARCHITECTURE & INTER-PORT COMMUNICATION

```
                         +-----------------------------------+
                         |      Browser / Client User        |
                         +-----------------------------------+
                                   |                 |
                   (Port 5173)     |                 |  (Port 8502)
                                   v                 v
                       +-------------------+   +--------------------+
                       |  React 18 (Vite)  |   | Python Streamlit   |
                       |  Executive UI     |   | Operations Lab     |
                       +-------------------+   +--------------------+
                                   |                 |
                   REST API Calls  |                 | Direct Data / API
                   (Port 8001)     v                 v
                       +------------------------------------+
                       |     FastAPI Backend (Uvicorn)      |
                       |  - L1 LRU Cache (Sub-2ms Latency)  |
                       |  - Master Orchestrator (5 Agents)  |
                       |  - Model Registry v3 (5 ML Models) |
                       |  - AST SQL Security Sanitizer      |
                       +------------------------------------+
                                         |
                         SQL Connection  |  (Port 3306)
                                         v
                       +------------------------------------+
                       |     MySQL 8.0 Data Warehouse       |
                       |  Database: novanest_db             |
                       |  10 Tables | 304,405 Rows          |
                       +------------------------------------+
```

---

## 3. FULL STEP-BY-STEP STARTUP PROCESS FOR ALL ENGINES

To start the complete NovaNest platform from scratch on Windows, open your command prompt or PowerShell and follow these steps in order:

### STEP 1: Verify & Start MySQL Database Engine (Port 3306)
*Ensure MySQL Server 8.0 is active and accepting connections.*

1. **Check if MySQL is already running:**
   ```powershell
   Get-Service -Name "MySQL*"
   ```
2. **If stopped, start the MySQL Windows service:**
   ```powershell
   net start MySQL80
   ```
3. **Database Connection Details:**
   - **Host:** `127.0.0.1` (or `localhost`)
   - **Port:** `3306`
   - **Database Name:** `novanest_db`
   - **Default User:** `root`
   - **Status Check:** Run `python -c "import socket; print(socket.socket().connect_ex(('127.0.0.1', 3306)) == 0)"` (returns `True` when listening).

---

### STEP 2: Start the FastAPI Core Microservice & AI Engine (Port 8001)
*Powers all analytical REST APIs, multi-agent AI copilot, and machine learning models.*

1. **Open a new terminal window** at the project root:
   ```powershell
   cd c:\Users\madha\OneDrive\Documents\NovaNest-main
   ```
2. **Activate your Python environment** (if using a virtual environment):
   ```powershell
   # If using venv:
   .\.venv\Scripts\Activate.ps1
   ```
3. **Launch Uvicorn server on port 8001:**
   ```powershell
   uvicorn api.main:app --host 127.0.0.1 --port 8001 --reload
   ```
4. **How to Verify it is Running:**
   - Open your browser to the Interactive Swagger API Docs: [http://localhost:8001/docs](http://localhost:8001/docs)
   - Or test the automated Health Check endpoint: [http://localhost:8001/api/v1/health](http://localhost:8001/api/v1/health)

---

### STEP 3: Start the React 18 Executive Frontend Engine (Port 5173)
*The modern Single-Page Application dashboard for executive decision intelligence.*

1. **Open a new terminal window** and navigate to the `frontend/` directory:
   ```powershell
   cd c:\Users\madha\OneDrive\Documents\NovaNest-main\frontend
   ```
2. **Install frontend dependencies** (only required on first setup):
   ```powershell
   npm install
   ```
3. **Start the Vite development server:**
   ```powershell
   npm run dev
   ```
4. **How to Verify it is Running:**
   - Open your browser to: [http://localhost:5173](http://localhost:5173)
   - You should see the NovaNest Executive Overview dashboard with live KPI gauges, Customer 360, Restaurant Intel, and AI Copilot.

---

### STEP 4: Start the Streamlit Operations Lab (Port 8502)
*Companion data science laboratory for deep operational drill-downs and model inspection.*

1. **Open a new terminal window** at the project root:
   ```powershell
   cd c:\Users\madha\OneDrive\Documents\NovaNest-main
   ```
2. **Run the Streamlit application pinned to port 8502:**
   ```powershell
   streamlit run streamlit_app/app.py --server.port 8502
   ```
3. **How to Verify it is Running:**
   - Open your browser to: [http://localhost:8502](http://localhost:8502)
   - You should see the interactive Streamlit analytics workspace with live filtering and diagnostic plots.

---

### STEP 5: Start Dockerized Observability Stack (Optional: Ports 3001 & 9090)
*For Prometheus metrics scraping and Grafana system health dashboards.*

1. **Launch containers via Docker Compose:**
   ```powershell
   cd c:\Users\madha\OneDrive\Documents\NovaNest-main
   docker-compose up -d
   ```
2. **Access Observability Portals:**
   - **Grafana Dashboards:** [http://localhost:3001](http://localhost:3001) (Default login: `admin` / `admin`)
   - **Prometheus Metrics:** [http://localhost:9090](http://localhost:9090)

---

## 4. ONE-CLICK INSTANT STARTUP SCRIPTS

To avoid opening 3 separate command prompts manually every time, you can use the automated startup scripts:

### Option A: Windows Batch Launcher (`start_novanest.bat`)
Double-click or run from terminal:
```cmd
.\start_novanest.bat
```
*This automatically spawns three distinct terminal windows labeled:*
- `[NovaNest - Backend API (:8001)]`
- `[NovaNest - React Frontend (:5173)]`
- `[NovaNest - Streamlit Lab (:8502)]`

### Option B: Windows Batch Shutdown (`stop_novanest.bat`)
Double-click or run from terminal to stop all development servers cleanly:
```cmd
.\stop_novanest.bat
```

---

## 5. TROUBLESHOOTING & PORT CONFLICT RESOLUTION

If any port fails to start because another process is holding it, use these commands to identify and free the port:

### 1. Identify which Process ID (PID) is using a port:
```powershell
# Check for Port 8001 (FastAPI):
netstat -ano | findstr :8001

# Check for Port 5173 (React):
netstat -ano | findstr :5173

# Check for Port 8502 (Streamlit):
netstat -ano | findstr :8502
```

### 2. Kill the conflicting process by its PID:
```powershell
# Replace <PID> with the actual number from the last column of netstat output:
taskkill /F /PID <PID>
```

### 3. Check all NovaNest listening ports at once:
```powershell
python -c "
import socket
ports = [(3306, 'MySQL'), (5173, 'React'), (8001, 'FastAPI'), (8502, 'Streamlit'), (3001, 'Grafana'), (9090, 'Prometheus')]
for p, name in ports:
    s = socket.socket()
    s.settimeout(0.3)
    active = (s.connect_ex(('127.0.0.1', p)) == 0)
    print(f'Port {p:<5} : {\"ACTIVE (RUNNING)\" if active else \"NOT LISTENING\"} [{name}]')
    s.close()
"
```

---

## 6. SUMMARY OF DEFAULT CREDENTIALS & TOKENS

- **MySQL Database:** User `root` | Host `localhost:3306` | DB `novanest_db`
- **FastAPI Token Auth:** Bearer JWT tokens configured in `api/security.py` (Default Dev Token: `novanest-dev-token-2026`)
- **Grafana Portal:** User `admin` | Password `admin` (Port 3001)
