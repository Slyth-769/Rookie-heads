@echo off
echo ========================================================
echo Starting Rookies - Disaster Management Alert System
echo Compliant with NDMA / OSDMA / IMD Standards
echo ========================================================

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    python app.py
) else (
    "C:\Users\KIIT\anaconda3\python.exe" app.py
)
pause
