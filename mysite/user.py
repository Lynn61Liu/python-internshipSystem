from __future__ import annotations

import os
import re

from flask import current_app, flash, redirect, render_template, request, session, url_for
from flask_bcrypt import Bcrypt

from mysite import app, db


flask_bcrypt = Bcrypt(app)
DEFAULT_USER_ROLE = "Student"


def user_home_url():
    if "loggedin" in session:
        role = session.get("role")
        if role == "Student":
            home_endpoint = "customer_home"
        elif role == "Employer":
            home_endpoint = "staff_home"
        elif role == "Admin":
            home_endpoint = "admin_home"
        else:
            home_endpoint = "logout"
    else:
        home_endpoint = "login"
    return url_for(home_endpoint)


@app.route("/")
def root():
    return redirect(user_home_url())


@app.route("/login", methods=["GET", "POST"])
def login():
    if "loggedin" in session:
        return redirect(user_home_url())

    if request.method == "POST" and {"username", "password"} <= set(request.form):
        username = request.form["username"]
        password = request.form["password"]

        with db.get_cursor() as cursor:
            cursor.execute(
                """
                SELECT user_id, username, password_hash, role, status
                FROM users
                WHERE username = %s;
                """,
                (username,),
            )
            account = cursor.fetchone()

        if account is None:
            return render_template("login.html", username=username, username_invalid=True)

        password_hash = account["password_hash"]
        if flask_bcrypt.check_password_hash(password_hash, password):
            session["loggedin"] = True
            session["user_id"] = account["user_id"]
            session["username"] = account["username"]
            session["role"] = account["role"]
            session["status"] = account["status"]
            return redirect(user_home_url())

        return render_template("login.html", username=username, password_invalid=True)

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "loggedin" in session:
        return redirect(user_home_url())

    if request.method == "POST" and {"username", "email", "password"} <= set(request.form):
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        username_error = None
        email_error = None
        password_errors = []

        with db.get_cursor() as cursor:
            cursor.execute("SELECT user_id FROM users WHERE username = %s;", (username,))
            account_already_exists = cursor.fetchone() is not None

        if account_already_exists:
            username_error = "An account already exists with this username."
        elif len(username) > 20:
            username_error = "Your username cannot exceed 20 characters."
        elif not re.fullmatch(r"[A-Za-z0-9]+", username):
            username_error = "Your username can only contain letters and numbers."

        if len(email) > 320:
            email_error = "Your email address cannot exceed 320 characters."
        elif not re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email):
            email_error = "Invalid email address."

        password_errors = validate_password(password)

        if username_error or email_error or password_errors:
            return render_template(
                "signup.html",
                username=username,
                email=email,
                username_error=username_error,
                email_error=email_error,
                password_error=" ".join(password_errors) if password_errors else None,
            )

        password_hash = flask_bcrypt.generate_password_hash(password)
        with db.get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (username, password_hash, email, role)
                VALUES (%s, %s, %s, %s);
                """,
                (username, password_hash, email, DEFAULT_USER_ROLE),
            )
            user_id = cursor.lastrowid

        with db.get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO students (user_id, university, course)
                VALUES (%s, NULL, NULL);
                """,
                (user_id,),
            )

        return render_template("signup.html", signup_successful=True)

    return render_template("signup.html")


@app.route("/profile")
def profile():
    if "loggedin" not in session:
        return redirect(url_for("login"))

    role = session.get("role")
    if role == "Student":
        query = """
            SELECT
                u.user_id,
                u.username,
                u.email,
                u.role,
                u.full_name,
                u.profile_image,
                s.university,
                s.course,
                s.resume_path,
                s.student_id
            FROM users u
            LEFT JOIN students s ON u.user_id = s.user_id
            WHERE u.user_id = %s;
        """
    elif role == "Employer":
        query = """
            SELECT
                u.user_id,
                u.username,
                u.email,
                u.role,
                u.full_name,
                u.profile_image,
                e.company_name,
                e.company_description,
                e.website,
                e.emp_id,
                e.logo_path
            FROM users u
            LEFT JOIN employers e ON u.user_id = e.user_id
            WHERE u.user_id = %s;
        """
    else:
        query = """
            SELECT
                u.*
            FROM users u
            WHERE u.user_id = %s;
        """

    with db.get_cursor() as cursor:
        cursor.execute(query, (session["user_id"],))
        profile_data = cursor.fetchone()

    return render_template("profile.html", profile=profile_data)


@app.route("/logout")
def logout():
    session.pop("loggedin", None)
    session.pop("user_id", None)
    session.pop("username", None)
    session.pop("role", None)
    return redirect(url_for("login"))


def _save_uploaded_file(file_storage, subdir: str, filename: str):
    if not file_storage or not file_storage.filename:
        return None
    target_dir = os.path.join(current_app.static_folder, subdir)
    os.makedirs(target_dir, exist_ok=True)
    full_path = os.path.join(target_dir, filename)
    file_storage.save(full_path)
    return os.path.join(subdir, filename).replace("\\", "/")


@app.route("/update_profile", methods=["POST"])
def update_profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    role = session.get("role")
    with db.get_cursor() as cursor:
        if role == "Student":
            full_name = request.form.get("full_name")
            university = request.form.get("university")
            course = request.form.get("course")
            resume_file = request.files.get("resume")
            photo_file = request.files.get("photo")
            delete_photo = request.form.get("delete_photo") == "true"

            resume_path = None
            if resume_file and resume_file.filename.endswith(".pdf"):
                resume_path = _save_uploaded_file(
                    resume_file, "resume", f"resume_user_{user_id}.pdf"
                )

            photo_relative_path = None
            if delete_photo:
                photo_relative_path = "images/default.jpg"
            elif photo_file and photo_file.filename:
                photo_relative_path = _save_uploaded_file(
                    photo_file, "images", f"user_{user_id}.jpg"
                )

            cursor.execute(
                """
                UPDATE users
                SET full_name = %s
                WHERE user_id = %s
                """,
                (full_name, user_id),
            )

            cursor.execute(
                """
                UPDATE students
                SET university = %s,
                    course = %s
                    {resume_clause}
                WHERE user_id = %s
                """.format(resume_clause=", resume_path = %s" if resume_path else ""),
                (university, course, resume_path, user_id)
                if resume_path
                else (university, course, user_id),
            )

            if photo_relative_path:
                cursor.execute(
                    """
                    UPDATE users
                    SET profile_image = %s
                    WHERE user_id = %s
                    """,
                    (photo_relative_path, user_id),
                )

        elif role == "Employer":
            company_name = request.form.get("company_name")
            company_description = request.form.get("company_description")
            website = request.form.get("website")
            logo_file = request.files.get("company_logo")
            delete_logo = request.form.get("delete_logo") == "true"

            logo_path = None
            if delete_logo:
                logo_path = "images/default.jpg"
            elif logo_file and logo_file.filename:
                logo_path = _save_uploaded_file(
                    logo_file, "images", f"logo_user_{user_id}.jpg"
                )

            cursor.execute(
                """
                UPDATE employers
                SET company_name = %s,
                    company_description = %s,
                    website = %s
                    {logo_clause}
                WHERE user_id = %s
                """.format(logo_clause=", logo_path = %s" if logo_path else ""),
                (company_name, company_description, website, logo_path, user_id)
                if logo_path
                else (company_name, company_description, website, user_id),
            )
        else:
            full_name = request.form.get("full_name")
            photo_file = request.files.get("adminPhoto")
            delete_photo = request.form.get("delete-image-flag") == "true"

            photo_relative_path = None
            if delete_photo:
                photo_relative_path = "images/default.jpg"
            elif photo_file and photo_file.filename:
                photo_relative_path = _save_uploaded_file(
                    photo_file, "images", f"user_{user_id}.jpg"
                )

            cursor.execute(
                """
                UPDATE users
                SET full_name = %s
                WHERE user_id = %s
                """,
                (full_name, user_id),
            )
            if photo_relative_path:
                cursor.execute(
                    """
                    UPDATE users
                    SET profile_image = %s
                    WHERE user_id = %s
                    """,
                    (photo_relative_path, user_id),
                )

    return redirect(url_for("profile"))


def validate_password(new_password, current_password=None):
    errors = []
    if len(new_password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not re.search(r"[A-Za-z]", new_password) or not re.search(r"\d", new_password):
        errors.append("Password must contain both letters and numbers.")

    if current_password:
        with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT password_hash FROM users WHERE user_id = %s",
                (session["user_id"],),
            )
            result = cursor.fetchone()
            data_pw_hash = result["password_hash"] if result else None
            if data_pw_hash and not flask_bcrypt.check_password_hash(
                data_pw_hash, current_password
            ):
                errors.append("Current password is incorrect.")
            if data_pw_hash and flask_bcrypt.check_password_hash(
                data_pw_hash, new_password
            ):
                errors.append("New password cannot be the same as the current password.")
    return errors


@app.route("/dbtest")
def dbtest():
    try:
        with db.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total_users FROM users")
            result = cursor.fetchone()
        return f"Database connection successful. Users: {result['total_users']}"
    except Exception as exc:  # pragma: no cover - route-level diagnostics
        return f"Database connection failed: {exc}"


@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "GET":
        return render_template("change_password.html")

    current_password = request.form["current_password"]
    new_password = request.form["new_password"]
    errors = validate_password(new_password, current_password)

    if errors:
        flash(" ".join(errors), "danger")
        return redirect(url_for("change_password"))

    new_password_hash = flask_bcrypt.generate_password_hash(new_password)
    with db.get_cursor() as cursor:
        cursor.execute(
            """
            UPDATE users SET password_hash = %s WHERE user_id = %s
            """,
            (new_password_hash, session["user_id"]),
        )

    flash("Password changed successfully.", "success")
    return redirect(url_for("change_password"))
