"""
User Model
Represents an authenticated hospital user (Admin, Doctor, or Nurse).
"""

from database.database import query_db, execute_db

class User:
    def __init__(self, user_id=None, username="", password_hash="", role="", email="", created_at=None):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.email = email
        self.created_at = created_at

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "role": self.role,
            "email": self.email,
            "created_at": str(self.created_at) if self.created_at else None
        }

    @classmethod
    def get_by_id(cls, user_id):
        row = query_db("SELECT * FROM users WHERE user_id = %s", (user_id,), one=True)
        return cls(**row) if row else None

    @classmethod
    def get_by_username(cls, username):
        row = query_db("SELECT * FROM users WHERE username = %s", (username,), one=True)
        return cls(**row) if row else None

    @classmethod
    def get_by_email(cls, email):
        row = query_db("SELECT * FROM users WHERE email = %s", (email,), one=True)
        return cls(**row) if row else None

    @classmethod
    def create(cls, username, password_hash, role, email):
        user_id = execute_db(
            "INSERT INTO users (username, password_hash, role, email) VALUES (%s, %s, %s, %s)",
            (username, password_hash, role, email)
        )
        return cls.get_by_id(user_id)

    @classmethod
    def delete(cls, user_id):
        return execute_db("DELETE FROM users WHERE user_id = %s", (user_id,))
