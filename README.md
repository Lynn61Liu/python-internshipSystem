# Local Run Guide

This project has been rebuilt to run locally with SQLite by default.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Open `http://127.0.0.1:5000`.

## Demo accounts

- `student1` / `Password123`
- `employer1` / `Password123`
- `admin1` / `Password123`

## Local database

- Default file: `instance/internship.sqlite3`
- Schema source: `mysite/schema.sql`
- Backend can be overridden with environment variables:

```bash
export APP_DB_BACKEND=sqlite
export APP_DB_NAME=instance/custom.sqlite3
```

MySQL is still supported, but only if you provide matching `APP_DB_*`
environment variables and install `mysqlclient`.
