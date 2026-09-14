# -*- coding: utf-8 -*-
"""
pdf_generator.py - وحدة إنشاء تقارير PDF الفردية لمفردات مرتب كل موظف
تنشئ تقريراً بصيغة PDF وقسيمة راتب A4 منسقة واحترافية باللغة العربية أو الإنجليزية
"""

import os
import sys
import re
import shutil
import tempfile
import subprocess
from datetime import datetime

def find_system_browser():
    """البحث عن متصفح Chromium / Chrome / Edge على أنظمة ويندوز وماك ولينكس للطباعة الصامتة إلى PDF"""
    candidates = [
        # Windows
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        # macOS
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        # Linux
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/usr/bin/microsoft-edge",
        "/usr/bin/microsoft-edge-stable",
        "/snap/bin/chromium",
        # System PATH lookups
        shutil.which("msedge"),
        shutil.which("chrome"),
        shutil.which("google-chrome"),
        shutil.which("google-chrome-stable"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        shutil.which("microsoft-edge"),
        shutil.which("brave-browser")
    ]
    for c in candidates:
        if c and os.path.isfile(c) and os.access(c, os.X_OK if sys.platform != 'win32' else os.R_OK):
            return c
    return None

def build_employee_slip_html(emp, month_name, days_in_month=30, friday_factor=2.0, lang="ar"):
    """بناء كود HTML احترافي لقسيمة الراتب ومفردات المرتب باللغة العربية أو الإنجليزية مطابق للطباعة A4"""
    is_en = (str(lang).lower() == "en")
    
    name = emp.get("name", "موظف" if not is_en else "Employee")
    emp_id = emp.get("emp_id", "-")
    basic_salary = float(emp.get("basic_salary") or 0.0)
    work_hours = float(emp.get("work_hours") or 10.0)
    attended_days = float(emp.get("attended_days") or 0.0)
    vacation_days = float(emp.get("vacation_days") or 0.0)
    friday_days = float(emp.get("friday_days") or 0.0)
    absence_days = float(emp.get("absence_days") or 0.0)
    overtime_hours = float(emp.get("overtime_hours") or 0.0)
    bonus = float(emp.get("bonus") or 0.0)
    
    total_advance = float(emp.get("total_advance") or 0.0)
    advance = float(emp.get("advance") or 0.0)
    remaining_advance = float(emp.get("remaining_advance") if emp.get("remaining_advance") is not None else (total_advance - advance))
    deduction = float(emp.get("deduction") or 0.0)

    # الحسابات
    day_rate = basic_salary / days_in_month if days_in_month > 0 else 0.0
    hour_rate = day_rate / work_hours if work_hours > 0 else 0.0
    paid_days = attended_days + vacation_days
    base_attendance_pay = paid_days * day_rate
    friday_extra_amount = friday_days * max(0.0, friday_factor - 1.0) * day_rate
    overtime_amount = overtime_hours * hour_rate
    total_earnings = base_attendance_pay + friday_extra_amount + overtime_amount + bonus

    absence_deduction = absence_days * day_rate
    total_deductions = advance + deduction

    net_salary = float(emp.get("net_salary") if emp.get("net_salary") is not None else max(0.0, total_earnings - total_deductions))

    daily_details = emp.get("daily_details") or []
    
    if is_en:
        current_time_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        currency = "EGP"
        doc_dir = "ltr"
        doc_lang = "en"
        font_family = "'Segoe UI', -apple-system, BlinkMacSystemFont, 'Inter', Roboto, sans-serif"
    else:
        current_time_str = datetime.now().strftime("%Y/%m/%d - %I:%M %p").replace("AM", "صباحاً").replace("PM", "مساءً")
        currency = "ج.م"
        doc_dir = "rtl"
        doc_lang = "ar"
        font_family = "'Cairo', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"

    # صفوف سجل البصمة اليومية
    punches_rows_html = ""
    if daily_details:
        for idx, d in enumerate(daily_details, 1):
            is_fri = d.get("is_friday", False)
            row_bg = "#f0fdf4" if is_fri else ("#ffffff" if idx % 2 == 1 else "#f8fafc")
            if is_en:
                fri_badge = '<span style="color:#0369a1; font-weight:bold;">Friday ✓</span>' if is_fri else 'Regular'
                hours_str = f"{d.get('worked_hours', 0)} hrs"
            else:
                fri_badge = '<span style="color:#0369a1; font-weight:bold;">جمعة ✓</span>' if is_fri else 'عادي'
                hours_str = f"{d.get('worked_hours', 0)} س"

            punches_rows_html += f"""
            <tr style="background-color: {row_bg};">
                <td style="padding: 6px 10px; border: 1px solid #e2e8f0; text-align: center;">{idx}</td>
                <td style="padding: 6px 10px; border: 1px solid #e2e8f0; text-align: center;">{d.get('date', '-')}</td>
                <td style="padding: 6px 10px; border: 1px solid #e2e8f0; text-align: center;">{fri_badge}</td>
                <td style="padding: 6px 10px; border: 1px solid #e2e8f0; text-align: center; color:#15803d; font-weight:600;">{d.get('check_in', '-')}</td>
                <td style="padding: 6px 10px; border: 1px solid #e2e8f0; text-align: center; color:#b91c1c; font-weight:600;">{d.get('check_out', '-')}</td>
                <td style="padding: 6px 10px; border: 1px solid #e2e8f0; text-align: center; font-weight:bold;">{hours_str}</td>
                <td style="padding: 6px 10px; border: 1px solid #e2e8f0; text-align: center;">{d.get('punches_count', 0)}</td>
            </tr>
            """

    # ترجمة العناوين والنصوص
    t = {
        "title": f"Payslip Statement — {name} — {month_name}" if is_en else f"مفردات مرتب — {name} — {month_name}",
        "sys_title": "PayGuard — Smart Payroll & Attendance System" if is_en else "نظام PayGuard الذكي للمرتبات وحضور البصمة",
        "slip_subtitle": "Monthly Employee Payslip — Detailed Statement" if is_en else "قسيمة راتب الموظف الشهرية — كشف استحقاق فردي",
        "date_lbl": "Report Date: " if is_en else "تاريخ التقرير: ",
        "print_btn": "🖨️ Print Now (Print / PDF)" if is_en else "🖨️ طباعة الآن (Print / PDF)",
        "close_btn": "✕ Close Window" if is_en else "✕ إغلاق النافذة",
        "emp_name": "Employee Name:" if is_en else "اسم الموظف:",
        "emp_id": "Employee ID / Code:" if is_en else "كود الموظف / البصمة:",
        "month_days": "Month Days:" if is_en else "أيام الشهر الفعلية:",
        "work_hours": "Official Work Hours:" if is_en else "ساعات العمل المقررة:",
        "basic_sal": "Monthly Basic Salary:" if is_en else "الراتب الأساسي الشهري:",
        "day_rate": "Daily Rate:" if is_en else "قيمة أجر اليوم:",
        "hour_rate": "Hourly Rate:" if is_en else "قيمة أجر الساعة:",
        "attended_days": "Actual Attendance:" if is_en else "أيام الحضور الفعلي:",
        "absence_days": "Absence Days:" if is_en else "أيام الغياب:",
        "friday_days": "Friday Attendance:" if is_en else "حضور أيام الجمعة:",
        "overtime_hours": "Overtime (Hrs):" if is_en else "ساعات إضافية (س +):",
        "vacation_days": "Paid Vacations:" if is_en else "إجازات مدفوعة:",
        "unit_days": "days" if is_en else "يوم",
        "unit_hrs_per_day": "hrs / day" if is_en else "ساعة / يوم",
        "unit_hrs": "hrs" if is_en else "ساعة",
        "factor_lbl": f"factor {friday_factor:g}x" if is_en else f"معامل {friday_factor:g}x",
        "title_earn": "➕ Earnings & Allowances" if is_en else "➕ الاستحقاقات والبدلات (له)",
        "base_pay_lbl": "Attendance & Paid Vacations Pay" if is_en else "أجر أيام الحضور والإجازات",
        "friday_pay_lbl": "Friday Work Allowance" if is_en else "بدل عمل أيام الجمعة (ضعف الأجر)",
        "overtime_pay_lbl": "Overtime Pay" if is_en else "أجر الساعات الإضافية (س +)",
        "bonus_lbl": "Bonuses & Allowances" if is_en else "البونص والمكافآت والبدلات",
        "gross_lbl": "Total Earnings (Gross)" if is_en else "إجمالي الاستحقاقات (Gross)",
        "title_deduct": "➖ Deductions & Loans" if is_en else "➖ الاستقطاعات والخصومات (عليه)",
        "loan_deduct_lbl": "Monthly Loan Installment" if is_en else "قسط تسديد السلفة لهذا الشهر",
        "penalty_lbl": "Penalties, Deductions & Delays" if is_en else "الجزاءات والخصومات والتأخير",
        "abs_deduct_lbl": "Absence Days (Deducted)" if is_en else "أيام الغياب (مخصومة من الأساسي)",
        "total_deduct_lbl": "Total Deductions" if is_en else "إجمالي المستقطع من المرتب",
        "adv_prev_lbl": "Previous Loan Balance" if is_en else "إجمالي رصيد السلفة السابق",
        "adv_paid_lbl": "Repaid This Month (Deducted)" if is_en else "المسدد هذا الشهر (المخصوم)",
        "adv_rem_lbl": "Remaining Loan for Next Month" if is_en else "الرصيد المتبقي للشهر القادم",
        "net_sal_lbl": f"Net Payable Salary for {month_name}:" if is_en else f"صافي الراتب المستحق للصرف لشهر {month_name}:",
        "punches_title": "Daily Attendance Punch Log for the Month:" if is_en else "سجل تفاصيل بصمات الحضور والانصراف خلال الشهر:",
        "th_num": "#" if is_en else "م",
        "th_date": "Date" if is_en else "التاريخ",
        "th_day": "Day" if is_en else "اليوم",
        "th_in": "Check-in" if is_en else "وقت الدخول",
        "th_out": "Check-out" if is_en else "وقت الخروج",
        "th_hours": "Worked Hours" if is_en else "ساعات العمل",
        "th_count": "Punches" if is_en else "عدد البصمات",
        "sign_emp": "Employee Receipt Signature" if is_en else "توقيع الموظف بالاستلام",
        "sign_acc": "Payroll Accountant Signature" if is_en else "توقيع المحاسب / مسؤول المرتبات",
        "sign_mgr": "General Management Approval" if is_en else "اعتماد الإدارة العامة"
    }

    html = f"""<!DOCTYPE html>
<html lang="{doc_lang}" dir="{doc_dir}">
<head>
    <meta charset="UTF-8">
    <title>{t['title']}</title>
    <style>
        @page {{
            size: A4 portrait;
            margin: 12mm 15mm;
        }}
        * {{
            box-sizing: border-box;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }}
        body {{
            font-family: {font_family};
            margin: 0;
            padding: 10px;
            background-color: #ffffff;
            color: #1e293b;
            direction: {doc_dir};
            font-size: 12px;
            line-height: 1.5;
        }}
        .slip-container {{
            max-width: 800px;
            margin: 0 auto;
            border: 2px solid #1e3a8a;
            border-radius: 12px;
            padding: 20px 24px;
            background: #ffffff;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 15px;
            margin-bottom: 15px;
        }}
        .header-title {{
            font-size: 20px;
            font-weight: 800;
            color: #1e3a8a;
            margin: 0 0 4px 0;
        }}
        .header-subtitle {{
            font-size: 13px;
            color: #64748b;
            font-weight: 600;
        }}
        .header-badge {{
            background: #1e3a8a;
            color: #ffffff;
            padding: 8px 16px;
            border-radius: 8px;
            text-align: center;
        }}
        .header-badge .month-val {{
            font-size: 16px;
            font-weight: 800;
        }}
        .header-badge .date-val {{
            font-size: 10px;
            opacity: 0.85;
            margin-top: 2px;
        }}
        
        /* كارت بيانات الموظف */
        .emp-card {{
            background: #f8fafc;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 16px;
        }}
        .emp-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px 14px;
        }}
        .emp-item-label {{
            font-size: 11px;
            color: #64748b;
            font-weight: 600;
            margin-bottom: 2px;
        }}
        .emp-item-val {{
            font-size: 13px;
            font-weight: 800;
            color: #0f172a;
        }}
        .emp-name-highlight {{
            font-size: 16px;
            color: #1e3a8a;
            font-weight: 900;
        }}

        /* جداول الحسابات والاستحقاقات */
        .calc-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 16px;
        }}
        .calc-table-box {{
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            overflow: hidden;
        }}
        .table-title {{
            padding: 8px 12px;
            font-size: 13px;
            font-weight: 800;
            text-align: center;
        }}
        .title-earn {{
            background: #f0fdf4;
            color: #166534;
            border-bottom: 1px solid #bbf7d0;
        }}
        .title-deduct {{
            background: #fef2f2;
            color: #991b1b;
            border-bottom: 1px solid #fecaca;
        }}
        .calc-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .calc-table td {{
            padding: 7px 12px;
            border-bottom: 1px solid #f1f5f9;
            font-size: 12px;
        }}
        .calc-table td:last-child {{
            text-align: {'right' if is_en else 'left'};
            font-weight: 700;
            direction: ltr;
        }}
        .calc-table tr:last-child td {{
            border-bottom: none;
            font-weight: 800;
            background: #f8fafc;
            font-size: 13px;
        }}

        /* رصيد السلف */
        .advance-summary-box {{
            background: #fff7ed;
            border: 1px solid #fdba74;
            border-radius: 8px;
            padding: 10px 14px;
            margin-bottom: 16px;
            display: flex;
            justify-content: space-around;
            align-items: center;
        }}
        .adv-stat {{
            text-align: center;
        }}
        .adv-stat-lbl {{
            font-size: 11px;
            font-weight: 700;
            color: #9a3412;
        }}
        .adv-stat-val {{
            font-size: 15px;
            font-weight: 900;
            color: #c2410c;
            margin-top: 2px;
        }}

        /* الصافي النهائي المستحق */
        .net-salary-box {{
            background: linear-gradient(135deg, #15803d 0%, #166534 100%);
            color: #ffffff;
            border-radius: 10px;
            padding: 14px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            box-shadow: 0 4px 12px rgba(22, 101, 52, 0.15);
        }}
        .net-lbl {{
            font-size: 16px;
            font-weight: 800;
        }}
        .net-val {{
            font-size: 24px;
            font-weight: 900;
            letter-spacing: 0.5px;
        }}

        /* جدول البصمات */
        .punches-section {{
            margin-bottom: 16px;
        }}
        .punches-heading {{
            font-size: 12px;
            font-weight: 800;
            color: #334155;
            margin-bottom: 6px;
        }}
        .punches-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 11px;
        }}
        .punches-table th {{
            background: #1e3a8a;
            color: #ffffff;
            padding: 6px 10px;
            font-weight: 700;
            border: 1px solid #1e3a8a;
        }}

        /* التوقيعات */
        .signatures {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-top: 25px;
            padding-top: 15px;
            border-top: 1px dashed #cbd5e1;
            text-align: center;
        }}
        .sign-title {{
            font-size: 11px;
            font-weight: 700;
            color: #475569;
            margin-bottom: 35px;
        }}
        .sign-line {{
            border-bottom: 1px solid #94a3b8;
            width: 80%;
            margin: 0 auto;
        }}

        /* أزرار الشاشة (تختفي عند الطباعة) */
        @media print {{
            .no-print {{
                display: none !important;
            }}
            body {{
                padding: 0;
            }}
            .slip-container {{
                border: none;
                padding: 0;
            }}
        }}
        .screen-buttons {{
            display: flex;
            justify-content: center;
            gap: 12px;
            margin-bottom: 15px;
        }}
        .btn {{
            padding: 8px 18px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
            border: none;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        .btn-print {{
            background: #1e3a8a;
            color: #ffffff;
        }}
        .btn-close {{
            background: #e2e8f0;
            color: #1e293b;
        }}
    </style>
</head>
<body>

    <div class="no-print screen-buttons">
        <button class="btn btn-print" onclick="window.print()">{t['print_btn']}</button>
        <button class="btn btn-close" onclick="window.close()">{t['close_btn']}</button>
    </div>

    <div class="slip-container">
        <!-- الترويسة -->
        <div class="header">
            <div>
                <h1 class="header-title">{t['sys_title']}</h1>
                <div class="header-subtitle">{t['slip_subtitle']}</div>
            </div>
            <div class="header-badge">
                <div class="month-val">{month_name}</div>
                <div class="date-val">{t['date_lbl']}{current_time_str}</div>
            </div>
        </div>

        <!-- كارت بيانات الموظف والدوام -->
        <div class="emp-card">
            <div class="emp-grid">
                <div>
                    <div class="emp-item-label">{t['emp_name']}</div>
                    <div class="emp-item-val emp-name-highlight">{name}</div>
                </div>
                <div>
                    <div class="emp-item-label">{t['emp_id']}</div>
                    <div class="emp-item-val">{emp_id}</div>
                </div>
                <div>
                    <div class="emp-item-label">{t['month_days']}</div>
                    <div class="emp-item-val">{days_in_month} {t['unit_days']}</div>
                </div>
                <div>
                    <div class="emp-item-label">{t['work_hours']}</div>
                    <div class="emp-item-val">{work_hours:g} {t['unit_hrs_per_day']}</div>
                </div>

                <div>
                    <div class="emp-item-label">{t['basic_sal']}</div>
                    <div class="emp-item-val" style="color:#0369a1;">{basic_salary:,.2f} {currency}</div>
                </div>
                <div>
                    <div class="emp-item-label">{t['day_rate']}</div>
                    <div class="emp-item-val">{day_rate:,.2f} {currency}</div>
                </div>
                <div>
                    <div class="emp-item-label">{t['hour_rate']}</div>
                    <div class="emp-item-val">{hour_rate:,.2f} {currency}</div>
                </div>
                <div>
                    <div class="emp-item-label">{t['attended_days']}</div>
                    <div class="emp-item-val" style="color:#15803d;">{attended_days:g} {t['unit_days']}</div>
                </div>

                <div>
                    <div class="emp-item-label">{t['absence_days']}</div>
                    <div class="emp-item-val" style="color:#b91c1c;">{absence_days:g} {t['unit_days']}</div>
                </div>
                <div>
                    <div class="emp-item-label">{t['friday_days']}</div>
                    <div class="emp-item-val">{friday_days:g} {t['unit_days']} ({t['factor_lbl']})</div>
                </div>
                <div>
                    <div class="emp-item-label">{t['overtime_hours']}</div>
                    <div class="emp-item-val">{overtime_hours:g} {t['unit_hrs']}</div>
                </div>
                <div>
                    <div class="emp-item-label">{t['vacation_days']}</div>
                    <div class="emp-item-val">{vacation_days:g} {t['unit_days']}</div>
                </div>
            </div>
        </div>

        <!-- جدول الاستحقاقات والاستقطاعات -->
        <div class="calc-grid">
            <!-- الاستحقاقات -->
            <div class="calc-table-box">
                <div class="table-title title-earn">{t['title_earn']}</div>
                <table class="calc-table">
                    <tr>
                        <td>{t['base_pay_lbl']}</td>
                        <td>{base_attendance_pay:,.2f} {currency}</td>
                    </tr>
                    <tr>
                        <td>{t['friday_pay_lbl']}</td>
                        <td>{friday_extra_amount:,.2f} {currency}</td>
                    </tr>
                    <tr>
                        <td>{t['overtime_pay_lbl']}</td>
                        <td>{overtime_amount:,.2f} {currency}</td>
                    </tr>
                    <tr>
                        <td>{t['bonus_lbl']}</td>
                        <td>{bonus:,.2f} {currency}</td>
                    </tr>
                    <tr>
                        <td>{t['gross_lbl']}</td>
                        <td style="color:#166534;">{total_earnings:,.2f} {currency}</td>
                    </tr>
                </table>
            </div>

            <!-- الاستقطاعات -->
            <div class="calc-table-box">
                <div class="table-title title-deduct">{t['title_deduct']}</div>
                <table class="calc-table">
                    <tr>
                        <td>{t['loan_deduct_lbl']}</td>
                        <td style="color:#c2410c;">{advance:,.2f} {currency}</td>
                    </tr>
                    <tr>
                        <td>{t['penalty_lbl']}</td>
                        <td style="color:#991b1b;">{deduction:,.2f} {currency}</td>
                    </tr>
                    <tr>
                        <td>{t['abs_deduct_lbl']}</td>
                        <td>{absence_days:g} {t['unit_days']} ({absence_deduction:,.2f} {currency})</td>
                    </tr>
                    <tr>
                        <td>{t['total_deduct_lbl']}</td>
                        <td style="color:#991b1b;">{total_deductions:,.2f} {currency}</td>
                    </tr>
                </table>
            </div>
        </div>

        <!-- قسم متابعة رصيد السلف -->
        <div class="advance-summary-box">
            <div class="adv-stat">
                <div class="adv-stat-lbl">{t['adv_prev_lbl']}</div>
                <div class="adv-stat-val">{total_advance:,.2f} {currency}</div>
            </div>
            <div style="font-size:18px; font-weight:bold; color:#f97316;">—</div>
            <div class="adv-stat">
                <div class="adv-stat-lbl">{t['adv_paid_lbl']}</div>
                <div class="adv-stat-val" style="color:#b91c1c;">{advance:,.2f} {currency}</div>
            </div>
            <div style="font-size:18px; font-weight:bold; color:#f97316;">=</div>
            <div class="adv-stat">
                <div class="adv-stat-lbl">{t['adv_rem_lbl']}</div>
                <div class="adv-stat-val" style="color:{'#dc2626' if remaining_advance < 0 else '#15803d'};">{remaining_advance:,.2f} {currency}</div>
            </div>
        </div>

        <!-- الصافي النهائي المستحق للصرف -->
        <div class="net-salary-box">
            <div class="net-lbl">{t['net_sal_lbl']}</div>
            <div class="net-val">{net_salary:,.2f} {currency}</div>
        </div>

        <!-- جدول تفاصيل البصمات إن وجد -->
        {'<div class="punches-section"><div class="punches-heading">' + t['punches_title'] + '</div><div style="overflow-x:auto;"><table class="punches-table"><thead><tr><th>' + t['th_num'] + '</th><th>' + t['th_date'] + '</th><th>' + t['th_day'] + '</th><th>' + t['th_in'] + '</th><th>' + t['th_out'] + '</th><th>' + t['th_hours'] + '</th><th>' + t['th_count'] + '</th></tr></thead><tbody>' + punches_rows_html + '</tbody></table></div></div>' if punches_rows_html else ''}

        <!-- التوقيعات والاعتماد -->
        <div class="signatures">
            <div>
                <div class="sign-title">{t['sign_emp']}</div>
                <div class="sign-line"></div>
            </div>
            <div>
                <div class="sign-title">{t['sign_acc']}</div>
                <div class="sign-line"></div>
            </div>
            <div>
                <div class="sign-title">{t['sign_mgr']}</div>
                <div class="sign-line"></div>
            </div>
        </div>
    </div>

</body>
</html>"""
    return html

def generate_employee_pdf(emp, month_name, output_dir=None, days_in_month=30, friday_factor=2.0, lang="ar"):
    """
    توليد ملف PDF فعلي باسم الموظف والشهر باللغة العربية أو الإنجليزية
    المسار الافتراضي للملفات: داخل مجلد تقارير_الموظفين_PDF بجوار البرنامج
    """
    is_en = (str(lang).lower() == "en")
    
    if not output_dir:
        from database import BASE_DIR
        output_dir = os.path.join(BASE_DIR, "تقارير_الموظفين_PDF")
    
    os.makedirs(output_dir, exist_ok=True)

    # تنظيف اسم الملف من أي رموز غير مقبولة في نظام ويندوز
    raw_name = emp.get("name") or (f"Employee_{emp.get('emp_id', '0')}" if is_en else f"موظف_{emp.get('emp_id', '0')}")
    safe_name = re.sub(r'[\\/*?:"<>|]', '_', str(raw_name).strip())
    safe_month = re.sub(r'[\\/*?:"<>|]', '_', str(month_name).strip())
    
    if is_en:
        pdf_filename = f"Salary_Slip_{safe_name}_{safe_month}.pdf"
    else:
        pdf_filename = f"مفردات_مرتب_{safe_name}_{safe_month}.pdf"
        
    pdf_path = os.path.join(output_dir, pdf_filename)

    # إنشاء كود الـ HTML
    html_content = build_employee_slip_html(emp, month_name, days_in_month, friday_factor, lang=lang)

    # إنشاء ملف HTML مؤقت
    temp_fd, temp_html_path = tempfile.mkstemp(suffix=".html", prefix="slip_")
    try:
        with open(temp_fd, 'w', encoding='utf-8') as f:
            f.write(html_content)

        browser = find_system_browser()
        if browser:
            # تشغيل المتصفح كـ Headless لطباعة PDF مباشرة وبدون رؤوس/تذييلات المتصفح
            cmd = [
                browser,
                "--headless",
                "--disable-gpu",
                "--no-pdf-header-footer",
                f"--print-to-pdf={pdf_path}",
                temp_html_path
            ]
            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
            if res.returncode == 0 and os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
                return {
                    "success": True,
                    "filename": pdf_filename,
                    "filepath": pdf_path,
                    "html_fallback": False
                }
        
        # في حال عدم وجود المتصفح، نحفظ ملف HTML منسق بنفس الاسم
        fallback_html_name = f"Salary_Slip_{safe_name}_{safe_month}.html" if is_en else f"مفردات_مرتب_{safe_name}_{safe_month}.html"
        fallback_path = os.path.join(output_dir, fallback_html_name)
        with open(fallback_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return {
            "success": True,
            "filename": fallback_html_name,
            "filepath": fallback_path,
            "html_fallback": True
        }

    finally:
        if os.path.exists(temp_html_path):
            try:
                os.remove(temp_html_path)
            except Exception:
                pass
