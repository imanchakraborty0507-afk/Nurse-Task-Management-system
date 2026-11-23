"""
Admin Blueprint
Handles administrator capabilities:
- System Dashboard & Live Metrics
- Nurse Management (CRUD)
- Doctor Management (CRUD)
- Department & Ward Management
- Shift Scheduling & Shift Assignments
- Global Attendance Ledger & Working Hours
- Tasks Overview & Reassignment
- Visual Analytics & Reports (Chart.js data)
"""

from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from routes.decorators import role_required
from models.nurse import Nurse
from models.doctor import Doctor
from models.department import Department
from models.ward import Ward
from models.shift import Shift
from models.patient import Patient
from models.task import Task
from models.task_log import TaskLog
from models.attendance import Attendance
from models.user import User
from services.auth_service import AuthService
from database.database import query_db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard")
@role_required("ADMIN")
def dashboard():
    today = date.today().isoformat()

    # Aggregate counts
    nurses = Nurse.get_all()
    doctors = Doctor.get_all()
    active_nurses = [n for n in nurses if n.employment_status == "ACTIVE"]

    # Attendance stats
    att_stats = Attendance.get_summary_stats(today)

    # Task stats
    task_counts = Task.get_counts()

    # Recent activity
    recent_logs = TaskLog.get_recent(limit=10)

    # Today's active tasks
    active_tasks = Task.get_all()[:6]

    return render_template(
        "admin/dashboard.html",
        total_nurses=len(nurses),
        total_doctors=len(doctors),
        active_nurses=len(active_nurses),
        present_nurses=att_stats.get("present_count", 0),
        task_counts=task_counts,
        recent_logs=recent_logs,
        active_tasks=active_tasks,
        today=today
    )

# --- NURSE CRUD ---
@admin_bp.route("/nurses")
@role_required("ADMIN")
def nurses():
    department_id = request.args.get("department_id", type=int)
    if department_id:
        nurse_list = Nurse.get_by_department(department_id)
    else:
        nurse_list = Nurse.get_all()
    departments = Department.get_all()
    return render_template("admin/nurses.html", nurses=nurse_list, departments=departments, selected_dept=department_id)

@admin_bp.route("/nurses/add", methods=["POST"])
@role_required("ADMIN")
def add_nurse():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip() or "nurse123"
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    gender = request.form.get("gender", "Female")
    dob = request.form.get("date_of_birth", "")
    qualification = request.form.get("qualification", "").strip()
    license_no = request.form.get("license_number", "").strip()
    dept_id = request.form.get("department_id", type=int)
    joining_date = request.form.get("joining_date", date.today().isoformat())

    if not username or not name or not dept_id or not license_no:
        flash("Please provide all required fields (username, name, license, department).", "danger")
        return redirect(url_for("admin.nurses"))

    if User.get_by_username(username):
        flash(f"Username '{username}' already exists. Please choose another.", "danger")
        return redirect(url_for("admin.nurses"))

    hashed_pw = AuthService.hash_password(password)
    user = User.create(username=username, password_hash=hashed_pw, role="NURSE", email=email)
    Nurse.create(
        user_id=user.user_id,
        name=name,
        phone=phone,
        email=email,
        gender=gender,
        date_of_birth=dob,
        qualification=qualification,
        license_number=license_no,
        department_id=dept_id,
        joining_date=joining_date,
        employment_status="ACTIVE"
    )
    flash(f"Nurse '{name}' registered successfully.", "success")
    return redirect(url_for("admin.nurses"))

@admin_bp.route("/nurses/edit/<int:nurse_id>", methods=["POST"])
@role_required("ADMIN")
def edit_nurse(nurse_id):
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    gender = request.form.get("gender", "Female")
    dob = request.form.get("date_of_birth", "")
    qualification = request.form.get("qualification", "").strip()
    license_no = request.form.get("license_number", "").strip()
    dept_id = request.form.get("department_id", type=int)
    status = request.form.get("employment_status", "ACTIVE")

    Nurse.update(nurse_id, name, phone, email, gender, dob, qualification, license_no, dept_id, status)
    flash(f"Nurse profile updated.", "success")
    return redirect(url_for("admin.nurses"))

@admin_bp.route("/nurses/delete/<int:nurse_id>", methods=["POST"])
@role_required("ADMIN")
def delete_nurse(nurse_id):
    Nurse.delete(nurse_id)
    flash("Nurse profile removed successfully.", "info")
    return redirect(url_for("admin.nurses"))

# --- DOCTOR CRUD ---
@admin_bp.route("/doctors")
@role_required("ADMIN")
def doctors():
    doctor_list = Doctor.get_all()
    departments = Department.get_all()
    return render_template("admin/doctors.html", doctors=doctor_list, departments=departments)

@admin_bp.route("/doctors/add", methods=["POST"])
@role_required("ADMIN")
def add_doctor():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip() or "doctor123"
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    spec = request.form.get("specialization", "").strip()
    license_no = request.form.get("license_number", "").strip()
    dept_id = request.form.get("department_id", type=int)

    if not username or not name or not dept_id or not license_no:
        flash("Please provide all required fields.", "danger")
        return redirect(url_for("admin.doctors"))

    if User.get_by_username(username):
        flash(f"Username '{username}' already exists.", "danger")
        return redirect(url_for("admin.doctors"))

    hashed_pw = AuthService.hash_password(password)
    user = User.create(username=username, password_hash=hashed_pw, role="DOCTOR", email=email)
    Doctor.create(
        user_id=user.user_id,
        name=name,
        phone=phone,
        email=email,
        specialization=spec,
        license_number=license_no,
        department_id=dept_id
    )
    flash(f"Doctor '{name}' added successfully.", "success")
    return redirect(url_for("admin.doctors"))

@admin_bp.route("/doctors/delete/<int:doctor_id>", methods=["POST"])
@role_required("ADMIN")
def delete_doctor(doctor_id):
    Doctor.delete(doctor_id)
    flash("Doctor removed successfully.", "info")
    return redirect(url_for("admin.doctors"))

# --- DEPARTMENTS & WARDS ---
@admin_bp.route("/departments")
@role_required("ADMIN")
def departments():
    dept_list = Department.get_all()
    ward_list = Ward.get_all()
    return render_template("admin/departments.html", departments=dept_list, wards=ward_list)

@admin_bp.route("/departments/add", methods=["POST"])
@role_required("ADMIN")
def add_department():
    name = request.form.get("department_name", "").strip()
    loc = request.form.get("location", "").strip()
    if name:
        Department.create(name, loc)
        flash(f"Department '{name}' created.", "success")
    return redirect(url_for("admin.departments"))

@admin_bp.route("/wards/add", methods=["POST"])
@role_required("ADMIN")
def add_ward():
    ward_name = request.form.get("ward_name", "").strip()
    dept_id = request.form.get("department_id", type=int)
    beds = request.form.get("number_of_beds", type=int, default=10)
    if ward_name and dept_id:
        Ward.create(ward_name, dept_id, beds)
        flash(f"Ward '{ward_name}' created.", "success")
    return redirect(url_for("admin.departments"))

# --- SHIFTS & ASSIGNMENTS ---
@admin_bp.route("/shifts")
@role_required("ADMIN")
def shifts():
    shift_list = Shift.get_all()
    nurses = Nurse.get_all()
    today = date.today().isoformat()
    return render_template("admin/shifts.html", shifts=shift_list, nurses=nurses, today=today)

@admin_bp.route("/shifts/assign", methods=["POST"])
@role_required("ADMIN")
def assign_shift():
    nurse_id = request.form.get("nurse_id", type=int)
    shift_id = request.form.get("shift_id", type=int)
    assigned_date = request.form.get("assigned_date", date.today().isoformat())
    Shift.assign_nurse_shift(nurse_id, shift_id, assigned_date)
    flash("Nurse shift assigned successfully.", "success")
    return redirect(url_for("admin.shifts"))

# --- ATTENDANCE LEDGER ---
@admin_bp.route("/attendance")
@role_required("ADMIN")
def attendance():
    target_date = request.args.get("date", date.today().isoformat())
    dept_id = request.args.get("department_id", type=int)
    records = Attendance.get_all(target_date=target_date, department_id=dept_id)
    departments = Department.get_all()
    stats = Attendance.get_summary_stats(target_date)
    return render_template(
        "admin/attendance.html",
        records=records,
        departments=departments,
        selected_date=target_date,
        selected_dept=dept_id,
        stats=stats
    )

# --- MASTER TASKS BOARD ---
@admin_bp.route("/tasks")
@role_required("ADMIN")
def tasks():
    status = request.args.get("status")
    priority = request.args.get("priority")
    dept_id = request.args.get("department_id", type=int)
    search = request.args.get("search")

    task_list = Task.get_all(status=status, priority=priority, department_id=dept_id, search=search)
    departments = Department.get_all()
    nurses = Nurse.get_all()
    counts = Task.get_counts()

    return render_template(
        "admin/tasks.html",
        tasks=task_list,
        departments=departments,
        nurses=nurses,
        counts=counts,
        current_status=status,
        current_priority=priority,
        current_search=search or ""
    )

@admin_bp.route("/tasks/reassign", methods=["POST"])
@role_required("ADMIN")
def reassign_task():
    task_id = request.form.get("task_id", type=int)
    new_nurse_id = request.form.get("nurse_id", type=int)
    if task_id and new_nurse_id:
        Task.reassign(task_id, new_nurse_id)
        from models.task_log import TaskLog
        TaskLog.record(
            task_id=task_id,
            user_id=1,
            old_status="REASSIGNED",
            new_status="ASSIGNED",
            action="TASK_REASSIGNED",
            comment=f"Admin reassigned task to nurse ID {new_nurse_id}"
        )
        flash("Task reassigned successfully.", "success")
    return redirect(url_for("admin.tasks"))

# --- VISUAL REPORTS & ANALYTICS ---
@admin_bp.route("/reports")
@role_required("ADMIN")
def reports():
    # Priority breakdown
    pri_rows = query_db("""
        SELECT priority, COUNT(*) AS count 
        FROM tasks 
        GROUP BY priority
    """)
    priority_data = {r["priority"]: r["count"] for r in pri_rows}

    # Status breakdown
    st_rows = query_db("""
        SELECT status, COUNT(*) AS count 
        FROM tasks 
        GROUP BY status
    """)
    status_data = {r["status"]: r["count"] for r in st_rows}

    # Department task breakdown
    dept_rows = query_db("""
        SELECT d.department_name, COUNT(t.task_id) AS task_count
        FROM departments d
        JOIN wards w ON d.department_id = w.department_id
        JOIN patients p ON w.ward_id = p.ward_id
        LEFT JOIN tasks t ON p.patient_id = t.patient_id
        GROUP BY d.department_name
    """)

    # Working hours per department
    hours_rows = query_db("""
        SELECT d.department_name, COALESCE(SUM(a.total_working_hours), 0) AS total_hours
        FROM departments d
        JOIN nurses n ON d.department_id = n.department_id
        LEFT JOIN attendance a ON n.nurse_id = a.nurse_id
        GROUP BY d.department_name
    """)

    # Attendance summary
    att_stats = Attendance.get_summary_stats()

    return render_template(
        "admin/reports.html",
        priority_data=priority_data,
        status_data=status_data,
        dept_rows=dept_rows,
        hours_rows=hours_rows,
        att_stats=att_stats
    )
