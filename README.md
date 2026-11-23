# Nurse Task Scheduling System

A Flask-based hospital task management application for managing nurses, doctors, tasks, attendance, and notifications.

## Features

- Role-based access for admin, doctor, and nurse users
- Nurse task assignment and tracking
- Attendance monitoring
- Shift management
- Department and ward management
- Notifications and dashboard views
- SQLite fallback with optional MySQL support

## Project Structure

- `app.py` — Flask application entry point
- `config.py` — app configuration and environment settings
- `routes/` — route blueprints for authentication, admin, nurse, doctor, and task flows
- `services/` — business logic for tasks, auth, notifications, and attendance
- `models/` — database models
- `templates/` — HTML templates
- `static/` — CSS, JS, and images
- `database/` — schema and seed scripts
- `tests/` — pytest-based tests

## Requirements

- Python 3.10+
- pip
- Optional: MySQL Server 8.0 (if you want to use MySQL instead of the built-in SQLite fallback)

## Setup

1. Open a terminal in the project folder.
2. Create and activate a virtual environment:

   Windows:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

   macOS/Linux:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a local environment file:
   ```bash
   copy .env.example .env
   ```

   On macOS/Linux:
   ```bash
   cp .env.example .env
   ```

5. Update the values in `.env` if needed.

## Database Configuration

The app supports both MySQL and SQLite.

### Option 1: SQLite (recommended for quick local run)

Set in `.env`:
```env
DB_TYPE=sqlite
```

The app will automatically create the SQLite database file at the path in `SQLITE_DB_PATH`.

### Option 2: MySQL

Set in `.env`:
```env
DB_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password_here
MYSQL_DB=nurse_task_db
```

If the database is not present, the app will attempt to create it automatically.

## Run the Application

From the project root, start the Flask server:

```bash
python app.py
```

Then open the app in your browser:

```text
http://127.0.0.1:5000
```

The app runs with debug mode enabled by default.

## Default Login Accounts

Seed data is automatically created when the database initializes. Example accounts:

- Admin:
  - Username: `admin`
  - Password: `admin123`

- Doctor:
  - Username: `dr_smith`
  - Password: `doctor123`

- Nurse:
  - Username: `nurse_emily`
  - Password: `nurse123`

## Run Tests

```bash
pytest
```

or:

```bash
python -m pytest
```

## Troubleshooting

- If dependencies fail to install, upgrade pip first:
  ```bash
  python -m pip install --upgrade pip
  ```
- If the database connection fails, check your `.env` values or switch to SQLite.
- If you see a missing template or static file issue, ensure you are running the app from the project root directory.

## Notes

This project is designed to work locally without extensive setup. The system automatically falls back to SQLite if MySQL is unavailable, making it easier to run and test.
