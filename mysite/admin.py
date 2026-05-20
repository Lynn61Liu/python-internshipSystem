from __future__ import annotations

from flask import jsonify, redirect, render_template, request, session, url_for

from mysite import app, db


@app.route("/admin/home")
def admin_home():
    if "loggedin" not in session:
        return redirect(url_for("login"))
    if session["role"] != "Admin":
        return render_template("access_denied.html"), 403

    with db.get_cursor() as cursor:
        cursor.execute(
            """
            SELECT
                i.*,
                e.company_name
            FROM internships i
            JOIN employers e ON i.company_id = e.emp_id
            ORDER BY i.company_id ASC
            """
        )
        internships = cursor.fetchall()
    return render_template("admin_home.html", internships=internships)


@app.route("/user/manage", methods=["GET", "POST"])
def user_manage():
    if "loggedin" not in session:
        return redirect(url_for("login"))
    if session["role"] != "Admin":
        return render_template("access_denied.html"), 403

    if request.method == "POST":
        data = request.get_json()
        user_id = data.get("user_id")
        new_status = data.get("status")
        if not user_id or new_status not in ["active", "inactive", "suspended"]:
            return jsonify({"error": "Invalid data submitted."}), 400

        with db.get_cursor() as cursor:
            cursor.execute(
                """
                UPDATE users SET status = %s WHERE user_id = %s
                """,
                (new_status.lower(), user_id),
            )
        return jsonify({"message": "User status updated successfully."})

    with db.get_cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM users ORDER BY user_id ASC
            """
        )
        user_list = cursor.fetchall()
    return render_template("user_manage.html", userList=user_list)
