"""
Attendance REST API Blueprint
Provides JSON endpoints for AJAX check-in, check-out, and active shift duration queries.
"""

from flask import Blueprint, request, jsonify, session
from routes.decorators import login_required
from models.nurse import Nurse
from services.attendance_service import AttendanceService

att_api_bp = Blueprint("attendance_api", __name__, url_prefix="/api/attendance")

@att_api_bp.route("/status", methods=["GET"])
@login_required
def status():
    nurse_id = session.get("nurse_id")
    if not nurse_id:
        nurse = Nurse.get_by_user_id(session["user_id"])
        if nurse:
            nurse_id = nurse.nurse_id

    if not nurse_id:
        return jsonify({"success": False, "error": "Not a nurse profile."}), 400

    info = AttendanceService.get_today_status(nurse_id)
    rec = info["record"]
    duration = None
    if info["is_checked_in"] and rec:
        duration = AttendanceService.compute_duration_display(rec.check_in, rec.check_out)

    return jsonify({
        "success": True,
        "is_checked_in": info["is_checked_in"],
        "is_checked_out": info["is_checked_out"],
        "status": info["status"],
        "record": rec.to_dict() if rec else None,
        "duration": duration
    })

@att_api_bp.route("/check-in", methods=["POST"])
@login_required
def check_in():
    nurse_id = session.get("nurse_id")
    if not nurse_id:
        nurse = Nurse.get_by_user_id(session["user_id"])
        if nurse:
            nurse_id = nurse.nurse_id

    if not nurse_id:
        return jsonify({"success": False, "error": "Only nurses can record attendance check-in."}), 403

    record, error = AttendanceService.check_in(nurse_id)
    if error:
        return jsonify({"success": False, "error": error}), 400

    return jsonify({
        "success": True,
        "message": f"Checked in successfully at {record.check_in}",
        "record": record.to_dict()
    })

@att_api_bp.route("/check-out", methods=["POST"])
@login_required
def check_out():
    nurse_id = session.get("nurse_id")
    if not nurse_id:
        nurse = Nurse.get_by_user_id(session["user_id"])
        if nurse:
            nurse_id = nurse.nurse_id

    if not nurse_id:
        return jsonify({"success": False, "error": "Only nurses can record attendance check-out."}), 403

    record, error = AttendanceService.check_out(nurse_id)
    if error:
        return jsonify({"success": False, "error": error}), 400

    duration = AttendanceService.compute_duration_display(record.check_in, record.check_out)
    return jsonify({
        "success": True,
        "message": f"Checked out successfully! Total working hours: {duration['hours_str']}",
        "record": record.to_dict(),
        "duration": duration
    })
