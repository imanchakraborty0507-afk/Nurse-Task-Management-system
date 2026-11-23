"""
Task Log Model
Maintains an immutable audit history of all task status transitions, updates, and nurse comments.
"""

from database.database import query_db, execute_db

class TaskLog:
    def __init__(self, log_id=None, task_id=None, user_id=None, old_status=None,
                 new_status="", action="", comment=None, timestamp=None,
                 username="", role="", task_title=""):
        self.log_id = log_id
        self.task_id = task_id
        self.user_id = user_id
        self.old_status = old_status
        self.new_status = new_status
        self.action = action
        self.comment = comment or ""
        self.timestamp = str(timestamp) if timestamp else ""
        self.username = username
        self.role = role
        self.task_title = task_title

    def to_dict(self):
        return {
            "log_id": self.log_id,
            "task_id": self.task_id,
            "user_id": self.user_id,
            "username": self.username,
            "role": self.role,
            "old_status": self.old_status,
            "new_status": self.new_status,
            "action": self.action,
            "comment": self.comment,
            "timestamp": self.timestamp,
            "task_title": self.task_title
        }

    @classmethod
    def get_by_task_id(cls, task_id):
        sql = """
            SELECT tl.*, u.username, u.role, t.task_title
            FROM task_logs tl
            JOIN users u ON tl.user_id = u.user_id
            JOIN tasks t ON tl.task_id = t.task_id
            WHERE tl.task_id = %s
            ORDER BY tl.timestamp ASC
        """
        rows = query_db(sql, (task_id,))
        return [cls(**row) for row in rows]

    @classmethod
    def get_recent(cls, limit=20):
        sql = """
            SELECT tl.*, u.username, u.role, t.task_title
            FROM task_logs tl
            JOIN users u ON tl.user_id = u.user_id
            JOIN tasks t ON tl.task_id = t.task_id
            ORDER BY tl.timestamp DESC
            LIMIT %s
        """
        rows = query_db(sql, (limit,))
        return [cls(**row) for row in rows]

    @classmethod
    def record(cls, task_id, user_id, old_status, new_status, action, comment=""):
        sql = """
            INSERT INTO task_logs (task_id, user_id, old_status, new_status, action, comment)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        log_id = execute_db(sql, (task_id, user_id, old_status, new_status, action, comment))
        row = query_db("""
            SELECT tl.*, u.username, u.role, t.task_title
            FROM task_logs tl
            JOIN users u ON tl.user_id = u.user_id
            JOIN tasks t ON tl.task_id = t.task_id
            WHERE tl.log_id = %s
        """, (log_id,), one=True)
        return cls(**row) if row else None
