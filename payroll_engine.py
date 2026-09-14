# -*- coding: utf-8 -*-
"""
payroll_engine.py - Core payroll calculation engine for PayGuard.
Calculates employee daily/hourly rates, attendance earnings, overtime, loan deductions, and net salary.
"""

def calculate_employee_payroll(
    basic_salary: float,
    work_hours: float,
    days_in_month: int,
    attended_days: float,
    vacation_days: float = 0.0,
    friday_days: float = 0.0,
    absence_days: float = 0.0,
    friday_factor: float = 2.0,
    overtime_hours: float = 0.0,
    bonus: float = 0.0,
    total_advance: float = 0.0,
    advance: float = 0.0,
    deduction: float = 0.0
):
    """
    Calculate employee earnings, deductions, loan balance rollovers, and net payable salary.
    """
    basic_salary = float(basic_salary or 0.0)
    work_hours = float(work_hours or 10.0)
    if work_hours <= 0:
        work_hours = 10.0
    days_in_month = int(days_in_month or 30)
    if days_in_month <= 0:
        days_in_month = 30

    attended_days = float(attended_days or 0.0)
    vacation_days = float(vacation_days or 0.0)
    friday_days = float(friday_days or 0.0)
    absence_days = float(absence_days or 0.0)
    friday_factor = float(friday_factor or 2.0)
    overtime_hours = float(overtime_hours or 0.0)
    bonus = float(bonus or 0.0)
    total_advance = float(total_advance or 0.0)
    advance = float(advance or 0.0)
    deduction = float(deduction or 0.0)

    # 1. Daily and hourly rate
    day_rate = basic_salary / days_in_month
    hour_rate = day_rate / work_hours

    # 2. Total paid attendance days (actual attended + paid vacations)
    paid_days = attended_days + vacation_days
    base_attendance_pay = paid_days * day_rate

    # 3. Friday work extra premium
    friday_extra_factor = max(0.0, friday_factor - 1.0)
    friday_extra_amount = friday_days * friday_extra_factor * day_rate

    # 4. Overtime pay calculation
    overtime_amount = overtime_hours * hour_rate

    # 5. Gross earnings (attendance, overtime, allowances, bonuses)
    total_attendance_and_bonus = base_attendance_pay + friday_extra_amount + overtime_amount + bonus

    # 6. Remaining loan balance (supports negative values for over-deductions)
    remaining_advance = total_advance - advance

    # 7. Total deductions
    total_deductions = advance + deduction

    # 8. Net payable salary
    net_salary = total_attendance_and_bonus - total_deductions
    if net_salary < 0:
        net_salary = 0.0

    return {
        "basic_salary": round(basic_salary, 2),
        "work_hours": round(work_hours, 2),
        "days_in_month": days_in_month,
        "day_rate": round(day_rate, 4),
        "hour_rate": round(hour_rate, 4),
        "attended_days": round(attended_days, 2),
        "vacation_days": round(vacation_days, 2),
        "friday_days": round(friday_days, 2),
        "absence_days": round(absence_days, 2),
        "paid_days": round(paid_days, 2),
        "base_attendance_pay": round(base_attendance_pay, 2),
        "friday_extra_amount": round(friday_extra_amount, 2),
        "overtime_hours": round(overtime_hours, 2),
        "overtime_amount": round(overtime_amount, 2),
        "bonus": round(bonus, 2),
        "total_advance": round(total_advance, 2),
        "advance": round(advance, 2),
        "remaining_advance": round(remaining_advance, 2),
        "deduction": round(deduction, 2),
        "total_attendance_and_bonus": round(total_attendance_and_bonus, 2),
        "total_deductions": round(total_deductions, 2),
        "net_salary": round(net_salary, 2)
    }

if __name__ == '__main__':
    # Test calculation model:
    # Loan: 20,000 EGP, Repayment: 2,000 EGP, Remaining: 18,000 EGP
    res = calculate_employee_payroll(
        basic_salary=7000,
        work_hours=10,
        days_in_month=31,
        attended_days=26,
        vacation_days=4,
        friday_days=0,
        absence_days=1,
        bonus=25.81,
        total_advance=20000,
        advance=2000,
        deduction=0.0035
    )
    print("Total Loan Balance:", res["total_advance"], "EGP")
    print("Repaid This Month:", res["advance"], "EGP")
    print("Remaining for Next Month:", res["remaining_advance"], "EGP")
    print("Net Payable Salary:", res["net_salary"], "EGP")

