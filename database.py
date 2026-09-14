# -*- coding: utf-8 -*-
"""
database.py - SQLite database management module for PayGuard.
Stores permanent employee profiles, monthly payroll sheets, and loan balance rollover records.
Ensures the database is saved adjacent to the executable, avoiding temporary directories.
"""

import sqlite3
import os
import sys
from datetime import datetime

def get_app_data_dir():
    """
    Get the appropriate storage directory for SQLite database and export files across platforms (Windows, macOS, Linux),
    taking frozen packages and system permissions into account.
    """
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        
        # On macOS inside a .app bundle, Contents/MacOS is read-only
        if sys.platform == "darwin" and "Contents/MacOS" in exe_dir:
            user_data = os.path.expanduser("~/Library/Application Support/PayGuard")
            os.makedirs(user_data, exist_ok=True)
            return user_data
            
        # Check write permissions adjacent to the executable
        try:
            test_file = os.path.join(exe_dir, ".pg_write_test")
            with open(test_file, "w") as f:
                f.write("ok")
            os.remove(test_file)
            return exe_dir
        except Exception:
            # Fallback to platform user data directory if direct write is denied
            if sys.platform == "win32":
                base = os.getenv("APPDATA", os.path.expanduser("~"))
                user_data = os.path.join(base, "PayGuard")
            elif sys.platform == "darwin":
                user_data = os.path.expanduser("~/Library/Application Support/PayGuard")
            else:
                user_data = os.path.expanduser("~/.local/share/PayGuard")
            os.makedirs(user_data, exist_ok=True)
            return user_data
    else:
        # In standard development environment
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_app_data_dir()
DB_PATH = os.path.join(BASE_DIR, "payroll.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # 1. Permanent employees table
    c.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            emp_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            job_title TEXT DEFAULT '',
            basic_salary REAL DEFAULT 0.0,
            work_hours REAL DEFAULT 10.0,
            total_advance REAL DEFAULT 0.0,
            remaining_advance REAL DEFAULT 0.0,
            hire_date TEXT DEFAULT '',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    for col in ["total_advance", "remaining_advance"]:
        try:
            c.execute(f"ALTER TABLE employees ADD COLUMN {col} REAL DEFAULT 0.0")
        except:
            pass

    # 2. Monthly payroll archive table
    c.execute('''
        CREATE TABLE IF NOT EXISTS monthly_sheets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month_name TEXT UNIQUE,
            year INTEGER,
            month INTEGER,
            days_in_month INTEGER,
            total_logs INTEGER DEFAULT 0,
            start_date TEXT,
            end_date TEXT,
            friday_factor REAL DEFAULT 2.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. Monthly employee payroll records table
    c.execute('''
        CREATE TABLE IF NOT EXISTS employee_payroll_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sheet_id INTEGER,
            month_name TEXT,
            emp_id TEXT,
            name TEXT,
            basic_salary REAL DEFAULT 0.0,
            work_hours REAL DEFAULT 10.0,
            day_rate REAL DEFAULT 0.0,
            hour_rate REAL DEFAULT 0.0,
            attended_days REAL DEFAULT 0.0,
            vacation_days REAL DEFAULT 0.0,
            friday_days REAL DEFAULT 0.0,
            absence_days REAL DEFAULT 0.0,
            overtime_hours REAL DEFAULT 0.0,
            overtime_amount REAL DEFAULT 0.0,
            friday_extra_amount REAL DEFAULT 0.0,
            bonus REAL DEFAULT 0.0,
            total_advance REAL DEFAULT 0.0,
            advance REAL DEFAULT 0.0,
            remaining_advance REAL DEFAULT 0.0,
            deduction REAL DEFAULT 0.0,
            net_salary REAL DEFAULT 0.0,
            notes TEXT DEFAULT '',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(sheet_id) REFERENCES monthly_sheets(id),
            UNIQUE(month_name, emp_id)
        )
    ''')

    for col in ["total_advance", "remaining_advance"]:
        try:
            c.execute(f"ALTER TABLE employee_payroll_records ADD COLUMN {col} REAL DEFAULT 0.0")
        except:
            pass

    conn.commit()
    conn.close()

def get_all_employees():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM employees WHERE is_active = 1 ORDER BY name ASC")
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows

def get_employee_by_id(emp_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM employees WHERE emp_id = ?", (str(emp_id),))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def save_or_update_employee(emp_id, name, basic_salary, work_hours=10.0, total_advance=0.0, remaining_advance=0.0, job_title='', hire_date=''):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO employees (emp_id, name, basic_salary, work_hours, total_advance, remaining_advance, job_title, hire_date, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(emp_id) DO UPDATE SET
            name = excluded.name,
            basic_salary = excluded.basic_salary,
            work_hours = excluded.work_hours,
            total_advance = excluded.total_advance,
            remaining_advance = excluded.remaining_advance,
            job_title = CASE WHEN excluded.job_title != '' THEN excluded.job_title ELSE employees.job_title END,
            hire_date = CASE WHEN excluded.hire_date != '' THEN excluded.hire_date ELSE employees.hire_date END,
            updated_at = CURRENT_TIMESTAMP
    ''', (str(emp_id), name.strip(), float(basic_salary), float(work_hours), float(total_advance), float(remaining_advance), job_title.strip(), hire_date.strip()))
    conn.commit()
    conn.close()

def save_monthly_sheet(month_name, year, month, days_in_month, total_logs, start_date, end_date, friday_factor=2.0):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO monthly_sheets (month_name, year, month, days_in_month, total_logs, start_date, end_date, friday_factor)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(month_name) DO UPDATE SET
            days_in_month = excluded.days_in_month,
            total_logs = excluded.total_logs,
            start_date = excluded.start_date,
            end_date = excluded.end_date,
            friday_factor = excluded.friday_factor
    ''', (month_name, year, month, days_in_month, total_logs, start_date, end_date, friday_factor))
    sheet_id = c.lastrowid
    conn.commit()
    conn.close()
    return sheet_id

def get_all_monthly_sheets():
    """Retrieve list of all archived monthly sheets."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM monthly_sheets ORDER BY id DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_monthly_sheet_by_name(month_name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM monthly_sheets WHERE month_name = ?", (month_name,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def save_payroll_record(rec):
    conn = get_connection()
    c = conn.cursor()
    
    if "total_advance" not in rec:
        rec["total_advance"] = 0.0
    if "remaining_advance" not in rec:
        rec["remaining_advance"] = max(0.0, float(rec["total_advance"]) - float(rec.get("advance", 0.0)))

    c.execute('''
        INSERT INTO employee_payroll_records (
            month_name, emp_id, name, basic_salary, work_hours,
            day_rate, hour_rate, attended_days, vacation_days,
            friday_days, absence_days, overtime_hours, overtime_amount,
            friday_extra_amount, bonus, total_advance, advance, remaining_advance, deduction, net_salary, notes, updated_at
        ) VALUES (
            :month_name, :emp_id, :name, :basic_salary, :work_hours,
            :day_rate, :hour_rate, :attended_days, :vacation_days,
            :friday_days, :absence_days, :overtime_hours, :overtime_amount,
            :friday_extra_amount, :bonus, :total_advance, :advance, :remaining_advance, :deduction, :net_salary, :notes, CURRENT_TIMESTAMP
        )
        ON CONFLICT(month_name, emp_id) DO UPDATE SET
            name = excluded.name,
            basic_salary = excluded.basic_salary,
            work_hours = excluded.work_hours,
            day_rate = excluded.day_rate,
            hour_rate = excluded.hour_rate,
            attended_days = excluded.attended_days,
            vacation_days = excluded.vacation_days,
            friday_days = excluded.friday_days,
            absence_days = excluded.absence_days,
            overtime_hours = excluded.overtime_hours,
            overtime_amount = excluded.overtime_amount,
            friday_extra_amount = excluded.friday_extra_amount,
            bonus = excluded.bonus,
            total_advance = excluded.total_advance,
            advance = excluded.advance,
            remaining_advance = excluded.remaining_advance,
            deduction = excluded.deduction,
            net_salary = excluded.net_salary,
            notes = excluded.notes,
            updated_at = CURRENT_TIMESTAMP
    ''', rec)

    # Update remaining loan balance in permanent employee profile for next month
    c.execute('''
        UPDATE employees 
        SET remaining_advance = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE emp_id = ?
    ''', (rec["remaining_advance"], str(rec["emp_id"])))

    conn.commit()
    conn.close()

def get_saved_payroll_by_month(month_name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM employee_payroll_records WHERE month_name = ? ORDER BY name ASC", (month_name,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def delete_monthly_sheet(month_name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM employee_payroll_records WHERE month_name = ?", (month_name,))
    c.execute("DELETE FROM monthly_sheets WHERE month_name = ?", (month_name,))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database successfully initialized at:", DB_PATH)

