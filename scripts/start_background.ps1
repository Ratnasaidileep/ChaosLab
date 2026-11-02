# ChaosLab Background Launcher
$BaseDir = "c:\Users\SaiDi\chaosLab"
$PythonExe = "$BaseDir\.venv\Scripts\python.exe"

Write-Host "Starting Product Service (Port 8001)..." -ForegroundColor Cyan
Start-Process -FilePath $PythonExe -ArgumentList "-m", "uvicorn", "services.product_service.main:app", "--host", "0.0.0.0", "--port", "8001" -WorkingDirectory $BaseDir -WindowStyle Hidden

Write-Host "Starting Order Service (Port 8002)..." -ForegroundColor Cyan
Start-Process -FilePath $PythonExe -ArgumentList "-m", "uvicorn", "services.order_service.main:app", "--host", "0.0.0.0", "--port", "8002" -WorkingDirectory $BaseDir -WindowStyle Hidden

Write-Host "Starting ChaosLab Backend API (Port 8000)..." -ForegroundColor Cyan
Start-Process -FilePath $PythonExe -ArgumentList "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000" -WorkingDirectory $BaseDir -WindowStyle Hidden

Write-Host "Starting React Frontend Dashboard (Port 3000)..." -ForegroundColor Cyan
Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "npm run dev" -WorkingDirectory "$BaseDir\frontend" -WindowStyle Hidden

Write-Host "Waiting for services to become ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 4

# Check health
$Ports = @(8001, 8002, 8000, 3000)
foreach ($Port in $Ports) {
    $Conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if ($Conn) {
        Write-Host " [OK] Service listening on port $Port" -ForegroundColor Green
    } else {
        Write-Host " [WAIT] Port $Port not yet listening, may need another second." -ForegroundColor Yellow
    }
}
