"""
Authentication & Authorization Tests
Validates role-based access control, login, password verification, and route security.
"""

import pytest
from app import create_app
from services.auth_service import AuthService
from models.user import User

@pytest.fixture
def app():
    app = create_app({"TESTING": True, "SECRET_KEY": "test-secret-key"})
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_password_hashing():
    raw = "securePassword123"
    hashed = AuthService.hash_password(raw)
    assert hashed != raw
    assert AuthService.verify_password(hashed, raw) is True
    assert AuthService.verify_password(hashed, "wrongPassword") is False

def test_authenticate_success():
    # Test authenticating seeded admin
    user, profile, err = AuthService.authenticate("admin", "admin123")
    assert err is None
    assert user is not None
    assert user.role == "ADMIN"

def test_authenticate_doctor():
    user, profile, err = AuthService.authenticate("dr_smith", "doctor123")
    assert err is None
    assert user is not None
    assert user.role == "DOCTOR"
    assert profile is not None
    assert profile.specialization != ""

def test_authenticate_nurse():
    user, profile, err = AuthService.authenticate("nurse_emily", "nurse123")
    assert err is None
    assert user is not None
    assert user.role == "NURSE"
    assert profile is not None
    assert profile.nurse_id is not None

def test_authenticate_invalid_credentials():
    user, profile, err = AuthService.authenticate("admin", "wrongpassword")
    assert user is None
    assert err is not None

def test_login_route_get(client):
    res = client.get("/login")
    assert res.status_code == 200
    assert b"MediCare Portal" in res.data

def test_login_post_and_redirect(client):
    res = client.post("/login", data={"username": "admin", "password": "admin123"}, follow_redirects=False)
    assert res.status_code in (302, 303)
    assert "/admin/dashboard" in res.headers["Location"]

def test_unauthorized_access_blocks_guest(client):
    res = client.get("/admin/dashboard", follow_redirects=False)
    # Should redirect to login
    assert res.status_code in (302, 303)
    assert "/login" in res.headers["Location"]

def test_role_mismatch_blocks_nurse_from_admin(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 5
        sess["username"] = "nurse_emily"
        sess["role"] = "NURSE"

    res = client.get("/admin/dashboard", follow_redirects=False)
    assert res.status_code in (302, 303)
    # Redirects to nurse dashboard
    assert "/nurse/dashboard" in res.headers["Location"]
