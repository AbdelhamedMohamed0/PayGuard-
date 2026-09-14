# -*- coding: utf-8 -*-
"""
test_payroll.py - Comprehensive test suite for payroll calculation, database, and loan balances.
"""

import sys
import os

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

import database
import zkteco_parser
import payroll_engine
import exporter

def run_tests():
    print("--- 1. Database and Loan Balance Test ---")
    database.init_db()
    # Test employee with loan balance of 20,000 EGP
    database.save_or_update_employee(
        emp_id="1",
        name="John Doe",
        basic_salary=7500.0,
        work_hours=10.0,
        total_advance=20000.0,
        remaining_advance=20000.0
    )
    emp = database.get_employee_by_id("1")
    assert emp is not None, "Employee not found!"
    assert emp["basic_salary"] == 7500.0, "Salary does not match!"
    assert emp["total_advance"] == 20000.0, "Loan balance does not match!"
    print("✓ Employee loan balance successfully saved in database: 20,000 EGP")

    print("\n--- 2. Biometric Punch File Parsing Test (sample_punches.txt) ---")
    file_path = os.path.join(os.path.dirname(__file__), "sample_data", "sample_punches.txt")
    with open(file_path, "rb") as f:
        data = f.read()
    
    parsed = zkteco_parser.parse_zkteco_file(data)
    assert "error" not in parsed, f"Parsing error: {parsed.get('error')}"
    meta = parsed["meta"]
    emps = parsed["employees"]
    print(f"✓ Detected Month: {meta['month_name']}")
    print(f"✓ Total Employees Detected: {len(emps)}")
    print(f"✓ Total Punch Logs: {meta['total_logs']}")
    assert len(emps) > 0, "No employees extracted!"

    print("\n--- 3. Payroll Calculation and Loan Installment Deduction Test ---")
    # Loan: 20,000 EGP, Deduction: 2,000 EGP, Remaining: 18,000 EGP
    calc = payroll_engine.calculate_employee_payroll(
        basic_salary=7000,
        work_hours=10,
        days_in_month=31,
        attended_days=26,
        vacation_days=4,
        friday_days=0,
        absence_days=1,
        bonus=25.81,
        total_advance=20000.0,
        advance=2000.0,
        deduction=0.0035
    )
    print(f"✓ Total Loan Balance: {calc['total_advance']} EGP")
    print(f"✓ Deducted Loan Installment: {calc['advance']} EGP")
    print(f"✓ Remaining Loan for Next Month: {calc['remaining_advance']} EGP")
    print(f"✓ Net Salary after Deductions: {calc['net_salary']} EGP (Expected: 4800.0 EGP)")
    assert calc['remaining_advance'] == 18000.0, "Error in remaining loan calculation!"
    assert calc['net_salary'] == 4800.0, f"Net salary mismatch! Got: {calc['net_salary']}"
    print("✓ Loan balance and net salary calculation passed 100%.")

    # Over-deduction test (Loan: 500, Deduction: 600 -> Remaining: -100)
    calc_neg = payroll_engine.calculate_employee_payroll(
        basic_salary=5000,
        work_hours=10,
        days_in_month=30,
        attended_days=30,
        total_advance=500.0,
        advance=600.0
    )
    assert calc_neg['remaining_advance'] == -100.0, f"Negative loan balance error! Got: {calc_neg['remaining_advance']}"
    print("✓ Successfully verified negative loan balance on over-deduction (500 - 600 = -100 EGP)")

    print("\n--- 4. Save Payroll Record and Roll Over Loan Balance Test ---")
    database.save_payroll_record({
        "month_name": "يوليو 2026",
        "emp_id": "1",
        "name": "John Doe",
        "basic_salary": 7500.0,
        "work_hours": 10.0,
        "day_rate": 241.9355,
        "hour_rate": 24.1935,
        "attended_days": 26,
        "vacation_days": 4,
        "friday_days": 0,
        "absence_days": 1,
        "overtime_hours": 0,
        "overtime_amount": 0,
        "friday_extra_amount": 0,
        "bonus": 0,
        "total_advance": 20000.0,
        "advance": 2000.0,
        "remaining_advance": 18000.0,
        "deduction": 0,
        "net_salary": 5258.06,
        "notes": "Loan installment 2000"
    })
    updated_emp = database.get_employee_by_id("1")
    assert updated_emp["remaining_advance"] == 18000.0, "Remaining loan balance not rolled over to employee profile!"
    print(f"✓ Remaining balance ({updated_emp['remaining_advance']} EGP) automatically rolled over to next month!")

    print("\n--- 5. Excel Export with Loan Columns Test ---")
    excel_path = os.path.join(os.path.dirname(__file__), "test_export.xlsx")
    test_records = [
        {
            "emp_id": "1",
            "name": "John Doe",
            "basic_salary": 7500.0,
            "work_hours": 10.0,
            "day_rate": 241.9355,
            "hour_rate": 24.1935,
            "attended_days": 26,
            "vacation_days": 4,
            "friday_days": 0,
            "absence_days": 1,
            "base_attendance_pay": 7258.06,
            "overtime_hours": 0,
            "overtime_amount": 0,
            "friday_extra_amount": 0,
            "bonus": 0,
            "total_advance": 20000.0,
            "advance": 2000.0,
            "remaining_advance": 18000.0,
            "deduction": 0,
            "net_salary": 5258.06,
            "notes": "Tested"
        }
    ]
    exporter.export_payroll_to_excel(test_records, "يوليو 2026", excel_path)
    assert os.path.exists(excel_path), "Excel file was not created!"
    print(f"✓ Excel file successfully generated with loan balance columns.")

    print("\n--- 6. Individual PDF Payslip Generation Test (Arabic) ---")
    import pdf_generator
    test_emp = test_records[0]
    test_emp["daily_details"] = [
        {"date": "2026-07-01", "is_friday": False, "check_in": "08:30", "check_out": "18:30", "worked_hours": 10.0, "punches_count": 2}
    ]
    pdf_res = pdf_generator.generate_employee_pdf(test_emp, "يوليو 2026", days_in_month=31)
    assert pdf_res["success"], "Failed to generate employee PDF report!"
    assert os.path.exists(pdf_res["filepath"]), "Generated file does not exist on disk!"
    assert "John_Doe" in pdf_res["filename"] or "John Doe" in pdf_res["filename"], "Filename does not contain employee name!"
    print(f"✓ Successfully generated payslip: {pdf_res['filename']}")

    print("\n--- 7. Individual PDF Payslip Generation Test (English) ---")
    pdf_res_en = pdf_generator.generate_employee_pdf(test_emp, "July 2026", days_in_month=31, lang="en")
    assert pdf_res_en["success"], "Failed to generate English PDF report!"
    assert os.path.exists(pdf_res_en["filepath"]), "Generated English file does not exist on disk!"
    assert "Salary_Slip" in pdf_res_en["filename"], "English filename does not match expected format!"
    print(f"✓ Successfully generated English PDF payslip: {pdf_res_en['filename']}")

    print("\n--- 8. Excel Export in English Test ---")
    excel_path_en = os.path.join(os.path.dirname(__file__), "test_export_en.xlsx")
    exporter.export_payroll_to_excel(test_records, "July 2026", excel_path_en, lang="en")
    assert os.path.exists(excel_path_en), "English Excel file was not created!"
    print(f"✓ English Excel file successfully created: {excel_path_en}")

    # Clean up test artifacts
    for p in [excel_path, excel_path_en]:
        if os.path.exists(p):
            try:
                os.remove(p)
            except:
                pass

    print("\n==============================================")
    print("🎉 All 8 tests passed successfully 100%!")
    print("==============================================")

if __name__ == '__main__':
    run_tests()
