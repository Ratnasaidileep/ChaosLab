@echo off
title ChaosLab Local Launcher
echo ==========================================================
echo     ChaosLab - Automated Failure Injection and Recovery
echo                  Running in Local Mode (No Docker Required)
echo ==========================================================

cd /d "%~dp0"

set "PYTHON_EXE=.\.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

echo [1/4] Starting Product Service (Port 8001)...
start "ChaosLab - Product Service" cmd /k "%PYTHON_EXE% -m uvicorn services.product_service.main:app --host 0.0.0.0 --port 8001"

echo [2/4] Starting Order Service (Port 8002)...
start "ChaosLab - Order Service" cmd /k "%PYTHON_EXE% -m uvicorn services.order_service.main:app --host 0.0.0.0 --port 8002"

echo [3/4] Starting ChaosLab Control Plane (Port 8000)...
start "ChaosLab - Backend API" cmd /k "%PYTHON_EXE% -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"

echo [4/4] Starting React Frontend Dashboard (Port 3000)...
start "ChaosLab - Frontend Dashboard" cmd /k "cd frontend && npm run dev"

echo.
echo ==========================================================
echo ChaosLab is running! Access the interfaces at:
echo.
echo   * Dashboard:        http://localhost:3000
echo   * Swagger API Docs: http://localhost:8000/docs
echo   * Product Service:  http://localhost:8001/products
echo   * Order Service:    http://localhost:8002/orders
echo ==========================================================
echo.
pause
