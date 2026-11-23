"""
Notification REST API Blueprint
Provides JSON endpoints for real-time polling, badge updates, and mark-as-read actions.
"""

from flask import Blueprint, jsonify, session
from routes.decorators import login_required
from services.notification_service import NotificationService

notif_bp = Blueprint("notifications_api", __name__, url_prefix="/api/notifications")

@notif_bp.route("/unread-count", methods=["GET"])
@login_required
def unread_count():
    user_id = session.get("user_id")
    count = NotificationService.get_unread_count(user_id)
    return jsonify({"success": True, "count": count})

@notif_bp.route("/", methods=["GET"])
@login_required
def get_notifications():
    user_id = session.get("user_id")
    notifs = NotificationService.get_user_notifications(user_id, limit=20)
    return jsonify({"success": True, "notifications": [n.to_dict() for n in notifs]})

@notif_bp.route("/<int:notification_id>/read", methods=["POST"])
@login_required
def mark_read(notification_id):
    user_id = session.get("user_id")
    NotificationService.mark_read(notification_id, user_id)
    return jsonify({"success": True, "message": "Marked as read."})

@notif_bp.route("/mark-all-read", methods=["POST"])
@login_required
def mark_all_read():
    user_id = session.get("user_id")
    NotificationService.mark_all_read(user_id)
    return jsonify({"success": True, "message": "All notifications marked as read."})
