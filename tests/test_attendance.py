"""
Attendance & Working Hours Calculation Tests
Validates check-in, duplicate prevention, checkout sequence,
and accurate total working hours computation.
"""

from datetime import datetime, date, timedelta
import pytest
from app import create_app
from services.attendance_service import AttendanceService
from models.attendance import Attendance

@pytest.fixture
def app():
    app = create_app({"TESTING": True, "SECRET_KEY": "test-att-key"})
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_working_hours_duration_display():
    # Test 8 hrs 15 mins calculation (06:55 to 15:10)
    in_time = "2026-09-23 06:55:00"
    out_time = "2026-09-23 15:10:00"

    res = AttendanceService.compute_duration_display(in_time, out_time)
    assert res["hours"] == 8
    assert res["minutes"] == 15
    assert "8 hours 15 minutes" in res["hours_str"]
    assert res["decimal_hours"] == 8.25
    assert res["is_overtime"] is True

def test_nurse_check_in_and_checkout_flow():
    # Use nurse_id 8 (Nurse Clara or another nurse without today's attendance)
    # First clear any existing test record for nurse 8 on today's date if present
    today = date.today().isoformat()
    from database.database import execute_db
    execute_db("DELETE FROM attendance WHERE nurse_id = 8 AND date = %s", (today,))

    # 1. Attempt checkout before checkin -> Should be blocked
    rec, err = AttendanceService.check_out(nurse_id=8)
    assert rec is None
    assert "must check in first" in err

    # 2. Check in
    att, err = AttendanceService.check_in(nurse_id=8)
    assert err is None
    assert att is not None
    assert att.check_in is not None

    # 3. Duplicate check-in -> Should be blocked
    dup_att, dup_err = AttendanceService.check_in(nurse_id=8)
    assert dup_att is None
    assert "already checked in" in dup_err

    # 4. Check out
    out_att, out_err = AttendanceService.check_out(nurse_id=8)
    assert out_err is None
    assert out_att is not None
    assert out_att.check_out is not None
    assert out_att.total_working_hours >= 0.0

    # 5. Duplicate checkout -> Should be blocked
    dup_out, dup_out_err = AttendanceService.check_out(nurse_id=8)
    assert dup_out is None
    assert "already checked out" in dup_out_err

def test_attendance_summary_stats():
    stats = Attendance.get_summary_stats()
    assert "present_count" in stats
    assert "total_records" in stats
    assert "total_hours" in stats
