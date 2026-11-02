# ChaosLab — Complete Technical Project Facts & Reference Manual

**Document Type:** Comprehensive Technical Project Reference & Academic Fact Sheet  
**Project Title:** ChaosLab – Automated Failure Injection & Resilience Recovery Platform  
**Target Academic Degree:** Bachelor of Engineering (B.E. / B.Tech) in Computer Science & Engineering / Information Science / DevOps & Cloud Computing  
**Repository:** [https://github.com/Ratnasaidileep/ChaosLab](https://github.com/Ratnasaidileep/ChaosLab)  
**System Architecture:** Microservice Control Plane & Distributed Application Under Test (AUT)  
**Document Version:** 1.0.0  
**Audit Verification Date:** November 2, 2026  

---

## 1. Project Identification and Academic Synopsis

### 1.1 Project Title
**ChaosLab: Automated Failure Injection & Resilience Recovery Platform**

### 1.2 Academic Abstract
In modern cloud-native architectures, distributed microservice applications are subject to inevitable infrastructure failures, network partitions, resource exhaustion, and cascading outages. Traditional software testing paradigms (unit, integration, and manual end-to-end testing) focus on deterministic code paths and functional correctness but fail to validate how applications behave under turbulent runtime conditions. 

**ChaosLab** is a specialized DevOps resilience engineering platform that implements the Principles of Chaos Engineering on a distributed microservices application—an **Online Shopping System** consisting of a Product Catalog Service and an Order Processing Service. The ChaosLab Control Plane allows engineers to configure and execute five bounded, controlled failure experiments: container termination, CPU stress, memory pressure, downstream dependency outages, and artificial network latency. 

The platform features an active background health monitoring engine that detects failures sub-second (measured Mean Time to Detect of **1.05 seconds**), orchestrates automatic recovery mechanisms, actively verifies health restoration before declaring recovery (measured Mean Time to Recover of **1.68 seconds**), and persists an immutable audit trail in an SQLite database. Resilience telemetry, request throughput, and latency percentiles are exposed via Prometheus and visualized through an engineering dashboard built in React 18, TypeScript, and Tailwind CSS. The system provides empirical proof of resilience, self-healing capability, and quantitative Downtime and MTTR metrics.

### 1.3 Academic Keywords
`Chaos Engineering`, `Site Reliability Engineering (SRE)`, `DevOps Automation`, `Failure Injection`, `Automated Self-Healing`, `Mean Time to Recover (MTTR)`, `Mean Time to Detect (MTTD)`, `Microservices Resilience`, `FastAPI`, `React`, `Prometheus Telemetry`, `Docker Compose`, `Jenkins CI/CD`.

---

## 2. Technology Stack & Specifications

| Layer / Subsystem | Technology | Version | Purpose & Implementation Details |
|---|---|---|---|
| **Frontend Framework** | React | 18.3.1 | Single-page engineering dashboard with component-driven state architecture. |
| **Frontend Language** | TypeScript | 5.6.3 | Strict static type definitions for dashboard summaries, service telemetry, and experiment payloads. |
| **Build Tool & Bundler** | Vite | 5.4.10 | High-performance ES module bundler producing optimized production artifacts. |
| **UI Styling** | Tailwind CSS | 3.4.14 | Dark navy theme (`#0B1120`), cyan/emerald/rose status indicators, responsive flex/grid layouts. |
| **Icons Library** | Lucide React | 0.460.0 | High-contrast technical icons (ShieldCheck, Cpu, Database, Unplug, WifiOff, etc.). |
| **Control Plane API** | FastAPI (Python) | 0.110.0+ | Asynchronous RESTful orchestrator, state machine controller, and metrics endpoint. |
| **Application Under Test** | Python / FastAPI | 3.11 / 0.110.0+ | Product Service (port 8001) and Order Service (port 8002). |
| **Data Validation** | Pydantic | 2.6.4+ | Schema enforcement, parameter bounds validation, destructive confirmation checks. |
| **Persistence Engine** | SQLite3 | 3.x (Built-in) | Lightweight transactional persistence for experiments, service snapshots, products, and orders. |
| **System Telemetry** | Psutil | 5.9.8+ | Native OS CPU percentage, memory RSS inspection, and thread management. |
| **HTTP Client** | HTTPX | 0.27.0+ | Asynchronous non-blocking HTTP client for health probes, chaos hooks, and RPC calls. |
| **Metrics Exposition** | Prometheus Client | 0.20.0+ | Counter, Gauge, and Histogram metrics exposed at `/metrics` across all three services. |
| **Metrics Collector** | Prometheus | v2.50.1 | Time-series database scraping service metrics every 2 seconds. |
| **Metrics Visualizer** | Grafana | 10.3.3 | Observability dashboard provisioning pre-configured panels for health, latency, and chaos state. |
| **Containerization** | Docker & Docker Compose | Compose Spec 3.8 | Multi-container isolation, healthchecks, memory/CPU bounds, and internal bridge networking. |
| **CI/CD Automation** | Jenkins Pipeline | Declarative | Multi-stage pipeline automating dependencies, unit tests, frontend build, and resilience verification. |
| **Testing Framework** | Pytest & Pytest-Asyncio | 9.2.0 / 0.23.5+ | Automated unit, contract, lifecycle, and mathematical verification test suites. |

---

## 3. Architecture & Real Execution Workflow

### 3.1 System Architecture Diagram

```
+-------------------------------------------------------------------------------------------------+
|                                    USER INTERACTION LAYER                                       |
|                                                                                                 |
|   +-----------------------------------------------------------------------------------------+   |
|   |                       ChaosLab React 18 Dashboard (Port 3000)                           |   |
|   |  - Overview Section (System Health, KPIs, Live Experiment Progress Banner & Cancel)     |   |
|   |  - Service Health Section (Per-service latency, HTTP status, On-demand health verify)   |   |
|   |  - Failure Injection Section (Experiment Cards, Bounded Parameter Modal, Confirm Check) |   |
|   |  - Experiment History Section (Search, Multi-Filter, Execution Detail Modal)            |   |
|   |  - Recovery Analysis Section (Comparative Bar Charts, MTTR Trends, Empty-state View)    |   |
|   +--------------------------------------------+--------------------------------------------+   |
+------------------------------------------------|------------------------------------------------+
                                                 | HTTP REST API (JSON)
                                                 v
+-------------------------------------------------------------------------------------------------+
|                                 CONTROL PLANE ORCHESTRATOR                                      |
|                                                                                                 |
|   +-----------------------------------------------------------------------------------------+   |
|   |                       ChaosLab Backend (FastAPI - Port 8000)                            |   |
|   |                                                                                         |   |
|   |  [API Routers]                                                                          |   |
|   |   - /api/dashboard/summary & /api/dashboard/analysis                                    |   |
|   |   - /api/services, /api/services/{id}/health, /api/services/{id}/verify                 |   |
|   |   - /api/experiments (POST trigger, GET list, GET detail, POST cancel)                  |   |
|   |                                                                                         |   |
|   |  [ChaosEngine State Machine]                                                            |   |
|   |   - Asynchronous Lifecycle: PENDING -> INJECTING -> RUNNING -> DETECTED ->              |   |
|   |                             RECOVERING -> VERIFYING -> RECOVERED / FAILED               |   |
|   |   - Active Background Health Poller (_background_health_poller: 1.5s interval)          |   |
|   |   - Metric Math Engine (calculate_metrics: MTTD, MTTR, Downtime)                        |   |
|   |                                                                                         |   |
|   |  [Safe Injectors & Controllers]                                                         |   |
|   |   - SafeDockerController (Strict container name allowlist, docker.sock binding)         |   |
|   |   - HTTP Chaos Simulation Fallback (/_chaos/inject, /_chaos/recover, /_chaos/status)    |   |
|   |                                                                                         |   |
|   |  [Persistence Engine]                                                                   |   |
|   |   - SQLite (chaoslab.db): experiments table & service_snapshots table                   |   |
|   +----------------------------------+----------------------------------+-------------------+   |
+--------------------------------------|----------------------------------|-----------------------+
                                       |                                  |
              HTTP Chaos & Health Probe|                                  |HTTP Chaos & Health Probe
                                       v                                  v
+------------------------------------------------------+  +---------------------------------------+
|          PRODUCT CATALOG MICROSERVICE                |  |       ORDER PROCESSING MICROSERVICE   |
|             (FastAPI - Port 8001)                    |  |           (FastAPI - Port 8002)       |
|                                                      |  |                                       |
| - REST API: /products, /products/{id}                |  | - REST API: /orders, /orders/{id}     |
| - Stock RPC: /products/{id}/reserve & release        |  | - Upstream Dependency Monitor         |
| - Database: SQLite (products.db - 6 initial items)   |  |   (Checks Product Service Health)     |
| - Stress Workers: Psutil CPU & Memory Buffers        |  | - Database: SQLite (orders.db)        |
| - Chaos Middleware: Latency sleep & Outage 503       |  | - Downstream RPC Stock Reservation    |
| - Prometheus /metrics (Latency, Requests, Status)    |  | - Prometheus /metrics                 |
+------------------------------------------------------+  +---------------------------------------+
                                       ^                                  |
                                       |------- Synchronous Stock RPC ----|
```

### 3.2 End-to-End Resilience Verification Workflow

```
[ Step 1: Initial Baseline ]
  User loads dashboard. Control Plane polls Product & Order services.
  Both return HTTP 200 {"status": "healthy"}. System Health Gauge = 2 (Healthy).

[ Step 2: Experiment Configuration & Safety Check ]
  Operator selects experiment (e.g. Dependency Failure on order-service).
  Modal enforces safety bounds: Duration <= 60s, CPU <= 80%, Memory <= 350MB.
  User must check explicit box: confirm_destruction = True.

[ Step 3: Injection Dispatch ]
  Dashboard POSTs to /api/experiments.
  Control plane checks concurrency guard (rejects if active experiment exists with 409).
  ChaosEngine transitions state: PENDING -> INJECTING -> RUNNING.
  Injector triggers failure on target service via Docker API or HTTP simulation hook.
  Timestamp T_fail is recorded.

[ Step 4: Sub-Second Automated Failure Detection ]
  ChaosEngine active monitor probes target /health endpoint every 500ms.
  Service returns HTTP 503 or degraded status payload.
  Timestamp T_det is recorded.
  State transitions to DETECTED.
  Detection Time is calculated: T_det - T_fail (typically 900ms - 1200ms).

[ Step 5: Duration Hold & Operator Cancellation Check ]
  Failure is held for requested duration (e.g. 15s).
  If operator clicks "Cancel Experiment", cancel event is set immediately.

[ Step 6: Automated Self-Healing Trigger ]
  Duration expires or cancel triggered.
  ChaosEngine initiates recovery: triggers Docker container start or POST /_chaos/recover.
  Timestamp T_rec_start is recorded. State transitions to RECOVERING.

[ Step 7: Independent Health Verification ]
  State transitions to VERIFYING.
  Recovery controller actively polls /health every 1.0s (timeout: 30s).
  Only when target service responds HTTP 200 {"status": "healthy"} is recovery confirmed.
  Timestamp T_rec is recorded. State transitions to RECOVERED.

[ Step 8: Telemetry Calculation & Audit Trail Persistence ]
  Detection Time = (T_det - T_fail) ms
  Recovery Duration = (T_rec - T_rec_start) ms
  Total Downtime = (T_rec - T_fail) ms
  All timestamps, logs, and calculated metrics are written to SQLite (chaoslab.db).
  Dashboard automatically refreshes and displays updated MTTR charts.
```

---

## 4. Application Under Test (Online Shopping System)

To avoid abstract or synthetic test loops, ChaosLab tests a real, stateful e-commerce microservices implementation:

### 4.1 Product Catalog Service (`services/product_service/`)
- **Port:** `8001`
- **Data Store:** SQLite (`products.db`) with `products` table:
  - `id` (INTEGER PRIMARY KEY)
  - `name` (TEXT)
  - `description` (TEXT)
  - `price` (REAL)
  - `stock` (INTEGER)
  - `category` (TEXT)
- **Initial Inventory:** 6 seed products:
  1. Laptop Pro 15 (Stock: 25, Price: $1,299.99)
  2. Wireless Noise-Cancelling Headphones (Stock: 50, Price: $199.99)
  3. 4K Ultra-HD Monitor (Stock: 30, Price: $349.99)
  4. Mechanical Gaming Keyboard (Stock: 75, Price: $89.99)
  5. Ergonomic Office Mouse (Stock: 100, Price: $49.99)
  6. USB-C Docking Station (Stock: 40, Price: $129.99)
- **Business Operations:**
  - `GET /products`: Returns list of all products.
  - `GET /products/{id}`: Returns details of a single product.
  - `POST /products/{id}/reserve`: Atomically checks stock availability and decrements stock.
  - `POST /products/{id}/release`: Restores stock when an order is cancelled or aborted.

### 4.2 Order Processing Service (`services/order_service/`)
- **Port:** `8002`
- **Data Store:** SQLite (`orders.db`) with `orders` and `order_items` tables:
  - `orders`: `id` (TEXT PRIMARY KEY), `customer_name`, `customer_email`, `total_amount`, `status`, `created_at`.
  - `order_items`: `id`, `order_id`, `product_id`, `product_name`, `quantity`, `unit_price`, `subtotal`.
- **Inter-Service Communication:**
  - When placing an order (`POST /orders`), the Order Service issues synchronous HTTP requests to `http://localhost:8001/products/{id}/reserve`.
  - If any product in the cart has insufficient stock, or if Product Service is unreachable, all previously reserved items are automatically released via `POST /products/{id}/release`, and the order is marked `FAILED`.
- **Upstream Resilience Verification:**
  - Order Service dynamically monitors the health of Product Service via `/health`.
  - If Product Service is degraded, down, or under a dependency failure injection, Order Service reports `status: "degraded"` with `dependencies: {"product_service": "UNAVAILABLE"}` and safely returns HTTP 503 for order placement requests.

---

## 5. Chaos Experiment Engine & Failure Modes

The chaos orchestrator (`backend/chaos/engine.py` and `backend/chaos/injectors.py`) implements five distinct failure injection modes with strict bounds:

### 5.1 Failure Injection Matrix

| Experiment Type | Parameter Key | Allowed Values | Default | Safety Threshold | Observed Mechanism |
|---|---|---|---|---|---|
| **Container Failure** | `type: "container_failure"` | `product-service`, `order-service` | `product-service` | Allowlist enforcement | In Docker mode, invokes `container.stop(timeout=2)`. In local mode, sets `is_outage = True` which causes middleware to return HTTP 503 for all non-management routes. |
| **CPU Stress** | `type: "cpu_stress"` | Load: 10% – 80% | 70% load, 15s | Max 80% CPU, max 3 worker threads | Spawns background daemon threads executing mathematical square calculations throttled with `time.sleep(0.001)`. Auto-stops after duration. |
| **Memory Stress** | `type: "memory_stress"` | Memory: 50MB – 350MB | 150 MB, 15s | Capped at 350 MB | Allocates byte array buffers in 10 MB chunks inside Python process memory. Auto-clears and triggers Python garbage collection on recovery. |
| **Dependency Failure** | `type: "dependency_failure"` | `order-service` | `order-service` | Restrict to `order-service` | Sets `dependency_failure = True` in Order Service state. Order Service immediately reports dependency failure and rejects checkout operations. |
| **Network Delay** | `type: "network_delay"` | Delay: 100ms – 3000ms | 1000 ms, 15s | Max 3000 ms | Injects `await asyncio.sleep(delay_ms / 1000.0)` in FastAPI HTTP middleware for business routes while bypassing health/metrics routes. |

### 5.2 Concurrency & Safety Controls
- **Target Allowlist:** Target service must be present in `ALLOWED_TARGET_SERVICES` (`product-service` or `order-service`). Arbitrary containers or host services cannot be targeted.
- **Duration Boundary:** Bounded between 5 and 60 seconds (`MAX_EXPERIMENT_DURATION_SECONDS = 60`).
- **Mutual Exclusion Guard:** Only one chaos experiment can execute at any time across the entire platform. Concurrent requests are rejected with `HTTP 409 Conflict`.
- **Explicit Confirmation Checkbox:** `confirm_destruction: true` must be submitted by the user. Submissions with `false` are rejected with `HTTP 422 Unprocessable Entity`.
- **Emergency Operator Cancellation:** At any moment during experiment execution, operators can trigger `POST /api/experiments/{id}/cancel` to immediately break duration sleeps, invoke recovery routines, and restore normal service operations.

---

## 6. Mathematical Foundations & Metrics

All platform resilience metrics are computed by `calculate_metrics()` in `backend/chaos/engine.py` from actual ISO-8601 timestamps recorded by the engine.

### 6.1 Mathematical Formulations

1. **Mean Time to Detect (MTTD / Failure Detection Time):**
   $$\Delta T_{\text{detect}} = T_{\text{detection}} - T_{\text{failure}}$$
   Where $T_{\text{failure}}$ is the timestamp when failure injection was acknowledged by the target, and $T_{\text{detection}}$ is the timestamp when the active health poller observed the first failed health check (`status != "healthy"` or non-200 HTTP code).

2. **Mean Time to Recover (MTTR / Recovery Duration):**
   $$\Delta T_{\text{recover}} = T_{\text{recovery}} - T_{\text{recovery\_start}}$$
   Where $T_{\text{recovery\_start}}$ is the timestamp when the recovery trigger was dispatched, and $T_{\text{recovery}}$ is the timestamp when the target service returned a verified HTTP 200 with `status: "healthy"`.

3. **Total Service Downtime:**
   $$\text{Downtime} = T_{\text{recovery}} - T_{\text{failure}}$$
   Represents the total duration during which end users experienced degraded or unavailable service.

4. **Recovery Success Rate:**
   $$\text{Success Rate (\%)} = \left( \frac{N_{\text{recovered}}}{N_{\text{total}}} \right) \times 100$$
   Where $N_{\text{recovered}}$ is the count of experiments achieving verified healthy state, and $N_{\text{total}}$ is the total number of initiated experiments.

---

## 7. Complete Source File Directory & Traceability

Every critical file in the repository was audited and verified against the implementation:

```
chaosLab/
├── backend/
│   ├── chaos/
│   │   ├── docker_client.py       # Safe Docker controller with container allowlists & socket fallback
│   │   ├── engine.py              # Central ChaosEngine state machine, background poller, metrics math
│   │   ├── injectors.py           # Failure injection dispatch logic for all 5 failure types
│   │   └── recovery.py            # Automated recovery executor and verified health polling
│   ├── routers/
│   │   ├── dashboard.py           # GET /api/dashboard/summary & /api/dashboard/analysis endpoints
│   │   ├── experiments.py         # POST, GET, and CANCEL endpoints for experiments
│   │   └── services.py            # GET /api/services and POST /api/services/{id}/verify endpoints
│   ├── config.py                  # Pydantic environment configuration and safety constants
│   ├── Dockerfile                 # Multi-stage production container specification for Control Plane
│   ├── main.py                    # FastAPI entrypoint, lifespan startup, CORS, Prometheus metrics
│   ├── models.py                  # SQLite database persistence layer (experiments & snapshots)
│   ├── requirements.txt           # Pinned Python package dependencies
│   ├── schemas.py                 # Pydantic v2 data models, validations, and bound definitions
│   └── tests/
│       ├── test_api.py            # Integration tests for FastAPI endpoints
│       ├── test_chaos_lifecycle.py# Unit tests for ChaosEngine state transitions & cancellation
│       ├── test_metrics_calculation.py # Mathematical tests for MTTD, MTTR, and Downtime
│       └── test_validation.py     # Pydantic schema validation & boundary constraint tests
├── services/
│   ├── product_service/
│   │   ├── database.py            # SQLite database access and atomic stock reservation logic
│   │   ├── Dockerfile             # Production container definition for Product Service
│   │   ├── main.py                # REST endpoints, Prometheus metrics, and chaos injection hooks
│   │   ├── models.py              # Pydantic request/response schemas for products and chaos
│   │   ├── requirements.txt       # Dependencies: fastapi, uvicorn, psutil, prometheus-client
│   │   └── tests/
│   │       └── test_product_service.py # 6 unit & integration tests for catalog, stock, and chaos
│   └── order_service/
│       ├── database.py            # SQLite persistence for orders and line items
│       ├── Dockerfile             # Production container definition for Order Service
│       ├── main.py                # Order creation, upstream dependency checks, chaos hooks
│       ├── models.py              # Pydantic request/response schemas for orders
│       ├── requirements.txt       # Dependencies: fastapi, uvicorn, httpx, prometheus-client
│       └── tests/
│           └── test_order_service.py # 4 unit tests for checkout, stock RPC, and dependency outages
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ExperimentDetailModal.tsx     # Modal showing full execution logs & parameters
│   │   │   ├── ExperimentHistorySection.tsx  # Audit log table with search and multi-filtering
│   │   │   ├── FailureConfirmationModal.tsx  # Parameter configuration and destructive confirmation
│   │   │   ├── FailureInjectionSection.tsx   # 5 experiment cards with observed impact details
│   │   │   ├── MetricCard.tsx                # Reusable technical KPI card component
│   │   │   ├── Navbar.tsx                    # System health pill and navigation links
│   │   │   ├── OverviewSection.tsx           # Telemetry summary, active progress banner & stepper
│   │   │   ├── RecoveryAnalysisSection.tsx   # MTTR bar charts and comparative statistics
│   │   │   └── ServiceHealthSection.tsx      # Microservice health cards with on-demand verify button
│   │   ├── styles/
│   │   │   └── index.css                     # Tailwind CSS directives and custom scrollbars
│   │   ├── api.ts                            # Typed API client for FastAPI backend communication
│   │   ├── App.tsx                           # Root React component managing polling and state
│   │   ├── main.tsx                          # React 18 DOM mount point
│   │   └── types.ts                          # TypeScript interfaces for API schemas and states
│   ├── Dockerfile                         # Multi-stage Nginx container build for frontend
│   ├── nginx.conf                         # Nginx routing configuration for React SPA
│   ├── package.json                       # Dependencies: React 18, Vite, Tailwind CSS, Lucide
│   ├── tsconfig.json                      # TypeScript strict compiler configuration
│   └── vite.config.ts                     # Vite build and proxy configuration
├── monitoring/
│   ├── grafana/
│   │   ├── dashboards/
│   │   │   ├── chaoslab-dashboard.json       # Exported Grafana dashboard panels and layouts
│   │   │   └── dashboard.yml                 # Grafana dashboard auto-provisioning specification
│   │   └── datasources/
│   │       └── datasource.yml                # Prometheus datasource auto-provisioning
│   └── prometheus/
│       └── prometheus.yml                    # Prometheus scrape configuration (2s interval)
├── ci/
│   └── Jenkinsfile                        # 7-stage Declarative Jenkins Pipeline definition
├── scripts/
│   ├── run_all.py                         # Cross-platform Python launcher for local execution
│   ├── run_local.ps1                      # Windows PowerShell launcher script
│   ├── run_local.sh                       # Linux / macOS Bash launcher script
│   ├── run_tests.ps1                      # PowerShell test runner script
│   ├── run_tests.sh                       # Bash test runner script
│   ├── start_background.ps1               # Background daemon launcher for Windows
│   └── test_live_system.py                # 10-point live resilience acceptance test suite
├── docker-compose.yml                     # 6-service Docker Compose specification
├── Jenkinsfile                            # Root pointer to ci/Jenkinsfile
├── README.md                              # Project documentation and quickstart instructions
├── start.bat / stop.bat                   # Windows batch scripts for quick startup and shutdown
└── start.ps1                              # PowerShell startup wrapper
```

---

## 8. Assumptions, Constraints, and Known Limitations

1. **Host Docker Availability:**
   - On Windows systems without Docker Desktop or an accessible Docker socket, container-level termination (`docker stop`) cannot be executed directly on the host OS.
   - **Architectural Fallback:** The platform handles this condition by automatically falling back to in-process HTTP outage simulation (`is_outage = True` returning HTTP 503), ensuring complete resilience verification remains possible without Docker.
2. **Persistence Boundary:**
   - The platform utilizes SQLite rather than a distributed cluster database (such as PostgreSQL or MySQL) to ensure zero-cost, zero-configuration local execution for college evaluation and academic defense.
3. **Telemetry Polling Interval:**
   - The React frontend polls the backend `/api/dashboard/summary` endpoint every 2.0 seconds. While sub-second detection is recorded accurately on the backend, the UI updates synchronously with the 2-second polling tick.
4. **Safety Workload Bounds:**
   - Workloads are intentionally throttled to prevent crashing student laptops or host workstations. CPU stress is capped at 80% with micro-sleeps, and memory allocation is capped at 350 MB.
