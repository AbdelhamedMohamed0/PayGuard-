@echo off
chcp 65001 > nul
echo Starting PayGuard - Smart Payroll & Biometric Attendance System...
python app.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] An error occurred while launching PayGuard.
    echo Please make sure dependencies are installed:
    echo pip install -r requirements.txt
    pause
)

