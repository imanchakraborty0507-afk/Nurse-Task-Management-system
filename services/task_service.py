"""
Task Service
Coordinates task lifecycle, nurse assignments, status progressions,
audit logging in task_logs, overdue checks, and notification dispatch.
"""

from datetime import datetime
from models.task import Task
from models.task_log import TaskLog
from models.notification import Notification
from models.nurse import Nurse
from models.user import User

class TaskService:
    VALID_TRANSITIONS = {
        "PENDING": ["ASSIGNED", "CANCELLED"],
        "ASSIGNED": ["IN_PROGRESS", "CANCELLED"],
        "IN_PROGRESS": ["COMPLETED", "CANCELLED"],
        "OVERDUE": ["IN_PROGRESS", "COMPLETED", "CANCELLED"],
        "COMPLETED": [],
        "CANCELLED": []
    }

    @staticmethod
    def create_task(title: str, description: str, patient_id: int, nurse_id: int, 
                    assigned_by_user_id: int, priority: str, due_time: str, notes: str = ""):
        """
        Creates a new clinical task, logs the action, and notifies the assigned nurse.
        """
        if not title or not description or not patient_id or not nurse_id or not due_time:
            return None, "Please fill in all required task fields."

        if priority not in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
            priority = "MEDIUM"

        # Create task
        task = Task.create(
            task_title=title.strip(),
            description=description.strip(),
            patient_id=int(patient_id),
            nurse_id=int(nurse_id),
            assigned_by=int(assigned_by_user_id),
            priority=priority,
            due_time=due_time,
            notes=notes.strip() if notes else ""
        )

        if not task:
            return None, "Failed to create task."

        # Audit log
        TaskLog.record(
            task_id=task.task_id,
            user_id=assigned_by_user_id,
            old_status=None,
            new_status="ASSIGNED",
            action="TASK_CREATED",
            comment=f"Task assigned with priority {priority} (Due: {due_time})"
        )

        # Notify assigned nurse
        nurse = Nurse.get_by_id(int(nurse_id))
        if nurse and nurse.user_id:
            Notification.create(
                user_id=nurse.user_id,
                title="New Task Assigned",
                message=f"You have been assigned task '{task.task_title}' (Priority: {priority}). Due: {due_time}",
                notification_type="TASK_ASSIGNED"
            )

        return task, None

    @staticmethod
    def update_task_status(task_id: int, new_status: str, acting_user_id: int, comment: str = "", notes: str = None):
        """
        Transitions task status (e.g. ASSIGNED -> IN_PROGRESS -> COMPLETED),
        enforces valid transitions, audits in task_logs, and notifies doctor/admin upon completion.
        """
        task = Task.get_by_id(task_id)
        if not task:
            return None, "Task not found."

        old_status = task.status

        # Check if already completed
        if old_status == "COMPLETED" and new_status != "COMPLETED":
            return None, "Completed tasks cannot be changed."

        # Verify allowed transition (unless admin override)
        acting_user = User.get_by_id(acting_user_id)
        is_admin = acting_user and acting_user.role == "ADMIN"

        if not is_admin:
            allowed = TaskService.VALID_TRANSITIONS.get(old_status, [])
            if new_status not in allowed and old_status != new_status:
                return None, f"Cannot transition task from {old_status} to {new_status}."

        # Update task
        updated_task = Task.update_status(task_id, new_status, notes=notes)

        # Record audit log
        action = f"STATUS_CHANGED_TO_{new_status}"
        log_comment = comment or f"Status updated from {old_status} to {new_status}"
        if notes:
            log_comment += f" | Notes: {notes}"

        TaskLog.record(
            task_id=task_id,
            user_id=acting_user_id,
            old_status=old_status,
            new_status=new_status,
            action=action,
            comment=log_comment
        )

        # If completed, notify task assigner (doctor or admin)
        if new_status == "COMPLETED" and task.assigned_by != acting_user_id:
            Notification.create(
                user_id=task.assigned_by,
                title="Task Completed",
                message=f"Task '{task.task_title}' for Patient {task.patient_name} was completed.",
                notification_type="TASK_COMPLETED"
            )

        return updated_task, None

    @staticmethod
    def add_task_note(task_id: int, user_id: int, note_text: str):
        """Appends notes to a task and records in audit log."""
        task = Task.get_by_id(task_id)
        if not task:
            return None, "Task not found."

        if not note_text.strip():
            return None, "Note content cannot be empty."

        existing_notes = task.notes or ""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        user = User.get_by_id(user_id)
        author = user.username if user else "User"

        new_entry = f"[{timestamp} by {author}]: {note_text.strip()}"
        combined_notes = f"{existing_notes}\n{new_entry}".strip() if existing_notes else new_entry

        updated_task = Task.update_notes(task_id, combined_notes)

        TaskLog.record(
            task_id=task_id,
            user_id=user_id,
            old_status=task.status,
            new_status=task.status,
            action="NOTE_ADDED",
            comment=f"Note: {note_text.strip()}"
        )

        return updated_task, None

    @staticmethod
    def mark_overdue_tasks():
        """Refreshes status of overdue tasks."""
        Task.check_and_mark_overdue()
