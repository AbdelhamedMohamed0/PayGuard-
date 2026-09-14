# -*- coding: utf-8 -*-
"""
exporter.py - Excel report generation module for PayGuard.
Formats and exports comprehensive monthly payroll sheets, earnings, and loan balances.
"""

import os
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

def export_payroll_to_excel(records, month_name, filepath, lang="ar"):
    """
    Export payroll records to a formatted Excel workbook in Arabic or English with loan tracking columns.
    """
    is_en = (str(lang).lower() == "en")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Payroll {month_name}" if is_en else f"مرتبات {month_name}"
    
    # Sheet reading direction: RTL for Arabic, LTR for English
    ws.views.sheetView[0].rightToLeft = not is_en

    # 1. Report title block
    ws.merge_cells("A1:V1")
    title_cell = ws["A1"]
    title_cell.value = f"PayGuard — Monthly Payroll Sheet & Loan Balances ({month_name})" if is_en else f"PayGuard — كشف كروكي المرتبات الشهري ورصيد السلف ({month_name})"
    title_cell.font = Font(name="Arial", size=16, bold=True, color="FFFFFF")
    title_cell.fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 40

    # 2. Column headers
    if is_en:
        headers = [
            "#", "Emp ID", "Employee Name", "Basic Salary", "Work Hours",
            "Day Rate", "Hour Rate", "Attendance", "Vacation", "Friday", "Absence",
            "Total Paid Days", "Overtime (Hrs)", "Overtime Pay", "Friday Allowance", "Bonus",
            "Total Loan", "Loan Repaid", "Remaining Loan", "Deductions", "Net Salary (EGP)", "Notes"
        ]
    else:
        headers = [
            "م", "كود الموظف", "اسم الموظف", "الراتب الأساسي", "ساعات العمل",
            "أجر اليوم", "أجر الساعة", "الحضور", "إجازات", "جمعة", "غياب",
            "إجمالي الحضور", "س +", "أجر الإضافي", "بدل الجمعة", "بونص",
            "إجمالي السلفة", "تسديد سلفة (مخصوم)", "المتبقي من السلفة", "خصومات", "صافي الراتب (ج.م)", "ملاحظات"
        ]
    
    ws.append([]) # Blank separator row
    ws.append(headers)
    ws.row_dimensions[3].height = 28

    header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    
    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=3, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border

    # 3. Insert employee records
    start_row = 4
    for idx, r in enumerate(records, 1):
        total_adv = float(r.get("total_advance") or 0.0)
        paid_adv = float(r.get("advance") or 0.0)
        rem_adv = float(r.get("remaining_advance") if r.get("remaining_advance") is not None else (total_adv - paid_adv))

        row_data = [
            idx,
            r.get("emp_id", ""),
            r.get("name", ""),
            r.get("basic_salary", 0.0),
            r.get("work_hours", 10.0),
            r.get("day_rate", 0.0),
            r.get("hour_rate", 0.0),
            r.get("attended_days", 0.0),
            r.get("vacation_days", 0.0),
            r.get("friday_days", 0.0),
            r.get("absence_days", 0.0),
            r.get("base_attendance_pay", 0.0),
            r.get("overtime_hours", 0.0),
            r.get("overtime_amount", 0.0),
            r.get("friday_extra_amount", 0.0),
            r.get("bonus", 0.0),
            total_adv,
            paid_adv,
            rem_adv,
            r.get("deduction", 0.0),
            r.get("net_salary", 0.0),
            r.get("notes", "")
        ]
        ws.append(row_data)
        current_row = start_row + idx - 1
        ws.row_dimensions[current_row].height = 22

        is_even = (idx % 2 == 0)
        row_bg = "F8FAFC" if is_even else "FFFFFF"
        row_fill = PatternFill(start_color=row_bg, end_color=row_bg, fill_type="solid")

        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=current_row, column=col_idx)
            cell.fill = row_fill
            cell.border = thin_border
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.font = Font(name="Arial", size=10)

            if col_idx == 3:
                cell.alignment = Alignment(horizontal="left" if is_en else "right", vertical="center")
                cell.font = Font(name="Arial", size=10, bold=True)
            
            if col_idx in [4, 6, 7, 12, 14, 15, 16, 17, 18, 19, 20, 21]:
                cell.number_format = '#,##0.00'
            
            # Highlight loan columns
            if col_idx in [17, 18, 19] and (total_adv > 0 or paid_adv > 0):
                cell.font = Font(name="Arial", size=10, bold=True, color="991B1B")

            # Highlight net salary column
            if col_idx == 21:
                cell.font = Font(name="Arial", size=11, bold=True, color="15803D")
                cell.fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")

    # 4. Total summary row
    last_row = start_row + len(records)
    ws.cell(row=last_row, column=1).value = "Total" if is_en else "الإجمالي"
    ws.cell(row=last_row, column=1).font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    ws.cell(row=last_row, column=1).fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    ws.cell(row=last_row, column=1).alignment = Alignment(horizontal="center", vertical="center")
    
    ws.merge_cells(start_row=last_row, start_column=1, end_row=last_row, end_column=3)

    for c in range(1, len(headers) + 1):
        cell = ws.cell(row=last_row, column=c)
        cell.border = thin_border
        cell.fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
        cell.font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
        cell.alignment = Alignment(horizontal="center", vertical="center")

    sum_cols = [4, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
    for sc in sum_cols:
        col_letter = get_column_letter(sc)
        total_cell = ws.cell(row=last_row, column=sc)
        total_cell.value = f"=SUM({col_letter}{start_row}:{col_letter}{last_row-1})"
        total_cell.number_format = '#,##0.00' if sc not in [8, 9, 10, 11] else '#,##0'

    ws.row_dimensions[last_row].height = 28

    # 5. Auto-fit column widths
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or "")
            if len(val_str) > max_len:
                max_len = len(val_str)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 11)
    
    ws.column_dimensions["C"].width = 24

    wb.save(filepath)
    return filepath
