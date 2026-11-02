# ChaosLab — Visual Artifact & Screenshot Inventory

**Document Type:** Formal Visual Documentation & Screenshot Catalogue  
**Project:** ChaosLab – Automated Failure Injection & Resilience Recovery Platform  
**Date:** November 2, 2026  

---

## 1. Inventory Summary

This catalogue details the visual evidence collected for the Bachelor of Engineering project report. It provides exact file paths, detailed technical descriptions, verified UI elements, and formal academic figure captions for every available and proposed screenshot.

---

## 2. Available Screenshots (Verified in Workspace)

### Screenshot 1: ChaosLab Main Dashboard Overview
- **Storage Location (Brain Artifact):**  
  `C:\Users\SaiDi\.gemini\antigravity\brain\6426f320-6318-416d-b53f-fcdc634e0b02\.user_uploaded\media_1793447065196_4406e3b1.png`
- **File Format:** Portable Network Graphics (PNG)
- **Image Resolution:** $1348 \times 586$ pixels
- **File Size:** $108,248$ bytes (~105.7 KB)
- **Visual Description:**
  - **Top Navigation Bar:** Dark navy background with cyan pulse brand logo, "ChaosLab DEVOPS PLATFORM", active "Overview" tab, "Service Health", "Failure Injection", "Experiment History", and "Recovery Analysis" tabs. Includes an emerald "SYSTEM RESILIENT" badge and links to API Docs, Prometheus, and Grafana.
  - **Hero Headline Banner:** Identifies "Application Under Test: Online Shopping System (Microservices architecture resilience verification suite)" with "Launch Experiment" and "View History" action buttons.
  - **First Row Metric Cards:**
    - *Overall System:* `HEALTHY` (Optimal badge) &bull; "Real-time multi-service status".
    - *Product Service:* `HEALTHY` (Healthy badge) &bull; Latency: `734ms`.
    - *Order Service:* `HEALTHY` (Healthy badge) &bull; Latency: `1531ms`.
    - *Avg Recovery Time:* `1.54s` (MTTR badge) &bull; Avg Downtime: `8.98s`.
  - **Second Row Metric Cards:**
    - *Total Experiments:* `23` &bull; "Intentional failure injections run".
    - *Successful Recoveries:* `15` (65.2% Rate badge) &bull; "Services verified healthy after chaos".
    - *Failed Recoveries:* `0` &bull; "Exceeded timeout or unrecovered".
- **Proposed College Report Caption:**
  > **Figure 6.1:** *ChaosLab Main Engineering Dashboard Overview displaying overall system resilience status, real-time microservice latency telemetry, and aggregate Mean Time to Recovery (MTTR) metrics.*

---

## 3. Recommended Screenshots for Final College Report

To provide complete visual coverage across all chapters of the project report, the following screenshots should be captured from the running application:

### Screenshot 2: Active Chaos Experiment Running Banner & Stepper
- **Target URL / View:** `http://localhost:3000` (Overview tab during active experiment)
- **Trigger:** Inject any experiment (e.g. CPU Stress on `product-service`).
- **Elements to Capture:**
  - Rose-tinted pulsing alert banner with active experiment name and ID.
  - 4-step execution stepper:
    - `1. Injected` (Cyan check)
    - `2. Detected` (Cyan check with detection latency in ms)
    - `3. Recovering` (State transition)
    - `4. Verified` (Health confirmation)
  - Red "Cancel Experiment" operator intervention button.
- **Proposed Caption:**
  > **Figure 6.2:** *Real-time execution stepper and active experiment banner illustrating sub-second automated failure detection and operator cancellation controls.*

### Screenshot 3: Failure Injection Configuration Modal
- **Target URL / View:** `http://localhost:3000` (Failure Injection tab $\rightarrow$ "Configure & Inject")
- **Elements to Capture:**
  - Bounded parameter sliders: Duration (5–60s), CPU Load (10–80%), Memory (50–350MB), Network Delay (100–3000ms).
  - Target service dropdown (`product-service` / `order-service`).
  - Mandatory safety confirmation checkbox ("I acknowledge this will intentionally degrade service health").
- **Proposed Caption:**
  > **Figure 6.3:** *Controlled failure injection modal enforcing parameter boundaries and mandatory destructive action confirmation.*

### Screenshot 4: Experiment History Audit Log Table
- **Target URL / View:** `http://localhost:3000` (Experiment History tab)
- **Elements to Capture:**
  - Full audit table showing Experiment ID, Type, Target Service, Start Time, Detection Time, Recovery Duration, Total Downtime, and Status Badge (`Recovered`, `Cancelled`, `Failed`).
  - Search bar and category dropdown filters.
- **Proposed Caption:**
  > **Figure 6.4:** *Persistent experiment audit log table with calculated downtime metrics, status badges, and multi-parameter filters.*

### Screenshot 5: Experiment Execution Detail Modal
- **Target URL / View:** `http://localhost:3000` (Experiment History tab $\rightarrow$ Click eye icon on any row)
- **Elements to Capture:**
  - JSON parameters block.
  - High-precision timestamp breakdown ($T_{\text{failure}}$, $T_{\text{detection}}$, $T_{\text{recovery\_start}}$, $T_{\text{recovery}}$).
  - Chronological event log trace.
- **Proposed Caption:**
  > **Figure 6.5:** *Detailed experiment execution modal displaying exact ISO-8601 timestamps, calculated downtime breakdown, and raw event traces.*

### Screenshot 6: Recovery Analysis & MTTR Comparison Graphs
- **Target URL / View:** `http://localhost:3000` (Recovery Analysis tab)
- **Elements to Capture:**
  - Top KPI cards: Recovery Success Rate, Avg Detection Time, Avg Recovery Duration, Avg Total Downtime.
  - Visual horizontal bar charts comparing MTTR across all 5 failure types.
- **Proposed Caption:**
  > **Figure 6.6:** *Comparative recovery analysis graph illustrating Mean Time to Recovery (MTTR) across different failure injection modes.*

### Screenshot 7: Microservices Health Section
- **Target URL / View:** `http://localhost:3000` (Service Health tab)
- **Elements to Capture:**
  - Microservice detail cards for Product Service and Order Service.
  - Real-time HTTP status, response latency, last failure timestamp, and "Verify Health" action button.
- **Proposed Caption:**
  > **Figure 6.7:** *Microservice health inspection view showing live latency metrics, health status, and on-demand verification triggers.*

### Screenshot 8: FastAPI Swagger Interactive Documentation
- **Target URL / View:** `http://localhost:8000/docs`
- **Elements to Capture:**
  - FastAPI OpenAPI interactive documentation displaying `/api/dashboard`, `/api/services`, and `/api/experiments` endpoint schemas.
- **Proposed Caption:**
  > **Figure 6.8:** *FastAPI OpenAPI interactive Swagger documentation for the ChaosLab Control Plane.*

### Screenshot 9: Automated Pytest Suite Execution
- **Target View:** Windows Terminal / PowerShell
- **Command:** `.\.venv\Scripts\python.exe -m pytest -v`
- **Elements to Capture:**
  - Green passing test summary: `29 passed in 4.55s`.
- **Proposed Caption:**
  > **Figure 6.9:** *Automated Pytest test execution demonstrating 100% pass rate across all microservice unit tests, API integration tests, and mathematical calculators.*

---

## 4. Screenshot Capture Procedure for Candidate

To capture any of the proposed figures above for your report document:
1. Ensure the platform is running:
   ```powershell
   cd c:\Users\SaiDi\chaosLab
   .\.venv\Scripts\python.exe scripts\run_all.py
   ```
2. Open Google Chrome or Microsoft Edge and navigate to `http://localhost:3000`.
3. Use the Windows Snipping Tool (`Windows Key + Shift + S`) to capture the relevant section.
4. Save the screenshot in a folder named `docs/screenshots/` (e.g. `docs/screenshots/figure_6_2_active_stepper.png`).
5. Insert the image into your Microsoft Word or LaTeX report document referencing the corresponding figure caption above.
