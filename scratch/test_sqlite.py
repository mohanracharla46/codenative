
import sqlite3

def test_sqlite():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute("SELECT language, COUNT(*) as count FROM content GROUP BY language").fetchall()
        if not rows:
            print("SQLite: No content found!")
        for row in rows:
            print(f"SQLite: Language: {row['language']}, Topics: {row['count']}")
    except Exception as e:
        print(f"SQLite Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_sqlite()
