CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    full_name TEXT,
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL CHECK (role IN ('Student', 'Employer', 'Admin')),
    password_hash BLOB NOT NULL,
    profile_image TEXT DEFAULT 'images/default.jpg',
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'inactive', 'suspended'))
);

CREATE TABLE IF NOT EXISTS students (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    university TEXT,
    course TEXT,
    resume_path TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS employers (
    emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    company_name TEXT NOT NULL,
    company_description TEXT,
    website TEXT,
    logo_path TEXT DEFAULT 'images/default.jpg',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS internships (
    internship_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    location TEXT,
    duration TEXT,
    salary REAL,
    deadline TEXT,
    stipend TEXT,
    skills_required TEXT,
    number_of_opening INTEGER DEFAULT 1,
    additional_info TEXT,
    FOREIGN KEY (company_id) REFERENCES employers(emp_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS applications (
    student_id INTEGER NOT NULL,
    internship_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'reviewing', 'accepted', 'rejected')),
    feedback TEXT,
    coverletter TEXT,
    PRIMARY KEY (student_id, internship_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (internship_id) REFERENCES internships(internship_id) ON DELETE CASCADE
);
