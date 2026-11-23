"""
Task REST API Blueprint
Provides JSON endpoints for AJAX status updates, notes, and task data.
"""

from flask import Blueprint, request, jsonify, session
from routes.decorators import login_required
from models.task import Task
from models.task_log import TaskLog
from services.task_service import TaskService

task_bp = Blueprint("tasks_api", __name__, url_prefix="/api/tasks")

@task_bp.route("/<int:task_id>", methods=["GET"])
@login_required
def get_task(task_id):
    task = Task.get_by_id(task_id)
    if not task:
        return jsonify({"success": False, "error": "Task not found."}), 404
    return jsonify({"success": True, "task": task.to_dict()})

@task_bp.route("/<int:task_id>/logs", methods=["GET"])
@login_required
def get_task_logs(task_id):
    logs = TaskLog.get_by_task_id(task_id)
    return jsonify({"success": True, "logs": [l.to_dict() for l in logs]})

@task_bp.route("/<int:task_id>/status", methods=["POST"])
@login_required
def update_status(task_id):
    data = request.get_json() or request.form
    new_status = data.get("status")
    comment = data.get("comment", "")
    notes = data.get("notes")

    if not new_status:
        return jsonify({"success": False, "error": "Status is required."}), 400

    updated_task, error = TaskService.update_task_status(
        task_id=task_id,
        new_status=new_status,
        acting_user_id=session["user_id"],
        comment=comment,
        notes=notes
    )

    if error:
        return jsonify({"success": False, "error": error}), 400

    return jsonify({
        "success": True,
        "message": f"Task status updated to {new_status}",
        "task": updated_task.to_dict()
    })

@task_bp.route("/<int:task_id>/notes", methods=["POST"])
@login_required
def add_note(task_id):
    data = request.get_json() or request.form
    note_text = data.get("note", "").strip()

    if not note_text:
        return jsonify({"success": False, "error": "Note text is required."}), 400

    updated_task, error = TaskService.add_task_note(task_id, session["user_id"], note_text)
    if error:
        return jsonify({"success": False, "error": error}), 400

    return jsonify({
        "success": True,
        "message": "Note added successfully.",
        "task": updated_task.to_dict()
    })
