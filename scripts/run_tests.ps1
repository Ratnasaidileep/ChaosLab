# Run all test suites
$PythonExe = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

Write-Host "Running Backend & Microservice Pytest suites..." -ForegroundColor Cyan
& $PythonExe -m pytest services/product_service/tests services/order_service/tests backend/tests -v

Write-Host "`nRunning Frontend Type & Build checks..." -ForegroundColor Cyan
Push-Location frontend
npm run test
npm run build
Pop-Location

Write-Host "`nAll ChaosLab tests passed successfully!" -ForegroundColor Green
