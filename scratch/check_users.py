import sqlite3

def check_users():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE is_admin = 1")
        rows = cursor.fetchall()
        print("Admin users found:")
        for row in rows:
            print(dict(row))
        
        cursor.execute("SELECT * FROM users WHERE email IN ('racharlamohan16@gmail.com', 'mohanracharla16@gmail.com')")
        print("\nSpecial users found:")
        for row in cursor.fetchall():
            print(dict(row))
    except Exception as e:

        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_users()
