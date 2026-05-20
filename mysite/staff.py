from __future__ import annotations

from flask import jsonify, redirect, render_template, request, session, url_for

from mysite import app, db


@app.route("/staff/home")
def staff_home():
    if "loggedin" not in session:
        return redirect(url_for("login"))
    if session["role"] != "Employer":
        return render_template("access_denied.html"), 403

    with db.get_cursor() as cursor:
        cursor.execute(
            """
            SELECT
                i.*,
                e.company_name
            FROM internships i
            JOIN employers e ON i.company_id = e.emp_id
            WHERE e.user_id = %s;
            """,
            (session["user_id"],),
        )
        internship_list = cursor.fetchall()
    return render_template("staff_home.html", intershipList=internship_list)


@app.route("/applications/<int:internship_id>")
def view_applications(internship_id):
    if "loggedin" not in session:
        return redirect(url_for("login"))

    with db.get_cursor() as cursor:
        cursor.execute(
            """
            SELECT
                a.*,
                s.*,
                u.full_name,
                u.email,
                u.profile_image,
                u.username,
                i.title AS internship_title,
                i.description AS internship_description
            FROM applications a
            JOIN students s ON a.student_id = s.student_id
            JOIN users u ON s.user_id = u.user_id
            JOIN internships i ON a.internship_id = i.internship_id
            WHERE a.internship_id = %s;
            """,
            (internship_id,),
        )
        applications = cursor.fetchall()
    return render_template(
        "view_applications.html",
        internship_id=internship_id,
        applications=applications,
    )


@app.route("/update_application_status", methods=["POST"])
def update_application_status():
    data = request.get_json()
    student_id = data["student_id"]
    internship_id = data["internship_id"]
    status = data["status"]
    feedback = data["feedback"]

    with db.get_cursor() as cursor:
        cursor.execute(
            """
            UPDATE applications
            SET status = %s, feedback = %s
            WHERE student_id = %s AND internship_id = %s
            """,
            (status, feedback, student_id, internship_id),
        )
    return jsonify({"success": True})
