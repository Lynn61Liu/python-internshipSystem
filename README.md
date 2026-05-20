# InternLink Internship Management System

InternLink is a role-based Flask web application for managing internship discovery, applications, and review workflows across three user types:

- Students
- Employers
- Administrators

The project is designed for local demonstration and development, with a SQLite-backed default setup and seeded sample data.

## Features

- Secure login with Student, Employer, and Admin roles
- Student dashboard for browsing internships and submitting applications
- Employer dashboard for viewing internships and reviewing applications
- Admin dashboard for user management and platform oversight
- Resume upload, profile image upload, and employer logo support
- Bootstrap-based templates with JavaScript-enhanced interactions
- Included local demo database for portfolio and showcase use

## Tech Stack

- Python
- Flask
- Flask-Bcrypt
- SQLite
- HTML / Jinja2
- Bootstrap
- JavaScript

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Open:

`http://127.0.0.1:5000`

## Demo Accounts

- Student: `student1` / `Password123`
- Employer: `employer1` / `Password123`
- Admin: `admin1` / `Password123`

Additional seeded employers, students, internships, and applications are also included in the demo database for richer UI presentation.

## Project Structure

```text
mysite/       Flask app package, routes, DB helpers, schema
templates/    Primary HTML templates used by the app
static/       JavaScript, images, resumes, and other static assets
tests/        Local smoke tests
instance/     Local SQLite database files
run.py        Local Flask entry point
```

## Database

The default local database is:

`instance/internship.sqlite3`

The relational schema is defined in:

`mysite/schema.sql`

The app defaults to SQLite for local use, but the DB layer keeps compatibility with a MySQL-style configuration path.

You can override the database path with environment variables:

```bash
export APP_DB_BACKEND=sqlite
export APP_DB_NAME=instance/custom.sqlite3
```

## Notes

- This repository is configured for local demo use first.
- The seeded SQLite database is intentionally included so the project can be run and presented immediately after cloning.
- Temporary smoke-test databases are ignored from version control.
