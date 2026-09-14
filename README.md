# 🛡️ PayGuard — Smart Payroll & Biometric Attendance System

<div align="center">

![PayGuard Banner](https://img.shields.io/badge/PayGuard-Enterprise%20v2.0-blue?style=for-the-badge&logo=shield)
![Python](https://img.shields.io/badge/Python-3.11%2B%20%7C%203.14-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Web%20Backend-black?style=for-the-badge&logo=flask)
![pywebview](https://img.shields.io/badge/GUI-PyWebView%20Desktop-4CAF50?style=for-the-badge)
![Security](https://img.shields.io/badge/Security-PyArmor%20Hardened-red?style=for-the-badge&logo=security)
![Bilingual](https://img.shields.io/badge/Languages-Arabic%20%7C%20English-emerald?style=for-the-badge)

**An intelligent, cross-platform enterprise system for automated biometric attendance parsing, payroll accounting, and employee loan balance governance.**

[Features](#-key-features) • [Architecture](#-project-architecture) • [Downloads](#-ready-to-run-releases) • [Quickstart](#-getting-started) • [CI/CD](#-automated-cicd-pipeline) • [Security](#-security--code-hardening)

</div>

---

## 🌟 Overview

**PayGuard** is a standalone, enterprise-grade desktop payroll application designed to eliminate manual spreadsheet errors by directly processing raw biometric punch logs from **ZKTeco** devices. 

It combines automated attendance analytics, exact financial calculation models, strict employee loan governance, permanent monthly SQLite archiving, and instant generation of publication-grade **A4 PDF payslips** and **Excel workbooks** in both Arabic and English.

---

## ✨ Key Features

### 1. 🔍 Intelligent Biometric Punch Engine
- Directly ingests raw punch logs (`.txt`, `.log`, tab-delimited or comma-delimited) exported from ZKTeco devices (e.g., K14 Pro) and compatible timeclocks.
- Automatically detects month, year, and the exact calendar days (28, 29, 30, or 31 days with leap-year handling).
- Computes daily attendance, multi-punch deduplication (earliest check-in and latest check-out), daily worked hours, Friday attendance, and unexcused absences.

### 2. 💰 Precision Payroll Accounting
- Full floating-point decimal precision across all financial fields (basic salary, hourly rates, daily rates, bonuses, deductions, and loan installments).
- Configurable Friday attendance multiplier (default 2.0x base daily rate).
- Accurate overtime calculation based on employee-specific hourly rates (`basic_salary / days_in_month / work_hours`).
- Real-time gross and net payable salary reconciliation.

### 3. 💳 Loan & Advance Balance Governance
- Automatic monthly rollover: deducts repayments from current salary and permanently updates remaining loan balances in the employee profile for subsequent months.
- **Over-Deduction Guard:** If an installment exceeds the remaining loan balance (e.g., deducting 600 EGP on a 500 EGP balance):
  - Triggers an instant visual warning banner.
  - Requires mandatory manager confirmation before committing.
  - Correctly records negative balances as employee credits (`-100 EGP`).

### 4. 🗄️ Permanent Monthly Archive & Local SQLite Database
- Embedded, zero-configuration SQLite database (`payroll.db`) stored adjacent to the executable (avoiding ephemeral temporary folders).
- Seamless switching between historical payroll sheets with full data restoration.
- Dedicated **Save All** functionality to commit all employee modifications simultaneously.
- Support for adding manual employee profiles without biometric punch logs.

### 5. 📑 Publication-Grade PDF Payslips & Excel Sheets
- **Individual A4 PDF Payslips:** Generates a separate, formatted PDF payslip for each employee named by employee and month (e.g., `Salary_Slip_John_Doe_July_2026.pdf`), complete with daily punch tables, earnings, deductions, and signature blocks.
- **Accounting-Grade Excel Export:** Exports the full monthly payroll sheet with styled headers, alternating row fills, currency formats, and automatic `SUM` formulas.
- Sheet reading direction adapts dynamically (Right-to-Left for Arabic, Left-to-Right for English).

### 6. 🌐 100% Bilingual Interface (Arabic & English)
- Instant one-click language toggle (Arabic / English) in the navigation bar with complete UI realignment (RTL / LTR).
- Crisp typography using `Plus Jakarta Sans` for English and `Cairo` for Arabic.
- User language preference is automatically persisted in `localStorage`.

### 7. 🔒 Code Hardening & Portable Executable
- Source code is obfuscated and hardened using **PyArmor** to protect core business logic and proprietary calculations.
- Bundled with **PyInstaller** into a single, zero-dependency standalone binary (`PayGuard.exe`) that runs on client workstations without requiring Python.

---

## 📂 Project Architecture

```text
payguard/
├── app.py                     # Application entry point and Flask + PyWebView backend
├── database.py                # SQLite database management and schema migrations
├── payroll_engine.py          # Financial calculation engine and rate formulas
├── zkteco_parser.py           # Biometric punch log parser and date range detector
├── exporter.py                # Excel spreadsheet generation engine (openpyxl)
├── pdf_generator.py           # Individual A4 PDF payslip builder (headless browser)
├── test_payroll.py            # Automated test suite (8 comprehensive tests)
├── templates/
│   └── index.html             # PayGuard Enterprise Single-Page Application (SPA)
├── sample_data/
│   └── sample_punches.txt     # Synthetic biometric punch dataset (5 employees, 286 punches)
├── .github/
│   └── workflows/
│       └── build.yml          # Automated multi-platform CI/CD (Windows, macOS, Linux)
├── build_exe.bat              # Local Windows build script with PyArmor + PyInstaller
├── run_app.bat                # Quick development launch script for Windows
├── PayGuard.spec              # PyInstaller multi-platform packaging configuration
├── requirements.txt           # Python library dependencies
├── .gitignore                 # Excludes build caches, databases, and sensitive files
└── README.md                  # Project documentation
```

---

## 📥 Ready-to-Run Releases

Precompiled binaries for each release are automatically published to the **[Releases](../../releases)** page:

| Platform | Download Asset | Execution Method |
|---|---|---|
| **Windows (x64)** | `PayGuard-Windows-x64.exe` | Portable standalone executable (no installation required) |
| **macOS (Universal / Apple Silicon & Intel)** | `PayGuard-macOS-Universal.zip` | Extract archive, open `PayGuard.app` |
| **Linux (x86_64)** | `PayGuard-Linux-x86_64.AppImage` | Grant executable permissions (`chmod +x`) and run |

> ### 🍎 Note for macOS Users:
> Because this application is not signed with an Apple Developer certificate, macOS Gatekeeper may display an *"unidentified developer"* notice on first launch:
> 1. Unzip `PayGuard-macOS-Universal.zip`.
> 2. Right-click on `PayGuard.app` and choose **Open**, then click **Open** in the dialog.
> 3. Alternatively: Go to **System Settings → Privacy & Security** and click **Open Anyway**.

---

## 🚀 Getting Started

### 1. Development Mode
```bash
# 1. Clone the repository
git clone https://github.com/AbdelhamedMohamed0/payguard.git
cd payguard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the automated test suite
python test_payroll.py

# 4. Start the application
python app.py
```

### 2. Building Standalone Binaries Locally

#### Windows:
```cmd
build_exe.bat
:: Or directly using PyInstaller:
pyinstaller --noconfirm PayGuard.spec
```

#### macOS:
```bash
pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm PayGuard.spec
# Generates dist/PayGuard.app
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install -y libgtk-3-dev libgirepository1.0-dev gir1.2-webkit2-4.0
pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm PayGuard.spec
# Generates dist/PayGuard
```

---

## 🔄 Automated CI/CD Pipeline

Cross-platform builds are handled automatically via GitHub Actions in `.github/workflows/build.yml`:
- **Trigger on Git Tag:** Pushing a version tag (e.g., `git tag v2.0.0 && git push origin v2.0.0`) automatically triggers clean builds on Windows, macOS, and Linux runners.
- **Automated Testing:** Each runner executes `python test_payroll.py` before compiling.
- **Release Assets:** Binaries and AppImages are packaged and uploaded directly as GitHub Release assets.
- **Manual Dispatch:** Workflows can also be run manually from the **Actions** tab on GitHub with optional PyArmor obfuscation toggled.

---

## 🛡️ Security & Code Hardening

- **Data Privacy:** Synthetic data is provided in `sample_data/sample_punches.txt`. Real employee punch logs must never be committed to source control.
- **Database Safety:** SQLite database files (`payroll.db`, `*.sqlite3`) are strictly excluded via `.gitignore`.
- **IP Protection:** Commercial deployments utilize PyArmor bytecode obfuscation to protect core calculation algorithms and proprietary features.

---

## 📄 License & Credits

- **Developer:** Abdelhamed Mohamed
- **System:** PayGuard Enterprise Payroll System

