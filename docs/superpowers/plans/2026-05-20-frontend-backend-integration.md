# Frontend Backend Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Flask app use the root `templates/` and `static/` assets as the primary frontend while preserving the local SQLite-backed backend.

**Architecture:** Keep `mysite` as the runtime package for app setup, routes, and database access. Repoint Flask to the root template/static directories, then reconcile backend query fields and template/static references so the imported frontend renders correctly without 404s or missing data.

**Tech Stack:** Flask, Jinja2, SQLite, Flask test client, unittest

---

### Task 1: Add frontend integration regression tests

**Files:**
- Modify: `tests/test_local_setup.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_root_templates_and_static_are_used(self):
    ...

def test_employer_and_admin_pages_render_frontend_fields(self):
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m unittest tests/test_local_setup.py`
Expected: FAIL because the app still points to `mysite/templates` or the rendered pages are missing frontend-specific content.

- [ ] **Step 3: Write minimal implementation**

Update the Flask app configuration and route query outputs just enough for the tests to pass.

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m unittest tests/test_local_setup.py`
Expected: PASS

### Task 2: Repoint Flask to root frontend assets

**Files:**
- Modify: `mysite/__init__.py`

- [ ] **Step 1: Set Flask template and static folders to the project root**

```python
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)
```

- [ ] **Step 2: Keep database/bootstrap behavior unchanged**

Retain `db.init_db(...)`, `db.ensure_schema(app)`, and `seed_demo_data()` exactly as the runtime initialization path.

- [ ] **Step 3: Run targeted tests**

Run: `.venv/bin/python -m unittest tests/test_local_setup.py`
Expected: Template rendering uses the imported frontend.

### Task 3: Align backend query fields with frontend templates

**Files:**
- Modify: `mysite/schema.sql`
- Modify: `mysite/__init__.py`
- Modify: `mysite/customer.py`
- Modify: `mysite/staff.py`

- [ ] **Step 1: Add fields expected by the frontend**

Add `skills_required` and `number_of_opening` to the `internships` schema.

- [ ] **Step 2: Seed the new fields**

Populate demo internship rows with values for the new columns.

- [ ] **Step 3: Update SQL selection paths if needed**

Ensure `customer_home`, `apply`, and `staff_home` queries expose the fields referenced by the root templates.

- [ ] **Step 4: Run tests**

Run: `.venv/bin/python -m unittest tests/test_local_setup.py`
Expected: Employer/student pages can render without undefined-field errors.

### Task 4: Fix template-to-static wiring mismatches

**Files:**
- Modify: `templates/profile.html`
- Modify: `templates/user_manage.html`
- Modify: `templates/view_applications.html`
- Optionally modify: `templates/change_password.html`
- Create or rename: `static/js/*.js`

- [ ] **Step 1: Make script paths match actual files**

Standardize on `static/js/...` and ensure the filesystem matches.

- [ ] **Step 2: Fix default image filename mismatches**

Normalize default image references to one filename/casing.

- [ ] **Step 3: Run smoke tests**

Run: `.venv/bin/python -m unittest tests/test_local_setup.py`
Expected: HTML references valid static asset URLs.

### Task 5: End-to-end route verification

**Files:**
- Modify: `tests/test_local_setup.py`

- [ ] **Step 1: Add route-level smoke coverage for login, profile, employer, admin, and application pages**

Use Flask test client with seeded demo accounts.

- [ ] **Step 2: Run the full test file**

Run: `.venv/bin/python -m unittest tests/test_local_setup.py`
Expected: PASS
