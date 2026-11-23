"""
Notification Service
Manages real-time alert delivery, badge counters, and read-state management.
"""

from models.notification import Notification

class NotificationService:
    @staticmethod
    def get_user_notifications(user_id: int, unread_only: bool = False, limit: int = 50):
        """Fetches notifications for a user."""
        return Notification.get_by_user(user_id, unread_only=unread_only, limit=limit)

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """Returns the number of unread notifications for a user."""
        return Notification.get_unread_count(user_id)

    @staticmethod
    def mark_read(notification_id: int, user_id: int):
        """Marks a single notification as read."""
        return Notification.mark_as_read(notification_id, user_id)

    @staticmethod
    def mark_all_read(user_id: int):
        """Marks all notifications as read for a user."""
        return Notification.mark_all_as_read(user_id)

    @staticmethod
    def send_notification(user_id: int, title: str, message: str, notification_type: str = "SYSTEM"):
        """Dispatches an alert to a user."""
        return Notification.create(user_id, title, message, notification_type)
