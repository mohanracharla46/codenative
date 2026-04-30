
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

def test_topic():
    conn, db_type = get_db_connection()
    try:
        cursor = conn.cursor() if db_type == "PostgreSQL" else conn
        if db_type == "PostgreSQL":
            cursor.execute("SELECT topic_slug, topic_title, content_html FROM content WHERE language = 'c' LIMIT 1")
            row = cursor.fetchone()
        else:
            row = conn.execute("SELECT topic_slug, topic_title, content_html FROM content WHERE language = 'c' LIMIT 1").fetchone()
        
        if row:
            print(f"Topic: {row['topic_slug']}")
            print(f"Content length: {len(row['content_html'])}")
            print(f"Content snippet: {row['content_html'][:100]}")
        else:
            print("No topic found for 'c'")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    test_topic()
