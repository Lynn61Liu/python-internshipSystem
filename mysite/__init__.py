from __future__ import annotations

from pathlib import Path

from flask import Flask
from flask_bcrypt import Bcrypt

from mysite import connect, db


BASE_DIR = Path(__file__).resolve().parent.parent

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)
app.secret_key = "Example Secret Key (CHANGE THIS TO YOUR OWN SECRET KEY!)"

db.init_db(
    app,
    connect.dbuser,
    connect.dbpass,
    connect.dbhost,
    connect.dbname,
    connect.dbport,
    backend=connect.dbbackend,
)

bcrypt = Bcrypt(app)


def seed_demo_data():
    with app.app_context():
        with db.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total FROM users")
            user_count = cursor.fetchone()["total"]
            if user_count:
                return

            demo_accounts = [
                ("student1", "Alice Student", "student@example.com", "Student"),
                ("employer1", "Bob Employer", "employer@example.com", "Employer"),
                ("admin1", "Cara Admin", "admin@example.com", "Admin"),
            ]

            created_ids = {}
            for username, full_name, email, role in demo_accounts:
                password_hash = bcrypt.generate_password_hash("Password123")
                cursor.execute(
                    """
                    INSERT INTO users
                        (username, full_name, email, role, password_hash, status)
                    VALUES (%s, %s, %s, %s, %s, 'active')
                    """,
                    (username, full_name, email, role, password_hash),
                )
                created_ids[role] = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO students (user_id, university, course, resume_path)
                VALUES (%s, %s, %s, NULL)
                """,
                (created_ids["Student"], "AUT", "Computer Science"),
            )
            cursor.execute(
                """
                INSERT INTO employers
                    (user_id, company_name, company_description, website)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    created_ids["Employer"],
                    "FutureTech",
                    "A demo employer account for local development.",
                    "https://example.com",
                ),
            )
            employer_id = cursor.lastrowid
            cursor.execute(
                """
                INSERT INTO internships
                    (company_id, title, description, location, duration, salary,
                     deadline, stipend, skills_required, number_of_opening,
                     additional_info)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    employer_id,
                    "Junior Web Developer Intern",
                    "Help maintain the internship portal and ship small Flask features.",
                    "Auckland",
                    "12 weeks",
                    28.5,
                    "2026-06-30",
                    "$1,200/month",
                    "Python, Flask, SQL, teamwork",
                    2,
                    "Demo listing created automatically for local setup.",
                ),
            )


db.ensure_schema(app)
seed_demo_data()


from mysite import admin, customer, staff, user  # noqa: E402,F401
