"""
Attendance Service
Coordinates nurse shift check-in, check-out, working hours calculation,
duplicate check-in prevention, and late/early/overtime evaluations.
"""

from datetime import datetime, date, time, timedelta
from models.attendance import Attendance
from models.shift import Shift

class AttendanceService:
    @staticmethod
    def get_today_status(nurse_id: int):
        """
        Retrieves today's attendance record, assigned shift, and status flags.
        """
        today_str = date.today().isoformat()
        att = Attendance.get_by_nurse_and_date(nurse_id, today_str)
        shift = Shift.get_nurse_shift(nurse_id, today_str)

        # Build status payload
        is_checked_in = att is not None and att.check_in is not None
        is_checked_out = att is not None and att.check_out is not None

        return {
            "record": att,
            "shift": shift,
            "date": today_str,
            "is_checked_in": is_checked_in,
            "is_checked_out": is_checked_out,
            "status": att.status if att else "NOT_CHECKED_IN"
        }

    @staticmethod
    def check_in(nurse_id: int):
        """
        Performs nurse check-in.
        Prevents duplicate check-in.
        Associates with assigned shift (or falls back to Morning shift).
        """
        now = datetime.now()
        today_date = now.date().isoformat()

        # Check for existing record
        existing = Attendance.get_by_nurse_and_date(nurse_id, today_date)
        if existing and existing.check_in:
            return None, "You have already checked in for today."

        # Fetch nurse's assigned shift for today
        shift = Shift.get_nurse_shift(nurse_id, today_date)
        if not shift:
            # Fallback to default shift (Shift ID 1)
            shift = Shift.get_by_id(1)

        # Parse scheduled times
        sched_start_str = shift.start_time
        sched_end_str = shift.end_time

        # Determine if late (e.g. check-in > scheduled_start + 15 minutes grace)
        status = "PRESENT"
        try:
            # Scheduled start time on today's date
            parts = sched_start_str.split(":")
            h, m = int(parts[0]), int(parts[1])
            sched_start_dt = datetime.combine(now.date(), time(h, m))
            if now > sched_start_dt + timedelta(minutes=15):
                status = "LATE"
        except Exception:
            pass

        now_str = now.strftime("%Y-%m-%d %H:%M:%S")

        if existing:
            # Update existing placeholder
            execute_sql = """
                UPDATE attendance 
                SET check_in = %s, status = %s 
                WHERE attendance_id = %s
            """
            from database.database import execute_db
            execute_db(execute_sql, (now_str, status, existing.attendance_id))
            att = Attendance.get_by_id(existing.attendance_id)
        else:
            att = Attendance.record_check_in(
                nurse_id=nurse_id,
                shift_id=shift.shift_id,
                att_date=today_date,
                sched_start=sched_start_str,
                sched_end=sched_end_str,
                check_in_dt=now_str,
                status=status
            )

        return att, None

    @staticmethod
    def check_out(nurse_id: int):
        """
        Performs nurse check-out.
        Ensures nurse checked in first.
        Calculates exact working hours and overtime.
        """
        now = datetime.now()
        today_date = now.date().isoformat()

        existing = Attendance.get_by_nurse_and_date(nurse_id, today_date)
        if not existing or not existing.check_in:
            return None, "You must check in first before checking out."

        if existing.check_out:
            return None, "You have already checked out for today."

        check_in_dt = datetime.fromisoformat(existing.check_in.replace(" ", "T"))
        duration = now - check_in_dt

        # Ensure positive duration
        total_seconds = max(0, duration.total_seconds())
        total_hours = round(total_seconds / 3600.0, 2)

        # Status check (half day if worked < 4 hours)
        status = existing.status
        if total_hours < 4.0 and status != "LATE":
            status = "HALF_DAY"

        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        updated_att = Attendance.record_check_out(
            attendance_id=existing.attendance_id,
            check_out_dt=now_str,
            working_hours=total_hours,
            status=status
        )

        return updated_att, None

    @staticmethod
    def compute_duration_display(check_in_str: str, check_out_str: str = None) -> dict:
        """
        Converts check-in and check-out to formatted strings:
        e.g., '8 hours 15 minutes' and evaluates overtime/early checkout.
        """
        if not check_in_str:
            return {"hours_str": "0 hours 0 minutes", "decimal_hours": 0.0, "is_overtime": False}

        in_dt = datetime.fromisoformat(check_in_str.replace(" ", "T"))
        out_dt = datetime.fromisoformat(check_out_str.replace(" ", "T")) if check_out_str else datetime.now()

        diff = max(timedelta(0), out_dt - in_dt)
        total_seconds = int(diff.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        decimal_hours = round(total_seconds / 3600.0, 2)
        is_overtime = decimal_hours > 8.0

        return {
            "hours_str": f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}",
            "decimal_hours": decimal_hours,
            "is_overtime": is_overtime,
            "hours": hours,
            "minutes": minutes
        }
