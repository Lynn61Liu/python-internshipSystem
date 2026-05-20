from mysite import app
from mysite import db
from flask import redirect, render_template, session, url_for, request, jsonify
import logging

@app.route('/staff/home')
def staff_home():
     if 'loggedin' not in session:
          return redirect(url_for('login'))

     userID = session.get('user_id', None)
    #logging.debug(f"User ID in session==========: {userID}")
     with db.get_cursor() as cursor:
          cursor.execute('''
                SELECT
                i.*,  e.company_name
               FROM internships i
               JOIN employers e ON i.company_id = e.emp_id
               WHERE e.user_id = %s;
            ''', (session['user_id'],))
          intershipList = cursor.fetchall()
          #logging.debug(f"Intership List fetched: {intershipList}")

     return render_template('staff_home.html',intershipList=intershipList)

# @app.route('/applications/<int:internship_id>')
# def view_applications(internship_id):
#      with db.get_cursor() as cursor:
#           cursor.execute('''
#                SELECT
#                a.*,
#                s.*,
#                u.full_name,u.email,u.profile_image,u.username
#                FROM applications a
#                JOIN students s ON a.student_id = s.student_id
#                JOIN users u ON s.user_id = u.user_id
#                WHERE a.internship_id = %s;
#           ''', (internship_id,))
#           applications = cursor.fetchall()
#           logging.debug(f"Applications fetched=======: {applications}")
#      return render_template('view_applications.html', internship_id=internship_id, applications=applications)

@app.route('/applications/<int:internship_id>')
def view_applications(internship_id):
    with db.get_cursor() as cursor:
        cursor.execute('''
               SELECT
               a.*,
               s.*,
               u.full_name, u.email, u.profile_image, u.username,
               i.title AS internship_title,
               i.description AS internship_description
               FROM applications a
               JOIN students s ON a.student_id = s.student_id
               JOIN users u ON s.user_id = u.user_id
               JOIN internships i ON a.internship_id = i.internship_id
               WHERE a.internship_id =  %s;
        ''', (internship_id,))
        applications = cursor.fetchall()
      #  logging.debug(f"Applications fetched=======: {applications}")

    return render_template('view_applications.html', internship_id=internship_id, applications=applications)

@app.route('/update_application_status', methods=['POST'])
def update_application_status():
    data = request.get_json()
    #logging.debug(f"Data received for status update>>>>>>>>>>>>>>>>>>: {data}")
    student_id = data['student_id']
    internship_id = data['internship_id']
    status = data['status']
    feedback = data['feedback']

    with db.get_cursor() as cursor:
        cursor.execute('''
            UPDATE applications
            SET status = %s, feedback = %s
            WHERE student_id = %s AND internship_id = %s
        ''', (status, feedback, student_id, internship_id))

    return jsonify({'success': True})