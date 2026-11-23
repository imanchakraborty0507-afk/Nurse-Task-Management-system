"""
Ward Model
Represents patient wards within hospital departments.
"""

from database.database import query_db, execute_db

class Ward:
    def __init__(self, ward_id=None, ward_name="", department_id=None, number_of_beds=10, department_name=""):
        self.ward_id = ward_id
        self.ward_name = ward_name
        self.department_id = department_id
        self.number_of_beds = number_of_beds
        self.department_name = department_name

    def to_dict(self):
        return {
            "ward_id": self.ward_id,
            "ward_name": self.ward_name,
            "department_id": self.department_id,
            "number_of_beds": self.number_of_beds,
            "department_name": self.department_name
        }

    @classmethod
    def get_all(cls):
        rows = query_db("""
            SELECT w.*, d.department_name 
            FROM wards w
            JOIN departments d ON w.department_id = d.department_id
            ORDER BY w.ward_name ASC
        """)
        return [cls(**row) for row in rows]

    @classmethod
    def get_by_id(cls, ward_id):
        row = query_db("""
            SELECT w.*, d.department_name 
            FROM wards w
            JOIN departments d ON w.department_id = d.department_id
            WHERE w.ward_id = %s
        """, (ward_id,), one=True)
        return cls(**row) if row else None

    @classmethod
    def get_by_department(cls, department_id):
        rows = query_db("""
            SELECT w.*, d.department_name 
            FROM wards w
            JOIN departments d ON w.department_id = d.department_id
            WHERE w.department_id = %s
            ORDER BY w.ward_name ASC
        """, (department_id,))
        return [cls(**row) for row in rows]

    @classmethod
    def create(cls, ward_name, department_id, number_of_beds):
        ward_id = execute_db(
            "INSERT INTO wards (ward_name, department_id, number_of_beds) VALUES (%s, %s, %s)",
            (ward_name, department_id, number_of_beds)
        )
        return cls.get_by_id(ward_id)

    @classmethod
    def delete(cls, ward_id):
        return execute_db("DELETE FROM wards WHERE ward_id = %s", (ward_id,))
