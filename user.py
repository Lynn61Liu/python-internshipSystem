from mysite import app
from mysite import db
from flask import redirect, render_template, request, session, url_for
from flask_bcrypt import Bcrypt
import re
import os
from flask import current_app
import logging
logging.basicConfig(level=logging.DEBUG)
from flask import flash
from flask_bcrypt import check_password_hash

# Create an instance of the Bcrypt class, which we'll be using to hash user
# passwords during login and registration.
flask_bcrypt = Bcrypt(app)

# Default role assigned to new users upon registration.
DEFAULT_USER_ROLE = 'Student'

def user_home_url():
    """Generates a URL to the homepage for the currently logged-in user.

    If the user is not logged in, this returns the URL for the login page
    instead. If the user appears to be logged in, but the role stored in their
    session cookie is invalid (i.e. not a recognised role), it returns the URL
    for the logout page to clear that invalid session data."""
    if 'loggedin' in session:
        role = session.get('role', None)
        #logging.debug(f"role info》》》》》》》》》》: {role}")
        if role=='Student':

            home_endpoint='customer_home'
        elif role=='Employer':
            home_endpoint='staff_home'
        elif role=='Admin':
            home_endpoint='admin_home'
        else:
            home_endpoint = 'logout'
    else:
        home_endpoint = 'login'
    logging.debug(f"home_endpoint: {home_endpoint}")
    return url_for(home_endpoint)

@app.route('/')
def root():
    """Root endpoint (/)

    Methods:
    - get: Redirects guests to the login page, and redirects logged-in users to
        their own role-specific homepage.
    """
    return redirect(user_home_url())

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page endpoint.

    Methods:
    - get: Renders the login page.
    - post: Attempts to log the user in using the credentials supplied via the
        login form, and either:
        - Redirects the user to their role-specific homepage (if successful)
        - Renders the login page again with an error message (if unsuccessful).

    If the user is already logged in, both get and post requests will redirect
    to their role-specific homepage.
    """
    if 'loggedin' in session:
         return redirect(user_home_url())

    if request.method=='POST' and 'username' in request.form and 'password' in request.form:
        # Get the login details submitted by the user.
        username = request.form['username']
        password = request.form['password']



        # Attempt to validate the login details against the database.
        with db.get_cursor() as cursor:
            # Try to retrieve the account details for the specified username.
            #
            # Note: we use a Python multiline string (triple quote) here to
            # make the query more readable in source code. This is just a style
            # choice: the line breaks are ignored by MySQL, and it would be
            # equally valid to put the whole SQL statement on one line like we
            # do at the beginning of the `signup` function.
            cursor.execute('''
                           SELECT user_id, username, password_hash, role,status
                           FROM users
                           WHERE username = %s;
                           ''', (username,))
            account = cursor.fetchone()

            if account is not None:
                # We found a matching account: now we need to check whether the
                # password they supplied matches the hash in our database.
                password_hash = account['password_hash']

                if flask_bcrypt.check_password_hash(password_hash, password):
                    # Password is correct. Save the user's ID, username, and role
                    # as session data, which we can access from other routes to
                    # determine who's currently logged in.
                    #
                    # Users can potentially see and edit these details using their
                    # web browser. However, the session cookie is signed with our
                    # app's secret key. That means if they try to edit the cookie
                    # to impersonate another user, the signature will no longer
                    # match and Flask will know the session data is invalid.
                    session['loggedin'] = True
                    session['user_id'] = account['user_id']
                    session['username'] = account['username']
                    session['role'] = account['role']
                    session['status'] = account['status']

                   # logging.debug(f"User {username} logged in with role {account['role']}")

                    return redirect(user_home_url())
                else:
                    # Password is incorrect. Re-display the login form, keeping
                    # the username provided by the user so they don't need to
                    # re-enter it. We also set a `password_invalid` flag that
                    # the template uses to display a validation message.
                    return render_template('login.html',
                                           username=username,
                                           password_invalid=True)
            else:
                # We didn't find an account in the database with this username.
                # Re-display the login form, keeping the username so the user
                # can see what they entered (otherwise, they might just keep
                # trying the same thing). We also set a `username_invalid` flag
                # that tells the template to display an appropriate message.
                #
                # Note: In this example app, we tell the user if the user
                # account doesn't exist. Many websites (e.g. Google, Microsoft)
                # do this, but other sites display a single "Invalid username
                # or password" message to prevent an attacker from determining
                # whether a username exists or not. Here, we accept that risk
                # to provide more useful feedback to the user.
                return render_template('login.html',
                                       username=username,
                                       username_invalid=True)

    # This was a GET request, or an invalid POST (no username and/or password),
    # so we just render the login form with no pre-populated details or flags.
    return render_template('login.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    """Signup (registration) page endpoint.

    Methods:
    - get: Renders the signup page.
    - post: Attempts to create a new user account using the details supplied
        via the signup form, then renders the signup page again with a welcome
        message (if successful) or one or more error message(s) explaining why
        signup could not be completed.

    If the user is already logged in, both get and post requests will redirect
    to their role-specific homepage.
    """
    if 'loggedin' in session:
         return redirect(user_home_url())

    if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form:
        # Get the details submitted via the form on the signup page, and store
        # the values in temporary local variables for ease of access.
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']


        username_error = None
        email_error = None
        password_error = None

        # Check whether there's an account with this username in the database.
        with db.get_cursor() as cursor:
            cursor.execute('SELECT user_id FROM users WHERE username = %s;',
                           (username,))
            account_already_exists = cursor.fetchone() is not None

        # Validate the username, ensuring that it's unique (as we just checked
        # above) and meets the naming constraints of our web app.
        if account_already_exists:
            username_error = 'An account already exists with this username.'
        elif len(username) > 20:
            # The user should never see this error during normal conditions,
            # because we set a maximum length of 20 on the input field in the
            # template. However, a user or attacker could easily override that
            # and submit a longer value, so we need to handle that case.
            username_error = 'Your username cannot exceed 20 characters.'
        elif not re.match(r'[A-Za-z0-9]+', username):
            username_error = 'Your username can only contain letters and numbers.'

        # Validate the new user's email address. Note: The regular expression
        # we use here isn't a perfect check for a valid address, but is
        # sufficient for this example.
        if len(email) > 320:
            # As above, the user should never see this error under normal
            # conditions because we set a maximum input length in the template.
            email_error = 'Your email address cannot exceed 320 characters.'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            email_error = 'Invalid email address.'

        # Validate password. Think about what other constraints might be useful
        # here for security (e.g. requiring a certain mix of character types,
        # or avoiding overly-common passwords). Make sure that you clearly
        # communicate any rules to the user, either through hints on the signup
        # page or with clear error messages here.
        #
        # Note: Unlike the username and email address, we don't enforce a
        # maximum password length. Because we'll be storing a hash of the
        # password in our database, and not the password itself, it doesn't
        # matter how long a password the user chooses. Whether it's 8 or 800
        # characters, the hash will always be the same length.

        # validate_password
        password_error = validate_password(password)



        if (username_error or email_error or password_error):
            # One or more errors were encountered, so send the user back to the
            # signup page with their username and email address pre-populated.
            # For security reasons, we never send back the password they chose.
            return render_template('signup.html',
                                   username=username,
                                   email=email,
                                   username_error=username_error,
                                   email_error=email_error,
                                   password_error=password_error)
        else:
            # The new account details are valid. Hash the user's new password
            # and create their account in the database.
            password_hash = flask_bcrypt.generate_password_hash(password)

            # Note: In this example, we just assume the SQL INSERT statement
            # below will run successfully. But what if it doesn't?
            #
            # If the INSERT fails for any reason, MySQL Connector will throw an
            # exception and the user will receive a generic error page. We
            # should implement our own error handling here to deal with that
            # possibility, and display a more useful message to the user.
            with db.get_cursor() as cursor:
                cursor.execute('''
                               INSERT INTO users (username, password_hash, email, role)
                               VALUES (%s, %s, %s, %s);
                               ''',
                               (username, password_hash, email, DEFAULT_USER_ROLE,))
                # Get the user ID of the newly created account.
                user_id = cursor.lastrowid
            # Create a new student account for the user, using the user ID we
            # just created.
            with db.get_cursor() as cursor:
                cursor.execute('''
                               INSERT INTO students (user_id, university, course)
                               VALUES (%s, NULL, NULL);
                               ''', (user_id,))


            return render_template('signup.html', signup_successful=True)

    # This was a GET request, or an invalid POST (no username, email, and/or
    # password). Render the signup page with no pre-populated form fields or
    # error messages.
    return render_template('signup.html')

@app.route('/profile')
def profile():
    """User Profile page endpoint.

    Methods:
    - get: Renders the user profile page for the current user.

    If the user is not logged in, requests will redirect to the login page.
    """
    if 'loggedin' not in session:
         return redirect(url_for('login'))
    else:
         role = session.get('role', None)

    if role == 'Student':
    # Retrieve user profile from the database.
     with db.get_cursor() as cursor:
        cursor.execute('''
            SELECT

                u.user_id,
                u.username,
                u.email,
                u.role,
                u.full_name,
                s.university,
                s.course,
                s.resume_path,
                s.student_id,
                u.profile_image
            FROM users u
            LEFT JOIN students s ON u.user_id = s.user_id
            WHERE u.user_id = %s;
        ''', (session['user_id'],))
        profile = cursor.fetchone()
    elif role == 'Employer':
        with db.get_cursor() as cursor:
            cursor.execute('''
                SELECT
                    u.user_id,
                    u.username,
                    u.email,
                    u.role,
                    u.full_name,
                    e.company_name,
                    e.company_description,
                    e.website,
                    e.emp_id,
                    e.logo_path
                FROM users u
                LEFT JOIN employers e ON u.user_id = e.user_id
                WHERE u.user_id = %s;
            ''', (session['user_id'],))
            profile = cursor.fetchone()
    elif role == 'Admin':
        with db.get_cursor() as cursor:
            cursor.execute('''
                SELECT
                    u.*
                FROM users u
                WHERE u.user_id = %s;
            ''', (session['user_id'],))
            profile = cursor.fetchone()
    return render_template('profile.html', profile=profile)

@app.route('/logout')
def logout():

    """Logout endpoint.

    Methods:
    - get: Logs the current user out (if they were logged in to begin with),
        and redirects them to the login page.
    """
    # Note that nothing actually happens on the server when a user logs out: we
    # just remove the cookie from their web browser. They could technically log
    # back in by manually restoring the cookie we've just deleted. In a high-
    # security web app, you may need additional protections against this (e.g.
    # keeping a record of active sessions on the server side).
    session.pop('loggedin', None)
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)

    return redirect(url_for('login'))


@app.route('/update_profile', methods=['POST'])
def update_profile():

    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('login'))

    if 'role' not in session or session['role'] == 'Student':
        full_name = request.form.get('full_name')
        university = request.form.get('university')
        course = request.form.get('course')
        resume_file = request.files.get('resume')

        resume_path = None
        photo_path = None

        # Validate resume_file
        if resume_file and resume_file.filename.endswith('.pdf'):
            resume_filename = f"resume_user_{user_id}.pdf"
            base_dir = current_app.root_path
            resume_dir = os.path.join(base_dir, 'static', 'resume')
            os.makedirs(resume_dir, exist_ok=True)
            resume_full_path = os.path.join(resume_dir, resume_filename)
            resume_file.save(resume_full_path)
            resume_path = os.path.join('resume', resume_filename).replace('\\', '/')

        #update photo
        photo_file = request.files.get('photo')
        photo_relative_path = None
        delete_photo = request.form.get('delete_photo') == 'true'
        if delete_photo:
            photo_relative_path = 'images/default.JPG'
        elif photo_file and photo_file.filename:
            base_dir = current_app.root_path
            photo_dir = os.path.join(base_dir, 'static', 'images')
            os.makedirs(photo_dir, exist_ok=True)
            photo_filename = f"user_{user_id}.jpg"
            photo_full_path = os.path.join(photo_dir, photo_filename)
            photo_file.save(photo_full_path)
            photo_relative_path = os.path.join('images', photo_filename).replace('\\', '/')
        profile.profile_image = photo_relative_path

        if photo_relative_path:
            profile.profile_image = photo_relative_path
        else:
            pass
        with db.get_cursor() as cursor:
            #  users
            cursor.execute('''
                UPDATE users
                SET full_name = %s
                WHERE user_id = %s
            ''', (full_name, user_id))



            cursor.execute('''
                UPDATE students
                SET university = %s,
                    course = %s
                    {resume_clause}
                WHERE user_id = %s
            '''.format(
                resume_clause = ", resume_path = %s" if resume_path else ""
            ),
            (university, course, resume_path, user_id) if resume_path else (university, course, user_id))


            if photo_relative_path:
                cursor.execute('''
                    UPDATE users
                    SET profile_image = %s
                    WHERE user_id = %s
                ''', (photo_relative_path, user_id))

    if 'role' in session and session['role'] == 'Employer':
        company_name = request.form.get('company_name')
        company_description = request.form.get('company_description')
        website = request.form.get('website')
        logo_file = request.files.get('company_logo')
        #logging.debug(f"employer ==================started to update profile")


        logo_path = None
        if delete_photo := request.form.get('delete_logo') == 'true':
            logo_path = 'images/default.JPG'
        elif logo_file and logo_file.filename:
            logo_filename = f"logo_user_{user_id}.jpg"
            base_dir = current_app.root_path
            logo_dir = os.path.join(base_dir, 'static', 'images')
            os.makedirs(logo_dir, exist_ok=True)
            logo_full_path = os.path.join(logo_dir, logo_filename)
            logo_file.save(logo_full_path)
            logo_path = os.path.join('images', logo_filename).replace('\\', '/')
        logging.debug(f"employer ==================started to update profile")
        with db.get_cursor() as cursor:

            cursor.execute('''
                UPDATE employers
                SET company_name = %s,
                    company_description = %s,
                    website = %s
                    {logo_clause}
                WHERE user_id = %s
            '''.format(
                logo_clause=", logo_path = %s" if logo_path else ""
            ),
            (company_name, company_description, website, logo_path, user_id) if logo_path else (company_name, company_description, website, user_id))
            logging.debug(f">>>>>>>>sql executed successfully")
    if 'role' not in session or session['role'] == 'Admin':
        full_name = request.form.get('full_name')
        photo_path = None
        #update photo
        photo_file = request.files.get('adminPhoto')
        logging.debug(f"admin photo file: {photo_file}")
        photo_relative_path = None
        delete_photo = request.form.get('delete-image-flag') == 'true'
        if delete_photo:
            photo_relative_path = 'images/default.JPG'
        elif photo_file and photo_file.filename:
            base_dir = current_app.root_path
            photo_dir = os.path.join(base_dir, 'static', 'images')
            os.makedirs(photo_dir, exist_ok=True)
            photo_filename = f"user_{user_id}.jpg"
            photo_full_path = os.path.join(photo_dir, photo_filename)
            photo_file.save(photo_full_path)
            photo_relative_path = os.path.join('images', photo_filename).replace('\\', '/')
        profile.profile_image = photo_relative_path

        if photo_relative_path:
            profile.profile_image = photo_relative_path
        else:
            pass
        with db.get_cursor() as cursor:
            cursor.execute('''
                UPDATE users
                SET full_name = %s
                WHERE user_id = %s
            ''', (full_name, user_id))

            if photo_relative_path:
                cursor.execute('''
                    UPDATE users
                    SET profile_image = %s
                    WHERE user_id = %s
                ''', (photo_relative_path, user_id))



    return redirect(url_for('profile'))


def validate_password(new_password, current_password=None):
    # Check if the new password meets the minimum requirements.
    errors = []
    if len(new_password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not re.search(r"[A-Za-z]", new_password) or not re.search(r"\d", new_password):
        errors.append("Password must contain both letters and numbers.")
    # Check if the new password is the same as the current password
    #find the current password in the database
    data_pw_hash = None
    if current_password:
        with db.get_cursor() as cursor:
            cursor.execute('SELECT password_hash FROM users WHERE user_id = %s', (session['user_id'],))
            result = cursor.fetchone()
            data_pw_hash = result['password_hash']
            if data_pw_hash and not flask_bcrypt.check_password_hash(data_pw_hash, current_password):
                errors.append("Current password is incorrect.")
            if data_pw_hash and flask_bcrypt.check_password_hash(data_pw_hash, new_password):
                errors.append("New password cannot be the same as the current password.")

    return errors



@app.route("/dbtest")
def dbtest():
    try:
        conn = MySQLdb.connect(
            host="xinghuang1124844.mysql.pythonanywhere-services.com",
            user=" ",
            passwd="internship",
            db="xinghuang1124844$internship"
        )
        return "✅ Database connection successful!"
    except Exception as e:
        return f"❌ Database connection failed: {e}"

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template('change_password.html')

    current_password = request.form['current_password']
    new_password = request.form['new_password']
    logging.debug(f"Current password: {current_password}, New password: {new_password}")

    errors = validate_password(new_password, current_password)
    logging.debug(f"===========Validation errors=====================: {errors}")

    if errors:
        combined_message = ' '.join(errors)
        logging.error(f"Password change failed: {combined_message}")
        flash(combined_message, 'danger')  # 'danger' is Bootstrap class for red alert
        return redirect(url_for('change_password'))
        #return redirect(url_for('change_password'), message=combined_message)

    else:
        # changet to hash the new password and update it in the database

        new_password_hash = flask_bcrypt.generate_password_hash(new_password)
        logging.debug(f"checeked and next to New password hash>>>>>>: {new_password_hash}")
        with db.get_cursor() as cursor:
                cursor.execute('''
                               UPDATE users SET password_hash = %s WHERE user_id = %s
                               ''',
                               (new_password_hash, session['user_id'],))
        combined_message = "Password changed successfully."
        flash(combined_message, 'success')
        return redirect(url_for('change_password'))