from __future__ import annotations

import os

from flask import current_app, flash, redirect, render_template, request, session, url_for

from mysite import app, db


@app.route("/customer/home")
def customer_home():
    if "loggedin" not in session:
        return redirect(url_for("login"))
    if session["role"] != "Student":
        return render_template("access_denied.html"), 403

    with db.get_cursor() as cursor:
        cursor.execute(
            """
            SELECT
                i.*,
                e.*,
                a.status
            FROM internships i
            JOIN employers e ON i.company_id = e.emp_id
            LEFT JOIN applications a
                ON a.internship_id = i.internship_id
                AND a.student_id = (
                    SELECT student_id FROM students WHERE user_id = %s
                )
            ORDER BY i.company_id ASC
            """,
            (session["user_id"],),
        )
        internships = cursor.fetchall()
    return render_template("customer_home.html", internships=internships)


@app.route("/apply/<int:internship_id>", methods=["GET", "POST"])
def apply(internship_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    if request.method == "GET":
        with db.get_cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    i.*,
                    e.company_name,
                    a.coverletter,
                    a.feedback,
                    a.status
                FROM internships i
                JOIN employers e ON i.company_id = e.emp_id
                LEFT JOIN students s ON s.user_id = %s
                LEFT JOIN applications a
                    ON a.student_id = s.student_id
                    AND a.internship_id = i.internship_id
                WHERE i.internship_id = %s
                """,
                (user_id, internship_id),
            )
            internship = cursor.fetchone()

            cursor.execute(
                """
                SELECT u.full_name, u.email, s.university, s.course, s.resume_path
                FROM students s
                JOIN users u ON s.user_id = u.user_id
                WHERE u.user_id = %s
                """,
                (user_id,),
            )
            student = cursor.fetchone()

        return render_template(
            "apply.html",
            internship=internship,
            student=student,
            review_mode=request.args.get("review"),
        )

    resume_file = request.files.get("resume")
    cover_letter = request.form.get("cover_letter")
    with db.get_cursor() as cursor:
        cursor.execute(
            """
            INSERT OR REPLACE INTO applications
                (internship_id, student_id, coverletter, status, feedback)
            VALUES (
                %s,
                (SELECT student_id FROM students WHERE user_id = %s),
                %s,
                'pending',
                NULL
            )
            """,
            (internship_id, user_id, cover_letter),
        )

    if resume_file and resume_file.filename.endswith(".pdf"):
        resume_filename = f"resume_user_{user_id}.pdf"
        resume_dir = os.path.join(current_app.static_folder, "resume")
        os.makedirs(resume_dir, exist_ok=True)
        resume_full_path = os.path.join(resume_dir, resume_filename)
        resume_file.save(resume_full_path)
        resume_path = os.path.join("resume", resume_filename).replace("\\", "/")
        with db.get_cursor() as cursor:
            cursor.execute(
                """
                UPDATE students SET resume_path = %s WHERE user_id = %s
                """,
                (resume_path, user_id),
            )

    flash("Application submitted successfully!", "success")
    return redirect(url_for("customer_home"))
