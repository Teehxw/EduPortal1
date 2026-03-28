# 📚 Course Management System

A Python-based command-line application for managing an online learning platform. Students can browse and enroll in courses, instructors can manage their courses and students, and admins can view platform-wide statistics.

---

## Features

### Student
- Search for courses by keyword, category, or price range
- Enroll in courses with credit card payment
- View active enrollments and course content (modules and lessons)
- Mark lessons as complete
- View grades and certificates
- View past payments

### Instructor
- Update course price, pass grade, and max student capacity
- Override enrollment (manually enroll a student into a course)
- View course statistics (active enrollment, completion rate, average final grade)

### Admin
- View top 5 courses by active enrollment
- View payment counts per course

---

## Project Structure

```
.
├── main.py          # Entry point and database setup
├── login.py         # Login and registration logic
├── student.py       # Student menu and functionality
├── instructor.py    # Instructor menu and functionality
├── admin.py         # Admin menu and functionality
└── project291.db    # SQLite database (auto-generated)
```

---

## Database Schema

| Table | Description |
|---|---|
| `users` | Stores all users (students, instructors, admins) |
| `courses` | Course listings with price, pass grade, and capacity |
| `enrollments` | Links users to courses with start/end timestamps |
| `modules` | Course modules with weights |
| `lessons` | Lessons within modules |
| `completion` | Tracks which lessons a student has completed |
| `grades` | Module grades per student |
| `certificates` | Issued when a student passes a course |
| `payments` | Payment records with masked card numbers |

---

## Getting Started

### Requirements

- Python 3.x
- SQLite3 (included with Python)

No external dependencies required.

### Running the Program

```bash
python main.py <database_file>
```

**Example:**
```bash
python main.py sample_db.sql
```

The database file will be read if it already exists. If you want to reset and recreate all tables from scratch, call `setup_db()` directly (note: this drops all existing data).

---

## Usage

On launch, you'll see the main menu:

```
**** WELCOME ****

1. Login
2. Register
3. Exit
```

**Registering** creates a new Student account. Instructors and Admins must be added directly to the database.

**Logging in** requires your user ID (uid) and password. After login, you are directed to the appropriate menu based on your role.

---

## Notes

- Credit card numbers are masked before storage — only the last 4 digits are saved.
- Enrollments are active for 1 year from the date of enrollment.
- Certificates are automatically issued or revoked when an instructor updates the pass grade, based on each student's completed lessons and weighted final grade.
- Pagination is used throughout the app — lists are displayed 5 items per page with next/previous navigation.
