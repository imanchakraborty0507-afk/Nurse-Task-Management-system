"""
Authentication Blueprint
Handles login, logout, profile view, and root dashboard routing.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.auth_service import AuthService
from routes.decorators import login_required
from models.user import User
from models.nurse import Nurse
from models.doctor import Doctor

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("auth.dashboard"))
    return redirect(url_for("auth.login"))

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user, role_profile, error_msg = AuthService.authenticate(username, password)
        if error_msg:
            flash(error_msg, "danger")
            return render_template("login.html", username=username)

        AuthService.set_user_session(session, user, role_profile)
        flash(f"Welcome back, {session.get('name', user.username)}!", "success")

        # Redirect based on role
        if user.role == "ADMIN":
            return redirect(url_for("admin.dashboard"))
        elif user.role == "DOCTOR":
            return redirect(url_for("doctor.dashboard"))
        elif user.role == "NURSE":
            return redirect(url_for("nurse.dashboard"))
        return redirect(url_for("auth.dashboard"))

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    AuthService.clear_user_session(session)
    flash("You have been signed out safely.", "info")
    return redirect(url_for("auth.login"))

@auth_bp.route("/dashboard")
@login_required
def dashboard():
    role = session.get("role")
    if role == "ADMIN":
        return redirect(url_for("admin.dashboard"))
    elif role == "DOCTOR":
        return redirect(url_for("doctor.dashboard"))
    elif role == "NURSE":
        return redirect(url_for("nurse.dashboard"))
    return render_template("dashboard.html")

@auth_bp.route("/profile")
@login_required
def profile():
    user_id = session.get("user_id")
    role = session.get("role")
    user = User.get_by_id(user_id)
    profile_data = None

    if role == "NURSE":
        profile_data = Nurse.get_by_user_id(user_id)
        return render_template("nurse/profile.html", nurse=profile_data, user=user)
    elif role == "DOCTOR":
        profile_data = Doctor.get_by_user_id(user_id)
        return render_template("doctor/profile.html", doctor=profile_data, user=user)
    else:
        return render_template("admin/profile.html", user=user)
