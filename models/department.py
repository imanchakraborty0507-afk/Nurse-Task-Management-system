"""
Department Model
Represents hospital medical departments.
"""

from database.database import query_db, execute_db

class Department:
    def __init__(self, department_id=None, department_name="", location=""):
        self.department_id = department_id
        self.department_name = department_name
        self.location = location

    def to_dict(self):
        return {
            "department_id": self.department_id,
            "department_name": self.department_name,
            "location": self.location
        }

    @classmethod
    def get_all(cls):
        rows = query_db("SELECT * FROM departments ORDER BY department_name ASC")
        return [cls(**row) for row in rows]

    @classmethod
    def get_by_id(cls, department_id):
        row = query_db("SELECT * FROM departments WHERE department_id = %s", (department_id,), one=True)
        return cls(**row) if row else None

    @classmethod
    def create(cls, department_name, location):
        dep_id = execute_db(
            "INSERT INTO departments (department_name, location) VALUES (%s, %s)",
            (department_name, location)
        )
        return cls.get_by_id(dep_id)

    @classmethod
    def update(cls, department_id, department_name, location):
        execute_db(
            "UPDATE departments SET department_name = %s, location = %s WHERE department_id = %s",
            (department_name, location, department_id)
        )
        return cls.get_by_id(department_id)

    @classmethod
    def delete(cls, department_id):
        return execute_db("DELETE FROM departments WHERE department_id = %s", (department_id,))
