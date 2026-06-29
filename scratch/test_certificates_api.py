import sys
import os
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock out any environment variables that might cause issues
os.environ['DATABASE_URL'] = '' # Force SQLite fallback locally

from app import app, get_db_connection, execute_query, release_db_connection

class TestCertificatesAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
        # Insert a dummy user in SQLite users table
        conn = get_db_connection()
        try:
            # Delete if duplicate exists
            execute_query(conn, "DELETE FROM users WHERE email = ?", ("test_cert_user@example.com",))
            # Insert normal user
            execute_query(conn, "INSERT INTO users (name, email, password, is_admin) VALUES (?, ?, ?, 0)", 
                          ("Normal Student", "test_cert_user@example.com", "dummy_password"))
            # Insert admin user
            execute_query(conn, "DELETE FROM users WHERE email = ?", ("test_cert_admin@example.com",))
            execute_query(conn, "INSERT INTO users (name, email, password, is_admin) VALUES (?, ?, ?, 1)", 
                          ("Admin User", "test_cert_admin@example.com", "dummy_password"))
            conn.commit()
            
            # Fetch user IDs
            u_normal = execute_query(conn, "SELECT id FROM users WHERE email = ?", ("test_cert_user@example.com",)).fetchone()
            self.normal_user_id = u_normal['id']
            
            u_admin = execute_query(conn, "SELECT id FROM users WHERE email = ?", ("test_cert_admin@example.com",)).fetchone()
            self.admin_user_id = u_admin['id']
            
            # Ensure stats clean state
            execute_query(conn, "DELETE FROM user_stats WHERE user_id = ?", (self.normal_user_id,))
            
            # Create a mock topic for testing Python certificate
            execute_query(conn, "DELETE FROM content WHERE language = ? AND topic_slug = ?", ("python", "test-python-topic"))
            execute_query(conn, "INSERT INTO content (language, topic_slug, topic_title, content_html, order_index) VALUES (?, ?, ?, ?, ?)",
                          ("python", "test-python-topic", "Test Python Topic", "<p>Python core topic</p>", 1))
            
            # Ensure progress is clean
            execute_query(conn, "DELETE FROM user_progress WHERE user_id = ? AND language = ?", (self.normal_user_id, "python"))
            
            conn.commit()
        finally:
            release_db_connection(conn)

    def tearDown(self):
        conn = get_db_connection()
        try:
            execute_query(conn, "DELETE FROM user_stats WHERE user_id = ?", (self.normal_user_id,))
            execute_query(conn, "DELETE FROM users WHERE id IN (?, ?)", (self.normal_user_id, self.admin_user_id))
            execute_query(conn, "DELETE FROM content WHERE language = ? AND topic_slug = ?", ("python", "test-python-topic"))
            execute_query(conn, "DELETE FROM user_progress WHERE user_id = ? AND language = ?", (self.normal_user_id, "python"))
            conn.commit()
        finally:
            release_db_connection(conn)

    def test_anonymous_access_denied(self):
        # Accessing certificates page as guest
        response = self.app.get('/admin/certificates')
        self.assertEqual(response.status_code, 302) # Should redirect (likely to signin or index)

        # Calling increment API as guest
        response = self.app.post('/admin/increment_certificate', json={"user_id": self.normal_user_id})
        self.assertEqual(response.status_code, 302)

    def test_normal_user_access_denied(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['user_id'] = self.normal_user_id
                sess['user_name'] = "Normal Student"
                sess['user_email'] = "test_cert_user@example.com"
                sess['is_admin'] = False

            # Accessing certificates page
            response = client.get('/admin/certificates')
            self.assertEqual(response.status_code, 302)

            # Calling increment API
            response = client.post('/admin/increment_certificate', json={"user_id": self.normal_user_id})
            self.assertEqual(response.status_code, 302)

    def test_admin_access_allowed(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['user_id'] = self.admin_user_id
                sess['user_name'] = "Admin User"
                sess['user_email'] = "test_cert_admin@example.com"
                sess['is_admin'] = True

            # Accessing certificates page
            response = client.get('/admin/certificates')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Certificate Management", response.data)
            self.assertIn(b"Normal Student", response.data)

    def test_admin_increment_certificates(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['user_id'] = self.admin_user_id
                sess['user_name'] = "Admin User"
                sess['user_email'] = "test_cert_admin@example.com"
                sess['is_admin'] = True

            # Initially no stats entry
            conn = get_db_connection()
            stats = execute_query(conn, "SELECT certificates FROM user_stats WHERE user_id = ?", (self.normal_user_id,)).fetchone()
            self.assertIsNone(stats)
            release_db_connection(conn)

            # Call increment API (first time, inserts row)
            response = client.post('/admin/increment_certificate', json={"user_id": self.normal_user_id})
            self.assertEqual(response.status_code, 200)

            conn = get_db_connection()
            stats = execute_query(conn, "SELECT certificates FROM user_stats WHERE user_id = ?", (self.normal_user_id,)).fetchone()
            self.assertIsNotNone(stats)
            self.assertEqual(stats['certificates'], 1)
            release_db_connection(conn)

            # Call increment API again (updates row)
            response = client.post('/admin/increment_certificate', json={"user_id": self.normal_user_id})
            self.assertEqual(response.status_code, 200)

            conn = get_db_connection()
            stats = execute_query(conn, "SELECT certificates FROM user_stats WHERE user_id = ?", (self.normal_user_id,)).fetchone()
            self.assertEqual(stats['certificates'], 2)
            release_db_connection(conn)

    def test_student_certificate_anonymous_denied(self):
        # Accessing student certificate page as guest redirects to signin
        response = self.app.get('/certificate/python')
        self.assertEqual(response.status_code, 302)

    def test_student_certificate_not_completed_redirect(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['user_id'] = self.normal_user_id
                sess['user_name'] = "Normal Student"
                sess['user_email'] = "test_cert_user@example.com"
                sess['is_admin'] = False

            # Accessing certificate page without completing the course should redirect to dashboard
            response = client.get('/certificate/python')
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.headers['Location'].endswith('/dashboard'))

    def test_student_certificate_invalid_course_404(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess['user_id'] = self.normal_user_id
                sess['user_name'] = "Normal Student"
                sess['user_email'] = "test_cert_user@example.com"
                sess['is_admin'] = False

            # Accessing invalid course should return 404
            response = client.get('/certificate/invalid_course')
            self.assertEqual(response.status_code, 404)

    def test_student_certificate_success(self):
        # Complete all Python topics for the user in the test database
        conn = get_db_connection()
        try:
            topics = execute_query(conn, "SELECT topic_slug FROM content WHERE language = ?", ("python",)).fetchall()
            for t in topics:
                execute_query(conn, """
                    INSERT INTO user_progress (user_id, language, topic_slug)
                    VALUES (?, ?, ?)
                    ON CONFLICT(user_id, language, topic_slug) DO NOTHING
                """, (self.normal_user_id, "python", t['topic_slug']))
            conn.commit()
        finally:
            release_db_connection(conn)

        with self.app as client:
            with client.session_transaction() as sess:
                sess['user_id'] = self.normal_user_id
                sess['user_name'] = "Normal Student"
                sess['user_email'] = "test_cert_user@example.com"
                sess['is_admin'] = False

            # Accessing Python certificate after completion
            response = client.get('/certificate/python')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Normal Student", response.data)
            self.assertIn(b"Python Core Lesson Suite", response.data)

if __name__ == '__main__':
    unittest.main()
