"""
Shift Model
Represents hospital work shifts (Morning, Evening, Night) and assignments.
"""

from database.database import query_db, execute_db

class Shift:
    def __init__(self, shift_id=None, shift_name="", start_time="", end_time=""):
        self.shift_id = shift_id
        self.shift_name = shift_name
        self.start_time = str(start_time)
        self.end_time = str(end_time)

    def to_dict(self):
        return {
            "shift_id": self.shift_id,
            "shift_name": self.shift_name,
            "start_time": self.start_time,
            "end_time": self.end_time
        }

    @classmethod
    def get_all(cls):
        rows = query_db("SELECT * FROM shifts ORDER BY start_time ASC")
        return [cls(**row) for row in rows]

    @classmethod
    def get_by_id(cls, shift_id):
        row = query_db("SELECT * FROM shifts WHERE shift_id = %s", (shift_id,), one=True)
        return cls(**row) if row else None

    @classmethod
    def create(cls, shift_name, start_time, end_time):
        shift_id = execute_db(
            "INSERT INTO shifts (shift_name, start_time, end_time) VALUES (%s, %s, %s)",
            (shift_name, start_time, end_time)
        )
        return cls.get_by_id(shift_id)

    @classmethod
    def update(cls, shift_id, shift_name, start_time, end_time):
        execute_db(
            "UPDATE shifts SET shift_name = %s, start_time = %s, end_time = %s WHERE shift_id = %s",
            (shift_name, start_time, end_time, shift_id)
        )
        return cls.get_by_id(shift_id)

    @classmethod
    def get_nurse_shift(cls, nurse_id, target_date):
        """Returns the assigned shift for a nurse on a specific date, or default to Morning Shift."""
        row = query_db("""
            SELECT s.* 
            FROM nurse_shifts ns
            JOIN shifts s ON ns.shift_id = s.shift_id
            WHERE ns.nurse_id = %s AND ns.assigned_date = %s
        """, (nurse_id, target_date), one=True)
        
        if row:
            return cls(**row)
        # Default to shift 1 (Morning) if not explicitly scheduled
        default_shift = cls.get_by_id(1)
        return default_shift

    @classmethod
    def assign_nurse_shift(cls, nurse_id, shift_id, assigned_date):
        """Assigns or updates a nurse's shift for a given date."""
        # Using REPLACE or check existence
        existing = query_db(
            "SELECT assignment_id FROM nurse_shifts WHERE nurse_id = %s AND assigned_date = %s",
            (nurse_id, assigned_date), one=True
        )
        if existing:
            execute_db(
                "UPDATE nurse_shifts SET shift_id = %s WHERE assignment_id = %s",
                (shift_id, existing["assignment_id"])
            )
        else:
            execute_db(
                "INSERT INTO nurse_shifts (nurse_id, shift_id, assigned_date) VALUES (%s, %s, %s)",
                (nurse_id, shift_id, assigned_date)
            )
        return True
