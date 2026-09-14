@echo off
chcp 65001 > nul
echo =========================================================
echo       Building and Obfuscating PayGuard Executable
echo =========================================================
echo.

echo [1/3] Installing requirements, PyArmor, and PyInstaller...
python -m pip install -r requirements.txt pyarmor pyinstaller
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install requirements via pip. Please check your Python environment.
    pause
    exit /b
)

echo.
echo [2/3] Obfuscating source files with PyArmor and bundling with PyInstaller...
python -m pyarmor.cli gen --pack "PayGuard.spec" app.py database.py zkteco_parser.py payroll_engine.py exporter.py pdf_generator.py

if %errorlevel% neq 0 (
    echo [ERROR] Failed during obfuscation or packaging!
    pause
    exit /b
)

echo.
echo [3/3] Packaging distribution files...
if exist "dist\PayGuard.exe" (
    if exist "sample_data\sample_punches.txt" (
        copy /y "sample_data\sample_punches.txt" "dist\" > nul
    )
    echo =========================================================
    echo [SUCCESS] PayGuard.exe generated successfully!
    echo Binary location: %~dp0dist\PayGuard.exe
    echo =========================================================
    echo.
    echo Launching PayGuard...
    start "" "dist\PayGuard.exe"
) else (
    echo [ERROR] Output executable not found in dist directory.
)

pause

