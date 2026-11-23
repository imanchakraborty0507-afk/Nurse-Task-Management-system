"""
Database Connection & Query Helper Module.
Supports MySQL 8.0 with automatic SQLite fallback for hassle-free testing.
Uses parameterized queries to prevent SQL injection.
"""

import os
import sys
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from config import Config
import pymysql
import pymysql.cursors

# Global flag to track which engine is currently active
ACTIVE_DB_TYPE = None

def get_connection():
    """
    Attempt to connect to MySQL database first.
    If MySQL is unreachable (or credentials missing), fallback gracefully to SQLite.
    """
    global ACTIVE_DB_TYPE
    
    if Config.DB_TYPE.lower() == "mysql":
        try:
            conn = pymysql.connect(
                host=Config.MYSQL_HOST,
                port=Config.MYSQL_PORT,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DB,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False,
                charset="utf8mb4"
            )
            ACTIVE_DB_TYPE = "mysql"
            return conn
        except Exception as e:
            # If database does not exist, try creating it
            try:
                temp_conn = pymysql.connect(
                    host=Config.MYSQL_HOST,
                    port=Config.MYSQL_PORT,
                    user=Config.MYSQL_USER,
                    password=Config.MYSQL_PASSWORD,
                    autocommit=True
                )
                with temp_conn.cursor() as cursor:
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.MYSQL_DB}` CHARACTER SET utf8mb4;")
                temp_conn.close()
                
                # Reconnect to newly created database
                conn = pymysql.connect(
                    host=Config.MYSQL_HOST,
                    port=Config.MYSQL_PORT,
                    user=Config.MYSQL_USER,
                    password=Config.MYSQL_PASSWORD,
                    database=Config.MYSQL_DB,
                    cursorclass=pymysql.cursors.DictCursor,
                    autocommit=False,
                    charset="utf8mb4"
                )
                ACTIVE_DB_TYPE = "mysql"
                return conn
            except Exception:
                # Fallback to SQLite
                pass

    # SQLite fallback
    ACTIVE_DB_TYPE = "sqlite"
    sqlite_path = Config.SQLITE_DB_PATH
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    return conn

def _adapt_query(query: str) -> str:
    """Adapts standard MySQL syntax to SQLite if SQLite is the active database."""
    if ACTIVE_DB_TYPE == "sqlite":
        # Replace %s placeholder with ?
        # Be careful not to replace % inside strftime or LIKE
        adapted = query.replace("%s", "?")
        # Replace MySQL NOW() with CURRENT_TIMESTAMP
        adapted = adapted.replace("NOW()", "CURRENT_TIMESTAMP")
        adapted = adapted.replace("CURRENT_DATE", "DATE('now')")
        return adapted
    return query

def query_db(query: str, args: tuple = (), one: bool = False):
    """
    Executes a SELECT query with parameterized arguments.
    Returns a list of dicts (or a single dict if one=True).
    """
    conn = get_connection()
    try:
        adapted_query = _adapt_query(query)
        if ACTIVE_DB_TYPE == "mysql":
            with conn.cursor() as cursor:
                cursor.execute(adapted_query, args)
                rv = cursor.fetchall()
                return (rv[0] if rv else None) if one else rv
        else:
            cursor = conn.cursor()
            cursor.execute(adapted_query, args)
            rv = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            return (rv[0] if rv else None) if one else rv
    finally:
        conn.close()

def execute_db(query: str, args: tuple = (), commit: bool = True) -> int:
    """
    Executes an INSERT, UPDATE, or DELETE parameterized query.
    Returns the lastrowid or affected rows.
    """
    conn = get_connection()
    try:
        adapted_query = _adapt_query(query)
        last_id = 0
        if ACTIVE_DB_TYPE == "mysql":
            with conn.cursor() as cursor:
                cursor.execute(adapted_query, args)
                last_id = cursor.lastrowid
            if commit:
                conn.commit()
            return last_id
        else:
            cursor = conn.cursor()
            cursor.execute(adapted_query, args)
            last_id = cursor.lastrowid
            if commit:
                conn.commit()
            cursor.close()
            return last_id
    except Exception as e:
        if commit:
            conn.rollback()
        raise e
    finally:
        conn.close()

def init_db(force_reseed: bool = False):
    """
    Initializes database schema and seed data.
    Works with both MySQL and SQLite fallback.
    """
    conn = get_connection()
    
    if ACTIVE_DB_TYPE == "mysql":
        print(f"[DB] Initializing MySQL Database: {Config.MYSQL_DB} on {Config.MYSQL_HOST}:{Config.MYSQL_PORT}...")
        try:
            schema_file = BASE_DIR / "database" / "schema.sql"
            seed_file = BASE_DIR / "database" / "seed.sql"
            
            with conn.cursor() as cursor:
                # Read schema
                with open(schema_file, "r", encoding="utf-8") as f:
                    schema_sql = f.read()
                for statement in schema_sql.split(";"):
                    stmt = statement.strip()
                    if stmt and not stmt.startswith("--") and not stmt.upper().startswith("CREATE DATABASE") and not stmt.upper().startswith("USE "):
                        cursor.execute(stmt)
                
                # Check if users table already has data
                cursor.execute("SELECT COUNT(*) as count FROM users")
                row = cursor.fetchone()
                if row["count"] == 0 or force_reseed:
                    with open(seed_file, "r", encoding="utf-8") as f:
                        seed_sql = f.read()
                    for statement in seed_sql.split(";"):
                        stmt = statement.strip()
                        if stmt and not stmt.startswith("--") and not stmt.upper().startswith("USE "):
                            cursor.execute(stmt)
            conn.commit()
            print("[DB] MySQL database initialized and seeded successfully.")
        finally:
            conn.close()
    else:
        print(f"[DB] Initializing SQLite database at: {Config.SQLITE_DB_PATH}...")
        try:
            cursor = conn.cursor()
            # Create SQLite tables
            cursor.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS departments (
                department_id INTEGER PRIMARY KEY AUTOINCREMENT,
                department_name TEXT NOT NULL UNIQUE,
                location TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS wards (
                ward_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ward_name TEXT NOT NULL,
                department_id INTEGER NOT NULL,
                number_of_beds INTEGER NOT NULL DEFAULT 10,
                FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS doctors (
                doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL,
                specialization TEXT NOT NULL,
                license_number TEXT NOT NULL UNIQUE,
                department_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (department_id) REFERENCES departments(department_id)
            );

            CREATE TABLE IF NOT EXISTS nurses (
                nurse_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL,
                gender TEXT NOT NULL,
                date_of_birth DATE NOT NULL,
                qualification TEXT NOT NULL,
                license_number TEXT NOT NULL UNIQUE,
                department_id INTEGER NOT NULL,
                joining_date DATE NOT NULL,
                employment_status TEXT NOT NULL DEFAULT 'ACTIVE',
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (department_id) REFERENCES departments(department_id)
            );

            CREATE TABLE IF NOT EXISTS patients (
                patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                blood_group TEXT NOT NULL,
                room_number TEXT NOT NULL,
                bed_number TEXT NOT NULL,
                ward_id INTEGER NOT NULL,
                admission_date DATE NOT NULL,
                discharge_date DATE,
                FOREIGN KEY (ward_id) REFERENCES wards(ward_id)
            );

            CREATE TABLE IF NOT EXISTS shifts (
                shift_id INTEGER PRIMARY KEY AUTOINCREMENT,
                shift_name TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS nurse_shifts (
                assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                nurse_id INTEGER NOT NULL,
                shift_id INTEGER NOT NULL,
                assigned_date DATE NOT NULL,
                FOREIGN KEY (nurse_id) REFERENCES nurses(nurse_id) ON DELETE CASCADE,
                FOREIGN KEY (shift_id) REFERENCES shifts(shift_id) ON DELETE CASCADE,
                UNIQUE (nurse_id, assigned_date)
            );

            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                nurse_id INTEGER NOT NULL,
                shift_id INTEGER NOT NULL,
                date DATE NOT NULL,
                scheduled_start TEXT NOT NULL,
                scheduled_end TEXT NOT NULL,
                check_in TIMESTAMP,
                check_out TIMESTAMP,
                total_working_hours REAL DEFAULT 0.0,
                status TEXT NOT NULL DEFAULT 'PRESENT',
                FOREIGN KEY (nurse_id) REFERENCES nurses(nurse_id) ON DELETE CASCADE,
                FOREIGN KEY (shift_id) REFERENCES shifts(shift_id),
                UNIQUE (nurse_id, date)
            );

            CREATE TABLE IF NOT EXISTS tasks (
                task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_title TEXT NOT NULL,
                description TEXT NOT NULL,
                patient_id INTEGER NOT NULL,
                nurse_id INTEGER NOT NULL,
                assigned_by INTEGER NOT NULL,
                priority TEXT NOT NULL DEFAULT 'MEDIUM',
                status TEXT NOT NULL DEFAULT 'ASSIGNED',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_time TIMESTAMP NOT NULL,
                completed_at TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
                FOREIGN KEY (nurse_id) REFERENCES nurses(nurse_id) ON DELETE CASCADE,
                FOREIGN KEY (assigned_by) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS task_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                old_status TEXT,
                new_status TEXT NOT NULL,
                action TEXT NOT NULL,
                comment TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS notifications (
                notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                notification_type TEXT NOT NULL DEFAULT 'TASK_UPDATE',
                is_read INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
            """)
            
            # Check if seeded
            cursor.execute("SELECT COUNT(*) as count FROM users")
            row = cursor.fetchone()
            if row[0] == 0 or force_reseed:
                today = datetime.now().strftime("%Y-%m-%d")
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                
                # Hashes generated from scrypt
                admin_hash = "scrypt:32768:8:1$Orciz4eJVBNK40Qy$99f85825120b2c1370a63322e0abf5b339db27def1ca2f898b1dced16e6a803e5d0bd4fb0b89ccc7eaba0beeef6189e3cc9eab48a0b31813dbae60d37f8083e5"
                doc_hash = "scrypt:32768:8:1$rTZtLbbPQZxgpG5p$8bc3d4868a3acbeb5ac24070129d3888eb7804bfc89b4a05d84ca9c5edba060f6d6ba96c86ab2e5d06dbf950a14ec6e8cf68ae1516ac814673973af066eefabb"
                nurse_hash = "scrypt:32768:8:1$wXrj7IG6yvj3AGe9$0857932b17e9420e93312763bad3cfe391f5b95cf9a9437e981077259e9e05e24458e5d4296d85e61d9960fd4026ba47dc3f89bc8a132957ae2b3bdb904a6bb2"

                # Departments
                cursor.executemany("INSERT OR REPLACE INTO departments VALUES (?, ?, ?)", [
                    (1, 'Cardiology', 'Building A, 3rd Floor'),
                    (2, 'Emergency', 'Building B, Ground Floor'),
                    (3, 'Pediatrics', 'Building C, 2nd Floor')
                ])

                # Wards
                cursor.executemany("INSERT OR REPLACE INTO wards VALUES (?, ?, ?, ?)", [
                    (1, 'Cardiac ICU', 1, 12),
                    (2, 'Coronary Care Ward', 1, 20),
                    (3, 'Emergency Trauma Unit', 2, 15),
                    (4, 'Pediatric General Ward', 3, 25)
                ])

                # Users
                users_data = [
                    (1, 'admin', admin_hash, 'ADMIN', 'admin@hospital.org', now_str),
                    (2, 'dr_smith', doc_hash, 'DOCTOR', 'smith@hospital.org', now_str),
                    (3, 'dr_sarah', doc_hash, 'DOCTOR', 'sarah@hospital.org', now_str),
                    (4, 'dr_raj', doc_hash, 'DOCTOR', 'raj@hospital.org', now_str),
                    (5, 'nurse_emily', nurse_hash, 'NURSE', 'emily@hospital.org', now_str),
                    (6, 'nurse_james', nurse_hash, 'NURSE', 'james@hospital.org', now_str),
                    (7, 'nurse_priya', nurse_hash, 'NURSE', 'priya@hospital.org', now_str),
                    (8, 'nurse_clara', nurse_hash, 'NURSE', 'clara@hospital.org', now_str),
                    (9, 'nurse_david', nurse_hash, 'NURSE', 'david@hospital.org', now_str),
                    (10, 'nurse_sophia', nurse_hash, 'NURSE', 'sophia@hospital.org', now_str),
                    (11, 'nurse_michael', nurse_hash, 'NURSE', 'michael@hospital.org', now_str),
                    (12, 'nurse_olivia', nurse_hash, 'NURSE', 'olivia@hospital.org', now_str)
                ]
                cursor.executemany("INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?, ?, ?)", users_data)

                # Doctors
                doctors_data = [
                    (1, 2, 'Dr. Robert Smith', '+1-555-0101', 'smith@hospital.org', 'Interventional Cardiology', 'DOC-LIC-8821', 1),
                    (2, 3, 'Dr. Sarah Connor', '+1-555-0102', 'sarah@hospital.org', 'Emergency Medicine & Trauma', 'DOC-LIC-7742', 2),
                    (3, 4, 'Dr. Rajesh Patel', '+1-555-0103', 'raj@hospital.org', 'Pediatric Intensive Care', 'DOC-LIC-9915', 3)
                ]
                cursor.executemany("INSERT OR REPLACE INTO doctors VALUES (?, ?, ?, ?, ?, ?, ?, ?)", doctors_data)

                # Nurses
                nurses_data = [
                    (1, 5, 'Emily Watson', '+1-555-0201', 'emily@hospital.org', 'Female', '1992-04-12', 'BSN, RN, CCRN', 'NUR-LIC-1001', 1, '2021-03-15', 'ACTIVE'),
                    (2, 6, 'James Miller', '+1-555-0202', 'james@hospital.org', 'Male', '1990-08-23', 'BSN, RN, CEN', 'NUR-LIC-1002', 2, '2020-07-01', 'ACTIVE'),
                    (3, 7, 'Priya Sharma', '+1-555-0203', 'priya@hospital.org', 'Female', '1995-01-18', 'MSN, CPNP-PC', 'NUR-LIC-1003', 3, '2022-02-10', 'ACTIVE'),
                    (4, 8, 'Clara Bennett', '+1-555-0204', 'clara@hospital.org', 'Female', '1993-11-05', 'BSN, RN', 'NUR-LIC-1004', 1, '2021-09-20', 'ACTIVE'),
                    (5, 9, 'David Lee', '+1-555-0205', 'david@hospital.org', 'Male', '1991-06-30', 'BSN, RN, TCRN', 'NUR-LIC-1005', 2, '2019-11-15', 'ACTIVE'),
                    (6, 10, 'Sophia Anderson', '+1-555-0206', 'sophia@hospital.org', 'Female', '1996-03-14', 'BSN, RN', 'NUR-LIC-1006', 3, '2023-01-05', 'ACTIVE'),
                    (7, 11, 'Michael Brown', '+1-555-0207', 'michael@hospital.org', 'Male', '1989-09-27', 'ADN, RN', 'NUR-LIC-1007', 1, '2018-05-12', 'ACTIVE'),
                    (8, 12, 'Olivia Garcia', '+1-555-0208', 'olivia@hospital.org', 'Female', '1994-12-08', 'BSN, RN', 'NUR-LIC-1008', 2, '2022-08-18', 'ACTIVE')
                ]
                cursor.executemany("INSERT OR REPLACE INTO nurses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", nurses_data)

                # Shifts
                cursor.executemany("INSERT OR REPLACE INTO shifts VALUES (?, ?, ?, ?)", [
                    (1, 'Morning Shift', '07:00:00', '15:00:00'),
                    (2, 'Evening Shift', '15:00:00', '23:00:00'),
                    (3, 'Night Shift', '23:00:00', '07:00:00')
                ])

                # Nurse Shifts
                cursor.executemany("INSERT OR REPLACE INTO nurse_shifts VALUES (?, ?, ?, ?)", [
                    (1, 1, 1, today),
                    (2, 2, 1, today),
                    (3, 3, 1, today),
                    (4, 4, 2, today),
                    (5, 5, 2, today),
                    (6, 6, 2, today),
                    (7, 7, 3, today),
                    (8, 8, 3, today)
                ])

                # Patients
                patients_data = [
                    (1, 'Johnathan Doe', 62, 'Male', 'O+', '301', 'B-1', 1, '2026-09-15', None),
                    (2, 'Eleanor Vance', 45, 'Female', 'A+', '304', 'B-2', 1, '2026-09-18', None),
                    (3, 'Carlos Mendez', 38, 'Male', 'B-', '102', 'B-1', 3, today, None),
                    (4, 'Lucas Wright', 7, 'Male', 'O-', '205', 'B-4', 4, '2026-09-17', None),
                    (5, 'Martha Stewart', 71, 'Female', 'AB+', '306', 'B-3', 2, '2026-09-14', None),
                    (6, 'Henry Adams', 54, 'Male', 'A-', '302', 'B-2', 1, '2026-09-12', None),
                    (7, 'Maya Lin', 29, 'Female', 'O+', '105', 'B-3', 3, today, None),
                    (8, 'Liam Johnson', 11, 'Male', 'B+', '208', 'B-1', 4, '2026-09-17', None),
                    (9, 'Samuel Green', 68, 'Male', 'A+', '310', 'B-1', 2, '2026-09-10', None),
                    (10, 'Chloe Davis', 5, 'Female', 'O+', '202', 'B-2', 4, today, None)
                ]
                cursor.executemany("INSERT OR REPLACE INTO patients VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", patients_data)

                # Attendance
                att_data = [
                    (1, 1, 1, yesterday, '07:00:00', '15:00:00', f"{yesterday} 06:55:00", f"{yesterday} 15:10:00", 8.25, 'PRESENT'),
                    (2, 2, 1, yesterday, '07:00:00', '15:00:00', f"{yesterday} 07:15:00", f"{yesterday} 15:00:00", 7.75, 'LATE'),
                    (3, 3, 1, yesterday, '07:00:00', '15:00:00', f"{yesterday} 07:00:00", f"{yesterday} 15:05:00", 8.08, 'PRESENT'),
                    (4, 4, 2, yesterday, '15:00:00', '23:00:00', f"{yesterday} 14:58:00", f"{yesterday} 23:02:00", 8.07, 'PRESENT'),
                    (5, 1, 1, today, '07:00:00', '15:00:00', f"{today} 06:58:00", None, 0.00, 'PRESENT')
                ]
                cursor.executemany("INSERT OR REPLACE INTO attendance VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", att_data)

                # Tasks
                due_soon = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
                due_critical = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
                past_due = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
                completed_time = (datetime.now() - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")

                tasks_data = [
                    (1, 'Administer IV Antibiotics (Ceftriaxone 1g)', 'Dilute in 50ml normal saline, infuse over 30 minutes. Monitor for allergic reaction.', 1, 1, 2, 'HIGH', 'IN_PROGRESS', now_str, due_soon, None, 'Patient tolerated first 15 mins well.'),
                    (2, 'Check Post-Op ECG & Vital Signs', 'Record 12-lead ECG, blood pressure, heart rate, and oxygen saturation. Report ST changes immediately.', 2, 1, 2, 'CRITICAL', 'ASSIGNED', now_str, due_critical, None, None),
                    (3, 'Administer Nebulization & Chest Physio', 'Salbutamol 2.5mg nebulization followed by gentle postural drainage.', 4, 3, 4, 'MEDIUM', 'COMPLETED', now_str, past_due, completed_time, 'Wheezing significantly reduced.'),
                    (4, 'Wound Dressing & Drain Inspection', 'Clean abdominal surgical site with Betadine, measure output from Jackson-Pratt drain.', 5, 4, 2, 'MEDIUM', 'ASSIGNED', now_str, due_soon, None, None),
                    (5, 'Trauma Blood Panel & Crossmatch', 'Draw 10ml blood for CBC, PT/INR, Crossmatch 2 units PRBC immediately.', 3, 2, 3, 'CRITICAL', 'ASSIGNED', now_str, due_critical, None, None),
                    (6, 'Blood Glucose Monitoring (Fasting)', 'Accu-Chek fingerstick glucose. If > 180 mg/dL, alert on-call doctor for sliding scale insulin.', 6, 1, 2, 'LOW', 'OVERDUE', now_str, past_due, None, 'Delayed due to urgent ECG on bed 1.')
                ]
                cursor.executemany("INSERT OR REPLACE INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", tasks_data)

                # Task Logs
                task_logs_data = [
                    (1, 1, 2, None, 'ASSIGNED', 'Task Created', 'Task assigned to Nurse Emily Watson', now_str),
                    (2, 1, 5, 'ASSIGNED', 'IN_PROGRESS', 'Task Started', 'Started antibiotic IV infusion', now_str),
                    (3, 2, 2, None, 'ASSIGNED', 'Task Created', 'Task assigned to Nurse Emily Watson', now_str),
                    (4, 3, 4, None, 'ASSIGNED', 'Task Created', 'Task assigned to Nurse Priya Sharma', now_str),
                    (5, 3, 7, 'ASSIGNED', 'IN_PROGRESS', 'Task Started', 'Began nebulizer therapy', now_str),
                    (6, 3, 7, 'IN_PROGRESS', 'COMPLETED', 'Task Completed', 'Wheezing resolved, lungs clear', completed_time)
                ]
                cursor.executemany("INSERT OR REPLACE INTO task_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?)", task_logs_data)

                # Notifications
                notifications_data = [
                    (1, 5, 'New Critical Task Assigned', 'Dr. Robert Smith assigned you: Check Post-Op ECG & Vital Signs for Eleanor Vance', 'TASK_ASSIGNED', 0, now_str),
                    (2, 5, 'Task Due Soon', 'Reminder: Administer IV Antibiotics is due in 2 hours', 'TASK_UPDATE', 0, now_str),
                    (3, 2, 'Task Completed', 'Nurse Priya Sharma completed Nebulization for Lucas Wright', 'TASK_COMPLETED', 1, completed_time),
                    (4, 5, 'Shift Schedule Reminder', 'You are assigned to Morning Shift (07:00 - 15:00) today.', 'SHIFT_ALERT', 1, now_str)
                ]
                cursor.executemany("INSERT OR REPLACE INTO notifications VALUES (?, ?, ?, ?, ?, ?, ?)", notifications_data)

            conn.commit()
            print("[DB] SQLite database initialized and seeded successfully.")
        finally:
            conn.close()

if __name__ == "__main__":
    init_db()
