"""
Doctor Model
Represents doctors, their specialization, department, and credentials.
"""

from database.database import query_db, execute_db

class Doctor:
    def __init__(self, doctor_id=None, user_id=None, name="", phone="", email="", 
                 specialization="", license_number="", department_id=None, 
                 department_name="", username=""):
        self.doctor_id = doctor_id
        self.user_id = user_id
        self.name = name
        self.phone = phone
        self.email = email
        self.specialization = specialization
        self.license_number = license_number
        self.department_id = department_id
        self.department_name = department_name
        self.username = username

    def to_dict(self):
        return {
            "doctor_id": self.doctor_id,
            "user_id": self.user_id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "specialization": self.specialization,
            "license_number": self.license_number,
            "department_id": self.department_id,
            "department_name": self.department_name,
            "username": self.username
        }

    @classmethod
    def get_all(cls):
        rows = query_db("""
            SELECT doc.*, d.department_name, u.username
            FROM doctors doc
            JOIN departments d ON doc.department_id = d.department_id
            JOIN users u ON doc.user_id = u.user_id
            ORDER BY doc.name ASC
        """)
        return [cls(**row) for row in rows]

    @classmethod
    def get_by_id(cls, doctor_id):
        row = query_db("""
            SELECT doc.*, d.department_name, u.username
            FROM doctors doc
            JOIN departments d ON doc.department_id = d.department_id
            JOIN users u ON doc.user_id = u.user_id
            WHERE doc.doctor_id = %s
        """, (doctor_id,), one=True)
        return cls(**row) if row else None

    @classmethod
    def get_by_user_id(cls, user_id):
        row = query_db("""
            SELECT doc.*, d.department_name, u.username
            FROM doctors doc
            JOIN departments d ON doc.department_id = d.department_id
            JOIN users u ON doc.user_id = u.user_id
            WHERE doc.user_id = %s
        """, (user_id,), one=True)
        return cls(**row) if row else None

    @classmethod
    def create(cls, user_id, name, phone, email, specialization, license_number, department_id):
        doctor_id = execute_db("""
            INSERT INTO doctors (user_id, name, phone, email, specialization, license_number, department_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (user_id, name, phone, email, specialization, license_number, department_id))
        return cls.get_by_id(doctor_id)

    @classmethod
    def update(cls, doctor_id, name, phone, email, specialization, license_number, department_id):
        execute_db("""
            UPDATE doctors
            SET name = %s, phone = %s, email = %s, specialization = %s, license_number = %s, department_id = %s
            WHERE doctor_id = %s
        """, (name, phone, email, specialization, license_number, department_id, doctor_id))
        return cls.get_by_id(doctor_id)

    @classmethod
    def delete(cls, doctor_id):
        doc = cls.get_by_id(doctor_id)
        if doc:
            execute_db("DELETE FROM doctors WHERE doctor_id = %s", (doctor_id,))
            execute_db("DELETE FROM users WHERE user_id = %s", (doc.user_id,))
            return True
        return False
