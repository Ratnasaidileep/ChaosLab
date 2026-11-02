"""ChaosLab Runner - Starts all 4 services and keeps them running."""
import subprocess
import sys
import time
import os

PYTHON = sys.executable
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

processes = []

def start():
    print("=" * 60)
    print("    ChaosLab - Automated Failure Injection and Recovery    ")
    print("=" * 60)

    print("[1/4] Starting Product Service on http://localhost:8001...")
    p1 = subprocess.Popen([PYTHON, "-m", "uvicorn", "services.product_service.main:app", "--host", "0.0.0.0", "--port", "8001"], cwd=BASE_DIR)
    processes.append(p1)

    print("[2/4] Starting Order Service on http://localhost:8002...")
    p2 = subprocess.Popen([PYTHON, "-m", "uvicorn", "services.order_service.main:app", "--host", "0.0.0.0", "--port", "8002"], cwd=BASE_DIR)
    processes.append(p2)

    print("[3/4] Starting ChaosLab Control Plane on http://localhost:8000...")
    p3 = subprocess.Popen([PYTHON, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"], cwd=BASE_DIR)
    processes.append(p3)

    print("[4/4] Starting Frontend Dashboard on http://localhost:3000...")
    frontend_dir = os.path.join(BASE_DIR, "frontend")
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    p4 = subprocess.Popen([npm_cmd, "run", "dev"], cwd=frontend_dir)
    processes.append(p4)

    print("\nAll ChaosLab components started!")
    print("Dashboard:       http://localhost:3000")
    print("Backend API:     http://localhost:8000/docs")
    print("Product Service: http://localhost:8001/products")
    print("Order Service:   http://localhost:8002/orders")
    print("\nChaosLab is running. Press Ctrl+C or run stop.bat to stop.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down ChaosLab...")
    finally:
        for p in processes:
            try:
                p.terminate()
            except Exception:
                pass

if __name__ == "__main__":
    start()
