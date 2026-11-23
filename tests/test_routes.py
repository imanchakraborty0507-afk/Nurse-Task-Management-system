"""
Comprehensive Route & View Integration Tests
Tests all endpoints for Admin, Doctor, and Nurse roles to ensure
clean Jinja rendering, valid context data, and error-free responses.
"""

import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app({"TESTING": True, "SECRET_KEY": "route-test-key"})
    return app.test_client()

def test_public_routes(client):
    # Root redirects to login
    r = client.get("/")
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]

    # Login page
    r = client.get("/login")
    assert r.status_code == 200
    assert b"MediCare Portal" in r.data

def test_admin_views(client):
    # Log in as admin
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["username"] = "admin"
        sess["role"] = "ADMIN"
        sess["name"] = "Hospital Administrator"

    routes = [
        "/admin/dashboard",
        "/admin/nurses",
        "/admin/doctors",
        "/admin/departments",
        "/admin/shifts",
        "/admin/attendance",
        "/admin/tasks",
        "/admin/reports",
        "/profile"
    ]
    for url in routes:
        res = client.get(url)
        assert res.status_code == 200, f"Failed on {url} with status {res.status_code}"

def test_doctor_views(client):
    # Log in as doctor
    with client.session_transaction() as sess:
        sess["user_id"] = 2
        sess["doctor_id"] = 1
        sess["username"] = "dr_smith"
        sess["role"] = "DOCTOR"
        sess["name"] = "Dr. John Smith"
        sess["department_name"] = "Cardiology"

    routes = [
        "/doctor/dashboard",
        "/doctor/patients",
        "/doctor/nurses",
        "/doctor/create_task",
        "/doctor/tasks",
        "/profile"
    ]
    for url in routes:
        res = client.get(url)
        assert res.status_code == 200, f"Failed on {url} with status {res.status_code}"

def test_nurse_views(client):
    # Log in as nurse
    with client.session_transaction() as sess:
        sess["user_id"] = 5
        sess["nurse_id"] = 1
        sess["username"] = "nurse_emily"
        sess["role"] = "NURSE"
        sess["name"] = "Emily Johnson"
        sess["department_name"] = "Cardiology"

    routes = [
        "/nurse/dashboard",
        "/nurse/tasks",
        "/nurse/attendance",
        "/nurse/notifications",
        "/profile"
    ]
    for url in routes:
        res = client.get(url)
        assert res.status_code == 200, f"Failed on {url} with status {res.status_code}"

def test_api_endpoints(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 5
        sess["nurse_id"] = 1
        sess["username"] = "nurse_emily"
        sess["role"] = "NURSE"

    # Attendance status
    res = client.get("/api/attendance/status")
    assert res.status_code == 200
    assert res.json["success"] is True

    # Notifications unread count
    res = client.get("/api/notifications/unread-count")
    assert res.status_code == 200
    assert "count" in res.json

    # Shifts list
    res = client.get("/api/shifts/")
    assert res.status_code == 200
    assert res.json["success"] is True
    assert len(res.json["shifts"]) >= 3
