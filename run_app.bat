@echo off
chcp 65001 > nul
echo تشغيل نظام PayGuard لإدارة المرتبات وحضور البصمة...
python app.py
if %errorlevel% neq 0 (
    echo.
    echo حدث خطأ أثناء التشغيل. تأكد من تثبيت المكتبات أولاً بتشغيل build_exe.bat أو:
    echo pip install -r requirements.txt
    pause
)
