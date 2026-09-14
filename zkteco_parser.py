# -*- coding: utf-8 -*-
"""
zkteco_parser.py - Biometric punch log parser for ZKTeco devices.
Supports UTF-8 and CP1256 encodings, multi-punch deduplication, daily hours, and Friday tracking.
"""

import os
from datetime import datetime, time, timedelta

ARABIC_MONTHS = [
    "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
    "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
]

def fix_mojibake(text):
    """
    Fix mojibake Arabic characters emitted by older ZKTeco firmware.
    e.g. ÍÖæÑ -> حضور and ÅäÕÑÇÝ -> انصراف.
    """
    try:
        # If string contains latin1 bytes originally from CP1256
        fixed = text.encode('latin1').decode('cp1256')
        return fixed
    except:
        return text

def parse_datetime(dt_str):
    """
    Parse date-time string into a Python datetime object.
    """
    dt_str = dt_str.strip()
    formats = [
        "%d/%m/%Y %I:%M:%S %p",
        "%d/%m/%Y %I:%M %p",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%d-%m-%Y %H:%M:%S"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue
    return None

def parse_zkteco_file(file_bytes_or_str):
    """
    Parse raw punch log file content into structured employee records.
    """
    if isinstance(file_bytes_or_str, bytes):
        # Attempt UTF-8 first, fallback to CP1256 (Windows Arabic default) or latin1
        try:
            content = file_bytes_or_str.decode('utf-8')
        except UnicodeDecodeError:
            try:
                content = file_bytes_or_str.decode('cp1256')
            except UnicodeDecodeError:
                content = file_bytes_or_str.decode('latin1', errors='ignore')
    else:
        content = file_bytes_or_str

    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if not lines:
        return {"error": "الملف فارغ أو غير صالح"}

    raw_records = []
    header_skipped = False

    for line in lines:
        parts = [p.strip() for p in line.split('\t')]
        if len(parts) < 4:
            # Fallback to comma separation if tab delimiter is absent
            parts = [p.strip() for p in line.split(',') if p.strip()]
            if len(parts) < 4:
                continue

        # Skip header row
        first_part_fixed = fix_mojibake(parts[0])
        if "الإداره" in first_part_fixed or "الإدارة" in first_part_fixed or "Name" in parts[1] or "Department" in parts[0]:
            header_skipped = True
            continue

        emp_name = fix_mojibake(parts[1])
        emp_id = str(parts[2]).strip()
        timestamp_str = parts[3]
        action_type = fix_mojibake(parts[4]) if len(parts) > 4 else "حضور"

        # Normalize action types
        if "ÍÖæÑ" in action_type or "حضور" in action_type:
            action_type = "حضور"
        elif "ÅäÕÑÇÝ" in action_type or "إنصراف" in action_type or "انصراف" in action_type:
            action_type = "انصراف"

        dt = parse_datetime(timestamp_str)
        if dt:
            raw_records.append({
                "emp_id": emp_id,
                "name": emp_name,
                "datetime": dt,
                "date": dt.date(),
                "time": dt.time(),
                "action": action_type
            })

    if not raw_records:
        return {"error": "لم نتمكن من استخراج بصمات صالحة من الملف. تأكد من صيغة الملف."}

    # Sort records chronologically
    raw_records.sort(key=lambda x: x["datetime"])

    # Infer month stats and date range
    all_dates = [r["date"] for r in raw_records]
    min_date = min(all_dates)
    max_date = max(all_dates)

    # Determine primary month and year
    detected_month_num = min_date.month
    detected_year = min_date.year
    month_key = f"{detected_year:04d}-{detected_month_num:02d}"
    month_name = f"{ARABIC_MONTHS[detected_month_num - 1]} {detected_year}"

    # Calculate actual days in month
    if detected_month_num in [1, 3, 5, 7, 8, 10, 12]:
        days_in_month = 31
    elif detected_month_num == 2:
        # Check leap year
        is_leap = (detected_year % 4 == 0 and detected_year % 100 != 0) or (detected_year % 400 == 0)
        days_in_month = 29 if is_leap else 28
    else:
        days_in_month = 30

    # Group punch records by employee and date
    # structure: employees[emp_id] = { 'name': ..., 'days': { date: [records] } }
    employees_data = {}

    for r in raw_records:
        eid = r["emp_id"]
        if eid not in employees_data:
            employees_data[eid] = {
                "emp_id": eid,
                "name": r["name"],
                "days": {}
            }
        # Update employee name if a longer/more complete string is found
        if len(r["name"]) > len(employees_data[eid]["name"]):
            employees_data[eid]["name"] = r["name"]

        d = r["date"]
        if d not in employees_data[eid]["days"]:
            employees_data[eid]["days"][d] = []
        employees_data[eid]["days"][d].append(r)

    # Summarize employee attendance
    parsed_employees = []

    for eid, info in employees_data.items():
        attended_dates = set()
        friday_dates = set()
        total_worked_hours = 0.0
        daily_details = []

        for d, recs in info["days"].items():
            attended_dates.add(d)
            # Check Friday (in Python Monday=0, Friday=4)
            is_friday = (d.weekday() == 4)
            if is_friday:
                friday_dates.add(d)

            # Identify earliest check-in and latest check-out
            recs_sorted = sorted(recs, key=lambda x: x["datetime"])
            check_in = recs_sorted[0]["datetime"]
            check_out = recs_sorted[-1]["datetime"] if len(recs_sorted) > 1 else None

            worked_hrs = 0.0
            if check_out and check_out > check_in:
                worked_hrs = round((check_out - check_in).total_seconds() / 3600.0, 2)
            
            total_worked_hours += worked_hrs

            daily_details.append({
                "date": d.strftime("%Y-%m-%d"),
                "is_friday": is_friday,
                "check_in": check_in.strftime("%I:%M %p"),
                "check_out": check_out.strftime("%I:%M %p") if check_out else "لم يبصم",
                "worked_hours": worked_hrs,
                "punches_count": len(recs)
            })

        attended_days_count = len(attended_dates)
        friday_days_count = len(friday_dates)
        absence_days_count = max(0, days_in_month - attended_days_count)

        parsed_employees.append({
            "emp_id": eid,
            "name": info["name"],
            "attended_days": attended_days_count,
            "friday_days": friday_days_count,
            "absence_days": absence_days_count,
            "total_worked_hours": round(total_worked_hours, 2),
            "daily_details": daily_details
        })

    # Sort employees alphabetically by name
    parsed_employees.sort(key=lambda x: x["name"])

    return {
        "meta": {
            "month_key": month_key,
            "month_name": month_name,
            "year": detected_year,
            "month": detected_month_num,
            "days_in_month": days_in_month,
            "total_logs": len(raw_records),
            "employees_count": len(parsed_employees),
            "start_date": min_date.strftime("%d/%m/%Y"),
            "end_date": max_date.strftime("%d/%m/%Y")
        },
        "employees": parsed_employees
    }
