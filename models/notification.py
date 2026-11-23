"""
Notification Model
Handles user alerts for task assignments, status progressions, and schedule reminders.
"""

from database.database import query_db, execute_db

class Notification:
    def __init__(self, notification_id=None, user_id=None, title="", message="",
                 notification_type="TASK_UPDATE", is_read=False, created_at=None):
        self.notification_id = notification_id
        self.user_id = user_id
        self.title = title
        self.message = message
        self.notification_type = notification_type
        self.is_read = bool(is_read)
        self.created_at = str(created_at) if created_at else ""

    def to_dict(self):
        return {
            "notification_id": self.notification_id,
            "user_id": self.user_id,
            "title": self.title,
            "message": self.message,
            "notification_type": self.notification_type,
            "is_read": self.is_read,
            "created_at": self.created_at
        }

    @classmethod
    def get_by_user(cls, user_id, unread_only=False, limit=50):
        sql = "SELECT * FROM notifications WHERE user_id = %s"
        args = [user_id]
        if unread_only:
            sql += " AND is_read = 0"
        sql += " ORDER BY created_at DESC LIMIT %s"
        args.append(limit)
        rows = query_db(sql, tuple(args))
        return [cls(**row) for row in rows]

    @classmethod
    def get_unread_count(cls, user_id):
        sql = "SELECT COUNT(*) AS count FROM notifications WHERE user_id = %s AND is_read = 0"
        row = query_db(sql, (user_id,), one=True)
        return row["count"] if row else 0

    @classmethod
    def create(cls, user_id, title, message, notification_type="TASK_UPDATE"):
        sql = """
            INSERT INTO notifications (user_id, title, message, notification_type, is_read)
            VALUES (%s, %s, %s, %s, 0)
        """
        notif_id = execute_db(sql, (user_id, title, message, notification_type))
        row = query_db("SELECT * FROM notifications WHERE notification_id = %s", (notif_id,), one=True)
        return cls(**row) if row else None

    @classmethod
    def mark_as_read(cls, notification_id, user_id=None):
        if user_id:
            execute_db("UPDATE notifications SET is_read = 1 WHERE notification_id = %s AND user_id = %s", (notification_id, user_id))
        else:
            execute_db("UPDATE notifications SET is_read = 1 WHERE notification_id = %s", (notification_id,))
        return True

    @classmethod
    def mark_all_as_read(cls, user_id):
        execute_db("UPDATE notifications SET is_read = 1 WHERE user_id = %s", (user_id,))
        return True
