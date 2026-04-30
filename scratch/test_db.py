
import os
import sqlite3
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        try:
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)
            conn = psycopg2.connect(db_url, cursor_factory=psycopg2.extras.RealDictCursor)
            return conn, "PostgreSQL"
        except Exception as e:
            print(f"PostgreSQL connection failed: {e}")
    
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn, "SQLite"

def test_content():
    conn, db_type = get_db_connection()
    print(f"Using {db_type}")
    
    try:
        cursor = conn.cursor() if db_type == "PostgreSQL" else conn
        if db_type == "PostgreSQL":
            cursor.execute("SELECT language, COUNT(*) as count FROM content GROUP BY language")
            rows = cursor.fetchall()
        else:
            rows = conn.execute("SELECT language, COUNT(*) as count FROM content GROUP BY language").fetchall()
        
        if not rows:
            print("No content found in database!")
        for row in rows:
            print(f"Language: {row['language']}, Topics: {row['count']}")
            
    except Exception as e:
        print(f"Error querying content: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_content()
