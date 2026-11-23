"""
Nurse Model
Represents nurses and their professional credentials, department, and status.
"""

from database.database import query_db, execute_db

class Nurse:
    def __init__(self, nurse_id=None, user_id=None, name="", phone="", email="", 
                 gender="", date_of_birth="", qualification="", license_number="", 
                 department_id=None, joining_date="", employment_status="ACTIVE", 
                 department_name="", username=""):
        self.nurse_id = nurse_id
        self.user_id = user_id
        self.name = name
        self.phone = phone
        self.email = email
        self.gender = gender
        self.date_of_birth = str(date_of_birth) if date_of_birth else ""
        self.qualification = qualification
        self.license_number = license_number
        self.department_id = department_id
        self.joining_date = str(joining_date) if joining_date else ""
        self.employment_status = employment_status
        self.department_name = department_name
        self.username = username

    def to_dict(self):
        return {
            "nurse_id": self.nurse_id,
            "user_id": self.user_id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "gender": self.gender,
            "date_of_birth": self.date_of_birth,
            "qualification": self.qualification,
            "license_number": self.license_number,
            "department_id": self.department_id,
            "department_name": self.department_name,
            "joining_date": self.joining_date,
            "employment_status": self.employment_status,
            "username": self.username
        }

    @classmethod
    def get_all(cls):
        rows = query_db("""
            SELECT n.*, d.department_name, u.username
            FROM nurses n
            JOIN departments d ON n.department_id = d.department_id
            JOIN users u ON n.user_id = u.user_id
            ORDER BY n.name ASC
        """)
        return [cls(**row) for row in rows]

    @classmethod
    def get_by_id(cls, nurse_id):
        row = query_db("""
            SELECT n.*, d.department_name, u.username
            FROM nurses n
            JOIN departments d ON n.department_id = d.department_id
            JOIN users u ON n.user_id = u.user_id
            WHERE n.nurse_id = %s
        """, (nurse_id,), one=True)
        return cls(**row) if row else None

    @classmethod
    def get_by_user_id(cls, user_id):
        row = query_db("""
            SELECT n.*, d.department_name, u.username
            FROM nurses n
            JOIN departments d ON n.department_id = d.department_id
            JOIN users u ON n.user_id = u.user_id
            WHERE n.user_id = %s
        """, (user_id,), one=True)
        return cls(**row) if row else None

    @classmethod
    def get_by_department(cls, department_id):
        rows = query_db("""
            SELECT n.*, d.department_name, u.username
            FROM nurses n
            JOIN departments d ON n.department_id = d.department_id
            JOIN users u ON n.user_id = u.user_id
            WHERE n.department_id = %s
            ORDER BY n.name ASC
        """, (department_id,))
        return [cls(**row) for row in rows]

    @classmethod
    def create(cls, user_id, name, phone, email, gender, date_of_birth, qualification, license_number, department_id, joining_date, employment_status='ACTIVE'):
        nurse_id = execute_db("""
            INSERT INTO nurses (user_id, name, phone, email, gender, date_of_birth, qualification, license_number, department_id, joining_date, employment_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, name, phone, email, gender, date_of_birth, qualification, license_number, department_id, joining_date, employment_status))
        return cls.get_by_id(nurse_id)

    @classmethod
    def update(cls, nurse_id, name, phone, email, gender, date_of_birth, qualification, license_number, department_id, employment_status):
        execute_db("""
            UPDATE nurses 
            SET name = %s, phone = %s, email = %s, gender = %s, date_of_birth = %s, 
                qualification = %s, license_number = %s, department_id = %s, employment_status = %s
            WHERE nurse_id = %s
        """, (name, phone, email, gender, date_of_birth, qualification, license_number, department_id, employment_status, nurse_id))
        return cls.get_by_id(nurse_id)

    @classmethod
    def delete(cls, nurse_id):
        nurse = cls.get_by_id(nurse_id)
        if nurse:
            execute_db("DELETE FROM nurses WHERE nurse_id = %s", (nurse_id,))
            execute_db("DELETE FROM users WHERE user_id = %s", (nurse.user_id,))
            return True
        return False
