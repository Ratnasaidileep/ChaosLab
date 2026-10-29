#!/usr/bin/env bash
set -e

PYTHON_CMD="python3"
if [ -f ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
fi

echo "Running Backend & Microservice Pytest suites..."
$PYTHON_CMD -m pytest services/product_service/tests services/order_service/tests backend/tests -v

echo "Running Frontend Type & Build checks..."
(cd frontend && npm run test && npm run build)

echo "All ChaosLab tests passed successfully!"
