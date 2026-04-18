import os
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
import sqlite3

# Load from parent dir
load_dotenv('../.env')

from sys import path
path.append('..')
from app import get_db_connection

def migrate():
    conn = get_db_connection()
    is_pg = hasattr(conn, 'cursor_factory')
    
    stats_sql = '''
        CREATE TABLE IF NOT EXISTS user_stats (
            user_id INTEGER PRIMARY KEY,
            study_minutes INTEGER DEFAULT 0,
            certificates INTEGER DEFAULT 0,
            current_streak INTEGER DEFAULT 0,
            max_streak INTEGER DEFAULT 0,
            last_active_date DATE
        )
    '''
    
    activity_sql = '''
        CREATE TABLE IF NOT EXISTS user_activity (
            user_id INTEGER,
            activity_date DATE,
            practice_count INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, activity_date)
        )
    '''
    
    if is_pg:
        cursor = conn.cursor()
        cursor.execute(stats_sql)
        cursor.execute(activity_sql)
        conn.commit()
    else:
        conn.execute(stats_sql)
        conn.execute(activity_sql)
        conn.commit()

    conn.close()
    print("Migration successful")

if __name__ == '__main__':
    migrate()
