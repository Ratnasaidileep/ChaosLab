# ChaosLab — Operational Runbook & Environment Setup Guide

**Document Type:** Technical Operations & Deployment Runbook  
**Project:** ChaosLab – Automated Failure Injection & Resilience Recovery Platform  
**Target Environment:** Local Workstation (Windows 11 / Linux / macOS) & Containerized Deployment  
**Document Version:** 1.0.0  
**Last Verified:** November 2, 2026  

---

## 1. System Requirements

### 1.1 Minimum Hardware Specifications
- **CPU:** Dual-Core Processor (x86_64 or ARM64)
- **RAM:** 4 GB RAM (8 GB recommended when running Docker Compose)
- **Storage:** 2 GB free disk space

### 1.2 Required Software Dependencies
| Software | Minimum Version | Verified Version | Purpose |
|---|---|---|---|
| **Python** | 3.10+ | 3.11.9 | Microservices & Control Plane runtime |
| **Node.js & npm** | Node 18+ / npm 9+ | Node v20.12.0 / npm 10.5.0 | React Vite frontend build and preview |
| **Git** | 2.30+ | 2.45+ | Version control |
| **Docker (Optional)** | 24.0+ | Docker Desktop (WSL2) | Multi-container deployment (Optional; system includes local fallback) |

---

## 2. Environment Variables & Configuration

The platform operates with sensible defaults out of the box. Custom configurations can be specified via environment variables or a `.env` file in the project root:

| Variable Name | Default Value | Description |
|---|---|---|
| `CHAOSLAB_HOST` | `0.0.0.0` | Host binding for ChaosLab Control Plane |
| `CHAOSLAB_PORT` | `8000` | Port for ChaosLab Control Plane API |
| `CHAOSLAB_DB_PATH` | `chaoslab.db` | SQLite database path for experiment history |
| `PRODUCT_SERVICE_URL` | `http://localhost:8001` | URL for Product Catalog Microservice |
| `ORDER_SERVICE_URL` | `http://localhost:8002` | URL for Order Processing Microservice |
| `HEALTH_CHECK_INTERVAL_SECONDS` | `1.5` | Background health polling interval (seconds) |
| `RECOVERY_TIMEOUT_SECONDS` | `30` | Maximum verification timeout before declaring recovery failed |
| `DETECTION_TIMEOUT_SECONDS` | `25` | Maximum window to detect active failure |
| `MAX_EXPERIMENT_DURATION_SECONDS`| `60` | Hard safety cap on chaos experiment duration |
| `MAX_CPU_LOAD_PERCENT` | `80` | Safety threshold for CPU stress injection |
| `MAX_MEMORY_MB` | `350` | Maximum memory allocation limit for stress testing |
| `ENABLE_DOCKER_CHAOS` | `true` | Attempts Docker socket connection; auto-falls back to HTTP simulation |
| `VITE_API_URL` | `http://localhost:8000` | Backend API base URL consumed by React frontend |

---

## 3. Step-by-Step Installation

### Step 3.1: Clone the Repository
```bash
git clone https://github.com/Ratnasaidileep/ChaosLab.git
cd ChaosLab
```

### Step 3.2: Configure Python Virtual Environment
```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\activate

# Install all backend and microservice dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt
pip install -r services/product_service/requirements.txt
pip install -r services/order_service/requirements.txt
```

```bash
# Linux / macOS Bash
python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r backend/requirements.txt
pip install -r services/product_service/requirements.txt
pip install -r services/order_service/requirements.txt
```

### Step 3.3: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## 4. Starting the Platform

### Method A: Single-Command Cross-Platform Launcher (Recommended)
This launcher spawns all 4 services (Product Service on 8001, Order Service on 8002, Backend on 8000, and Frontend on 3000) concurrently using managed subprocesses and handles clean shutdown on `Ctrl+C`:

```powershell
# Windows
.\.venv\Scripts\python.exe scripts/run_all.py
```

```bash
# Linux / macOS
python3 scripts/run_all.py
```

### Method B: Windows PowerShell Launcher
```powershell
.\scripts\run_local.ps1
```

### Method C: Windows Batch Launcher
```cmd
start.bat
```

### Method D: Docker Compose (When Docker Desktop is installed)
```bash
docker compose up -d --build
```

---

## 5. Verified Access URLs

Once started, the following services will be available:

| Service / Interface | URL | Description |
|---|---|---|
| **ChaosLab Dashboard** | [http://localhost:3000](http://localhost:3000) | Primary web user interface |
| **Control Plane API Swagger** | [http://localhost:8000/docs](http://localhost:8000/docs) | Interactive OpenAPI documentation |
| **Control Plane Health** | [http://localhost:8000/health](http://localhost:8000/health) | Control Plane status and active experiment |
| **Product Service API** | [http://localhost:8001/products](http://localhost:8001/products) | Product catalog endpoint |
| **Order Service API** | [http://localhost:8002/orders](http://localhost:8002/orders) | Order placement and listing endpoint |
| **Prometheus Scraper** | [http://localhost:9090](http://localhost:9090) | Telemetry query browser (Docker mode) |
| **Grafana Dashboard** | [http://localhost:3001](http://localhost:3001) | Pre-configured dashboard (Docker mode) |

---

## 6. Running Automated Tests

### 6.1 Run Pytest Unit & Integration Suite
Executes all 29 automated tests across microservices, validation, lifecycle, and math calculators:

```powershell
# Windows
.\.venv\Scripts\python.exe -m pytest -v
```

```bash
# Linux / macOS
pytest -v
```

### 6.2 Run Frontend Quality & Build Checks
Validates TypeScript compilation and generates optimized production bundle:

```bash
cd frontend
npm run test    # Runs tsc --noEmit
npm run build   # Compiles production bundle to frontend/dist/
cd ..
```

### 6.3 Run Live System Acceptance Test Suite
Runs the 10-point end-to-end integration test against active running services:

```powershell
.\.venv\Scripts\python.exe scripts/test_live_system.py
```

---

## 7. How to Execute a Controlled Chaos Experiment

### Via Dashboard UI:
1. Open [http://localhost:3000](http://localhost:3000) in your browser.
2. Click on the **"Failure Injection"** tab in the top navigation bar.
3. Select an experiment card (e.g., **"Service Dependency Failure"**).
4. In the configuration modal:
   - Select Target Service: `order-service`
   - Set Duration: `15` seconds
   - Check the mandatory confirmation checkbox: *"I confirm intentional failure injection for resilience testing"*.
5. Click **"Inject Failure"**.
6. Switch to the **"Overview"** tab to view the live 4-step execution stepper (Injected $\rightarrow$ Detected $\rightarrow$ Recovering $\rightarrow$ Verified).
7. Once verified, visit the **"Experiment History"** tab to view the recorded detection time, recovery duration, and downtime.

### Via REST API (`curl`):
```bash
curl -X POST http://localhost:8000/api/experiments \
  -H "Content-Type: application/json" \
  -d '{
    "type": "dependency_failure",
    "target_service": "order-service",
    "duration_seconds": 10,
    "confirm_destruction": true
  }'
```

### Cancelling an Active Experiment Mid-Run:
- Click the red **"Cancel Experiment"** button on the dashboard banner, OR:
```bash
curl -X POST http://localhost:8000/api/experiments/{EXPERIMENT_ID}/cancel
```

---

## 8. Shutdown & Cleanup Procedures

### To Stop Local Development Processes:
- Press `Ctrl + C` in the terminal running `scripts/run_all.py` or `run_local.ps1`.
- Alternatively, run the cleanup batch script:
  ```cmd
  stop.bat
  ```

### To Force-Kill Any Lingering Zombie Processes on Windows:
```powershell
Get-Process | Where-Object { $_.ProcessName -match "python|uvicorn|node" } | Stop-Process -Force
```

### To Reset SQLite Databases to Fresh Seed State:
```powershell
Remove-Item -Force products.db, orders.db, chaoslab.db -ErrorAction SilentlyContinue
```
*(New databases with seed data are automatically recreated upon the next application startup).*

---

## 9. Troubleshooting & FAQ

### Issue 1: Port Collision (`[Errno 10048] address already in use`)
- **Cause:** A previous uvicorn or node process was not terminated cleanly.
- **Solution:** Execute:
  ```powershell
  Get-NetTCPConnection -LocalPort 8000, 8001, 8002, 3000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
  ```

### Issue 2: Windows AppStore Python Virtualization Fault
- **Cause:** Running `python` without activating the virtual environment invokes the restricted WindowsApps executable.
- **Solution:** Always run via the virtual environment path: `.\.venv\Scripts\python.exe`.

### Issue 3: Docker Unavailable Warning
- **Log Message:** `"Docker socket not found / Docker not available, falling back to HTTP simulation"`
- **Explanation:** This is an expected, verified fallback behavior when Docker Desktop is not installed on the host. The platform continues running in High-Fidelity Simulation Mode without loss of functionality.
