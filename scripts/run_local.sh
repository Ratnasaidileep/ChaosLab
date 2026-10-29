#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "    ChaosLab – Automated Failure Injection & Recovery     "
echo "=========================================================="

PYTHON_CMD="python3"
if [ -f ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
fi

echo "[1/4] Starting Product Service on http://localhost:8001..."
$PYTHON_CMD -m uvicorn services.product_service.main:app --host 0.0.0.0 --port 8001 &
PID_PRODUCT=$!

echo "[2/4] Starting Order Service on http://localhost:8002..."
$PYTHON_CMD -m uvicorn services.order_service.main:app --host 0.0.0.0 --port 8002 &
PID_ORDER=$!

echo "[3/4] Starting ChaosLab Control Plane on http://localhost:8000..."
$PYTHON_CMD -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
PID_BACKEND=$!

echo "[4/4] Starting Frontend Dashboard on http://localhost:3000..."
(cd frontend && npm run dev) &
PID_FRONTEND=$!

cleanup() {
    echo "Stopping all ChaosLab services..."
    kill $PID_PRODUCT $PID_ORDER $PID_BACKEND $PID_FRONTEND 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo ""
echo "All ChaosLab components started!"
echo "Dashboard:       http://localhost:3000"
echo "Backend API:     http://localhost:8000/docs"
echo "Product Service: http://localhost:8001/products"
echo "Order Service:   http://localhost:8002/orders"
echo ""
echo "Press Ctrl+C to terminate all services."

wait
