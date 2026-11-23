"""
Doctor Blueprint
Provides doctors with:
- Clinical Dashboard (admitted patients, assigned nurses, task summary)
- Patient Roster (active admissions, room & bed assignments, medical history)
- Nurse Directory (department staff, active shifts, availability)
- Task Creation Form (patient selection, nurse assignment, priority, due time, clinical notes)
- Task Monitoring Table with live filters, overdue highlights, and audit logs
"""

from datetime import datetime, timedelta, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.decorators import role_required
from models.doctor import Doctor
from models.patient import Patient
from models.nurse import Nurse
from models.task import Task
from models.task_log import TaskLog
from models.department import Department
from services.task_service import TaskService

doctor_bp = Blueprint("doctor", __name__, url_prefix="/doctor")

def _get_current_doctor():
    user_id = session.get("user_id")
    return Doctor.get_by_user_id(user_id)

@doctor_bp.route("/dashboard")
@role_required("DOCTOR")
def dashboard():
    doctor = _get_current_doctor()
    if not doctor:
        flash("Doctor profile not found.", "danger")
        return redirect(url_for("auth.login"))

    # Active patients
    patients = Patient.get_all(active_only=True)

    # Department nurses
    dept_nurses = Nurse.get_by_department(doctor.department_id) if doctor.department_id else Nurse.get_all()

    # Tasks assigned by this doctor
    task_counts = Task.get_counts(doctor_user_id=session["user_id"])
    doctor_tasks = Task.get_by_assigned_by(session["user_id"])

    return render_template(
        "doctor/dashboard.html",
        doctor=doctor,
        patients=patients[:6],
        nurses=dept_nurses,
        task_counts=task_counts,
        tasks=doctor_tasks[:6],
        total_patients=len(patients)
    )

@doctor_bp.route("/patients")
@role_required("DOCTOR")
def patients():
    doctor = _get_current_doctor()
    patient_list = Patient.get_all(active_only=True)
    return render_template("doctor/patients.html", doctor=doctor, patients=patient_list)

@doctor_bp.route("/nurses")
@role_required("DOCTOR")
def nurses():
    doctor = _get_current_doctor()
    nurse_list = Nurse.get_all()
    departments = Department.get_all()
    return render_template("doctor/nurses.html", doctor=doctor, nurses=nurse_list, departments=departments)

@doctor_bp.route("/create_task", methods=["GET", "POST"])
@doctor_bp.route("/tasks/create", methods=["GET", "POST"])
@role_required("DOCTOR")
def create_task():
    doctor = _get_current_doctor()

    if request.method == "POST":
        title = request.form.get("task_title", "").strip()
        description = request.form.get("description", "").strip()
        patient_id = request.form.get("patient_id", type=int)
        nurse_id = request.form.get("nurse_id", type=int)
        priority = request.form.get("priority", "MEDIUM")
        due_date = request.form.get("due_date", "")
        due_time = request.form.get("due_time", "")
        notes = request.form.get("notes", "").strip()

        # Combine due_date and due_time
        due_datetime_str = f"{due_date} {due_time}:00" if due_date and due_time else None

        task, error = TaskService.create_task(
            title=title,
            description=description,
            patient_id=patient_id,
            nurse_id=nurse_id,
            assigned_by_user_id=session["user_id"],
            priority=priority,
            due_time=due_datetime_str,
            notes=notes
        )

        if error:
            flash(error, "danger")
            patients = Patient.get_all(active_only=True)
            nurses = Nurse.get_all()
            return render_template("doctor/create_task.html", doctor=doctor, patients=patients, nurses=nurses)

        flash(f"Task '{title}' assigned to nurse successfully!", "success")
        return redirect(url_for("doctor.tasks"))

    # GET
    patients = Patient.get_all(active_only=True)
    nurses = Nurse.get_all()
    
    # Preselected patient if query param passed
    selected_patient_id = request.args.get("patient_id", type=int)

    # Default due datetime: 4 hours from now
    default_due = datetime.now() + timedelta(hours=4)
    default_date = default_due.strftime("%Y-%m-%d")
    default_time = default_due.strftime("%H:%M")

    return render_template(
        "doctor/create_task.html",
        doctor=doctor,
        patients=patients,
        nurses=nurses,
        selected_patient_id=selected_patient_id,
        default_date=default_date,
        default_time=default_time
    )

@doctor_bp.route("/tasks")
@role_required("DOCTOR")
def tasks():
    doctor = _get_current_doctor()
    status_filter = request.args.get("status")
    priority_filter = request.args.get("priority")
    search = request.args.get("search")

    task_list = Task.get_by_assigned_by(session["user_id"])

    # In-memory filter or status filter
    if status_filter:
        if status_filter == "OVERDUE":
            task_list = [t for t in task_list if t.is_overdue or t.status == "OVERDUE"]
        else:
            task_list = [t for t in task_list if t.status == status_filter]
    if priority_filter:
        task_list = [t for t in task_list if t.priority == priority_filter]
    if search:
        search_lower = search.lower()
        task_list = [t for t in task_list if search_lower in t.task_title.lower() or search_lower in t.patient_name.lower()]

    counts = Task.get_counts(doctor_user_id=session["user_id"])

    return render_template(
        "doctor/tasks.html",
        doctor=doctor,
        tasks=task_list,
        counts=counts,
        current_status=status_filter,
        current_priority=priority_filter,
        current_search=search or ""
    )

@doctor_bp.route("/tasks/<int:task_id>")
@role_required("DOCTOR")
def task_details(task_id):
    doctor = _get_current_doctor()
    task = Task.get_by_id(task_id)
    if not task:
        flash("Task not found.", "danger")
        return redirect(url_for("doctor.tasks"))

    logs = TaskLog.get_by_task_id(task_id)
    return render_template("doctor/task_details.html", doctor=doctor, task=task, logs=logs)
