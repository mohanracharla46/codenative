from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
import requests
import time
import sqlite3
import hashlib
import os
import subprocess
import tempfile
from datetime import datetime
from functools import wraps
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv() # Load variables from .env

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.urandom(24)  # Secret key for session management

# Database configuration
DATABASE = 'users.db'

# NOTE: replace with your RapidAPI key
RAPIDAPI_KEY = "YOUR_RAPIDAPI_KEY_HERE"

# Use this endpoint to request final result immediately
JUDGE0_URL = "https://judge0-ce.p.rapidapi.com/submissions?base64_encoded=false&wait=true"
HEADERS = {
    "X-RapidAPI-Key":"10727c2773msh9eabacde663f00fp132fecjsn0ca2559a7d1e",
    "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com",
    "Content-Type": "application/json"
}

# Authentication Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('signin_page', next=request.path, error='login_required'))
        return f(*args, **kwargs)
    return decorated_function


def get_db_connection():
    """Create a database connection (PostgreSQL if DATABASE_URL exists, else SQLite)"""
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        try:
            # Handle potential 'postgres://' vs 'postgresql://' issue common in some platforms
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)
            
            conn = psycopg2.connect(db_url, cursor_factory=psycopg2.extras.RealDictCursor)
            return conn
        except Exception as e:
            print(f"PostgreSQL connection failed: {e}. Falling back to SQLite.")
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(conn, query, params=None):
    """Abstraction layer to handle different SQL placeholders (?, %s)"""
    is_pg = hasattr(conn, 'cursor_factory') # Basic check for psycopg2 connection
    if is_pg:
        query = query.replace('?', '%s')
        # PostgreSQL doesn't support INSERT OR REPLACE, use INSERT ... ON CONFLICT
        if 'INSERT OR REPLACE' in query:
            # We specifically handle the content table case
            query = query.replace('INSERT OR REPLACE INTO content', 'INSERT INTO content')
            query += ' ON CONFLICT (language, topic_slug) DO UPDATE SET topic_title = EXCLUDED.topic_title, content_html = EXCLUDED.content_html, order_index = EXCLUDED.order_index'
    
    cursor = conn.cursor()
    cursor.execute(query, params or ())
    return cursor

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    """Initialize the database with users and content tables"""
    conn = get_db_connection()
    # Create users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Check if is_admin column exists (migration)
    cursor = conn.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'is_admin' not in columns:
        conn.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
        conn.commit()

    # Create content table
    conn.execute('''
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
    ''')
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

# Admin Decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            flash("Admin access required.", "error")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# Initialize database on startup (Only for local SQLite)
if not os.environ.get('DATABASE_URL'):
    init_db()

# Authentication Routes
@app.route("/signin.html")
def signin_page():
    return render_template("signin.html")

@app.route("/signup", methods=["POST"])
def signup():
    """Handle user registration"""
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not name or not email or not password:
            return jsonify({"message": "All fields are required"}), 400

        # Hash the password
        hashed_password = hash_password(password)

        # Insert user into database
        conn = get_db_connection()
        try:
            execute_query(conn,
                'INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                (name, email, hashed_password)
            )
            conn.commit()
            conn.close()
            return jsonify({"message": "Account created successfully"}), 201
        except (sqlite3.IntegrityError, psycopg2.IntegrityError):
            conn.close()
            return jsonify({"message": "Email already exists"}), 409

    except Exception as e:
        return jsonify({"message": f"Server error: {str(e)}"}), 500

@app.route("/signin", methods=["POST"])
def signin():
    """Handle user login"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        next_url = request.args.get('next') or url_for('index')

        if not email or not password:
            return jsonify({"message": "Email and password are required"}), 400

        # Hash the password
        hashed_password = hash_password(password)

        # Check credentials
        conn = get_db_connection()
        user = execute_query(conn,
            'SELECT * FROM users WHERE email = ? AND password = ?',
            (email, hashed_password)
        ).fetchone()
        conn.close()

        if user:
            # Promote specific email to admin for development/access
            if email == 'racharlamohan16@gmail.com' and not user['is_admin']:
                conn = get_db_connection()
                execute_query(conn, 'UPDATE users SET is_admin = 1 WHERE id = ?', (user['id'],))
                conn.commit()
                conn.close()
                user = dict(user)
                user['is_admin'] = 1

            # Store user info in session
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['is_admin'] = bool(user['is_admin'])
            
            return jsonify({
                "message": "Sign in successful",
                "user": {
                    "name": user['name'],
                    "email": user['email'],
                    "is_admin": bool(user['is_admin'])
                },
                "next": next_url if not user['is_admin'] else url_for('admin_dashboard')
            }), 200
        else:
            return jsonify({"message": "Invalid email or password"}), 401

    except Exception as e:
        return jsonify({"message": f"Server error: {str(e)}"}), 500

@app.route("/logout")
def logout():
    """Handle user logout"""
    user_name = session.get('user_name', 'User')
    session.clear()
    # Store logout message in session for next page load
    session['logout_message'] = f"Goodbye {user_name}! You have been logged out successfully. See you soon! 👋"
    return redirect(url_for('index'))

@app.route("/dashboard")
@login_required
def dashboard():
    """Render the user dashboard"""
    return render_template("dashboard.html")

@app.route("/")
def index():
    # Get logout message if it exists
    logout_msg = session.pop('logout_message', None)
    return render_template("index.html", logout_message=logout_msg)

@app.route("/c.html")
@login_required
def c_page():
    return render_template("c.html")

@app.route("/java.html")
@login_required
def java_page():
    return render_template("java.html")

@app.route("/python.html")
@login_required
def python_page():
    return render_template("python.html")

@app.route("/compiler.html")
@login_required
def compiler_page():
    return render_template("compiler.html")

@app.route("/roadmap.html")
@login_required
def roadmap_page():
    return render_template("roadmap.html")

@app.route("/terms-conditions.html")
def terms_conditions():
    return render_template("terms-conditions.html")

# Admin Routes
@app.route("/admin")
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    contents = execute_query(conn, 'SELECT * FROM content ORDER BY language, order_index').fetchall()
    users_count = execute_query(conn, 'SELECT COUNT(*) FROM users').fetchone()
    users_count = users_count[0] if isinstance(users_count, tuple) else (users_count.get('count') if hasattr(users_count, 'get') else list(users_count.values())[0])
    
    all_users = execute_query(conn, 'SELECT id, name, email, is_admin, created_at FROM users ORDER BY id DESC').fetchall()
    conn.close()
    return render_template("admin/dashboard.html", contents=contents, users_count=users_count, all_users=all_users)

@app.route("/admin/add_content", methods=["POST"])
@admin_required
def add_content():
    try:
        data = request.json
        language = data.get('language')
        topic_slug = data.get('topic_slug')
        topic_title = data.get('topic_title')
        content_html = data.get('content_html')
        order_index = data.get('order_index', 0)

        conn = get_db_connection()
        execute_query(conn, '''
            INSERT OR REPLACE INTO content (language, topic_slug, topic_title, content_html, order_index)
            VALUES (?, ?, ?, ?, ?)
        ''', (language, topic_slug, topic_title, content_html, order_index))
        conn.commit()
        conn.close()
        return jsonify({"message": "Content added/updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/admin/delete_content/<int:id>", methods=["POST"])
@admin_required
def delete_content(id):
    try:
        conn = get_db_connection()
        execute_query(conn, 'DELETE FROM content WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Content deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# Content API for dynamic pages
@app.route("/api/content/<language>")
def get_language_content(language):
    conn = get_db_connection()
    topics = execute_query(conn, 'SELECT topic_slug, topic_title FROM content WHERE language = ? ORDER BY order_index', (language.lower(),)).fetchall()
    conn.close()
    return jsonify([dict(t) for t in topics])

@app.route("/api/content/<language>/<topic_slug>")
def get_topic_content(language, topic_slug):
    conn = get_db_connection()
    topic = execute_query(conn, 'SELECT * FROM content WHERE language = ? AND topic_slug = ?', (language.lower(), topic_slug)).fetchone()
    conn.close()
    if topic:
        return jsonify(dict(topic))
    return jsonify({"message": "Not found"}), 404

@app.route("/run", methods=["POST"])
def run():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"output": "No input data received"}), 400

        source = data.get("code", "")
        language_id = str(data.get("language_id", ""))

        if not source or not language_id:
            return jsonify({"output": "Missing code or language_id"}), 400

        # Run code locally depending on language using secure Docker Sandboxing
        output_result = ""
        
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Resolve temp_dir absolute path for Docker volume mounting
                mnt_dir = os.path.abspath(temp_dir)

                if language_id == '71':  # Python
                    file_path = os.path.join(mnt_dir, 'script.py')
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(source)
                    cmd = ['docker', 'run', '--rm', '--memory=100m', '--cpus=0.5', '--net=none', '-v', f'{mnt_dir}:/code', '-w', '/code', 'python:3.9-slim', 'python', 'script.py']
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    output_result = result.stdout + result.stderr

                elif language_id == '62':  # Java
                    file_path = os.path.join(mnt_dir, 'Main.java')
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(source)
                    
                    cmd_compile = ['docker', 'run', '--rm', '--memory=200m', '--cpus=0.5', '--net=none', '-v', f'{mnt_dir}:/code', '-w', '/code', 'openjdk:11', 'javac', 'Main.java']
                    compile_result = subprocess.run(cmd_compile, capture_output=True, text=True, timeout=10)
                    
                    if compile_result.returncode != 0:
                        output_result = compile_result.stderr
                    else:
                        cmd_run = ['docker', 'run', '--rm', '--memory=200m', '--cpus=0.5', '--net=none', '-v', f'{mnt_dir}:/code', '-w', '/code', 'openjdk:11', 'java', 'Main']
                        run_result = subprocess.run(cmd_run, capture_output=True, text=True, timeout=10)
                        output_result = run_result.stdout + run_result.stderr

                elif language_id == '50':  # C
                    file_path = os.path.join(mnt_dir, 'script.c')
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(source)
                    
                    cmd_compile = ['docker', 'run', '--rm', '--memory=100m', '--cpus=0.5', '--net=none', '-v', f'{mnt_dir}:/code', '-w', '/code', 'gcc:latest', 'gcc', 'script.c', '-o', 'script.exe']
                    compile_result = subprocess.run(cmd_compile, capture_output=True, text=True, timeout=10)
                    
                    if compile_result.returncode != 0:
                        output_result = compile_result.stderr
                    else:
                        cmd_run = ['docker', 'run', '--rm', '--memory=100m', '--cpus=0.5', '--net=none', '-v', f'{mnt_dir}:/code', '-w', '/code', 'gcc:latest', './script.exe']
                        run_result = subprocess.run(cmd_run, capture_output=True, text=True, timeout=10)
                        output_result = run_result.stdout + run_result.stderr

                elif language_id == '54':  # C++
                    file_path = os.path.join(mnt_dir, 'script.cpp')
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(source)
                        
                    cmd_compile = ['docker', 'run', '--rm', '--memory=100m', '--cpus=0.5', '--net=none', '-v', f'{mnt_dir}:/code', '-w', '/code', 'gcc:latest', 'g++', 'script.cpp', '-o', 'script.exe']
                    compile_result = subprocess.run(cmd_compile, capture_output=True, text=True, timeout=10)
                    
                    if compile_result.returncode != 0:
                        output_result = compile_result.stderr
                    else:
                        cmd_run = ['docker', 'run', '--rm', '--memory=100m', '--cpus=0.5', '--net=none', '-v', f'{mnt_dir}:/code', '-w', '/code', 'gcc:latest', './script.exe']
                        run_result = subprocess.run(cmd_run, capture_output=True, text=True, timeout=10)
                        output_result = run_result.stdout + run_result.stderr

                elif language_id == '63':  # Node.js
                    file_path = os.path.join(mnt_dir, 'script.js')
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(source)
                        
                    cmd = ['docker', 'run', '--rm', '--memory=100m', '--cpus=0.5', '--net=none', '-v', f'{mnt_dir}:/code', '-w', '/code', 'node:16-slim', 'node', 'script.js']
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    output_result = result.stdout + result.stderr

                else:
                    output_result = f"Unsupported language ID: {language_id}"

            except subprocess.TimeoutExpired:
                output_result = "Execution timed out (10 seconds limit)."
            except FileNotFoundError as e:
                output_result = f"Docker not found on system: {str(e)}\nMake sure Docker is installed on your server."
            except Exception as e:
                output_result = f"Docker execution error: {str(e)}"
        
        return jsonify({"output": output_result or "No output"})

    except Exception as e:
        return jsonify({"output": f"Server error: {str(e)}"}), 500


if __name__ == "__main__":
    # In SQLite mode we can init local db, for Supabase you did it manually
    if not os.environ.get('DATABASE_URL'):
        init_db()
    app.run(debug=True)
