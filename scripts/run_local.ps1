# ChaosLab Local Environment Launcher (Windows PowerShell)
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "    ChaosLab - Automated Failure Injection and Recovery   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$BaseDir = (Resolve-Path "$PSScriptRoot\..").Path
$PythonExe = "$BaseDir\.venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

Write-Host "[1/4] Starting Product Service on http://localhost:8001..." -ForegroundColor Green
$ProductProcess = Start-Process -FilePath $PythonExe -ArgumentList "-m", "uvicorn", "services.product_service.main:app", "--host", "0.0.0.0", "--port", "8001" -WorkingDirectory $BaseDir -PassThru

Write-Host "[2/4] Starting Order Service on http://localhost:8002..." -ForegroundColor Green
$OrderProcess = Start-Process -FilePath $PythonExe -ArgumentList "-m", "uvicorn", "services.order_service.main:app", "--host", "0.0.0.0", "--port", "8002" -WorkingDirectory $BaseDir -PassThru

Write-Host "[3/4] Starting ChaosLab Control Plane on http://localhost:8000..." -ForegroundColor Green
$BackendProcess = Start-Process -FilePath $PythonExe -ArgumentList "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000" -WorkingDirectory $BaseDir -PassThru

Write-Host "[4/4] Starting Frontend Dashboard on http://localhost:3000..." -ForegroundColor Green
$FrontendProcess = Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "npm run dev" -WorkingDirectory "$BaseDir\frontend" -PassThru

Write-Host ""
Write-Host "All ChaosLab components started!" -ForegroundColor Cyan
Write-Host "Dashboard:       http://localhost:3000" -ForegroundColor White
Write-Host "Backend API:     http://localhost:8000/docs" -ForegroundColor White
Write-Host "Product Service: http://localhost:8001/products" -ForegroundColor White
Write-Host "Order Service:   http://localhost:8002/orders" -ForegroundColor White
Write-Host ""
Write-Host "ChaosLab is running. Press Ctrl+C to stop all services." -ForegroundColor Gray

try {
    Wait-Process -Id $BackendProcess.Id, $ProductProcess.Id, $OrderProcess.Id
} finally {
    Write-Host "Terminating background processes..." -ForegroundColor Yellow
    Stop-Process -Id $ProductProcess.Id -ErrorAction SilentlyContinue
    Stop-Process -Id $OrderProcess.Id -ErrorAction SilentlyContinue
    Stop-Process -Id $BackendProcess.Id -ErrorAction SilentlyContinue
    Stop-Process -Id $FrontendProcess.Id -ErrorAction SilentlyContinue
}
