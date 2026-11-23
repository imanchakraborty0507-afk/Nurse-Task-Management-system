"""
Authentication and Role-Based Authorization Decorators for Flask Routes.
"""

from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"success": False, "error": "Authentication required. Please login."}), 401
            flash("Please sign in to access this portal.", "warning")
            return redirect(url_for("auth.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*allowed_roles):
    """
    Decorator to restrict route access to specific roles: ADMIN, DOCTOR, NURSE.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get("user_id"):
                if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return jsonify({"success": False, "error": "Authentication required."}), 401
                flash("Please sign in to access this page.", "warning")
                return redirect(url_for("auth.login"))

            user_role = session.get("role")
            if user_role not in allowed_roles:
                if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    return jsonify({"success": False, "error": "Access denied for your role."}), 403
                flash("Access denied. You do not have permission to view that page.", "danger")
                # Redirect to appropriate dashboard
                if user_role == "ADMIN":
                    return redirect(url_for("admin.dashboard"))
                elif user_role == "DOCTOR":
                    return redirect(url_for("doctor.dashboard"))
                elif user_role == "NURSE":
                    return redirect(url_for("nurse.dashboard"))
                return redirect(url_for("auth.login"))

            return f(*args, **kwargs)
        return decorated_function
    return decorator
