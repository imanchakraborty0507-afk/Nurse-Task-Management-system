"""
Task Model
Represents hospital patient care tasks assigned to nurses.
Supports status transitions: ASSIGNED -> IN_PROGRESS -> COMPLETED
Tracks priority, due time, overdue detection, and audit trail links.
"""

from datetime import datetime
from database.database import query_db, execute_db

class Task:
    def __init__(self, task_id=None, task_title="", description="", patient_id=None,
                 nurse_id=None, assigned_by=None, priority="MEDIUM", status="ASSIGNED",
                 created_at=None, due_time=None, completed_at=None, notes=None,
                 patient_name="", room_number="", bed_number="", ward_name="",
                 nurse_name="", assigned_by_name="", department_name=""):
        self.task_id = task_id
        self.task_title = task_title
        self.description = description
        self.patient_id = patient_id
        self.nurse_id = nurse_id
        self.assigned_by = assigned_by
        self.priority = priority
        self.status = status
        self.created_at = str(created_at) if created_at else ""
        self.due_time = str(due_time) if due_time else ""
        self.completed_at = str(completed_at) if completed_at else None
        self.notes = notes or ""
        
        # Joined display attributes
        self.patient_name = patient_name
        self.room_number = room_number
        self.bed_number = bed_number
        self.ward_name = ward_name
        self.nurse_name = nurse_name
        self.assigned_by_name = assigned_by_name
        self.department_name = department_name

    @property
    def is_overdue(self):
        if self.status in ("COMPLETED", "CANCELLED"):
            return False
        if not self.due_time:
            return False
        try:
            # Parse datetime
            due_dt = datetime.fromisoformat(self.due_time.replace(" ", "T"))
            return datetime.now() > due_dt
        except Exception:
            return False

    def to_dict(self):
        return {
            "task_id": self.task_id,
            "task_title": self.task_title,
            "description": self.description,
            "patient_id": self.patient_id,
            "patient_name": self.patient_name,
            "room_number": self.room_number,
            "bed_number": self.bed_number,
            "ward_name": self.ward_name,
            "nurse_id": self.nurse_id,
            "nurse_name": self.nurse_name,
            "assigned_by": self.assigned_by,
            "assigned_by_name": self.assigned_by_name,
            "department_name": self.department_name,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at,
            "due_time": self.due_time,
            "completed_at": self.completed_at,
            "notes": self.notes,
            "is_overdue": self.is_overdue
        }

    @classmethod
    def _base_query(cls):
        return """
            SELECT 
                t.*,
                p.name AS patient_name,
                p.room_number,
                p.bed_number,
                w.ward_name,
                d.department_name,
                n.name AS nurse_name,
                u.username AS assigned_by_name
            FROM tasks t
            JOIN patients p ON t.patient_id = p.patient_id
            JOIN wards w ON p.ward_id = w.ward_id
            JOIN departments d ON w.department_id = d.department_id
            JOIN nurses n ON t.nurse_id = n.nurse_id
            JOIN users u ON t.assigned_by = u.user_id
        """

    @classmethod
    def get_by_id(cls, task_id):
        sql = cls._base_query() + " WHERE t.task_id = %s"
        row = query_db(sql, (task_id,), one=True)
        return cls(**row) if row else None

    @classmethod
    def get_all(cls, status=None, priority=None, department_id=None, search=None):
        sql = cls._base_query() + " WHERE 1=1"
        args = []
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if status:
            if status == "OVERDUE":
                sql += " AND (t.status = 'OVERDUE' OR (t.status NOT IN ('COMPLETED', 'CANCELLED') AND t.due_time < %s))"
                args.append(now_str)
            else:
                sql += " AND t.status = %s"
                args.append(status)
        if priority:
            sql += " AND t.priority = %s"
            args.append(priority)
        if department_id:
            sql += " AND w.department_id = %s"
            args.append(department_id)
        if search:
            sql += " AND (t.task_title LIKE %s OR p.name LIKE %s OR n.name LIKE %s)"
            search_param = f"%{search}%"
            args.extend([search_param, search_param, search_param])
            
        sql += " ORDER BY CASE t.priority WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 WHEN 'MEDIUM' THEN 3 ELSE 4 END, t.due_time ASC"
        rows = query_db(sql, tuple(args))
        return [cls(**row) for row in rows]

    @classmethod
    def get_by_nurse(cls, nurse_id, status=None):
        sql = cls._base_query() + " WHERE t.nurse_id = %s"
        args = [nurse_id]
        if status:
            sql += " AND t.status = %s"
            args.append(status)
        sql += " ORDER BY CASE t.priority WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 WHEN 'MEDIUM' THEN 3 ELSE 4 END, t.due_time ASC"
        rows = query_db(sql, tuple(args))
        return [cls(**row) for row in rows]

    @classmethod
    def get_by_patient(cls, patient_id):
        sql = cls._base_query() + " WHERE t.patient_id = %s ORDER BY t.created_at DESC"
        rows = query_db(sql, (patient_id,))
        return [cls(**row) for row in rows]

    @classmethod
    def get_by_assigned_by(cls, user_id):
        sql = cls._base_query() + " WHERE t.assigned_by = %s ORDER BY t.created_at DESC"
        rows = query_db(sql, (user_id,))
        return [cls(**row) for row in rows]

    @classmethod
    def create(cls, task_title, description, patient_id, nurse_id, assigned_by, priority, due_time, notes=""):
        sql = """
            INSERT INTO tasks (task_title, description, patient_id, nurse_id, assigned_by, priority, status, due_time, notes)
            VALUES (%s, %s, %s, %s, %s, %s, 'ASSIGNED', %s, %s)
        """
        task_id = execute_db(sql, (task_title, description, patient_id, nurse_id, assigned_by, priority, str(due_time), notes))
        return cls.get_by_id(task_id)

    @classmethod
    def update_status(cls, task_id, new_status, notes=None):
        completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if new_status == "COMPLETED" else None
        if completed_at:
            if notes is not None:
                sql = "UPDATE tasks SET status = %s, completed_at = %s, notes = %s WHERE task_id = %s"
                execute_db(sql, (new_status, completed_at, notes, task_id))
            else:
                sql = "UPDATE tasks SET status = %s, completed_at = %s WHERE task_id = %s"
                execute_db(sql, (new_status, completed_at, task_id))
        else:
            if notes is not None:
                sql = "UPDATE tasks SET status = %s, notes = %s WHERE task_id = %s"
                execute_db(sql, (new_status, notes, task_id))
            else:
                sql = "UPDATE tasks SET status = %s WHERE task_id = %s"
                execute_db(sql, (new_status, task_id))
        return cls.get_by_id(task_id)

    @classmethod
    def update_notes(cls, task_id, notes):
        execute_db("UPDATE tasks SET notes = %s WHERE task_id = %s", (notes, task_id))
        return cls.get_by_id(task_id)

    @classmethod
    def reassign(cls, task_id, new_nurse_id):
        execute_db("UPDATE tasks SET nurse_id = %s WHERE task_id = %s", (new_nurse_id, task_id))
        return cls.get_by_id(task_id)

    @classmethod
    def check_and_mark_overdue(cls):
        """Finds any tasks not completed whose due_time has passed, and sets status to OVERDUE."""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = """
            UPDATE tasks 
            SET status = 'OVERDUE' 
            WHERE status IN ('ASSIGNED', 'IN_PROGRESS', 'PENDING') 
              AND due_time < %s
        """
        execute_db(sql, (now_str,))

    @classmethod
    def get_counts(cls, nurse_id=None, doctor_user_id=None):
        where_clause = ""
        args = []
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        args.append(now_str)

        if nurse_id:
            where_clause = "WHERE nurse_id = %s"
            args.append(nurse_id)
        elif doctor_user_id:
            where_clause = "WHERE assigned_by = %s"
            args.append(doctor_user_id)

        sql = f"""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) AS pending,
                SUM(CASE WHEN status = 'ASSIGNED' THEN 1 ELSE 0 END) AS assigned,
                SUM(CASE WHEN status = 'IN_PROGRESS' THEN 1 ELSE 0 END) AS in_progress,
                SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) AS completed,
                SUM(CASE WHEN status = 'OVERDUE' OR (status NOT IN ('COMPLETED', 'CANCELLED') AND due_time < %s) THEN 1 ELSE 0 END) AS overdue
            FROM tasks
            {where_clause}
        """
        row = query_db(sql, tuple(args), one=True)
        return row or {"total": 0, "pending": 0, "assigned": 0, "in_progress": 0, "completed": 0, "overdue": 0}
