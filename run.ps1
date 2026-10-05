# PowerShell launcher for PathWise Future Me Simulator
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Launching Pathwise 🔮 Future Me Simulator" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$PythonPath = $null
if (Test-Path "$ScriptDir\.venv\bin\python.exe") {
    $PythonPath = "$ScriptDir\.venv\bin\python.exe"
} elseif (Test-Path "$ScriptDir\.venv\Scripts\python.exe") {
    $PythonPath = "$ScriptDir\.venv\Scripts\python.exe"
} elseif (Test-Path "$ScriptDir\venv\bin\python.exe") {
    $PythonPath = "$ScriptDir\venv\bin\python.exe"
} else {
    $PythonPath = "python"
}

Write-Host "[INFO] Using Python: $PythonPath" -ForegroundColor Green
& $PythonPath -m streamlit run src/app.py
