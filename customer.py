from mysite import app
from mysite import db
from flask import redirect, render_template, session, url_for,flash,request
import logging
logging.basicConfig(level=logging.DEBUG)
import os
from flask import current_app


@app.route('/customer/home')
def customer_home():
     """Customer Homepage endpoint.

     Methods:
     - get: Renders the homepage for the current customer, or an "Access
          Denied" 403: Forbidden page if the current user has a different role.

     If the user is not logged in, requests will redirect to the login page.
     """

     if 'loggedin' not in session:
          # The user isn't logged in, so redirect them to the login page.
          return redirect(url_for('login'))
     elif session['role']!='Student':
          # The user isn't logged in with a customer account, so return an
          # "Access Denied" page instead. We don't do a redirect here, because
          # we're not sending them somewhere else: just delivering an
          # alternative page.
          #
          # Note: the '403' below returns HTTP status code 403: Forbidden to the
          # browser, indicating that the user was not allowed to access the
          # requested page.
          return render_template('access_denied.html'), 403

     # The user is logged in with a customer account, so render the customer
     # homepage as requested.

     with db.get_cursor() as cursor:
        cursor.execute('''
           SELECT
               i.*,
               e.*,
               a.status
               FROM internships i
               JOIN employers e ON i.company_id = e.emp_id
               LEFT JOIN applications a
               ON a.internship_id = i.internship_id AND a.student_id = (
                    SELECT student_id FROM students WHERE user_id = %s
               )
               ORDER BY i.company_id ASC
        ''', (session['user_id'],))
        internships = cursor.fetchall()
     return render_template('customer_home.html',internships=internships)


@app.route('/apply/<int:internship_id>', methods=['GET', 'POST'])
def apply(internship_id):
    user_id = session.get('user_id')
    #get application info
    if request.method == 'GET':
     with db.get_cursor() as cursor:
          # Internship info
          cursor.execute('''
               SELECT
          i.*,
          e.company_name,
          a.coverletter,a.feedback
          FROM internships i
          JOIN employers e ON i.company_id = e.emp_id
          LEFT JOIN students s ON s.user_id = %s
          LEFT JOIN applications a ON a.student_id = s.student_id AND a.internship_id = i.internship_id
          WHERE i.internship_id = %s
          ''', (user_id, internship_id))
          internship = cursor.fetchone()

          # Student info
          cursor.execute('''
               SELECT u.full_name, u.email, s.university, s.course, s.resume_path
               FROM students s
               JOIN users u ON s.user_id = u.user_id
               WHERE u.user_id = %s
          ''', (user_id,))
          student = cursor.fetchone()
     return render_template('apply.html', internship=internship, student=student,review_mode = request.args.get('review') )


     #handle apply form submission
    if request.method == 'POST':
        resume_file = request.files['resume']
        cover_letter = request.form.get('cover_letter')
        with db.get_cursor() as cursor:
            cursor.execute('''
                 INSERT INTO applications (internship_id, student_id, coverletter,status,feedback)
                VALUES (%s,
               (SELECT student_id FROM students WHERE user_id = %s), %s, 'pending', 'NULL'
               );
            ''', (internship_id, user_id, cover_letter))
        flash('Application submitted successfully!', 'success')



          # update the resume path of sudent table
        if resume_file and resume_file.filename.endswith('.pdf'):
            resume_filename = f"resume_user_{user_id}.pdf"
            base_dir = current_app.root_path
            resume_dir = os.path.join(base_dir, 'static', 'resume')
            os.makedirs(resume_dir, exist_ok=True)
            resume_full_path = os.path.join(resume_dir, resume_filename)
            resume_file.save(resume_full_path)
            resume_path = os.path.join('resume', resume_filename).replace('\\', '/')
            with db.get_cursor() as cursor:
               cursor.execute('''
                UPDATE students SET resume_path = %s WHERE user_id = %s
                ''', (resume_path, user_id))




    return redirect(url_for('customer_home'))

