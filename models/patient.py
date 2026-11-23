"""
Patient Model
Represents admitted hospital patients.
"""

from database.database import query_db, execute_db

class Patient:
    def __init__(self, patient_id=None, name="", age=0, gender="", blood_group="", 
                 room_number="", bed_number="", ward_id=None, admission_date="", 
                 discharge_date=None, ward_name="", department_name=""):
        self.patient_id = patient_id
        self.name = name
        self.age = age
        self.gender = gender
        self.blood_group = blood_group
        self.room_number = room_number
        self.bed_number = bed_number
        self.ward_id = ward_id
        self.admission_date = str(admission_date) if admission_date else ""
        self.discharge_date = str(discharge_date) if discharge_date else None
        self.ward_name = ward_name
        self.department_name = department_name

    def to_dict(self):
        return {
            "patient_id": self.patient_id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "blood_group": self.blood_group,
            "room_number": self.room_number,
            "bed_number": self.bed_number,
            "ward_id": self.ward_id,
            "ward_name": self.ward_name,
            "department_name": self.department_name,
            "admission_date": self.admission_date,
            "discharge_date": self.discharge_date
        }

    @classmethod
    def get_all(cls, active_only=True):
        sql = """
            SELECT p.*, w.ward_name, d.department_name
            FROM patients p
            JOIN wards w ON p.ward_id = w.ward_id
            JOIN departments d ON w.department_id = d.department_id
        """
        if active_only:
            sql += " WHERE p.discharge_date IS NULL"
        sql += " ORDER BY p.admission_date DESC"
        rows = query_db(sql)
        return [cls(**row) for row in rows]

    @classmethod
    def get_by_id(cls, patient_id):
        row = query_db("""
            SELECT p.*, w.ward_name, d.department_name
            FROM patients p
            JOIN wards w ON p.ward_id = w.ward_id
            JOIN departments d ON w.department_id = d.department_id
            WHERE p.patient_id = %s
        """, (patient_id,), one=True)
        return cls(**row) if row else None

    @classmethod
    def create(cls, name, age, gender, blood_group, room_number, bed_number, ward_id, admission_date):
        patient_id = execute_db("""
            INSERT INTO patients (name, age, gender, blood_group, room_number, bed_number, ward_id, admission_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, age, gender, blood_group, room_number, bed_number, ward_id, admission_date))
        return cls.get_by_id(patient_id)
