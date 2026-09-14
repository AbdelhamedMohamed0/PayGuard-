# -*- coding: utf-8 -*-
"""
app.py - Main entry point and backend server for PayGuard.
Integrates SQLite database, ZKTeco punch parser, payroll engine, and historical monthly archives.
"""

import os
import sys
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file

import database
import zkteco_parser
import payroll_engine
import exporter
import pdf_generator

def get_template_dir():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'templates')
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

app = Flask(__name__, template_folder=get_template_dir())

# Active memory cache for the currently loaded month
CURRENT_MONTH_CACHE = {
    "meta": {},
    "employees": []
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_history')
def get_history():
    """Fetch list of archived monthly sheets."""
    sheets = database.get_all_monthly_sheets()
    return jsonify({"sheets": sheets})

@app.route('/load_month')
def load_month():
    """Load full payroll data for an archived month."""
    month_name = request.args.get('month')
    if not month_name:
        return jsonify({"error": "يرجى تحديد الشهر"}), 400

    sheet_meta = database.get_monthly_sheet_by_name(month_name)
    if not sheet_meta:
        return jsonify({"error": "الشهر غير موجود في الأرشيف"}), 404

    records = database.get_saved_payroll_by_month(month_name)
    
    # Update in-memory cache
    CURRENT_MONTH_CACHE["meta"] = sheet_meta
    CURRENT_MONTH_CACHE["employees"] = records

    return jsonify({
        "meta": sheet_meta,
        "employees": records
    })

@app.route('/delete_month', methods=['POST'])
def delete_month():
    month_name = request.json.get("month_name")
    if month_name:
        database.delete_monthly_sheet(month_name)
        return jsonify({"status": "success"})
    return jsonify({"error": "اسم الشهر مطلوب"}), 400

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "يرجى اختيار ملف بصمة صالح"}), 400

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return jsonify({"error": "لم يتم اختيار أي ملف"}), 400

    raw_bytes = uploaded_file.read()
    parse_result = zkteco_parser.parse_zkteco_file(raw_bytes)

    if "error" in parse_result:
        return jsonify({"error": parse_result["error"]}), 400

    meta = parse_result["meta"]
    parsed_emps = parse_result["employees"]

    # Save monthly sheet metadata in SQLite
    sheet_id = database.save_monthly_sheet(
        month_name=meta["month_name"],
        year=meta["year"],
        month=meta["month"],
        days_in_month=meta["days_in_month"],
        total_logs=meta["total_logs"],
        start_date=meta["start_date"],
        end_date=meta["end_date"],
        friday_factor=2.0
    )

    # Enrich and evaluate each employee record against local database (new vs existing)
    enriched_employees = []
    for emp in parsed_emps:
        eid = str(emp["emp_id"])
        db_emp = database.get_employee_by_id(eid)

        if db_emp and db_emp["basic_salary"] > 0:
            is_new = False
            basic_salary = float(db_emp["basic_salary"])
            work_hours = float(db_emp["work_hours"] or 10.0)
            emp_name = db_emp["name"] or emp["name"]
            # Carried forward loan balance from previous month
            total_advance = float(db_emp.get("remaining_advance") or db_emp.get("total_advance") or 0.0)
        else:
            is_new = True
            basic_salary = 0.0
            work_hours = 10.0
            emp_name = emp["name"]
            total_advance = 0.0

        advance_this_month = 0.0

        calc = payroll_engine.calculate_employee_payroll(
            basic_salary=basic_salary,
            work_hours=work_hours,
            days_in_month=meta["days_in_month"],
            attended_days=emp["attended_days"],
            vacation_days=0.0,
            friday_days=emp["friday_days"],
            absence_days=emp["absence_days"],
            friday_factor=2.0,
            overtime_hours=0.0,
            bonus=0.0,
            total_advance=total_advance,
            advance=advance_this_month,
            deduction=0.0
        )

        emp_record = {
            "emp_id": eid,
            "name": emp_name,
            "is_new": is_new,
            "basic_salary": basic_salary,
            "work_hours": work_hours,
            "attended_days": emp["attended_days"],
            "vacation_days": 0.0,
            "friday_days": emp["friday_days"],
            "absence_days": emp["absence_days"],
            "overtime_hours": 0.0,
            "bonus": 0.0,
            "total_advance": total_advance,
            "advance": advance_this_month,
            "remaining_advance": calc["remaining_advance"],
            "deduction": 0.0,
            "day_rate": calc["day_rate"],
            "hour_rate": calc["hour_rate"],
            "base_attendance_pay": calc["base_attendance_pay"],
            "friday_extra_amount": calc["friday_extra_amount"],
            "overtime_amount": calc["overtime_amount"],
            "net_salary": calc["net_salary"],
            "daily_details": emp.get("daily_details", [])
        }

        # Automatically persist employee record to current month sheet
        database.save_payroll_record({
            "month_name": meta["month_name"],
            "emp_id": eid,
            "name": emp_name,
            "basic_salary": basic_salary,
            "work_hours": work_hours,
            "day_rate": calc["day_rate"],
            "hour_rate": calc["hour_rate"],
            "attended_days": emp["attended_days"],
            "vacation_days": 0.0,
            "friday_days": emp["friday_days"],
            "absence_days": emp["absence_days"],
            "overtime_hours": 0.0,
            "overtime_amount": 0.0,
            "friday_extra_amount": calc["friday_extra_amount"],
            "bonus": 0.0,
            "total_advance": total_advance,
            "advance": advance_this_month,
            "remaining_advance": calc["remaining_advance"],
            "deduction": 0.0,
            "net_salary": calc["net_salary"],
            "notes": ""
        })

        enriched_employees.append(emp_record)

    CURRENT_MONTH_CACHE["meta"] = meta
    CURRENT_MONTH_CACHE["employees"] = enriched_employees

    return jsonify({
        "meta": meta,
        "employees": enriched_employees
    })

@app.route('/save_employee', methods=['POST'])
def save_employee_endpoint():
    data = request.json or {}
    emp = data.get("emp")
    month_name = data.get("month_name") or CURRENT_MONTH_CACHE.get("meta", {}).get("month_name", "شهر غير محدد")

    if not emp or not emp.get("emp_id"):
        return jsonify({"error": "بيانات غير مكتملة"}), 400

    eid = str(emp["emp_id"])
    name = emp.get("name", "")
    salary = float(emp.get("basic_salary") or 0.0)
    hours = float(emp.get("work_hours") or 10.0)
    total_advance = float(emp.get("total_advance") or 0.0)
    advance = float(emp.get("advance") or 0.0)
    remaining_advance = total_advance - advance

    # 1. Update permanent employee record (for future months)
    database.save_or_update_employee(
        emp_id=eid,
        name=name,
        basic_salary=salary,
        work_hours=hours,
        total_advance=total_advance,
        remaining_advance=remaining_advance
    )

    # 2. Update and persist monthly payroll record immediately
    database.save_payroll_record({
        "month_name": month_name,
        "emp_id": eid,
        "name": name,
        "basic_salary": salary,
        "work_hours": hours,
        "day_rate": float(emp.get("day_rate") or 0.0),
        "hour_rate": float(emp.get("hour_rate") or 0.0),
        "attended_days": float(emp.get("attended_days") or 0.0),
        "vacation_days": float(emp.get("vacation_days") or 0.0),
        "friday_days": float(emp.get("friday_days") or 0.0),
        "absence_days": float(emp.get("absence_days") or 0.0),
        "overtime_hours": float(emp.get("overtime_hours") or 0.0),
        "overtime_amount": float(emp.get("overtime_amount") or 0.0),
        "friday_extra_amount": float(emp.get("friday_extra_amount") or 0.0),
        "bonus": float(emp.get("bonus") or 0.0),
        "total_advance": total_advance,
        "advance": advance,
        "remaining_advance": remaining_advance,
        "deduction": float(emp.get("deduction") or 0.0),
        "net_salary": float(emp.get("net_salary") or 0.0),
        "notes": emp.get("notes", "")
    })

    # Update in-memory cache
    for cached_emp in CURRENT_MONTH_CACHE["employees"]:
        if cached_emp["emp_id"] == eid:
            cached_emp.update(emp)
            cached_emp["total_advance"] = total_advance
            cached_emp["advance"] = advance
            cached_emp["remaining_advance"] = remaining_advance
            cached_emp["is_new"] = False
            break

    return jsonify({"status": "success"})

@app.route('/save_all', methods=['POST'])
def save_all_endpoint():
    data = request.json or {}
    month_name = data.get("month_name") or CURRENT_MONTH_CACHE.get("meta", {}).get("month_name", "شهر غير محدد")
    employees = data.get("employees") or CURRENT_MONTH_CACHE.get("employees", [])

    if not employees:
        return jsonify({"error": "لا توجد بيانات موظفين لحفظها"}), 400

    meta = CURRENT_MONTH_CACHE.get("meta", {})
    database.save_monthly_sheet(
        month_name=month_name,
        year=meta.get("year", 2026),
        month=meta.get("month", 1),
        days_in_month=meta.get("days_in_month", 30),
        total_logs=meta.get("total_logs", len(employees)),
        start_date=meta.get("start_date", ""),
        end_date=meta.get("end_date", ""),
        friday_factor=float(data.get("friday_factor") or meta.get("friday_factor") or 2.0)
    )

    for emp in employees:
        eid = str(emp["emp_id"])
        name = emp.get("name", "")
        salary = float(emp.get("basic_salary") or 0.0)
        hours = float(emp.get("work_hours") or 10.0)
        total_advance = float(emp.get("total_advance") or 0.0)
        advance = float(emp.get("advance") or 0.0)
        remaining_advance = total_advance - advance

        database.save_or_update_employee(
            emp_id=eid,
            name=name,
            basic_salary=salary,
            work_hours=hours,
            total_advance=total_advance,
            remaining_advance=remaining_advance
        )

        database.save_payroll_record({
            "month_name": month_name,
            "emp_id": eid,
            "name": name,
            "basic_salary": salary,
            "work_hours": hours,
            "day_rate": float(emp.get("day_rate") or 0.0),
            "hour_rate": float(emp.get("hour_rate") or 0.0),
            "attended_days": float(emp.get("attended_days") or 0.0),
            "vacation_days": float(emp.get("vacation_days") or 0.0),
            "friday_days": float(emp.get("friday_days") or 0.0),
            "absence_days": float(emp.get("absence_days") or 0.0),
            "overtime_hours": float(emp.get("overtime_hours") or 0.0),
            "overtime_amount": float(emp.get("overtime_amount") or 0.0),
            "friday_extra_amount": float(emp.get("friday_extra_amount") or 0.0),
            "bonus": float(emp.get("bonus") or 0.0),
            "total_advance": total_advance,
            "advance": advance,
            "remaining_advance": remaining_advance,
            "deduction": float(emp.get("deduction") or 0.0),
            "net_salary": float(emp.get("net_salary") or 0.0),
            "notes": emp.get("notes", "")
        })

    CURRENT_MONTH_CACHE["meta"]["month_name"] = month_name
    CURRENT_MONTH_CACHE["employees"] = employees

    return jsonify({"status": "success", "count": len(employees)})

@app.route('/export_excel')
def export_excel_endpoint():
    month = request.args.get('month') or CURRENT_MONTH_CACHE.get("meta", {}).get("month_name", "الشهر")
    lang = request.args.get('lang', 'ar')
    employees = CURRENT_MONTH_CACHE.get("employees", [])

    if not employees or CURRENT_MONTH_CACHE.get("meta", {}).get("month_name") != month:
        employees = database.get_saved_payroll_by_month(month)

    if not employees:
        return "لا توجد بيانات لتصديرها لهذا الشهر!", 404

    is_en = (str(lang).lower() == "en")
    filename = f"Payroll_{month.replace(' ', '_')}.xlsx" if is_en else f"كشف_مرتبات_{month.replace(' ', '_')}.xlsx"
    filepath = os.path.join(database.BASE_DIR, filename)
    exporter.export_payroll_to_excel(employees, month, filepath, lang=lang)

    return send_file(filepath, as_attachment=True)

@app.route('/employee_slip/<emp_id>')
def employee_slip_endpoint(emp_id):
    """Render individual employee HTML payslip ready for instant printing."""
    month = request.args.get('month') or CURRENT_MONTH_CACHE.get("meta", {}).get("month_name", "الشهر")
    lang = request.args.get('lang', 'ar')
    meta = CURRENT_MONTH_CACHE.get("meta", {})
    days_in_month = meta.get("days_in_month", 30)
    friday_factor = meta.get("friday_factor", 2.0)

    emp = None
    for e in CURRENT_MONTH_CACHE.get("employees", []):
        if str(e.get("emp_id")) == str(emp_id):
            emp = e
            break
    
    if not emp:
        records = database.get_saved_payroll_by_month(month)
        for r in records:
            if str(r.get("emp_id")) == str(emp_id):
                emp = r
                break
    
    if not emp:
        return "الموظف غير موجود في بيانات هذا الشهر", 404

    html = pdf_generator.build_employee_slip_html(emp, month, days_in_month=days_in_month, friday_factor=friday_factor, lang=lang)
    return html

@app.route('/export_employee_pdf', methods=['POST', 'GET'])
def export_employee_pdf_endpoint():
    """Generate individual employee PDF payslip and automatically open on Windows."""
    data = request.json or {}
    emp_id = request.args.get('emp_id') or data.get('emp_id')
    month = request.args.get('month') or data.get('month_name') or CURRENT_MONTH_CACHE.get("meta", {}).get("month_name", "الشهر")
    lang = request.args.get('lang') or data.get('lang', 'ar')
    
    meta = CURRENT_MONTH_CACHE.get("meta", {})
    days_in_month = meta.get("days_in_month", 30)
    friday_factor = float(data.get("friday_factor") or meta.get("friday_factor") or 2.0)

    emp = data.get("emp")
    if not emp:
        for e in CURRENT_MONTH_CACHE.get("employees", []):
            if str(e.get("emp_id")) == str(emp_id):
                emp = dict(e)
                break
        if not emp:
            records = database.get_saved_payroll_by_month(month)
            for r in records:
                if str(r.get("emp_id")) == str(emp_id):
                    emp = dict(r)
                    break

    if not emp:
        return jsonify({"error": "الموظف غير موجود"}), 404

    # Retrieve daily punches log from cache if available
    if "daily_details" not in emp:
        for ce in CURRENT_MONTH_CACHE.get("employees", []):
            if str(ce.get("emp_id")) == str(emp.get("emp_id")) and "daily_details" in ce:
                emp["daily_details"] = ce["daily_details"]
                break

    result = pdf_generator.generate_employee_pdf(emp, month, days_in_month=days_in_month, friday_factor=friday_factor, lang=lang)
    
    opened = False
    if os.name == 'nt' and os.path.exists(result["filepath"]):
        try:
            os.startfile(result["filepath"])
            opened = True
        except Exception:
            pass

    return jsonify({
        "status": "success",
        "filename": result["filename"],
        "filepath": result["filepath"],
        "opened": opened,
        "is_html": result["html_fallback"]
    })

@app.route('/download_employee_pdf')
def download_employee_pdf_endpoint():
    """Download generated employee PDF payslip."""
    filename = request.args.get('filename')
    if not filename:
        return "اسم الملف غير محدد", 400
    folder = os.path.join(database.BASE_DIR, "تقارير_الموظفين_PDF")
    filepath = os.path.join(folder, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True, download_name=filename)
    return "الملف غير موجود", 404

@app.route('/open_pdf_folder')
def open_pdf_folder_endpoint():
    """Open PDF slips directory in Windows Explorer, macOS Finder, or Linux file manager."""
    import subprocess
    folder = os.path.join(database.BASE_DIR, "تقارير_الموظفين_PDF")
    os.makedirs(folder, exist_ok=True)
    if os.name == 'nt':
        os.startfile(folder)
    elif sys.platform == 'darwin':
        subprocess.run(['open', folder])
    else:
        subprocess.run(['xdg-open', folder])
    return jsonify({"status": "success", "folder": folder})


def start_gui():
    """Launch desktop application with native webview GUI window."""
    database.init_db()

    try:
        import webview
        server_thread = threading.Thread(target=lambda: app.run(port=5892, debug=False, use_reloader=False), daemon=True)
        server_thread.start()

        webview.create_window(
            title='PayGuard - Smart Payroll & Attendance System',
            url='http://127.0.0.1:5892',
            width=1280,
            height=890,
            resizable=True,
            min_size=(980, 680)
        )
        webview.start()
    except Exception as e:
        import webbrowser
        print(f"Opening PayGuard in default browser: {e}")
        threading.Timer(1.0, lambda: webbrowser.open('http://127.0.0.1:5892')).start()
        app.run(port=5892, debug=False)

if __name__ == '__main__':
    start_gui()

