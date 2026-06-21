import sys
import os
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock out any environment variables that might cause issues
os.environ['DATABASE_URL'] = '' # Force SQLite fallback locally

from app import app, get_db_connection, execute_query, release_db_connection

class TestFeedbackAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
        # Insert a dummy user in SQLite users table
        conn = get_db_connection()
        try:
            execute_query(conn, "DELETE FROM users WHERE email = ?", ("test_feedback_user@example.com",))
            # password cannot be null in init_db.py schema, so supply a hashed or dummy value
            execute_query(conn, "INSERT INTO users (name, email, password) VALUES (?, ?, ?)", 
                          ("Real Mohan", "test_feedback_user@example.com", "dummy_password"))
            conn.commit()
            
            # Fetch user ID
            user = execute_query(conn, "SELECT id FROM users WHERE email = ?", ("test_feedback_user@example.com",)).fetchone()
            self.user_id = user['id']
            
            # Delete any existing feedback for this user
            execute_query(conn, "DELETE FROM feedback WHERE user_id = ?", (self.user_id,))
            conn.commit()
        finally:
            release_db_connection(conn)

    def tearDown(self):
        conn = get_db_connection()
        try:
            execute_query(conn, "DELETE FROM feedback WHERE user_id = ?", (self.user_id,))
            execute_query(conn, "DELETE FROM users WHERE id = ?", (self.user_id,))
            conn.commit()
        finally:
            release_db_connection(conn)

    def test_submit_feedback_logged_in(self):
        # Set up a session using the test client
        with self.app as client:
            with client.session_transaction() as sess:
                sess['user_id'] = self.user_id
                sess['user_name'] = "Real Mohan"
                sess['user_email'] = "test_feedback_user@example.com"
            
            # Post to feedback API with 'Tutorial User' / empty email
            response = client.post('/api/submit_feedback', json={
                'name': 'Tutorial User',
                'email': '',
                'college': 'My College',
                'rating': 5,
                'message': 'This is a test message'
            })
            
            self.assertEqual(response.status_code, 200)
            
            # Verify in the DB that the feedback name and email were overwritten with actual user details
            conn = get_db_connection()
            try:
                feedback = execute_query(conn, "SELECT * FROM feedback WHERE user_id = ?", (self.user_id,)).fetchone()
                self.assertIsNotNone(feedback)
                self.assertEqual(feedback['name'], "Real Mohan")
                self.assertEqual(feedback['email'], "test_feedback_user@example.com")
                self.assertEqual(feedback['college'], "My College")
                self.assertEqual(feedback['rating'], 5)
                self.assertEqual(feedback['message'], "This is a test message")
                print("\n=== SUCCESS: Feedback name and email successfully overridden! ===")
            finally:
                release_db_connection(conn)

if __name__ == '__main__':
    unittest.main()
