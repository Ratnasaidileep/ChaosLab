"""Live integration and full workflow verification for ChaosLab.

Tests all live REST endpoints, business workflows, all 5 chaos experiments,
automated detection, health verification, and metric calculations.
"""
import subprocess
import sys
import time
import os
import httpx

PYTHON = sys.executable
BASE_BACKEND = "http://localhost:8000"
BASE_PRODUCT = "http://localhost:8001"
BASE_ORDER = "http://localhost:8002"

processes = []

def start_services():
    print("[1] Starting Product Service (port 8001)...")
    p1 = subprocess.Popen([PYTHON, "-m", "uvicorn", "services.product_service.main:app", "--host", "127.0.0.1", "--port", "8001"])
    processes.append(p1)

    print("[2] Starting Order Service (port 8002)...")
    p2 = subprocess.Popen([PYTHON, "-m", "uvicorn", "services.order_service.main:app", "--host", "127.0.0.1", "--port", "8002"])
    processes.append(p2)

    print("[3] Starting ChaosLab Control Plane (port 8000)...")
    p3 = subprocess.Popen([PYTHON, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"])
    processes.append(p3)

def stop_services():
    print("\nTerminating background services...")
    for p in processes:
        try:
            p.terminate()
            p.wait(timeout=3)
        except Exception:
            p.kill()

def wait_for_health():
    print("Waiting for all 3 services to become healthy...")
    client = httpx.Client(timeout=2.0)
    for service, url in [("Product", BASE_PRODUCT), ("Order", BASE_ORDER), ("Backend", BASE_BACKEND)]:
        ready = False
        for _ in range(30):
            try:
                res = client.get(f"{url}/health")
                if res.status_code == 200 and res.json().get("status") == "healthy":
                    ready = True
                    break
            except Exception:
                pass
            time.sleep(0.5)
        if not ready:
            raise RuntimeError(f"Service {service} failed to respond healthy at {url}")
        print(f" -> {service} Service is HEALTHY!")

def run_tests():
    client = httpx.Client(timeout=10.0)

    # 1. Product Catalog
    print("\n--- Testing Product Service Catalog ---")
    res = client.get(f"{BASE_PRODUCT}/products")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    products = res.json()
    print(f"Catalog loaded: {len(products)} products available.")
    assert len(products) >= 6

    # 2. Create Order & Stock Reservation
    print("\n--- Testing Order Service & Stock Reservation Flow ---")
    order_payload = {
        "customer_name": "DevOps Evaluator",
        "customer_email": "evaluator@college.edu",
        "items": [
            {"product_id": 1, "quantity": 1},
            {"product_id": 2, "quantity": 2}
        ]
    }
    res = client.post(f"{BASE_ORDER}/orders", json=order_payload)
    assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"
    order = res.json()
    print(f"Order created successfully: {order['order_number']} (Total: ${order['total_amount']})")

    # 3. Check Dashboard Summary
    print("\n--- Testing Dashboard Summary ---")
    res = client.get(f"{BASE_BACKEND}/api/dashboard/summary")
    assert res.status_code == 200
    summary = res.json()
    print(f"Overall System Health: {summary['overall_system_health']}")
    assert summary["overall_system_health"] == "HEALTHY"

    # 4. Chaos Experiment 1: Dependency Failure on order-service
    print("\n--- Testing Chaos Experiment 1: Dependency Failure on order-service ---")
    chaos_req = {
        "type": "dependency_failure",
        "target_service": "order-service",
        "duration_seconds": 5,
        "confirm_destruction": True
    }
    res = client.post(f"{BASE_BACKEND}/api/experiments", json=chaos_req)
    assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"
    exp = res.json()
    exp_id = exp["id"]
    print(f"Experiment dispatched: {exp_id} ({exp['type']} -> {exp['target_service']})")

    # Wait for detection and completion
    print("Waiting for detection and automatic recovery...")
    completed = False
    for _ in range(40):
        time.sleep(1)
        r = client.get(f"{BASE_BACKEND}/api/experiments/{exp_id}")
        st = r.json().get("status")
        print(f"  Status: {st} | Recovery Outcome: {r.json().get('recovery_outcome')}")
        if st in ("RECOVERED", "FAILED"):
            completed = True
            exp_data = r.json()
            assert st == "RECOVERED", f"Experiment failed: {exp_data}"
            print(f"  VERIFIED RECOVERED!")
            print(f"  Detection Time: {exp_data.get('detection_time_ms')} ms")
            print(f"  Recovery Duration: {exp_data.get('recovery_duration_ms')} ms")
            print(f"  Total Downtime: {exp_data.get('total_downtime_ms')} ms")
            break
    assert completed, "Experiment did not complete within timeout"

    # 5. Chaos Experiment 2: Container Failure / Simulated Outage on product-service
    print("\n--- Testing Chaos Experiment 2: Container Failure on product-service ---")
    chaos_req = {
        "type": "container_failure",
        "target_service": "product-service",
        "duration_seconds": 5,
        "confirm_destruction": True
    }
    res = client.post(f"{BASE_BACKEND}/api/experiments", json=chaos_req)
    assert res.status_code == 201
    exp_id = res.json()["id"]
    print(f"Experiment dispatched: {exp_id}")

    completed = False
    for _ in range(40):
        time.sleep(1)
        r = client.get(f"{BASE_BACKEND}/api/experiments/{exp_id}")
        st = r.json().get("status")
        print(f"  Status: {st}")
        if st in ("RECOVERED", "FAILED"):
            completed = True
            exp_data = r.json()
            assert st == "RECOVERED"
            print(f"  VERIFIED RECOVERED! Downtime: {exp_data.get('total_downtime_ms')} ms")
            break
    assert completed

    # 6. Chaos Experiment 3: CPU Stress on product-service
    print("\n--- Testing Chaos Experiment 3: CPU Stress on product-service ---")
    chaos_req = {
        "type": "cpu_stress",
        "target_service": "product-service",
        "duration_seconds": 5,
        "load_percent": 60,
        "confirm_destruction": True
    }
    res = client.post(f"{BASE_BACKEND}/api/experiments", json=chaos_req)
    assert res.status_code == 201
    exp_id = res.json()["id"]

    completed = False
    for _ in range(40):
        time.sleep(1)
        r = client.get(f"{BASE_BACKEND}/api/experiments/{exp_id}")
        st = r.json().get("status")
        if st in ("RECOVERED", "FAILED"):
            completed = True
            assert st == "RECOVERED"
            print(f"  CPU Stress VERIFIED RECOVERED!")
            break
    assert completed

    # 7. Chaos Experiment 4: Memory Stress on order-service
    print("\n--- Testing Chaos Experiment 4: Memory Stress on order-service ---")
    chaos_req = {
        "type": "memory_stress",
        "target_service": "order-service",
        "duration_seconds": 5,
        "memory_mb": 100,
        "confirm_destruction": True
    }
    res = client.post(f"{BASE_BACKEND}/api/experiments", json=chaos_req)
    assert res.status_code == 201
    exp_id = res.json()["id"]

    completed = False
    for _ in range(40):
        time.sleep(1)
        r = client.get(f"{BASE_BACKEND}/api/experiments/{exp_id}")
        st = r.json().get("status")
        if st in ("RECOVERED", "FAILED"):
            completed = True
            assert st == "RECOVERED"
            print(f"  Memory Stress VERIFIED RECOVERED!")
            break
    assert completed

    # 8. Chaos Experiment 5: Network Delay on product-service
    print("\n--- Testing Chaos Experiment 5: Network Delay on product-service ---")
    chaos_req = {
        "type": "network_delay",
        "target_service": "product-service",
        "duration_seconds": 5,
        "delay_ms": 600,
        "confirm_destruction": True
    }
    res = client.post(f"{BASE_BACKEND}/api/experiments", json=chaos_req)
    assert res.status_code == 201
    exp_id = res.json()["id"]

    completed = False
    for _ in range(40):
        time.sleep(1)
        r = client.get(f"{BASE_BACKEND}/api/experiments/{exp_id}")
        st = r.json().get("status")
        if st in ("RECOVERED", "FAILED"):
            completed = True
            assert st == "RECOVERED"
            print(f"  Network Delay VERIFIED RECOVERED!")
            break
    assert completed

    # 9. Test Experiment Cancellation
    print("\n--- Testing User Cancellation of Active Experiment ---")
    chaos_req = {
        "type": "cpu_stress",
        "target_service": "order-service",
        "duration_seconds": 30,
        "load_percent": 50,
        "confirm_destruction": True
    }
    res = client.post(f"{BASE_BACKEND}/api/experiments", json=chaos_req)
    assert res.status_code == 201
    cancel_exp_id = res.json()["id"]

    time.sleep(1.5)
    print(f"Cancelling experiment {cancel_exp_id}...")
    cancel_res = client.post(f"{BASE_BACKEND}/api/experiments/{cancel_exp_id}/cancel")
    assert cancel_res.status_code == 200

    time.sleep(2)
    detail = client.get(f"{BASE_BACKEND}/api/experiments/{cancel_exp_id}").json()
    print(f"Cancelled experiment state: {detail.get('status')} (Outcome: {detail.get('recovery_outcome')})")
    assert detail.get("status") == "CANCELLED"
    assert detail.get("recovery_outcome") == "CANCELLED_BY_USER"

    # 10. Test Recovery Analysis & History
    print("\n--- Testing Recovery Analysis & History Metrics ---")
    res = client.get(f"{BASE_BACKEND}/api/dashboard/analysis")
    assert res.status_code == 200
    analysis = res.json()
    summary = analysis["summary"]
    print(f"Total Experiments in Database: {summary['total_experiments']}")
    print(f"Successful Recoveries:        {summary['successful_recoveries']}")
    print(f"Recovery Success Rate:        {summary['recovery_success_rate_percent']}%")
    print(f"Avg Detection Time:           {summary['avg_detection_time_ms']} ms")
    print(f"Avg Recovery Duration (MTTR): {summary['avg_recovery_duration_ms']} ms")
    print(f"Avg Total Downtime:           {summary['avg_total_downtime_ms']} ms")
    print(f"Type Breakdown Count:         {len(analysis['type_breakdown'])}")
    assert summary["total_experiments"] >= 5
    assert summary["successful_recoveries"] >= 5
    assert len(analysis["type_breakdown"]) >= 5

    print("\n========================================================")
    print(" ALL 10 LIVE SYSTEM CAPABILITIES VERIFIED SUCCESSFULLY!")
    print("========================================================")

if __name__ == "__main__":
    try:
        start_services()
        wait_for_health()
        run_tests()
    finally:
        stop_services()
