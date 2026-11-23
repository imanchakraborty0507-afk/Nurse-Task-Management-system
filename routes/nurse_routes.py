"""
Nurse Blueprint
Provides nurses with:
- Clinical Dashboard (shift status, live check-in/out banner, task metrics)
- Tasks View (filter by status, update to IN_PROGRESS, COMPLETED, add notes)
- Task Details Modal/Page with complete audit trail
- Shift & Attendance Ledger
- Notification Inbox
"""

from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.decorators import role_required
from models.nurse import Nurse
from models.task import Task
from models.task_log import TaskLog
from models.attendance import Attendance
from models.shift import Shift
from models.notification import Notification
from services.attendance_service import AttendanceService
from services.task_service import TaskService

nurse_bp = Blueprint("nurse", __name__, url_prefix="/nurse")

def _get_current_nurse():
    user_id = session.get("user_id")
    return Nurse.get_by_user_id(user_id)

@nurse_bp.route("/dashboard")
@role_required("NURSE")
def dashboard():
    nurse = _get_current_nurse()
    if not nurse:
        flash("Nurse profile not found.", "danger")
        return redirect(url_for("auth.login"))

    today_str = date.today().isoformat()
    att_info = AttendanceService.get_today_status(nurse.nurse_id)
    task_counts = Task.get_counts(nurse_id=nurse.nurse_id)
    my_tasks = Task.get_by_nurse(nurse.nurse_id)

    # Calculate active hours display if checked in
    duration_info = None
    if att_info["is_checked_in"]:
        rec = att_info["record"]
        duration_info = AttendanceService.compute_duration_display(rec.check_in, rec.check_out)

    # Unread notifications
    notifs = Notification.get_by_user(session["user_id"], unread_only=True, limit=5)

    return render_template(
        "nurse/dashboard.html",
        nurse=nurse,
        att_info=att_info,
        duration_info=duration_info,
        task_counts=task_counts,
        tasks=my_tasks[:5],
        notifications=notifs,
        today=today_str
    )

@nurse_bp.route("/tasks")
@role_required("NURSE")
def tasks():
    nurse = _get_current_nurse()
    status_filter = request.args.get("status")
    all_tasks = Task.get_by_nurse(nurse.nurse_id, status=status_filter)
    counts = Task.get_counts(nurse_id=nurse.nurse_id)
    return render_template(
        "nurse/tasks.html",
        nurse=nurse,
        tasks=all_tasks,
        counts=counts,
        current_status=status_filter
    )

@nurse_bp.route("/tasks/<int:task_id>")
@role_required("NURSE")
def task_details(task_id):
    nurse = _get_current_nurse()
    task = Task.get_by_id(task_id)
    if not task or task.nurse_id != nurse.nurse_id:
        flash("Task not found or unauthorized.", "danger")
        return redirect(url_for("nurse.tasks"))

    logs = TaskLog.get_by_task_id(task_id)
    return render_template("nurse/task_details.html", nurse=nurse, task=task, logs=logs)

@nurse_bp.route("/tasks/<int:task_id>/start", methods=["POST"])
@role_required("NURSE")
def start_task(task_id):
    nurse = _get_current_nurse()
    task = Task.get_by_id(task_id)
    if not task or task.nurse_id != nurse.nurse_id:
        flash("Task not found or access denied.", "danger")
        return redirect(url_for("nurse.tasks"))

    updated_task, error = TaskService.update_task_status(
        task_id=task_id,
        new_status="IN_PROGRESS",
        acting_user_id=session["user_id"],
        comment=f"Nurse {nurse.name} started this task."
    )
    if error:
        flash(error, "danger")
    else:
        flash(f"Task '{task.task_title}' is now in progress.", "success")
    return redirect(request.referrer or url_for("nurse.tasks"))

@nurse_bp.route("/tasks/<int:task_id>/complete", methods=["POST"])
@role_required("NURSE")
def complete_task(task_id):
    nurse = _get_current_nurse()
    task = Task.get_by_id(task_id)
    if not task or task.nurse_id != nurse.nurse_id:
        flash("Task not found or access denied.", "danger")
        return redirect(url_for("nurse.tasks"))

    notes = request.form.get("notes", "").strip()
    updated_task, error = TaskService.update_task_status(
        task_id=task_id,
        new_status="COMPLETED",
        acting_user_id=session["user_id"],
        comment=f"Nurse {nurse.name} marked task as completed.",
        notes=notes if notes else None
    )
    if error:
        flash(error, "danger")
    else:
        flash(f"Task '{task.task_title}' completed successfully.", "success")
    return redirect(request.referrer or url_for("nurse.tasks"))

@nurse_bp.route("/tasks/<int:task_id>/note", methods=["POST"])
@role_required("NURSE")
def add_note(task_id):
    nurse = _get_current_nurse()
    task = Task.get_by_id(task_id)
    if not task or task.nurse_id != nurse.nurse_id:
        flash("Task not found.", "danger")
        return redirect(url_for("nurse.tasks"))

    note_text = request.form.get("note", "").strip()
    updated_task, error = TaskService.add_task_note(task_id, session["user_id"], note_text)
    if error:
        flash(error, "danger")
    else:
        flash("Clinical note added to task.", "success")
    return redirect(request.referrer or url_for("nurse.task_details", task_id=task_id))

@nurse_bp.route("/attendance")
@role_required("NURSE")
def attendance():
    nurse = _get_current_nurse()
    history = Attendance.get_nurse_history(nurse.nurse_id, limit=30)
    today_status = AttendanceService.get_today_status(nurse.nurse_id)
    duration_info = None
    if today_status["is_checked_in"]:
        rec = today_status["record"]
        duration_info = AttendanceService.compute_duration_display(rec.check_in, rec.check_out)

    return render_template(
        "nurse/attendance.html",
        nurse=nurse,
        history=history,
        today_status=today_status,
        duration_info=duration_info
    )

@nurse_bp.route("/check-in", methods=["POST"])
@role_required("NURSE")
def check_in():
    nurse = _get_current_nurse()
    record, error = AttendanceService.check_in(nurse.nurse_id)
    if error:
        flash(error, "warning")
    else:
        flash(f"Checked in successfully at {record.check_in}!", "success")
    return redirect(request.referrer or url_for("nurse.dashboard"))

@nurse_bp.route("/check-out", methods=["POST"])
@role_required("NURSE")
def check_out():
    nurse = _get_current_nurse()
    record, error = AttendanceService.check_out(nurse.nurse_id)
    if error:
        flash(error, "warning")
    else:
        dur = AttendanceService.compute_duration_display(record.check_in, record.check_out)
        flash(f"Checked out! Total working time: {dur['hours_str']} ({record.total_working_hours} hrs)", "success")
    return redirect(request.referrer or url_for("nurse.dashboard"))

@nurse_bp.route("/notifications")
@role_required("NURSE")
def notifications():
    nurse = _get_current_nurse()
    notif_list = Notification.get_by_user(session["user_id"])
    return render_template("nurse/notifications.html", nurse=nurse, notifications=notif_list)
