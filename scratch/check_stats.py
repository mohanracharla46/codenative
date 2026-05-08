import sqlite3
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM users')
print(f"Users: {cursor.fetchone()[0]}")
cursor.execute('SELECT COUNT(*) FROM user_progress')
print(f"Progress entries: {cursor.fetchone()[0]}")
conn.close()
