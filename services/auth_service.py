"""
Authentication Service
Handles user login, password hashing, session configuration, and role authorization.
"""

from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from models.nurse import Nurse
from models.doctor import Doctor

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plaintext password securely."""
        return generate_password_hash(password, method="scrypt")

    @staticmethod
    def verify_password(stored_hash: str, password: str) -> bool:
        """Verify plaintext password against hash, supporting pbkdf2 and scrypt."""
        if not stored_hash or not password:
            return False
        return check_password_hash(stored_hash, password)

    @staticmethod
    def authenticate(username: str, password: str):
        """
        Verify credentials. Returns (user, role_profile, error_msg).
        role_profile is a Nurse or Doctor object if applicable.
        """
        if not username or not password:
            return None, None, "Please provide both username and password."

        user = User.get_by_username(username.strip())
        if not user:
            return None, None, "Invalid username or password."

        if not AuthService.verify_password(user.password_hash, password):
            return None, None, "Invalid username or password."

        # Fetch linked role profile
        role_profile = None
        if user.role == "NURSE":
            role_profile = Nurse.get_by_user_id(user.user_id)
        elif user.role == "DOCTOR":
            role_profile = Doctor.get_by_user_id(user.user_id)

        return user, role_profile, None

    @staticmethod
    def set_user_session(session, user, role_profile=None):
        """Populate Flask session with user identity and metadata."""
        session.clear()
        session["user_id"] = user.user_id
        session["username"] = user.username
        session["role"] = user.role
        session["email"] = user.email

        if user.role == "NURSE" and role_profile:
            session["nurse_id"] = role_profile.nurse_id
            session["name"] = role_profile.name
            session["department_name"] = role_profile.department_name
        elif user.role == "DOCTOR" and role_profile:
            session["doctor_id"] = role_profile.doctor_id
            session["name"] = role_profile.name
            session["specialization"] = role_profile.specialization
            session["department_name"] = role_profile.department_name
        elif user.role == "ADMIN":
            session["name"] = "Hospital Administrator"
            session["department_name"] = "Administration"
        else:
            session["name"] = user.username

    @staticmethod
    def clear_user_session(session):
        """Clear user session on logout."""
        session.clear()
