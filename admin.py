from mysite import app
from mysite import db
from flask import redirect, render_template, session, url_for, flash

@app.route('/admin/home')
def admin_home():
     """Admin Homepage endpoint.

     Methods:
     - get: Renders the homepage for the current admin user, or an "Access
          Denied" 403: Forbidden page if the current user has a different role.

     If the user is not logged in, requests will redirect to the login page.
     """
     if 'loggedin' not in session:
          return redirect(url_for('login'))
     elif session['role']!='Admin':
          return render_template('access_denied.html'), 403
     with db.get_cursor() as cursor:
        cursor.execute('''
          SELECT
               i.*,
               e.company_name
          FROM internships i
          JOIN employers e ON i.company_id = e.emp_id
          ORDER BY i.company_id ASC
        ''')
        internships = cursor.fetchall()
     return render_template('admin_home.html',internships=internships)

   # add route for user management
from flask import request, session, redirect, url_for, render_template, jsonify

@app.route('/user/manage', methods=['GET', 'POST'])
def user_manage():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    elif session['role'] != 'Admin':
        return render_template('access_denied.html'), 403

    if request.method == 'POST':
        #update user status
        data = request.get_json()
        user_id = data.get('user_id')
        new_status = data.get('status')

        if not user_id or new_status not in ['active', 'inactive', 'suspended']:
          return jsonify({'error': 'Invalid data submitted.'}), 400


        with db.get_cursor() as cursor:
            cursor.execute('''
                UPDATE users SET status = %s WHERE user_id = %s
            ''', (new_status.lower(), user_id))

        return jsonify({'message': 'User status updated successfully.'})

    else:
        # GET request to fetch user list
        with db.get_cursor() as cursor:
            cursor.execute('''
                SELECT * FROM users ORDER BY user_id ASC
            ''')
            userList = cursor.fetchall()

        return render_template('user_manage.html', userList=userList)


