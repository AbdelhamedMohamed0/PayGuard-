@echo off
chcp 65001 > nul
echo =========================================================
echo       جاري بناء وتشفير ملف EXE لتطبيق PayGuard
echo =========================================================
echo.

echo [1/4] تثبيت المتطلبات وأدوات التشفير والحماية...
python -m pip install -r requirements.txt pyarmor
if %errorlevel% neq 0 (
    echo [خطأ] تعذر تثبيت المتطلبات عبر pip. يرجى التأكد من بايثون.
    pause
    exit /b
)

echo.
echo [2/4] جاري تشفير وحماية كافة ملفات بايثون وبناء ملف PayGuard.exe المغلق عبر PyArmor و PyInstaller...
python -m pyarmor.cli gen --pack "PayGuard.spec" app.py database.py zkteco_parser.py payroll_engine.py exporter.py pdf_generator.py

if %errorlevel% neq 0 (
    echo [خطأ] حدث خطأ أثناء تشفير وتجميع ملف الـ EXE!
    pause
    exit /b
)

echo.
echo [3/4] تجهيز حزمة العميل المشفرة (النسخة_المشفرة_للعميل)...
if not exist "النسخة_المشفرة_للعميل" mkdir "النسخة_المشفرة_للعميل"
if exist "dist\PayGuard.exe" (
    copy /y "dist\PayGuard.exe" "النسخة_المشفرة_للعميل\PayGuard.exe" > nul
    copy /y "شهر.txt" "dist\" > nul
    copy /y "شهر.txt" "النسخة_المشفرة_للعميل\" > nul
    echo =========================================================
    echo [مبروك!] تم إنشاء ملف PayGuard.exe المشفر بنجاح تام:
    echo المسار: %~dp0النسخة_المشفرة_للعميل\PayGuard.exe
    echo =========================================================
    echo.
    echo [4/4] جاري تشغيل البرنامج الآن...
    start "" "النسخة_المشفرة_للعميل\PayGuard.exe"
) else (
    echo لم يتم العثور على ملف EXE الناتج في مجلد dist.
)

pause
