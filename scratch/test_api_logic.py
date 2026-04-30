
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_api():
    # We can't easily test the local server if it's not running, 
    # but we can test the database directly to see if the queries we use in app.py work.
    import psycopg2
    from psycopg2 import pool
    import psycopg2.extras

    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("DATABASE_URL not found")
        return

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    try:
        # Test the exact logic from app.py
        db_pool = pool.ThreadedConnectionPool(1, 5, db_url)
        conn = db_pool.getconn()
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        cursor = conn.cursor()
        
        # Test topics list
        lang = 'c'
        cursor.execute('SELECT topic_slug, topic_title, 0 as completed FROM content WHERE language = %s ORDER BY order_index', (lang,))
        topics = cursor.fetchall()
        print(f"API Test (Topics): Found {len(topics)} topics for {lang}")
        
        # Test specific topic
        slug = 'introduction'
        cursor.execute('SELECT content_html FROM content WHERE language = %s AND topic_slug = %s', (lang, slug))
        topic = cursor.fetchone()
        if topic:
            print(f"API Test (Content): Found content for {slug} ({len(topic['content_html'])} bytes)")
        else:
            print(f"API Test (Content): NOT FOUND for {slug}")
            
        db_pool.putconn(conn)
    except Exception as e:
        print(f"API Test Error: {e}")

if __name__ == "__main__":
    test_api()
