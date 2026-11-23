"""
Nurse Task Management System
Flask Main Application Entrypoint
"""

import os
from datetime import datetime, date
from flask import Flask, render_template, session, redirect, url_for
from config import Config
from database.database import init_db
from models.task import Task
from models.notification import Notification

# Import blueprints
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.nurse_routes import nurse_bp
from routes.doctor_routes import doctor_bp
from routes.task_routes import task_bp
from routes.attendance_routes import att_api_bp
from routes.shift_routes import shift_bp
from routes.notification_routes import notif_bp

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(nurse_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(att_api_bp)
    app.register_blueprint(shift_bp)
    app.register_blueprint(notif_bp)

    # Initialize Database tables and seeds if needed
    with app.app_context():
        try:
            init_db()
        except Exception as e:
            app.logger.warning(f"Database auto-init note: {e}")

    # Before request hook to periodically flag overdue tasks
    @app.before_request
    def check_overdue():
        try:
            Task.check_and_mark_overdue()
        except Exception:
            pass

    # Context processors for global template variables
    @app.context_processor
    def inject_global_data():
        unread_notifs = 0
        if session.get("user_id"):
            try:
                unread_notifs = Notification.get_unread_count(session["user_id"])
            except Exception:
                unread_notifs = 0

        return {
            "current_year": datetime.now().year,
            "today_date": date.today().strftime("%A, %B %d, %Y"),
            "unread_notifications_count": unread_notifs,
            "current_user_name": session.get("name", session.get("username", "Guest")),
            "current_user_role": session.get("role", "GUEST"),
            "current_department": session.get("department_name", "Clinical Services")
        }

    # Custom Jinja filters for badges and formatting
    @app.template_filter("priority_badge")
    def priority_badge_filter(priority):
        p = (priority or "").upper()
        mapping = {
            "CRITICAL": "badge-priority-critical",
            "HIGH": "badge-priority-high",
            "MEDIUM": "badge-priority-medium",
            "LOW": "badge-priority-low"
        }
        return mapping.get(p, "bg-secondary")

    @app.template_filter("status_badge")
    def status_badge_filter(status):
        s = (status or "").upper()
        mapping = {
            "COMPLETED": "badge-status-completed",
            "IN_PROGRESS": "badge-status-in-progress",
            "ASSIGNED": "badge-status-assigned",
            "PENDING": "badge-status-pending",
            "OVERDUE": "badge-status-overdue",
            "CANCELLED": "badge-status-cancelled"
        }
        return mapping.get(s, "bg-secondary")

    @app.template_filter("format_dt")
    def format_datetime_filter(dt_val, fmt="%b %d, %Y %I:%M %p"):
        if not dt_val:
            return "—"
        try:
            if isinstance(dt_val, str):
                dt_obj = datetime.fromisoformat(dt_val.replace(" ", "T"))
            else:
                dt_obj = dt_val
            return dt_obj.strftime(fmt)
        except Exception:
            return str(dt_val)

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(403)
    def access_forbidden(e):
        return render_template("403.html"), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template("500.html"), 500

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
