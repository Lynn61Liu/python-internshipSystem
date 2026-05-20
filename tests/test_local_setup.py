import importlib
import os
import sys
import tempfile
import unittest


class LocalSetupTestCase(unittest.TestCase):
    def load_app(self):
        tmpdir = tempfile.mkdtemp()
        db_path = os.path.join(tmpdir, "internship.sqlite3")
        os.environ["APP_DB_BACKEND"] = "sqlite"
        os.environ["APP_DB_NAME"] = db_path

        stale_modules = [name for name in sys.modules if name == "mysite" or name.startswith("mysite.")]
        for module_name in stale_modules:
            sys.modules.pop(module_name, None)
        mysite = importlib.import_module("mysite")
        return mysite.app, db_path

    def test_mysite_import_and_local_db_bootstrap(self):
        app, db_path = self.load_app()

        self.assertEqual(app.config["DB_BACKEND"], "sqlite")
        self.assertTrue(os.path.exists(db_path))

    def test_root_templates_and_static_are_used(self):
        app, _ = self.load_app()
        self.assertTrue(app.template_folder.endswith("/templates"))
        self.assertTrue(app.static_folder.endswith("/static"))
        self.assertFalse(app.template_folder.endswith("/mysite/templates"))
        self.assertFalse(app.static_folder.endswith("/mysite/static"))

    def test_frontend_pages_and_assets_render(self):
        app, _ = self.load_app()
        client = app.test_client()

        login_response = client.get("/login")
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("Log in", login_response.get_data(as_text=True))

        static_response = client.get("/static/js/profile.js")
        self.assertEqual(static_response.status_code, 200)
        self.assertIn("editBtn", static_response.get_data(as_text=True))
        static_response.close()

        with client:
            client.post(
                "/login",
                data={"username": "student1", "password": "Password123"},
            )
            profile_response = client.get("/profile")
            self.assertEqual(profile_response.status_code, 200)
            self.assertIn("/static/js/profile.js", profile_response.get_data(as_text=True))
            apply_response = client.get("/apply/1")
            self.assertEqual(apply_response.status_code, 200)
            self.assertIn("Apply for", apply_response.get_data(as_text=True))

    def test_employer_and_admin_pages_render_frontend_fields(self):
        app, _ = self.load_app()
        client = app.test_client()

        with client:
            client.post(
                "/login",
                data={"username": "employer1", "password": "Password123"},
            )
            staff_response = client.get("/staff/home")
            self.assertEqual(staff_response.status_code, 200)
            self.assertIn("Skills Required", staff_response.get_data(as_text=True))

        with client:
            client.get("/logout")
            client.post(
                "/login",
                data={"username": "admin1", "password": "Password123"},
            )
            admin_response = client.get("/admin/home")
            self.assertEqual(admin_response.status_code, 200)
            self.assertIn("Available Internships", admin_response.get_data(as_text=True))
            user_manage_response = client.get("/user/manage")
            self.assertEqual(user_manage_response.status_code, 200)
            self.assertIn("User Listing", user_manage_response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
