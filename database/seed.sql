-- Nurse Task Management System - Seed Data
-- -------------------------------------------------------------

USE nurse_task_db;

-- 1. Insert Departments
INSERT INTO departments (department_id, department_name, location) VALUES
(1, 'Cardiology', 'Building A, 3rd Floor'),
(2, 'Emergency', 'Building B, Ground Floor'),
(3, 'Pediatrics', 'Building C, 2nd Floor')
ON DUPLICATE KEY UPDATE department_name=VALUES(department_name);

-- 2. Insert Wards
INSERT INTO wards (ward_id, ward_name, department_id, number_of_beds) VALUES
(1, 'Cardiac ICU', 1, 12),
(2, 'Coronary Care Ward', 1, 20),
(3, 'Emergency Trauma Unit', 2, 15),
(4, 'Pediatric General Ward', 3, 25)
ON DUPLICATE KEY UPDATE ward_name=VALUES(ward_name);

-- 3. Insert Users (Password hashes for: admin123, doctor123, nurse123)
-- Admin: user_id = 1
-- Doctors: user_id = 2, 3, 4
-- Nurses: user_id = 5, 6, 7, 8, 9, 10, 11, 12
INSERT INTO users (user_id, username, password_hash, role, email, created_at) VALUES
(1, 'admin', 'scrypt:32768:8:1$Orciz4eJVBNK40Qy$99f85825120b2c1370a63322e0abf5b339db27def1ca2f898b1dced16e6a803e5d0bd4fb0b89ccc7eaba0beeef6189e3cc9eab48a0b31813dbae60d37f8083e5', 'ADMIN', 'admin@hospital.org', NOW()),

-- Doctors
(2, 'dr_smith', 'scrypt:32768:8:1$rTZtLbbPQZxgpG5p$8bc3d4868a3acbeb5ac24070129d3888eb7804bfc89b4a05d84ca9c5edba060f6d6ba96c86ab2e5d06dbf950a14ec6e8cf68ae1516ac814673973af066eefabb', 'DOCTOR', 'smith@hospital.org', NOW()),
(3, 'dr_sarah', 'scrypt:32768:8:1$rTZtLbbPQZxgpG5p$8bc3d4868a3acbeb5ac24070129d3888eb7804bfc89b4a05d84ca9c5edba060f6d6ba96c86ab2e5d06dbf950a14ec6e8cf68ae1516ac814673973af066eefabb', 'DOCTOR', 'sarah@hospital.org', NOW()),
(4, 'dr_raj', 'scrypt:32768:8:1$rTZtLbbPQZxgpG5p$8bc3d4868a3acbeb5ac24070129d3888eb7804bfc89b4a05d84ca9c5edba060f6d6ba96c86ab2e5d06dbf950a14ec6e8cf68ae1516ac814673973af066eefabb', 'DOCTOR', 'raj@hospital.org', NOW()),

-- Nurses
(5, 'nurse_emily', 'scrypt:32768:8:1$wXrj7IG6yvj3AGe9$0857932b17e9420e93312763bad3cfe391f5b95cf9a9437e981077259e9e05e24458e5d4296d85e61d9960fd4026ba47dc3f89bc8a132957ae2b3bdb904a6bb2', 'NURSE', 'emily@hospital.org', NOW()),
(6, 'nurse_james', 'scrypt:32768:8:1$wXrj7IG6yvj3AGe9$0857932b17e9420e93312763bad3cfe391f5b95cf9a9437e981077259e9e05e24458e5d4296d85e61d9960fd4026ba47dc3f89bc8a132957ae2b3bdb904a6bb2', 'NURSE', 'james@hospital.org', NOW()),
(7, 'nurse_priya', 'scrypt:32768:8:1$wXrj7IG6yvj3AGe9$0857932b17e9420e93312763bad3cfe391f5b95cf9a9437e981077259e9e05e24458e5d4296d85e61d9960fd4026ba47dc3f89bc8a132957ae2b3bdb904a6bb2', 'NURSE', 'priya@hospital.org', NOW()),
(8, 'nurse_clara', 'scrypt:32768:8:1$wXrj7IG6yvj3AGe9$0857932b17e9420e93312763bad3cfe391f5b95cf9a9437e981077259e9e05e24458e5d4296d85e61d9960fd4026ba47dc3f89bc8a132957ae2b3bdb904a6bb2', 'NURSE', 'clara@hospital.org', NOW()),
(9, 'nurse_david', 'scrypt:32768:8:1$wXrj7IG6yvj3AGe9$0857932b17e9420e93312763bad3cfe391f5b95cf9a9437e981077259e9e05e24458e5d4296d85e61d9960fd4026ba47dc3f89bc8a132957ae2b3bdb904a6bb2', 'NURSE', 'david@hospital.org', NOW()),
(10, 'nurse_sophia', 'scrypt:32768:8:1$wXrj7IG6yvj3AGe9$0857932b17e9420e93312763bad3cfe391f5b95cf9a9437e981077259e9e05e24458e5d4296d85e61d9960fd4026ba47dc3f89bc8a132957ae2b3bdb904a6bb2', 'NURSE', 'sophia@hospital.org', NOW()),
(11, 'nurse_michael', 'scrypt:32768:8:1$wXrj7IG6yvj3AGe9$0857932b17e9420e93312763bad3cfe391f5b95cf9a9437e981077259e9e05e24458e5d4296d85e61d9960fd4026ba47dc3f89bc8a132957ae2b3bdb904a6bb2', 'NURSE', 'michael@hospital.org', NOW()),
(12, 'nurse_olivia', 'scrypt:32768:8:1$wXrj7IG6yvj3AGe9$0857932b17e9420e93312763bad3cfe391f5b95cf9a9437e981077259e9e05e24458e5d4296d85e61d9960fd4026ba47dc3f89bc8a132957ae2b3bdb904a6bb2', 'NURSE', 'olivia@hospital.org', NOW())
ON DUPLICATE KEY UPDATE username=VALUES(username);

-- 4. Insert Doctors
INSERT INTO doctors (doctor_id, user_id, name, phone, email, specialization, license_number, department_id) VALUES
(1, 2, 'Dr. Robert Smith', '+1-555-0101', 'smith@hospital.org', 'Interventional Cardiology', 'DOC-LIC-8821', 1),
(2, 3, 'Dr. Sarah Connor', '+1-555-0102', 'sarah@hospital.org', 'Emergency Medicine & Trauma', 'DOC-LIC-7742', 2),
(3, 4, 'Dr. Rajesh Patel', '+1-555-0103', 'raj@hospital.org', 'Pediatric Intensive Care', 'DOC-LIC-9915', 3)
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 5. Insert Nurses (8 Nurses)
INSERT INTO nurses (nurse_id, user_id, name, phone, email, gender, date_of_birth, qualification, license_number, department_id, joining_date, employment_status) VALUES
(1, 5, 'Emily Watson', '+1-555-0201', 'emily@hospital.org', 'Female', '1992-04-12', 'BSN, RN, CCRN', 'NUR-LIC-1001', 1, '2021-03-15', 'ACTIVE'),
(2, 6, 'James Miller', '+1-555-0202', 'james@hospital.org', 'Male', '1990-08-23', 'BSN, RN, CEN', 'NUR-LIC-1002', 2, '2020-07-01', 'ACTIVE'),
(3, 7, 'Priya Sharma', '+1-555-0203', 'priya@hospital.org', 'Female', '1995-01-18', 'MSN, CPNP-PC', 'NUR-LIC-1003', 3, '2022-02-10', 'ACTIVE'),
(4, 8, 'Clara Bennett', '+1-555-0204', 'clara@hospital.org', 'Female', '1993-11-05', 'BSN, RN', 'NUR-LIC-1004', 1, '2021-09-20', 'ACTIVE'),
(5, 9, 'David Lee', '+1-555-0205', 'david@hospital.org', 'Male', '1991-06-30', 'BSN, RN, TCRN', 'NUR-LIC-1005', 2, '2019-11-15', 'ACTIVE'),
(6, 10, 'Sophia Anderson', '+1-555-0206', 'sophia@hospital.org', 'Female', '1996-03-14', 'BSN, RN', 'NUR-LIC-1006', 3, '2023-01-05', 'ACTIVE'),
(7, 11, 'Michael Brown', '+1-555-0207', 'michael@hospital.org', 'Male', '1989-09-27', 'ADN, RN', 'NUR-LIC-1007', 1, '2018-05-12', 'ACTIVE'),
(8, 12, 'Olivia Garcia', '+1-555-0208', 'olivia@hospital.org', 'Female', '1994-12-08', 'BSN, RN', 'NUR-LIC-1008', 2, '2022-08-18', 'ACTIVE')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 6. Insert Shifts
INSERT INTO shifts (shift_id, shift_name, start_time, end_time) VALUES
(1, 'Morning Shift', '07:00:00', '15:00:00'),
(2, 'Evening Shift', '15:00:00', '23:00:00'),
(3, 'Night Shift', '23:00:00', '07:00:00')
ON DUPLICATE KEY UPDATE shift_name=VALUES(shift_name);

-- 7. Nurse Shift Assignments (Today's active shifts)
INSERT INTO nurse_shifts (assignment_id, nurse_id, shift_id, assigned_date) VALUES
(1, 1, 1, CURRENT_DATE),
(2, 2, 1, CURRENT_DATE),
(3, 3, 1, CURRENT_DATE),
(4, 4, 2, CURRENT_DATE),
(5, 5, 2, CURRENT_DATE),
(6, 6, 2, CURRENT_DATE),
(7, 7, 3, CURRENT_DATE),
(8, 8, 3, CURRENT_DATE)
ON DUPLICATE KEY UPDATE shift_id=VALUES(shift_id);

-- 8. Insert Patients (10 Patients)
INSERT INTO patients (patient_id, name, age, gender, blood_group, room_number, bed_number, ward_id, admission_date, discharge_date) VALUES
(1, 'Johnathan Doe', 62, 'Male', 'O+', '301', 'B-1', 1, DATE_SUB(CURRENT_DATE, INTERVAL 3 DAY), NULL),
(2, 'Eleanor Vance', 45, 'Female', 'A+', '304', 'B-2', 1, DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY), NULL),
(3, 'Carlos Mendez', 38, 'Male', 'B-', '102', 'B-1', 3, CURRENT_DATE, NULL),
(4, 'Lucas Wright', 7, 'Male', 'O-', '205', 'B-4', 4, DATE_SUB(CURRENT_DATE, INTERVAL 2 DAY), NULL),
(5, 'Martha Stewart', 71, 'Female', 'AB+', '306', 'B-3', 2, DATE_SUB(CURRENT_DATE, INTERVAL 4 DAY), NULL),
(6, 'Henry Adams', 54, 'Male', 'A-', '302', 'B-2', 1, DATE_SUB(CURRENT_DATE, INTERVAL 5 DAY), NULL),
(7, 'Maya Lin', 29, 'Female', 'O+', '105', 'B-3', 3, CURRENT_DATE, NULL),
(8, 'Liam Johnson', 11, 'Male', 'B+', '208', 'B-1', 4, DATE_SUB(CURRENT_DATE, INTERVAL 2 DAY), NULL),
(9, 'Samuel Green', 68, 'Male', 'A+', '310', 'B-1', 2, DATE_SUB(CURRENT_DATE, INTERVAL 6 DAY), NULL),
(10, 'Chloe Davis', 5, 'Female', 'O+', '202', 'B-2', 4, CURRENT_DATE, NULL)
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- 9. Sample Attendance Records (Yesterday and Today)
INSERT INTO attendance (attendance_id, nurse_id, shift_id, date, scheduled_start, scheduled_end, check_in, check_out, total_working_hours, status) VALUES
(1, 1, 1, DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY), '07:00:00', '15:00:00', 
    CONCAT(DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY), ' 06:55:00'), 
    CONCAT(DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY), ' 15:10:00'), 8.25, 'PRESENT'),
(2, 2, 1, DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY), '07:00:00', '15:00:00', 
    CONCAT(DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY), ' 07:15:00'), 
    CONCAT(DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY), ' 15:00:00'), 7.75, 'LATE'),
(3, 3, 1, DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY), '07:00:00', '15:00:00', 
    CONCAT(DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY), ' 07:00:00'), 
    CONCAT(DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY), ' 15:05:00'), 8.08, 'PRESENT'),
(4, 4, 2, DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY), '15:00:00', '23:00:00', 
    CONCAT(DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY), ' 14:58:00'), 
    CONCAT(DATE_SUB(CURRENT_DATE, INTERVAL 1 DAY), ' 23:02:00'), 8.07, 'PRESENT'),
-- Today's attendance (Active shift for Emily checked-in)
(5, 1, 1, CURRENT_DATE, '07:00:00', '15:00:00', 
    CONCAT(CURRENT_DATE, ' 06:58:00'), NULL, 0.00, 'PRESENT')
ON DUPLICATE KEY UPDATE status=VALUES(status);

-- 10. Sample Tasks
INSERT INTO tasks (task_id, task_title, description, patient_id, nurse_id, assigned_by, priority, status, created_at, due_time, completed_at, notes) VALUES
(1, 'Administer IV Antibiotics (Ceftriaxone 1g)', 'Dilute in 50ml normal saline, infuse over 30 minutes. Monitor for allergic reaction.', 1, 1, 2, 'HIGH', 'IN_PROGRESS', 
    DATE_SUB(NOW(), INTERVAL 2 HOUR), DATE_ADD(NOW(), INTERVAL 2 HOUR), NULL, 'Patient tolerated first 15 mins well.'),
(2, 'Check Post-Op ECG & Vital Signs', 'Record 12-lead ECG, blood pressure, heart rate, and oxygen saturation. Report ST changes immediately.', 2, 1, 2, 'CRITICAL', 'ASSIGNED', 
    DATE_SUB(NOW(), INTERVAL 1 HOUR), DATE_ADD(NOW(), INTERVAL 1 HOUR), NULL, NULL),
(3, 'Administer Nebulization & Chest Physio', 'Salbutamol 2.5mg nebulization followed by gentle postural drainage.', 4, 3, 4, 'MEDIUM', 'COMPLETED', 
    DATE_SUB(NOW(), INTERVAL 5 HOUR), DATE_SUB(NOW(), INTERVAL 2 HOUR), DATE_SUB(NOW(), INTERVAL 3 HOUR), 'Wheezing significantly reduced.'),
(4, 'Wound Dressing & Drain Inspection', 'Clean abdominal surgical site with Betadine, measure output from Jackson-Pratt drain.', 5, 4, 2, 'MEDIUM', 'ASSIGNED', 
    DATE_SUB(NOW(), INTERVAL 3 HOUR), DATE_ADD(NOW(), INTERVAL 4 HOUR), NULL, NULL),
(5, 'Trauma Blood Panel & Crossmatch', 'Draw 10ml blood for CBC, PT/INR, Crossmatch 2 units PRBC immediately.', 3, 2, 3, 'CRITICAL', 'ASSIGNED', 
    DATE_SUB(NOW(), INTERVAL 30 MINUTE), DATE_ADD(NOW(), INTERVAL 30 MINUTE), NULL, NULL),
(6, 'Blood Glucose Monitoring (Fasting)', 'Accu-Chek fingerstick glucose. If > 180 mg/dL, alert on-call doctor for sliding scale insulin.', 6, 1, 2, 'LOW', 'OVERDUE', 
    DATE_SUB(NOW(), INTERVAL 4 HOUR), DATE_SUB(NOW(), INTERVAL 1 HOUR), NULL, 'Delayed due to urgent ECG on bed 1.')
ON DUPLICATE KEY UPDATE task_title=VALUES(task_title);

-- 11. Task Logs (Audit trail)
INSERT INTO task_logs (log_id, task_id, user_id, old_status, new_status, action, comment, timestamp) VALUES
(1, 1, 2, NULL, 'ASSIGNED', 'Task Created', 'Task assigned to Nurse Emily Watson', DATE_SUB(NOW(), INTERVAL 2 HOUR)),
(2, 1, 5, 'ASSIGNED', 'IN_PROGRESS', 'Task Started', 'Started antibiotic IV infusion', DATE_SUB(NOW(), INTERVAL 90 MINUTE)),
(3, 2, 2, NULL, 'ASSIGNED', 'Task Created', 'Task assigned to Nurse Emily Watson', DATE_SUB(NOW(), INTERVAL 1 HOUR)),
(4, 3, 4, NULL, 'ASSIGNED', 'Task Created', 'Task assigned to Nurse Priya Sharma', DATE_SUB(NOW(), INTERVAL 5 HOUR)),
(5, 3, 7, 'ASSIGNED', 'IN_PROGRESS', 'Task Started', 'Began nebulizer therapy', DATE_SUB(NOW(), INTERVAL 4 HOUR)),
(6, 3, 7, 'IN_PROGRESS', 'COMPLETED', 'Task Completed', 'Wheezing resolved, lungs clear', DATE_SUB(NOW(), INTERVAL 3 HOUR))
ON DUPLICATE KEY UPDATE action=VALUES(action);

-- 12. Notifications
INSERT INTO notifications (notification_id, user_id, title, message, notification_type, is_read, created_at) VALUES
(1, 5, 'New Critical Task Assigned', 'Dr. Robert Smith assigned you: Check Post-Op ECG & Vital Signs for Eleanor Vance', 'TASK_ASSIGNED', FALSE, DATE_SUB(NOW(), INTERVAL 1 HOUR)),
(2, 5, 'Task Due Soon', 'Reminder: Administer IV Antibiotics is due in 2 hours', 'TASK_UPDATE', FALSE, DATE_SUB(NOW(), INTERVAL 30 MINUTE)),
(3, 2, 'Task Completed', 'Nurse Priya Sharma completed Nebulization for Lucas Wright', 'TASK_COMPLETED', TRUE, DATE_SUB(NOW(), INTERVAL 3 HOUR)),
(4, 5, 'Shift Schedule Reminder', 'You are assigned to Morning Shift (07:00 - 15:00) today.', 'SHIFT_ALERT', TRUE, DATE_SUB(NOW(), INTERVAL 6 HOUR))
ON DUPLICATE KEY UPDATE title=VALUES(title);
