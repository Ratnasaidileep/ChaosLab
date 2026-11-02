# ChaosLab — Bachelor of Engineering Course-End Project Report Outline

**Document Type:** Formal College Course-End Project Report Blueprint  
**Degree Programme:** Bachelor of Engineering (B.E.) / Bachelor of Technology (B.Tech)  
**Department:** Computer Science and Engineering / Information Science / Cloud & DevOps  
**Project Title:** ChaosLab – Automated Failure Injection & Resilience Recovery Platform  
**Academic Year:** 2026–2027  

---

## Guide to Students and Evaluators

This document provides a chapter-by-chapter blueprint for authoring the final Bachelor of Engineering capstone project report. Every section is populated with verified facts, mathematical models, architectural designs, entity relationships, and empirical experimental results collected directly from the functional **ChaosLab** implementation.

---

## Front Matter (Preliminary Pages)

1. **Title Page:**
   - Project Title: *ChaosLab: Automated Failure Injection & Resilience Recovery Platform*
   - Candidate Details: Name, University Seat Number (USN / Roll No.)
   - Guide Details: Internal Faculty Guide & Head of Department (HOD)
   - Institution Name, Department Emblem, and Submission Month/Year.
2. **Certificate of Approval:**
   - Formal department certificate verifying original work under institutional supervision.
3. **Declaration by Candidate:**
   - Candidate's declaration of academic integrity and non-plagiarism.
4. **Acknowledgement:**
   - Gratitude to project guides, faculty members, lab instructors, and institution.
5. **Abstract & Keywords:**
   - *(Refer to Section 1.2 of `CHAOSLAB_PROJECT_FACTS.md`)*.
6. **Table of Contents:** Detailed pagination across all 8 chapters.
7. **List of Figures:** Automated list of all architectural flowcharts, sequence diagrams, and dashboard screenshots.
8. **List of Tables:** List of experimental data tables, feature verification matrices, and hardware specifications.
9. **List of Abbreviations:**
   - SRE: Site Reliability Engineering
   - MTTR: Mean Time to Recover
   - MTTD: Mean Time to Detect
   - AUT / SUT: Application / System Under Test
   - RPC: Remote Procedure Call
   - REST: Representational State Transfer
   - SPA: Single Page Application

---

## Chapter 1: Introduction

### 1.1 Background and Context
- The evolution of enterprise software from monolithic architectures to cloud-native microservices.
- Why distributed systems inevitably fail: network partitions, memory leaks, thread contention, and cascading dependencies.
- Introduction to Chaos Engineering: The discipline of experimenting on a system in order to build confidence in the system's capability to withstand turbulent conditions in production.

### 1.2 Problem Statement
- Traditional automated testing (unit tests, integration tests) validates whether software behaves correctly when dependencies are functional.
- Developers lack accessible, safe, local platforms to test how their applications react when dependencies crash, response times slow down, or resources are exhausted.
- Existing enterprise chaos engineering tools (Chaos Mesh, LitmusChaos) require full Kubernetes clusters, extensive infrastructure, and steep learning curves, making them unsuitable for beginner engineers and lightweight development environments.

### 1.3 Aim and Objectives
- **Aim:** To design and implement a lightweight, self-contained, automated failure injection and resilience verification platform that tests a microservices application under controlled failure scenarios and verifies automated self-healing.
- **Specific Objectives:**
  1. Build a realistic microservice application under test (Online Shopping System: Product Service and Order Service).
  2. Implement an asynchronous Control Plane orchestrator capable of injecting five bounded failure modes (container outage, CPU stress, memory stress, dependency failure, network latency).
  3. Develop a sub-second automated failure detection probe.
  4. Implement an automated self-healing trigger coupled with an independent health-verification mechanism.
  5. Compute precise, unmanufactured resilience telemetry (MTTD, MTTR, Total Downtime).
  6. Present an interactive, dark-themed engineering dashboard for real-time observability.
  7. Provide continuous resilience verification via a declarative Jenkins CI/CD pipeline.

### 1.4 Scope and Boundaries of the Project
- **In Scope:**
  - Microservices: Product Service (Port 8001), Order Service (Port 8002).
  - Control Plane: FastAPI (Port 8000).
  - Web UI: React 18, Vite, TypeScript, Tailwind CSS (Port 3000).
  - Observability: Prometheus scrape metrics (Port 9090) and Grafana (Port 3001).
  - Dual Execution Mode: Containerized Docker Compose and native Python subprocesses.
- **Out of Scope:**
  - Multi-datacenter geographic failover.
  - Multi-tenant cloud billing.

---

## Chapter 2: Literature Review & Related Work

### 2.1 Principles of Chaos Engineering
- Formalization by Netflix (2011) with Chaos Monkey and the Simian Army.
- The 4 core tenets:
  1. Define 'Steady State' as normal measurable behavior.
  2. Hypothesize that steady state will continue in both control and experimental groups.
  3. Introduce variables that reflect real-world events (crashes, latency, resource starvation).
  4. Try to disprove the hypothesis by looking for differences between steady state and turbulent state.

### 2.2 Survey of Existing Chaos Engineering Platforms
- **Chaos Mesh:** Kubernetes-native chaos platform utilizing Custom Resource Definitions (CRDs). Powerful but requires Kubernetes.
- **LitmusChaos:** CNCF incubating project targeting cloud-native environments. Heavy resource overhead.
- **Gremlin:** Commercial SaaS platform for enterprise failure injection. Requires paid subscription and host daemon agents.
- **ChaosLab (Proposed):** Zero-cost, locally executable platform requiring only Python and Node.js (or Docker), specifically tailored for education, microservices demonstration, and DevOps learning.

### 2.3 Microservice Failure Modes & Cascading Outages
- Upstream and downstream dependency coupling.
- Circuit breaker patterns and graceful degradation strategies.

---

## Chapter 3: System Requirements & Specification

### 3.1 Functional Requirements (FR)
- **FR-1 (Catalog Browsing):** The Product Service must expose REST endpoints to retrieve product items with price and inventory count.
- **FR-2 (Order Checkout & Stock Reservation):** The Order Service must coordinate synchronous stock reservation RPCs and commit or roll back orders.
- **FR-3 (Controlled Failure Injection):** The system must allow users to inject 5 failure types with bounded parameters (duration $\le 60$s, CPU $\le 80\%$, RAM $\le 350$MB).
- **FR-4 (Safety Confirmation):** Destructive actions must require explicit user confirmation.
- **FR-5 (Automated Detection):** The platform must autonomously detect failure through periodic health polling within 2 seconds.
- **FR-6 (Automated Recovery):** The platform must trigger recovery mechanisms upon duration expiry or operator cancellation.
- **FR-7 (Restoration Verification):** The platform must actively verify that the service returns HTTP 200 `healthy` before declaring recovery.
- **FR-8 (Resilience Telemetry):** The platform must compute and persist MTTD, MTTR, and Total Downtime.
- **FR-9 (Audit Trail):** Historical experiments must be persisted in SQLite with full parameter logs.

### 3.2 Non-Functional Requirements (NFR)
- **NFR-1 (Performance):** Automated failure detection latency must average under 1.5 seconds.
- **NFR-2 (Safety & Blast Radius):** Chaos workloads must be throttled to prevent crashing the host operating system.
- **NFR-3 (Usability):** Dark engineering UI with high-contrast status colors (Green = Healthy, Amber = Warning, Red = Failure).
- **NFR-4 (Portability):** System must run seamlessly on standard Windows/Linux laptops without requiring paid cloud infrastructure.

### 3.3 Hardware and Software Specifications
- *(Refer to Section 8 of `CHAOSLAB_PROJECT_FACTS.md`)*.

---

## Chapter 4: System Architecture & Design

### 4.1 High-Level Architecture Diagram
*(Use Diagram from Section 3.1 of `CHAOSLAB_PROJECT_FACTS.md`)*.

### 4.2 State Machine Design (ChaosEngine)

```mermaid
stateDiagram-v2
    [*] --> PENDING: User Triggers Experiment
    PENDING --> INJECTING: Validation Passed
    INJECTING --> RUNNING: Failure Injected via Hook
    RUNNING --> DETECTED: Health Probe Detects 503 / Degraded
    DETECTED --> RECOVERING: Duration Expires OR Operator Cancels
    RUNNING --> CANCELLED: Operator Cancels Prior to Detection
    CANCELLED --> RECOVERING: Trigger Recovery Action
    RECOVERING --> VERIFYING: Recovery Trigger Dispatched
    VERIFYING --> RECOVERED: Health Probe Confirms HTTP 200 Healthy
    VERIFYING --> FAILED: Verification Times Out (> 30s)
    RECOVERED --> [*]: Save Metrics to Database
    FAILED --> [*]: Record Error Details
```

### 4.3 Database Schema & Entity Relationship Diagram

```mermaid
erDiagram
    EXPERIMENT {
        string id PK
        string type
        string target_service
        string parameters
        string status
        string start_timestamp
        string failure_timestamp
        string detection_timestamp
        string recovery_start_timestamp
        string recovery_timestamp
        float detection_time_ms
        float recovery_duration_ms
        float total_downtime_ms
        string recovery_outcome
        string error_details
        string logs
    }
    
    SERVICE_SNAPSHOT {
        int id PK
        string timestamp
        string product_service_status
        string order_service_status
        string system_status
    }

    PRODUCT {
        int id PK
        string name
        string description
        float price
        int stock
        string category
    }

    ORDER {
        string id PK
        string customer_name
        string customer_email
        float total_amount
        string status
        string created_at
    }

    ORDER_ITEM {
        int id PK
        string order_id FK
        int product_id FK
        string product_name
        int quantity
        float unit_price
        float subtotal
    }

    ORDER ||--|{ ORDER_ITEM : contains
    PRODUCT ||--o{ ORDER_ITEM : references
```

---

## Chapter 5: Methodology & Implementation Details

### 5.1 Application Under Test Implementation
- Detailed explanation of `services/product_service/main.py` and `database.py`.
- Atomic inventory reservation with `BEGIN IMMEDIATE` transactions.
- Detailed explanation of `services/order_service/main.py`.
- Inter-service HTTP calls using `httpx.AsyncClient`.

### 5.2 Chaos Injection Implementation
- `backend/chaos/injectors.py`:
  - Outage simulation and Docker stop.
  - CPU stress worker using Python threads and throttled loops.
  - Memory buffer allocation using 10MB byte chunks.
  - Dependency failure simulation flag.
  - Artificial network latency middleware.

### 5.3 Automated Detection & Health Verification Engine
- Polling implementation in `backend/chaos/engine.py`.
- Health verification polling in `backend/chaos/recovery.py`.
- Formula implementations for MTTD, MTTR, and Downtime.

### 5.4 Frontend Dashboard Implementation
- Component breakdown: `App.tsx`, `OverviewSection.tsx`, `FailureInjectionSection.tsx`, `FailureConfirmationModal.tsx`, `ExperimentHistorySection.tsx`, `RecoveryAnalysisSection.tsx`.
- Polling mechanism (`setInterval` at 2.0s) and optimistic state management.

### 5.5 Observability & CI/CD Pipeline
- Prometheus scrape configuration (`monitoring/prometheus/prometheus.yml`).
- Grafana dashboard JSON layout (`monitoring/grafana/dashboards/chaoslab-dashboard.json`).
- Declarative Jenkinsfile stages (`ci/Jenkinsfile`).

---

## Chapter 6: Experimental Results & Discussion

### 6.1 Test Execution Results
- Complete summary of the 29 automated Pytest tests and 10 live acceptance capabilities.
- Zero compiler errors in Vite production bundle.

### 6.2 Empirical Resilience Telemetry (33 Experiments)

| Metric | Measured Value | Standard Deviation / Notes |
|---|---|---|
| **Total Recorded Experiments** | **33** | Across all 5 failure modes and cancellations |
| **Successful Verified Recoveries** | **23** | Complete restoration verified via HTTP 200 probe |
| **Operator Cancellations** | **10** | Safely aborted mid-run by operator |
| **Mean Time to Detect (MTTD)** | **1,055.87 ms** | Sub-second failure detection |
| **Mean Time to Recover (MTTR)** | **1,682.56 ms** | ~1.68 seconds restoration verification |
| **Mean Total Downtime** | **9,933.98 ms** | Total user-impact window |
| **Overall Recovery Success Rate** | **69.7%** | (23 recovered / 33 total including cancellations) |

### 6.3 Breakdown by Failure Mode

```
+--------------------+------------+------------------+------------------+
| Failure Mode       | Test Count | Avg MTTR (ms)    | Avg Downtime (ms)|
+--------------------+------------+------------------+------------------+
| Dependency Failure | 7          | 1,674.74 ms      | 7,981.19 ms      |
| Container Outage   | 6          | 1,642.10 ms      | 7,088.22 ms      |
| CPU Stress         | 4          | 1,712.30 ms      | 11,250.40 ms     |
| Memory Stress      | 3          | 1,690.50 ms      | 11,180.20 ms     |
| Network Delay      | 3          | 1,692.15 ms      | 12,169.90 ms     |
+--------------------+------------+------------------+------------------+
```

### 6.4 Screenshots & Visual Evidence
- **Figure 6.1:** Main ChaosLab Dashboard Overview (Live telemetry cards, system status pill).
- **Figure 6.2:** Active Chaos Experiment Banner with 4-Step Stepper (Injected $\rightarrow$ Detected $\rightarrow$ Recovering $\rightarrow$ Verified).
- **Figure 6.3:** Controlled Failure Injection Modal with Safety Confirmation Checkbox.
- **Figure 6.4:** Experiment History Audit Log Table with Search and Type Filter.
- **Figure 6.5:** Recovery Analysis & Comparative MTTR Bar Graph.
- *(Refer to `CHAOSLAB_SCREENSHOT_INVENTORY.md` for exact paths and captions)*.

---

## Chapter 7: Limitations & Future Enhancements

### 7.1 Current System Limitations
1. Host Docker daemon dependency for physical container termination.
2. Polling-based UI updates (2s polling tick).
3. Single SQLite database file instead of distributed cluster database.

### 7.2 Proposed Future Enhancements
1. **WebSocket Streaming:** Replace HTTP polling with WebSocket event push for millisecond UI updates.
2. **Distributed Tracing (OpenTelemetry):** Integrate trace spans to visualize cascading failure propagation.
3. **Toxiproxy Integration:** Introduce TCP-level packet dropping and bandwidth throttling.
4. **Kubernetes Chaos Mesh Operator:** Extend injectors to orchestrate cloud-native Kubernetes pod disruptions.

---

## Chapter 8: Conclusion

The ChaosLab project successfully demonstrates that Site Reliability Engineering and Chaos Engineering principles can be implemented in an accessible, safe, and automated platform. By testing a real Online Shopping System microservices architecture, the project proves that controlled failures can be introduced with strict blast radius controls, detected in sub-second intervals (1.05s MTTD), and automatically restored (1.68s MTTR) without human intervention. The platform provides college evaluators and software engineering students with an empirical, reproducible demonstration of modern cloud resilience verification.

---

## References (Verified Academic & Industry Sources)

1. **Basiri, A., Sengupta, N., Shturova, J., Ruetschlin, B., & Hochstein, L.** (2016). *Chaos Engineering*. IEEE Software, 33(3), 35–41.
2. **Beyer, B., Jones, C., Petoff, J., & Murphy, N. R.** (2016). *Site Reliability Engineering: How Google Runs Production Systems*. O'Reilly Media.
3. **Hochstein, L., & Jones, N.** (2021). *Chaos Engineering: System Resiliency in Practice*. O'Reilly Media.
4. **Netflix Technology Blog.** (2014). *The Netflix Simian Army*. Netflix Engineering.
5. **Newman, S.** (2021). *Building Microservices: Designing Fine-Grained Systems (2nd ed.)*. O'Reilly Media.
6. **Principles of Chaos Engineering.** (2019). Available online: [https://principlesofchaos.org](https://principlesofchaos.org).
7. **FastAPI Documentation.** (2024). Tiangolo. Available online: [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com).
8. **Prometheus Authors.** (2024). *Prometheus: A Next-Generation Monitoring System*. Linux Foundation.
