"""
Shift REST API Blueprint
Provides JSON endpoints for shift lists, nurse schedules, and shift updates.
"""

from flask import Blueprint, jsonify, request
from routes.decorators import login_required
from models.shift import Shift

shift_bp = Blueprint("shifts_api", __name__, url_prefix="/api/shifts")

@shift_bp.route("/", methods=["GET"])
@login_required
def list_shifts():
    shifts = Shift.get_all()
    return jsonify({"success": True, "shifts": [s.to_dict() for s in shifts]})

@shift_bp.route("/nurse/<int:nurse_id>", methods=["GET"])
@login_required
def get_nurse_shift(nurse_id):
    target_date = request.args.get("date")
    shift = Shift.get_nurse_shift(nurse_id, target_date)
    return jsonify({"success": True, "shift": shift.to_dict() if shift else None})
