"""
Task Lifecycle & Audit Log Tests
Validates task creation, priority assignment, status transitions,
audit log preservation, and overdue detection.
"""

from datetime import datetime, timedelta
import pytest
from app import create_app
from services.task_service import TaskService
from models.task import Task
from models.task_log import TaskLog

@pytest.fixture
def app():
    app = create_app({"TESTING": True, "SECRET_KEY": "test-tasks-key"})
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_task_creation_and_defaults():
    due = (datetime.now() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
    task, err = TaskService.create_task(
        title="Administer Oral Antibiotic Test",
        description="Verify patient swallows pill with full glass of water.",
        patient_id=1,
        nurse_id=1,
        assigned_by_user_id=2, # Dr. Smith
        priority="HIGH",
        due_time=due
    )
    assert err is None
    assert task is not None
    assert task.status == "ASSIGNED"
    assert task.priority == "HIGH"
    assert task.patient_id == 1
    assert task.nurse_id == 1

def test_task_status_progression():
    # 1. Create a task
    due = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
    task, _ = TaskService.create_task(
        title="Vitals Assessment Routine",
        description="Check BP, temperature, SpO2.",
        patient_id=2,
        nurse_id=1,
        assigned_by_user_id=2,
        priority="MEDIUM",
        due_time=due
    )
    task_id = task.task_id

    # 2. Advance to IN_PROGRESS
    updated, err = TaskService.update_task_status(task_id, "IN_PROGRESS", acting_user_id=5, comment="Nurse Emily started the check")
    assert err is None
    assert updated.status == "IN_PROGRESS"

    # 3. Advance to COMPLETED
    completed, err = TaskService.update_task_status(task_id, "COMPLETED", acting_user_id=5, comment="Check finished", notes="BP: 120/80, SpO2: 98%")
    assert err is None
    assert completed.status == "COMPLETED"
    assert completed.completed_at is not None

    # 4. Attempting to reopen a completed task by non-admin should fail
    reopened, err = TaskService.update_task_status(task_id, "ASSIGNED", acting_user_id=5)
    assert reopened is None
    assert "Completed tasks cannot be changed" in err

def test_task_notes_and_audit_trail():
    due = (datetime.now() + timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S")
    task, _ = TaskService.create_task(
        title="Dressing Change Test",
        description="Sterile wound dressing change.",
        patient_id=1,
        nurse_id=1,
        assigned_by_user_id=2,
        priority="LOW",
        due_time=due
    )
    
    # Append note
    updated, err = TaskService.add_task_note(task.task_id, user_id=5, note_text="Wound is healing cleanly without erythema.")
    assert err is None
    assert "Wound is healing cleanly" in updated.notes

    # Verify logs
    logs = TaskLog.get_by_task_id(task.task_id)
    assert len(logs) >= 2
    actions = [l.action for l in logs]
    assert "TASK_CREATED" in actions
    assert "NOTE_ADDED" in actions

def test_overdue_detection():
    # Create task with due time in the past
    past_due = (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
    task, _ = TaskService.create_task(
        title="Emergency Stat Lab Draw",
        description="Draw venous blood sample.",
        patient_id=1,
        nurse_id=1,
        assigned_by_user_id=2,
        priority="CRITICAL",
        due_time=past_due
    )
    assert task.is_overdue is True

    # Run check and mark overdue
    TaskService.mark_overdue_tasks()
    refreshed = Task.get_by_id(task.task_id)
    assert refreshed.status == "OVERDUE"
