import sys
import os
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Force SQLite fallback locally
os.environ['DATABASE_URL'] = ''

from fastapi.testclient import TestClient
import app as app_module
from app import app, get_db_connection, execute_query, release_db_connection

class TestExportUsers(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Store original admin check
        self.original_admin_check = app_module._admin_check
        
        # Add test users to the database
        conn = get_db_connection()
        try:
            execute_query(conn, "DELETE FROM users WHERE email = ?", ("test_export_user_unique_99@example.com",))
            execute_query(conn, "INSERT INTO users (name, email, password, mobile, is_admin) VALUES (?, ?, ?, ?, ?)",
                          ("Export Test User", "test_export_user_unique_99@example.com", "dummy_pass", "9999999999", 0))
            conn.commit()
            
            user = execute_query(conn, "SELECT id FROM users WHERE email = ?", ("test_export_user_unique_99@example.com",)).fetchone()
            self.test_user_id = user['id']
        finally:
            release_db_connection(conn)

    def tearDown(self):
        # Restore original admin check
        app_module._admin_check = self.original_admin_check
        
        # Clean up database
        conn = get_db_connection()
        try:
            execute_query(conn, "DELETE FROM users WHERE id = ?", (self.test_user_id,))
            conn.commit()
        finally:
            release_db_connection(conn)

    def test_export_users_unauthorized(self):
        # Mock admin check to return False
        app_module._admin_check = lambda r: False
        
        response = self.client.get("/admin/export_users", follow_redirects=False)
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers.get("location"), "/")

    def test_export_users_authorized(self):
        # Mock admin check to return True
        app_module._admin_check = lambda r: True
        
        response = self.client.get("/admin/export_users")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("content-type"), "text/csv; charset=utf-8")
        self.assertIn("attachment; filename=users_export.csv", response.headers.get("content-disposition"))
        
        # Decode and parse CSV content
        content = response.content.decode("utf-8")
        
        # Check Byte Order Mark (BOM)
        self.assertTrue(content.startswith('\ufeff'))
        
        # Check headers
        self.assertIn("User ID,Name,Email,Mobile,Role,Referral Code,Referred By ID,Verified Referrals,Joined At", content)
        # Check that our test user is present in the output
        self.assertIn("Export Test User", content)
        self.assertIn("test_export_user_unique_99@example.com", content)
        self.assertIn("9999999999", content)

if __name__ == "__main__":
    unittest.main()
