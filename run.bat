@echo off
setlocal
cd /d "%~dp0"
title PathWise 🔮 Future Me Simulator

echo ============================================================
echo   Launching Pathwise 🔮 Future Me Simulator
echo ============================================================
echo.

if exist ".venv\bin\python.exe" (
    echo [INFO] Using virtual environment at .venv\bin\python.exe
    ".venv\bin\python.exe" -m streamlit run src/app.py
    goto :end
)

if exist ".venv\Scripts\python.exe" (
    echo [INFO] Using virtual environment at .venv\Scripts\python.exe
    ".venv\Scripts\python.exe" -m streamlit run src/app.py
    goto :end
)

if exist "venv\bin\python.exe" (
    echo [INFO] Using virtual environment at venv\bin\python.exe
    "venv\bin\python.exe" -m streamlit run src/app.py
    goto :end
)

echo [INFO] Using system python
python -m streamlit run src/app.py

:end
if errorlevel 1 (
    echo.
    echo [ERROR] Application exited with an error.
    echo Press any key to close...
    pause >nul
)
