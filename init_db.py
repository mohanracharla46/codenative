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
            google_id TEXT UNIQUE,
            otp_code TEXT,
            otp_expiry TIMESTAMP,
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
            google_id TEXT UNIQUE,
            otp_code TEXT,
            otp_expiry TIMESTAMP,
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
            quiz_json TEXT,
            custom_css TEXT,
            custom_js TEXT,
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
            quiz_json TEXT,
            custom_css TEXT,
            custom_js TEXT,
            order_index INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(language, topic_slug)
        )
    '''

    # SQL for Feedback Table
    feedback_sql = '''
        CREATE TABLE IF NOT EXISTS feedback (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            name TEXT,
            email TEXT,
            college TEXT,
            rating INTEGER,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''' if is_pg else '''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            name TEXT,
            email TEXT,
            college TEXT,
            rating INTEGER,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    '''

    # SQL for User Progress
    progress_sql = '''
        CREATE TABLE IF NOT EXISTS user_progress (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            language TEXT NOT NULL,
            topic_slug TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, language, topic_slug)
        )
    ''' if is_pg else '''
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            language TEXT NOT NULL,
            topic_slug TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, language, topic_slug)
        )
    '''

    # SQL for User Activity (Heatmap)
    activity_sql = '''
        CREATE TABLE IF NOT EXISTS user_activity (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            activity_date DATE DEFAULT CURRENT_DATE,
            practice_count INTEGER DEFAULT 0,
            UNIQUE(user_id, activity_date)
        )
    ''' if is_pg else '''
        CREATE TABLE IF NOT EXISTS user_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            activity_date DATE DEFAULT CURRENT_DATE,
            practice_count INTEGER DEFAULT 0,
            UNIQUE(user_id, activity_date)
        )
    '''

    # SQL for User Stats
    stats_sql = '''
        CREATE TABLE IF NOT EXISTS user_stats (
            user_id INTEGER PRIMARY KEY REFERENCES users(id),
            study_minutes INTEGER DEFAULT 0,
            certificates INTEGER DEFAULT 0,
            current_streak INTEGER DEFAULT 0,
            max_streak INTEGER DEFAULT 0,
            last_activity DATE
        )
    ''' if is_pg else '''
        CREATE TABLE IF NOT EXISTS user_stats (
            user_id INTEGER PRIMARY KEY REFERENCES users(id),
            study_minutes INTEGER DEFAULT 0,
            certificates INTEGER DEFAULT 0,
            current_streak INTEGER DEFAULT 0,
            max_streak INTEGER DEFAULT 0,
            last_activity DATE
        )
    '''

    if is_pg:
        cursor = conn.cursor()
        cursor.execute(users_sql)
        cursor.execute(content_sql)
        cursor.execute(feedback_sql)
        cursor.execute(progress_sql)
        cursor.execute(activity_sql)
        cursor.execute(stats_sql)
        
        # Check and add missing columns to users table
        cols_to_check = {
            'is_admin': 'INTEGER DEFAULT 0',
            'mobile': 'TEXT',
            'google_id': 'TEXT UNIQUE',
            'otp_code': 'TEXT',
            'otp_expiry': 'TIMESTAMP'
        }
        
        for col, col_type in cols_to_check.items():
            cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='{col}'")
            if not cursor.fetchone():
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {col_type}")
        
        conn.commit()
    else:
        # SQLite
        conn.execute(users_sql)
        conn.execute(content_sql)
        conn.execute(feedback_sql)
        conn.execute(progress_sql)
        conn.execute(activity_sql)
        conn.execute(stats_sql)
        
        cursor = conn.execute("PRAGMA table_info(users)")
        existing_cols = [col[1] for col in cursor.fetchall()]
        
        cols_to_check = {
            'is_admin': 'INTEGER DEFAULT 0',
            'mobile': 'TEXT',
            'google_id': 'TEXT UNIQUE',
            'otp_code': 'TEXT',
            'otp_expiry': 'TIMESTAMP'
        }
        
        for col, col_type in cols_to_check.items():
            if col not in existing_cols:
                conn.execute(f"ALTER TABLE users ADD COLUMN {col} {col_type}")
        
        conn.commit()
    
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
