# ChaosLab Direct Local Launcher (Windows PowerShell)
# No Docker required! Runs all services natively on Windows.

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

$PythonExe = "$ScriptDir\.venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

& $PythonExe "$ScriptDir\scripts\run_all.py"
