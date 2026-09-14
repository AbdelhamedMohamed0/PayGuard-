# -*- coding: utf-8 -*-
"""
test_payroll.py - اختبار شامل لكافة وظائف النظام ورصيد السلف
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
    print("--- 1. اختبار قاعدة البيانات ورصيد السلف ---")
    database.init_db()
    # اختبار موظف عليه سلفة 20,000 ج.م
    database.save_or_update_employee(
        emp_id="1",
        name="Ebrahim Yasser",
        basic_salary=7500.0,
        work_hours=10.0,
        total_advance=20000.0,
        remaining_advance=20000.0
    )
    emp = database.get_employee_by_id("1")
    assert emp is not None, "الموظف غير موجود!"
    assert emp["basic_salary"] == 7500.0, "الراتب غير متطابق!"
    assert emp["total_advance"] == 20000.0, "رصيد السلفة غير متطابق!"
    print("✓ تم حفظ رصيد السلفة للموظف في قاعدة البيانات بنجاح: 20,000 ج.م")

    print("\n--- 2. اختبار قراءة ملف البصمة شهر.txt ---")
    file_path = os.path.join(os.path.dirname(__file__), "شهر.txt")
    with open(file_path, "rb") as f:
        data = f.read()
    
    parsed = zkteco_parser.parse_zkteco_file(data)
    assert "error" not in parsed, f"خطأ في التحليل: {parsed.get('error')}"
    meta = parsed["meta"]
    emps = parsed["employees"]
    print(f"✓ الشهر المكتشف: {meta['month_name']}")
    print(f"✓ عدد الموظفين المكتشفين: {len(emps)}")
    print(f"✓ إجمالي سجلات البصمة: {meta['total_logs']}")
    assert len(emps) > 0, "لم يتم استخراج موظفين!"

    print("\n--- 3. اختبار المعادلة الحسابية وخصم قسط السلفة ---")
    # اختبار سلفة 20,000 ج.م، خصم 2,000 ج.م، المتبقي 18,000 ج.م
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
    print(f"✓ إجمالي رصيد السلفة: {calc['total_advance']} ج.م")
    print(f"✓ المخصوم من السلفة هذا الشهر: {calc['advance']} ج.م")
    print(f"✓ المتبقي من السلفة للشهر القادم: {calc['remaining_advance']} ج.م")
    print(f"✓ صافي الراتب بعد خصم قسط السلفة: {calc['net_salary']} ج.م (المتوقع: 4800.0 ج.م)")
    assert calc['remaining_advance'] == 18000.0, "خطأ في حساب السلفة المتبقية!"
    assert calc['net_salary'] == 4800.0, f"الصافي غير متطابق! الناتج: {calc['net_salary']}"
    print("✓ حساب السلف والمتبقي وصافي الراتب تم بنجاح 100%.")

    # اختبار تجاوز قسط السلفة للرصيد (سلفة 500، خصم 600 -> المتبقي -100)
    calc_neg = payroll_engine.calculate_employee_payroll(
        basic_salary=5000,
        work_hours=10,
        days_in_month=30,
        attended_days=30,
        total_advance=500.0,
        advance=600.0
    )
    assert calc_neg['remaining_advance'] == -100.0, f"خطأ في احتساب السلفة بالسالب! الناتج: {calc_neg['remaining_advance']}"
    print("✓ تم التحقق بنجاح من احتساب رصيد السلفة بالسالب عند تجاوز الخصم للرصيد (500 - 600 = -100 ج.م)")

    print("\n--- 4. اختبار حفظ تسديد السلفة في السجل وتحديث بطاقة الموظف ---")
    database.save_payroll_record({
        "month_name": "يوليو 2026",
        "emp_id": "1",
        "name": "Ebrahim Yasser",
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
        "notes": "خصم قسط 2000"
    })
    updated_emp = database.get_employee_by_id("1")
    assert updated_emp["remaining_advance"] == 18000.0, "لم يتم ترحيل رصيد السلفة المتبقي في بطاقة الموظف!"
    print(f"✓ تم ترحيل الرصيد المتبقي ({updated_emp['remaining_advance']} ج.م) للشهر القادم في بطاقة الموظف أوتوماتيكياً!")

    print("\n--- 5. اختبار تصدير ملف Excel بأعمدة السلف ---")
    excel_path = os.path.join(os.path.dirname(__file__), "test_export.xlsx")
    test_records = [
        {
            "emp_id": "1",
            "name": "Ebrahim Yasser",
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
            "notes": "تم الاختبار"
        }
    ]
    exporter.export_payroll_to_excel(test_records, "يوليو 2026", excel_path)
    assert os.path.exists(excel_path), "لم يتم إنشاء ملف Excel!"
    print(f"✓ تم إنشاء ملف Excel بنجاح متضمناً أعمدة السلف.")

    print("\n--- 6. اختبار توليد ملف PDF الفردي باسم الموظف والشهر ---")
    import pdf_generator
    test_emp = test_records[0]
    test_emp["daily_details"] = [
        {"date": "2026-07-01", "is_friday": False, "check_in": "08:30", "check_out": "18:30", "worked_hours": 10.0, "punches_count": 2}
    ]
    pdf_res = pdf_generator.generate_employee_pdf(test_emp, "يوليو 2026", days_in_month=31)
    assert pdf_res["success"], "فشل توليد تقرير PDF للموظف!"
    assert os.path.exists(pdf_res["filepath"]), "الملف المنشأ غير موجود على القرص!"
    assert "Ebrahim_Yasser" in pdf_res["filename"] or "Ebrahim Yasser" in pdf_res["filename"], "اسم الملف لا يحتوي على اسم الموظف!"
    print(f"✓ تم توليد التقرير بنجاح باسم: {pdf_res['filename']}")
    print("\n--- 7. اختبار توليد ملف PDF باللغة الإنجليزية (English Payslip) ---")
    pdf_res_en = pdf_generator.generate_employee_pdf(test_emp, "July 2026", days_in_month=31, lang="en")
    assert pdf_res_en["success"], "فشل توليد تقرير PDF باللغة الإنجليزية!"
    assert os.path.exists(pdf_res_en["filepath"]), "الملف المنشأ غير موجود على القرص!"
    assert "Salary_Slip" in pdf_res_en["filename"], "اسم الملف الإنجليزي غير مطابق للنمط المطلوب!"
    print(f"✓ تم توليد تقرير PDF الإنجليزي بنجاح: {pdf_res_en['filename']}")

    print("\n--- 8. اختبار تصدير ملف Excel باللغة الإنجليزية (English Excel Sheet) ---")
    excel_path_en = os.path.join(os.path.dirname(__file__), "test_export_en.xlsx")
    exporter.export_payroll_to_excel(test_records, "July 2026", excel_path_en, lang="en")
    assert os.path.exists(excel_path_en), "لم يتم إنشاء ملف Excel الإنجليزي!"
    print(f"✓ تم إنشاء ملف Excel باللغة الإنجليزية بنجاح: {excel_path_en}")

    print("\n==============================================")
    print("🎉 جميع الاختبارات الثمانية بما فيها دعم اللغتين نجحت 100%!")
    print("==============================================")

if __name__ == '__main__':
    run_tests()
