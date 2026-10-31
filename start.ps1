# ChaosLab Direct Local Launcher (Windows PowerShell)
# No Docker required! Runs all services natively on Windows.

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

& powershell -ExecutionPolicy Bypass -File "$ScriptDir\scripts\run_local.ps1"
