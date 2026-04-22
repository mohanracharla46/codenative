import sqlite3
import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

DATABASE = 'users.db'

def get_db_connection():
    """Create a database connection (PostgreSQL if DATABASE_URL exists, else SQLite)"""
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        try:
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)
            conn = psycopg2.connect(db_url, cursor_factory=psycopg2.extras.RealDictCursor)
            return conn
        except Exception as e:
            print(f"Failed to connect to Supabase: {e}")
            raise
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    is_pg = hasattr(conn, 'cursor_factory')
    
    print(f"Initializing {'PostgreSQL (Supabase)' if is_pg else 'SQLite (' + DATABASE + ')'}...")

    # SQL for Users Table
    users_sql = '''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            mobile TEXT,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''' if is_pg else '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            mobile TEXT,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    '''
    
    # SQL for Content Table
    content_sql = '''
        CREATE TABLE IF NOT EXISTS content (
            id SERIAL PRIMARY KEY,
            language TEXT NOT NULL,
            topic_slug TEXT NOT NULL,
            topic_title TEXT NOT NULL,
            content_html TEXT NOT NULL,
            order_index INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(language, topic_slug)
        )
    ''' if is_pg else '''
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            language TEXT NOT NULL,
            topic_slug TEXT NOT NULL,
            topic_title TEXT NOT NULL,
            content_html TEXT NOT NULL,
            order_index INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(language, topic_slug)
        )
    '''

    if is_pg:
        cursor = conn.cursor()
        cursor.execute(users_sql)
        cursor.execute(content_sql)
        
        # Check if is_admin column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='is_admin'
        """)
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
        
        # Check if mobile column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='mobile'
        """)
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE users ADD COLUMN mobile TEXT")
        
        conn.commit()
    else:
        # SQLite
        conn.execute(users_sql)
        conn.execute(content_sql)
        
        cursor = conn.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'is_admin' not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
        
        if 'mobile' not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN mobile TEXT")
        
        conn.commit()
    
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
