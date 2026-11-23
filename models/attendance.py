"""
Attendance Model
Manages nurse shift attendance, check-in, check-out, and working hours calculation.
"""

from datetime import datetime, date
from database.database import query_db, execute_db

class Attendance:
    def __init__(self, attendance_id=None, nurse_id=None, shift_id=None, date=None,
                 scheduled_start=None, scheduled_end=None, check_in=None, check_out=None,
                 total_working_hours=0.00, status="PRESENT", nurse_name="", shift_name="",
                 department_name=""):
        self.attendance_id = attendance_id
        self.nurse_id = nurse_id
        self.shift_id = shift_id
        self.date = str(date) if date else ""
        self.scheduled_start = str(scheduled_start) if scheduled_start else ""
        self.scheduled_end = str(scheduled_end) if scheduled_end else ""
        self.check_in = str(check_in) if check_in else None
        self.check_out = str(check_out) if check_out else None
        self.total_working_hours = float(total_working_hours or 0.0)
        self.status = status
        self.nurse_name = nurse_name
        self.shift_name = shift_name
        self.department_name = department_name

    def to_dict(self):
        return {
            "attendance_id": self.attendance_id,
            "nurse_id": self.nurse_id,
            "nurse_name": self.nurse_name,
            "shift_id": self.shift_id,
            "shift_name": self.shift_name,
            "department_name": self.department_name,
            "date": self.date,
            "scheduled_start": self.scheduled_start,
            "scheduled_end": self.scheduled_end,
            "check_in": self.check_in,
            "check_out": self.check_out,
            "total_working_hours": self.total_working_hours,
            "status": self.status
        }

    @classmethod
    def get_by_id(cls, attendance_id):
        sql = """
            SELECT a.*, n.name AS nurse_name, s.shift_name, d.department_name
            FROM attendance a
            JOIN nurses n ON a.nurse_id = n.nurse_id
            JOIN shifts s ON a.shift_id = s.shift_id
            LEFT JOIN departments d ON n.department_id = d.department_id
            WHERE a.attendance_id = %s
        """
        row = query_db(sql, (attendance_id,), one=True)
        return cls(**row) if row else None

    @classmethod
    def get_by_nurse_and_date(cls, nurse_id, target_date):
        sql = """
            SELECT a.*, n.name AS nurse_name, s.shift_name, d.department_name
            FROM attendance a
            JOIN nurses n ON a.nurse_id = n.nurse_id
            JOIN shifts s ON a.shift_id = s.shift_id
            LEFT JOIN departments d ON n.department_id = d.department_id
            WHERE a.nurse_id = %s AND a.date = %s
        """
        row = query_db(sql, (nurse_id, str(target_date)), one=True)
        return cls(**row) if row else None

    @classmethod
    def get_nurse_history(cls, nurse_id, limit=30):
        sql = """
            SELECT a.*, n.name AS nurse_name, s.shift_name, d.department_name
            FROM attendance a
            JOIN nurses n ON a.nurse_id = n.nurse_id
            JOIN shifts s ON a.shift_id = s.shift_id
            LEFT JOIN departments d ON n.department_id = d.department_id
            WHERE a.nurse_id = %s
            ORDER BY a.date DESC
            LIMIT %s
        """
        rows = query_db(sql, (nurse_id, limit))
        return [cls(**row) for row in rows]

    @classmethod
    def get_all(cls, target_date=None, department_id=None):
        sql = """
            SELECT a.*, n.name AS nurse_name, s.shift_name, d.department_name
            FROM attendance a
            JOIN nurses n ON a.nurse_id = n.nurse_id
            JOIN shifts s ON a.shift_id = s.shift_id
            LEFT JOIN departments d ON n.department_id = d.department_id
            WHERE 1=1
        """
        args = []
        if target_date:
            sql += " AND a.date = %s"
            args.append(str(target_date))
        if department_id:
            sql += " AND n.department_id = %s"
            args.append(department_id)
        sql += " ORDER BY a.date DESC, a.check_in DESC"
        rows = query_db(sql, tuple(args))
        return [cls(**row) for row in rows]

    @classmethod
    def record_check_in(cls, nurse_id, shift_id, att_date, sched_start, sched_end, check_in_dt, status="PRESENT"):
        sql = """
            INSERT INTO attendance (nurse_id, shift_id, date, scheduled_start, scheduled_end, check_in, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        att_id = execute_db(sql, (nurse_id, shift_id, str(att_date), str(sched_start), str(sched_end), str(check_in_dt), status))
        return cls.get_by_id(att_id)

    @classmethod
    def record_check_out(cls, attendance_id, check_out_dt, working_hours, status=None):
        if status:
            sql = """
                UPDATE attendance
                SET check_out = %s, total_working_hours = %s, status = %s
                WHERE attendance_id = %s
            """
            execute_db(sql, (str(check_out_dt), working_hours, status, attendance_id))
        else:
            sql = """
                UPDATE attendance
                SET check_out = %s, total_working_hours = %s
                WHERE attendance_id = %s
            """
            execute_db(sql, (str(check_out_dt), working_hours, attendance_id))
        return cls.get_by_id(attendance_id)

    @classmethod
    def get_summary_stats(cls, target_date=None):
        if not target_date:
            target_date = date.today().isoformat()
        sql = """
            SELECT 
                COUNT(*) AS total_records,
                SUM(CASE WHEN check_in IS NOT NULL THEN 1 ELSE 0 END) AS present_count,
                SUM(CASE WHEN status = 'LATE' THEN 1 ELSE 0 END) AS late_count,
                SUM(CASE WHEN check_out IS NOT NULL THEN 1 ELSE 0 END) AS checked_out_count,
                COALESCE(SUM(total_working_hours), 0.0) AS total_hours
            FROM attendance
            WHERE date = %s
        """
        row = query_db(sql, (str(target_date),), one=True)
        return row or {
            "total_records": 0,
            "present_count": 0,
            "late_count": 0,
            "checked_out_count": 0,
            "total_hours": 0.0
        }
