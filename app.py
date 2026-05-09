from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash, Response, send_from_directory
from werkzeug.utils import secure_filename
import requests
import time
import sqlite3
import hashlib
import os
import subprocess
import tempfile
from datetime import datetime, timedelta
from functools import wraps
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Google OAuth imports
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

load_dotenv() # Load variables from .env

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.environ.get('SECRET_KEY', 'codenative_fallback_secret_key_secure_12345')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

@app.context_processor
def inject_ga():
    return dict(ga_id='G-YHH2J3PXVZ')

# Allow HTTP for OAuth in development
if not os.environ.get('DATABASE_URL') or '127.0.0.1' in os.environ.get('GOOGLE_REDIRECT_URI', ''):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Database configuration
DATABASE = 'users.db'

def get_db_connection():
    """Open one fresh connection per request — correct pattern for Vercel serverless.
    Supabase Free allows only 2 simultaneous direct connections; no pool needed."""
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        try:
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)
            conn = psycopg2.connect(db_url)
            conn.cursor_factory = psycopg2.extras.RealDictCursor
            return conn
        except Exception as e:
            print(f"CRITICAL: DB connection failed: {e}")
            raise Exception(f"Failed to connect to Supabase: {e}")

    # Fallback to SQLite (local dev)
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def release_db_connection(conn):
    """Close the connection — called at the end of every request."""
    if conn:
        try:
            conn.close()
        except Exception:
            pass

def execute_query(conn, query, params=None):
    """Abstraction layer to handle different SQL placeholders (?, %s)"""
    is_pg = hasattr(conn, 'cursor_factory') # Basic check for psycopg2 connection
    if is_pg:
        query = query.replace('?', '%s')
        # PostgreSQL doesn't support INSERT OR REPLACE, use INSERT ... ON CONFLICT
        if 'INSERT OR REPLACE' in query:
            # We specifically handle the content table case
            query = query.replace('INSERT OR REPLACE INTO content', 'INSERT INTO content')
            query += ' ON CONFLICT (language, topic_slug) DO UPDATE SET topic_title = EXCLUDED.topic_title, content_html = EXCLUDED.content_html, quiz_json = EXCLUDED.quiz_json, custom_css = EXCLUDED.custom_css, custom_js = EXCLUDED.custom_js, order_index = EXCLUDED.order_index'
    
    cursor = conn.cursor()
    cursor.execute(query, params or ())
    return cursor

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    """Initialize the database with users and content tables"""
    conn = get_db_connection()
    is_pg = hasattr(conn, 'cursor_factory')
    
    # SQL for Users Table
    users_sql = '''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            mobile TEXT,
            password TEXT, -- Password can be null for Google-only users
            google_id TEXT UNIQUE,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''' if is_pg else '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            mobile TEXT,
            password TEXT, -- Password can be null for Google-only users
            google_id TEXT UNIQUE,
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

    # SQL for User Stats
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

    # SQL for User Activity
    activity_sql = '''
        CREATE TABLE IF NOT EXISTS user_activity (
            user_id INTEGER,
            activity_date DATE,
            practice_count INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, activity_date)
        )
    '''

    # SQL for User Progress
    progress_sql = '''
        CREATE TABLE IF NOT EXISTS user_progress (
            user_id INTEGER,
            language TEXT,
            topic_slug TEXT,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, language, topic_slug)
        )
    '''

    # SQL for Feedback Table
    feedback_sql = '''
        CREATE TABLE IF NOT EXISTS feedback (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            name TEXT,
            email TEXT,
            mobile TEXT,
            college TEXT,
            rating INTEGER,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''' if is_pg else '''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            email TEXT,
            mobile TEXT,
            college TEXT,
            rating INTEGER,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    '''

    # SQL for Careers Table (Jobs & Workshops)
    careers_sql = '''
        CREATE TABLE IF NOT EXISTS careers (
            id SERIAL PRIMARY KEY,
            type TEXT NOT NULL, -- e.g. job, workshop
            title TEXT NOT NULL,
            company TEXT,
            location TEXT,
            description TEXT,
            link TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''' if is_pg else '''
        CREATE TABLE IF NOT EXISTS careers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL, -- e.g. job, workshop
            title TEXT NOT NULL,
            company TEXT,
            location TEXT,
            description TEXT,
            link TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    '''
    # SQL for Career Applications Table
    career_applications_sql = '''
        CREATE TABLE IF NOT EXISTS career_applications (
            id SERIAL PRIMARY KEY,
            career_id INTEGER REFERENCES careers(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            whatsapp TEXT,
            college TEXT,
            passout_year TEXT,
            resume_link TEXT,
            cover_letter TEXT,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''' if is_pg else '''
        CREATE TABLE IF NOT EXISTS career_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            career_id INTEGER REFERENCES careers(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            whatsapp TEXT,
            college TEXT,
            passout_year TEXT,
            resume_link TEXT,
            cover_letter TEXT,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    '''

    if is_pg:
        cursor = conn.cursor()
        cursor.execute(users_sql)
        cursor.execute(content_sql)
        cursor.execute(stats_sql)
        cursor.execute(activity_sql)
        cursor.execute(progress_sql)
        cursor.execute(feedback_sql)
        cursor.execute(careers_sql)
        cursor.execute(career_applications_sql)
        
        # Check if is_admin column exists (Postgres migration)
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='is_admin'
        """)
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
        
        # Check if mobile column exists (Postgres migration)
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='mobile'
        """)
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE users ADD COLUMN mobile TEXT")
        
        # Check if OTP columns exist (Postgres migration)
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='otp_code'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE users ADD COLUMN otp_code TEXT")
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='otp_expiry' ")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE users ADD COLUMN otp_expiry TIMESTAMP")
        
        # Check if google_id column exists (Postgres migration)
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='google_id'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE users ADD COLUMN google_id TEXT UNIQUE")
        
        # Check if feedback mobile/college columns exist (Postgres migration)
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='feedback' AND column_name='mobile'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE feedback ADD COLUMN mobile TEXT")
        
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='feedback' AND column_name='college'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE feedback ADD COLUMN college TEXT")

        # Check if quiz_json/custom_css/custom_js columns exist (Postgres migration)
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='content' AND column_name='quiz_json'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE content ADD COLUMN quiz_json TEXT")
        
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='content' AND column_name='custom_css'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE content ADD COLUMN custom_css TEXT")
            
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='content' AND column_name='custom_js'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE content ADD COLUMN custom_js TEXT")

        # Check if career_applications columns exist (Postgres migration)
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='career_applications' AND column_name='whatsapp'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE career_applications ADD COLUMN whatsapp TEXT")
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='career_applications' AND column_name='college'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE career_applications ADD COLUMN college TEXT")
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='career_applications' AND column_name='passout_year'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE career_applications ADD COLUMN passout_year TEXT")

        conn.commit()
    else:
        # SQLite
        conn.execute(users_sql)
        conn.execute(content_sql)
        conn.execute(stats_sql)
        conn.execute(activity_sql)
        conn.execute(progress_sql)
        conn.execute(feedback_sql)
        conn.execute(careers_sql)
        conn.execute(career_applications_sql)
        
        # Check if is_admin column exists (SQLite migration)
        cursor = conn.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'is_admin' not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
        
        if 'mobile' not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN mobile TEXT")
        
        if 'otp_code' not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN otp_code TEXT")
        if 'otp_expiry' not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN otp_expiry TIMESTAMP")
        
        if 'google_id' not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN google_id TEXT")
        
        # Check if custom_css/js columns exist (SQLite migration)
        cursor = conn.execute("PRAGMA table_info(content)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'custom_css' not in columns:
            conn.execute("ALTER TABLE content ADD COLUMN custom_css TEXT")
        if 'custom_js' not in columns:
            conn.execute("ALTER TABLE content ADD COLUMN custom_js TEXT")
        if 'quiz_json' not in columns:
            conn.execute("ALTER TABLE content ADD COLUMN quiz_json TEXT")

        # Check if career_applications columns exist (SQLite migration)
        cursor = conn.execute("PRAGMA table_info(career_applications)")
        ca_cols = [col[1] for col in cursor.fetchall()]
        if 'whatsapp' not in ca_cols:
            conn.execute("ALTER TABLE career_applications ADD COLUMN whatsapp TEXT")
        if 'college' not in ca_cols:
            conn.execute("ALTER TABLE career_applications ADD COLUMN college TEXT")
        if 'passout_year' not in ca_cols:
            conn.execute("ALTER TABLE career_applications ADD COLUMN passout_year TEXT")
        
        conn.commit()
    
    release_db_connection(conn)
    print("Database initialized successfully!")

# Auth Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for('signin_page', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Admin Decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            flash("Admin access required.", "error")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# Initialize database on startup
# try:
#     init_db()
# except Exception as e:
#     print(f"Note: Database initialization skipped or failed: {e}")

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
        mobile = data.get('mobile')
        password = data.get('password')

        if not name or not email or not password:
            return jsonify({"message": "All fields are required"}), 400

        # Hash the password
        hashed_password = hash_password(password)

        # Insert user into database
        conn = get_db_connection()
        try:
            execute_query(conn,
                'INSERT INTO users (name, email, mobile, password) VALUES (?, ?, ?, ?)',
                (name, email, mobile, hashed_password)
            )
            conn.commit()
            release_db_connection(conn)
            return jsonify({"message": "Account created successfully"}), 201
        except (sqlite3.IntegrityError, psycopg2.IntegrityError):
            release_db_connection(conn)
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
        release_db_connection(conn)

        if user:
            # Promote specific email to admin for development/access
            if email == 'racharlamohan16@gmail.com' and not user['is_admin']:
                conn = get_db_connection()
                execute_query(conn, 'UPDATE users SET is_admin = 1 WHERE id = ?', (user['id'],))
                conn.commit()
                release_db_connection(conn)
                user = dict(user)
                user['is_admin'] = 1

            # Store user info in session
            session.permanent = True
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

# Forgot Password Routes
def send_email(to_email, subject, body):
    """Helper function to send email via SMTP"""
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_user = os.environ.get('SMTP_USER')
    smtp_password = os.environ.get('SMTP_PASSWORD')

    if not smtp_user or not smtp_password:
        print("ERROR: SMTP credentials not set in .env")
        return False

    try:
        msg = MIMEMultipart()
        sender_name = os.environ.get('SENDER_NAME', 'Code Native')
        msg['From'] = f"{sender_name} <{smtp_user}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False

@app.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    email = data.get("email")
    
    conn = get_db_connection()
    user = execute_query(conn, "SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    
    if not user:
        release_db_connection(conn)
        return jsonify({"message": "Email not found"}), 404
    
    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))
    expiry = datetime.now() + timedelta(minutes=10)
    
    execute_query(conn, "UPDATE users SET otp_code = ?, otp_expiry = ? WHERE email = ?", (otp, expiry, email))
    conn.commit()
    release_db_connection(conn)
    
    subject = "Your Code Native Password Reset OTP"
    body = f"Hello,\n\nYour OTP for password reset is: {otp}\n\nThis code will expire in 10 minutes.\n\nIf you did not request this, please ignore this email."
    
    if send_email(email, subject, body):
        return jsonify({"message": "OTP sent successfully to your email."})
    else:
        return jsonify({"message": "Failed to send email. Please check SMTP settings."}), 500

@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    email = data.get("email")
    otp = data.get("otp")
    
    conn = get_db_connection()
    user = execute_query(conn, "SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    
    if not user:
        release_db_connection(conn)
        return jsonify({"message": "User not found"}), 404
    
    # Check OTP and Expiry
    db_otp = user['otp_code']
    db_expiry = user['otp_expiry']
    
    if isinstance(db_expiry, str):
        try:
            db_expiry = datetime.strptime(db_expiry.split('.')[0], '%Y-%m-%d %H:%M:%S')
        except:
            db_expiry = datetime.strptime(db_expiry, '%Y-%m-%dT%H:%M:%S')

    if db_otp == otp and datetime.now() < db_expiry:
        release_db_connection(conn)
        return jsonify({"message": "OTP verified successfully"})
    else:
        release_db_connection(conn)
        return jsonify({"message": "Invalid or expired OTP"}), 400

@app.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    email = data.get("email")
    otp = data.get("otp")
    new_password = data.get("new_password")
    
    conn = get_db_connection()
    user = execute_query(conn, "SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    
    if not user:
        release_db_connection(conn)
        return jsonify({"message": "User not found"}), 404
        
    db_otp = user['otp_code']
    db_expiry = user['otp_expiry']
    if isinstance(db_expiry, str):
        try:
            db_expiry = datetime.strptime(db_expiry.split('.')[0], '%Y-%m-%d %H:%M:%S')
        except:
            db_expiry = datetime.strptime(db_expiry, '%Y-%m-%dT%H:%M:%S')

    if db_otp == otp and datetime.now() < db_expiry:
        hashed_pw = hash_password(new_password)
        execute_query(conn, "UPDATE users SET password = ?, otp_code = NULL, otp_expiry = NULL WHERE email = ?", (hashed_pw, email))
        conn.commit()
        release_db_connection(conn)
        return jsonify({"message": "Password reset successfully!"})
    else:
        release_db_connection(conn)
        return jsonify({"message": "Session expired or invalid. Please try again."}), 400

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "http://127.0.0.1:5000/login/google/callback")
# In production, this must be an HTTPS URL. For local dev, http is fine.
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

@app.route("/login/google")
def login_google():
    """Initiate Google OAuth flow"""
    # Use a dummy secret key for the flow if one isn't provided
    redirect_uri = GOOGLE_REDIRECT_URI
    
    # Configure OAuth 2.0 Flow
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=[
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
            "openid"
        ],
        redirect_uri=redirect_uri
    )

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    session['oauth_state'] = state
    # Store the code verifier for PKCE
    session['code_verifier'] = flow.code_verifier
    # Store the next URL so we can redirect there after login
    session['oauth_next'] = request.args.get('next', '')
    return redirect(authorization_url)

@app.route("/login/google/callback")
def google_callback():
    """Handle Google OAuth callback"""
    state = session.get('oauth_state')
    
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=[
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
            "openid"
        ],
        state=state,
        redirect_uri=GOOGLE_REDIRECT_URI
    )
    
    # Restore the code verifier for PKCE
    flow.code_verifier = session.get('code_verifier')

    try:
        flow.fetch_token(authorization_response=request.url)
    except Exception as e:
        print(f"Error fetching token: {e}")
        return redirect(url_for('signin_page', error='oauth_failed'))

    credentials = flow.credentials
    
    # Verify the ID token
    try:
        id_info = id_token.verify_oauth2_token(
            credentials.id_token, 
            google_requests.Request(), 
            GOOGLE_CLIENT_ID
        )
    except ValueError:
        return redirect(url_for('signin_page', error='invalid_token'))

    google_id = id_info.get('sub')
    email = id_info.get('email')
    name = id_info.get('name')
    
    if not email:
        return redirect(url_for('signin_page', error='no_email'))

    conn = get_db_connection()
    # Check if user exists by google_id
    user = execute_query(conn, "SELECT * FROM users WHERE google_id = ?", (google_id,)).fetchone()
    
    if not user:
        # Check if user exists by email (link account)
        user = execute_query(conn, "SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user:
            execute_query(conn, "UPDATE users SET google_id = ? WHERE id = ?", (google_id, user['id']))
            conn.commit()
        else:
            # Create new user
            execute_query(conn, "INSERT INTO users (name, email, google_id) VALUES (?, ?, ?)", (name, email, google_id))
            conn.commit()
            user = execute_query(conn, "SELECT * FROM users WHERE google_id = ?", (google_id,)).fetchone()

    release_db_connection(conn)

    # Log user in
    session.permanent = True
    session['user_id'] = user['id']
    session['user_name'] = user['name']
    session['user_email'] = user['email']
    session['is_admin'] = bool(user['is_admin'])
    
    flash(f"Signed in as {user['name']}", "success")
    
    # Redirect to next page if set (e.g. from chatbot login prompt), else dashboard
    next_url = session.pop('oauth_next', None)
    if next_url and next_url.startswith('http') and 'codenative' in next_url:
        return redirect(next_url)
    elif next_url and next_url.startswith('/'):
        return redirect(next_url)
    return redirect(url_for('dashboard') if not user['is_admin'] else url_for('admin_dashboard'))

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
    user_id = session.get('user_id')
    conn = get_db_connection()
    stats = execute_query(conn, "SELECT * FROM user_stats WHERE user_id = ?", (user_id,)).fetchone()
    
    if stats:
        stats = dict(stats)
        stats['study_hours'] = round(stats['study_minutes'] / 60, 1)
    else:
        stats = {
            'study_hours': 0.0,
            'study_minutes': 0,
            'certificates': 0,
            'current_streak': 0,
            'max_streak': 0
        }
    
    # Calculate consistency & total practices
    activities = execute_query(conn, "SELECT activity_date, practice_count FROM user_activity WHERE user_id = ? ORDER BY activity_date ASC", (user_id,)).fetchall()
    
    # Calculate Real Course Progress
    courses = [
        {'id': 'python', 'name': 'Python Core', 'icon': 'fab fa-python', 'bg': 'python-bg', 'header_bg': '#3776ab', 'link': '/python.html'},
        {'id': 'c', 'name': 'C Architecture', 'icon': 'fas fa-code-branch', 'bg': 'c-bg', 'header_bg': '#00599c', 'link': '/c.html'},
        {'id': 'java', 'name': 'Java Masterclass', 'icon': 'fab fa-java', 'bg': 'java-bg', 'header_bg': '#ed8b00', 'link': '/java.html'},
        {'id': 'web', 'name': 'Web Development', 'icon': 'fab fa-html5', 'bg': 'web-bg', 'header_bg': '#e34f26', 'link': '/web.html'},
        {'id': 'js', 'name': 'JavaScript Expert', 'icon': 'fab fa-js', 'bg': 'js-bg', 'header_bg': '#f7df1e', 'link': '/js.html'}
    ]
    
    user_courses = []
    for course in courses:
        # Total topics in this language
        total_topics = execute_query(conn, "SELECT COUNT(*) as count FROM content WHERE language = ?", (course['id'],)).fetchone()
        total_topics = total_topics['count'] if total_topics else 0
        
        if total_topics > 0:
            # Topics completed by user
            completed = execute_query(conn, "SELECT COUNT(*) as count FROM user_progress WHERE user_id = ? AND language = ?", (user_id, course['id'])).fetchone()
            completed_count = completed['count'] if completed else 0
            
            # Last completed topic
            last_topic = execute_query(conn, """
                SELECT c.topic_title 
                FROM user_progress p 
                JOIN content c ON p.topic_slug = c.topic_slug AND p.language = c.language
                WHERE p.user_id = ? AND p.language = ?
                ORDER BY p.completed_at DESC LIMIT 1
            """, (user_id, course['id'])).fetchone()
            
            course_data = course.copy()
            course_data['progress'] = int((completed_count / total_topics) * 100) if total_topics > 0 else 0
            course_data['last_topic'] = last_topic['topic_title'] if last_topic else "Not started yet"
            user_courses.append(course_data)

    release_db_connection(conn)
    
    total_practices = sum([a['practice_count'] for a in activities])
    total_days_active = len(activities)

    # Consistency = days active / days elapsed this year (Jan 1 → today), capped at 100
    today_date = datetime.today().date()
    year_start = today_date.replace(month=1, day=1)
    days_elapsed = max((today_date - year_start).days + 1, 1)
    consistency = min(int((total_days_active / days_elapsed) * 100), 100)
    
    activity_data = [dict(a) for a in activities]
    
    return render_template("dashboard.html", stats=stats, total_practices=total_practices, consistency=consistency, activity_data=activity_data, user_courses=user_courses)

def update_user_activity(user_id, is_practice=False):
    conn = get_db_connection()
    today_str = datetime.today().strftime('%Y-%m-%d')
    try:
        act = execute_query(conn, "SELECT practice_count FROM user_activity WHERE user_id = ? AND activity_date = ?", (user_id, today_str)).fetchone()
        practice_inc = 1 if is_practice else 0
        if act:
            execute_query(conn, "UPDATE user_activity SET practice_count = practice_count + ? WHERE user_id = ? AND activity_date = ?", (practice_inc, user_id, today_str))
        else:
            execute_query(conn, "INSERT INTO user_activity (user_id, activity_date, practice_count) VALUES (?, ?, ?)", (user_id, today_str, practice_inc))
            
        stats = execute_query(conn, "SELECT * FROM user_stats WHERE user_id = ?", (user_id,)).fetchone()
        study_inc = 1 if not is_practice else 0
        
        if not stats:
            execute_query(conn, "INSERT INTO user_stats (user_id, study_minutes, certificates, current_streak, max_streak, last_active_date) VALUES (?, ?, 0, 1, 1, ?)", (user_id, study_inc, today_str))
        else:
            last_date = stats['last_active_date']
            # safely parse last_date
            if isinstance(last_date, str):
                try:
                    last_date = datetime.strptime(last_date.split(' ')[0], '%Y-%m-%d').date()
                except:
                    last_date = None
            elif hasattr(last_date, 'date'):
                last_date = last_date.date()
            elif isinstance(last_date, datetime):
                last_date = last_date.date()
                
            today_date = datetime.today().date()
            delta = (today_date - last_date).days if last_date else 0
            
            new_streak = stats['current_streak']
            if delta == 1:
                new_streak += 1
            elif delta > 1:
                new_streak = 1
                
            new_max = max(stats['max_streak'], new_streak)
            if delta == 0:
                new_streak = stats['current_streak']
                
            execute_query(conn, "UPDATE user_stats SET study_minutes = study_minutes + ?, current_streak = ?, max_streak = ?, last_active_date = ? WHERE user_id = ?", 
                          (study_inc, new_streak, new_max, today_str, user_id))
        conn.commit()
    except Exception as e:
        print("Error tracking activity:", e)
    finally:
        release_db_connection(conn)

@app.route("/api/complete_topic", methods=["POST"])
@login_required
def complete_topic():
    try:
        data = request.json
        user_id = session['user_id']
        language = data.get('language')
        topic_slug = data.get('topic_slug')
        
        if not language or not topic_slug:
            return jsonify({"message": "Missing language or slug"}), 400
            
        conn = get_db_connection()
        execute_query(conn, """
            INSERT INTO user_progress (user_id, language, topic_slug)
            VALUES (?, ?, ?)
            ON CONFLICT (user_id, language, topic_slug) DO NOTHING
        """, (user_id, language, topic_slug))
        conn.commit()
        release_db_connection(conn)
        
        # Also track this as a study activity
        update_user_activity(user_id, is_practice=False)
        
        return jsonify({"message": "Progress saved"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/api/log_study", methods=["POST"])
def log_study():
    if 'user_id' in session:
        update_user_activity(session['user_id'], is_practice=False)
        return jsonify({"status": "ok"})
    return jsonify({"status": "unauthorized"}), 401

@app.route("/")
def index():
    # Get logout message if it exists
    logout_msg = session.pop('logout_message', None)
    
    # Fetch started counts for all courses to show social proof on home page
    conn = get_db_connection()
    counts = {}
    langs = ['c', 'java', 'python', 'web', 'js']
    for lang in langs:
        res = execute_query(conn, 'SELECT COUNT(DISTINCT user_id) as count FROM user_progress WHERE language = ?', (lang,)).fetchone()
        counts[lang] = res['count'] if res else 0
    release_db_connection(conn)

    # Student Reviews (Transcribed from user images)
    reviews = [
        {
            "name": "Sagar",
            "rating": 5,
            "message": "Great platform for learning coding in Telugu! Clear tutorials, interactive compiler, and covers all major languages. Highly recommended for beginners!",
            "role": "Independent Scholar",
            "date": "2026-05-05",
            "initial": "S"
        },
        {
            "name": "Kanna Vemula",
            "rating": 5,
            "message": "I like the interface and it's good platform to learn java or any other language from scratch in Telugu! 😊",
            "role": "Sree Chaitanya Institute of Tech",
            "date": "2026-05-04",
            "initial": "K"
        },
        {
            "name": "Shivateja",
            "rating": 5,
            "message": "Great innovative work by the CodeNative team! Wishing you all more success and growth ahead. 🔥",
            "role": "Independent Scholar",
            "date": "2026-05-04",
            "initial": "S"
        },
        {
            "name": "Deva",
            "rating": 5,
            "message": "Good Web for beginners, such good idea it is. Content is in Telugu, and the AI is next level asalu! Good Initiative.",
            "role": "Independent Scholar",
            "date": "2026-05-04",
            "initial": "D"
        },
        {
            "name": "Srikar Manchala",
            "rating": 5,
            "message": "Very useful platform for native speakers. Everything is explained clearly in Telugu. 🚀",
            "role": "Bharath Institute of Higher Ed",
            "date": "2026-05-04",
            "initial": "S"
        },
        {
            "name": "PapaRao Rapuri",
            "rating": 5,
            "message": "CodeNative is very helpful for beginners. The step-by-step approach makes learning programming easy to follow. Highly recommended!",
            "role": "Independent Scholar",
            "date": "2026-05-01",
            "initial": "P"
        },
        {
            "name": "Tutorial User",
            "rating": 5,
            "message": "Oh chala useful and simply understanding. Best platform for Telugu students. 😊",
            "role": "Independent Scholar",
            "date": "2026-04-25",
            "initial": "T"
        },
        {
            "name": "Venkatesh",
            "rating": 5,
            "message": "All good, UI is good. The platform is consistent and easy to navigate. Keep it up!",
            "role": "MLRIT",
            "date": "2026-05-04",
            "initial": "V"
        },
        {
            "name": "Vaishu",
            "rating": 5,
            "message": "Excellent Platform. Friendly Content and very easy to understand for beginners. 🌟",
            "role": "Independent Scholar",
            "date": "2026-05-04",
            "initial": "V"
        },
        {
            "name": "Ajay Patel Boppa",
            "rating": 5,
            "message": "Such a good website to prepare for courses in Telugu easily. Concepts are explained very well.",
            "role": "Jyothismathi Institute of Tech",
            "date": "2026-05-04",
            "initial": "A"
        },
        {
            "name": "Zuck",
            "rating": 5,
            "message": "This initiative is impactful because it removes language barriers in tech education. Teaching programming in Telugu helps thousands build real skills.",
            "role": "CBIT",
            "date": "2026-05-04",
            "initial": "Z"
        },
        {
            "name": "Tutorial User",
            "rating": 5,
            "message": "Ui is Good, Easy understanding content. Very helpful for beginners.",
            "role": "Independent Scholar",
            "date": "2026-04-26",
            "initial": "T"
        }
    ]
    
    return render_template("index.html", logout_message=logout_msg, course_counts=counts, reviews=reviews)

@app.route("/c.html")
def c_page():
    return render_template("c.html")

@app.route("/java.html")
def java_page():
    return render_template("java.html")

@app.route("/python.html")
def python_page():
    return render_template("python.html")

@app.route("/compiler.html")
def compiler_page():
    return render_template("compiler.html")

@app.route("/roadmap.html")
def roadmap_page():
    return render_template("roadmap.html")

@app.route("/terms-conditions.html")
def terms_conditions():
    return render_template("terms-conditions.html")

@app.route("/privacy-policy.html")
def privacy_policy():
    return render_template("privacy-policy.html")

@app.route("/cookie-policy.html")
def cookie_policy():
    return render_template("cookie-policy.html")

@app.route("/web.html")
def web_page():
    return render_template("web.html")

@app.route("/js.html")
def js_page():
    return render_template("js.html")

@app.route("/videos.html")
def videos_page():
    return render_template("videos.html")

@app.route("/careers.html")
@login_required
def careers_page():
    conn = get_db_connection()
    careers = execute_query(conn, "SELECT * FROM careers ORDER BY id DESC").fetchall()
    release_db_connection(conn)
    return render_template("careers.html", careers=careers)

@app.route("/apply/<int:career_id>")
@login_required
def apply_page(career_id):
    conn = get_db_connection()
    career = execute_query(conn, "SELECT * FROM careers WHERE id = ?", (career_id,)).fetchone()
    release_db_connection(conn)
    if not career:
        return "Career post not found", 404
    
    # Prefill user info if logged in
    user_name = session.get('user_name', '')
    user_email = session.get('user_email', '')
    return render_template("apply.html", career=career, user_name=user_name, user_email=user_email)

@app.route("/apply_submit", methods=["POST"])
@login_required
def apply_submit():
    try:
        career_id = request.form.get('career_id')
        name = request.form.get('name')
        email = request.form.get('email')
        whatsapp = request.form.get('whatsapp')
        college = request.form.get('college')
        passout_year = request.form.get('passout_year')
        cover_letter = request.form.get('cover_letter')

        resume_link = request.form.get('resume_link') or ""
        resume_file = request.files.get('resume')
        if resume_file and resume_file.filename != "":
            import base64
            file_bytes = resume_file.read()
            encoded = base64.b64encode(file_bytes).decode('utf-8')
            content_type = resume_file.content_type or 'application/octet-stream'
            resume_link = f"data:{content_type};base64,{encoded}"

        if not resume_link:
            return jsonify({"message": "Please upload a resume file or provide a public link."}), 400

        if not career_id or not name or not email:
            return jsonify({"message": "Career, Name and Email are required"}), 400

        conn = get_db_connection()
        execute_query(conn, '''
            INSERT INTO career_applications (career_id, name, email, whatsapp, college, passout_year, resume_link, cover_letter)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (career_id, name, email, whatsapp, college, passout_year, resume_link, cover_letter))
        conn.commit()
        release_db_connection(conn)
        return jsonify({"message": "Application submitted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route("/uploads/resumes/<path:filename>")
def serve_resume(filename):
    import base64
    conn = get_db_connection()
    if filename.isdigit():
        app_data = execute_query(conn, "SELECT resume_link FROM career_applications WHERE id = ?", (int(filename),)).fetchone()
    else:
        app_data = execute_query(conn, "SELECT resume_link FROM career_applications WHERE resume_link LIKE ?", (f"%{filename}%",)).fetchone()
    release_db_connection(conn)

    if not app_data or not app_data['resume_link']:
        return "File not found", 404

    val = app_data['resume_link']
    if val.startswith("data:"):
        try:
            header, base64_str = val.split(",", 1)
            content_type = header.split(";")[0].replace("data:", "")
            file_bytes = base64.b64decode(base64_str)
            return Response(file_bytes, mimetype=content_type)
        except Exception as e:
            return f"Error: {str(e)}", 500
    elif val.startswith("http://") or val.startswith("https://"):
        return redirect(val)
    else:
        import tempfile
        clean_name = os.path.basename(val)
        local_dir = os.path.join('static', 'uploads', 'resumes')
        if os.path.exists(os.path.join(local_dir, clean_name)):
            return send_from_directory(local_dir, clean_name)
        
        tmp_dir = os.path.join(tempfile.gettempdir(), 'codenative_resumes')
        if os.path.exists(os.path.join(tmp_dir, clean_name)):
            return send_from_directory(tmp_dir, clean_name)
        
        return "File not found", 404

@app.route("/feedback.html")
def feedback_page():
    return render_template("feedback.html")

@app.route("/api/submit_feedback", methods=["POST"])
def submit_feedback():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        college = data.get('college')
        rating = data.get('rating')
        message = data.get('message')
        user_id = session.get('user_id')

        if not message and not rating:
            return jsonify({"message": "Either a rating or a message is required"}), 400

        conn = get_db_connection()
        execute_query(conn, 
            "INSERT INTO feedback (user_id, name, email, college, rating, message) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, name, email, college, rating, message)
        )
        conn.commit()
        release_db_connection(conn)

        return jsonify({"message": "Feedback submitted successfully! Thank you. 😊"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# Admin Feedback Route
@app.route("/admin/feedback")
@admin_required
def admin_feedback():
    conn = get_db_connection()
    feedbacks = execute_query(conn, "SELECT * FROM feedback ORDER BY created_at DESC").fetchall()
    release_db_connection(conn)
    
    # Calculate stats
    total_responses = len(feedbacks)
    sum_ratings = 0
    valid_ratings_count = 0
    
    for f in feedbacks:
        if f['rating']:
            try:
                sum_ratings += int(f['rating'])
                valid_ratings_count += 1
            except (ValueError, TypeError):
                continue
                
    avg_rating = round(sum_ratings / valid_ratings_count, 1) if valid_ratings_count > 0 else 0
    satisfaction = round((avg_rating / 5) * 100, 1) if avg_rating > 0 else 0
    
    stats = {
        'total': total_responses,
        'avg': avg_rating,
        'satisfaction': satisfaction
    }
    
    return render_template("admin/feedback.html", feedbacks=feedbacks, stats=stats)

# Admin Routes
@app.route("/admin")
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    contents = execute_query(conn, 'SELECT id, language, topic_slug, topic_title, content_html, quiz_json, custom_css, custom_js, order_index, created_at FROM content ORDER BY language, order_index').fetchall()
    
    # Total Users
    users_count_res = execute_query(conn, 'SELECT COUNT(*) as count FROM users').fetchone()
    users_count = users_count_res['count'] if hasattr(users_count_res, 'get') else users_count_res[0]
    
    # Language Distribution
    lang_dist = execute_query(conn, 'SELECT language, COUNT(*) as count FROM content GROUP BY language').fetchall()
    lang_labels = [row['language'].capitalize() for row in lang_dist]
    lang_counts = [row['count'] for row in lang_dist]

    # Daily User Registrations (Last 7 days)
    is_pg = hasattr(conn, 'cursor_factory')
    if is_pg:
        user_growth = execute_query(conn, """
            SELECT TO_CHAR(created_at, 'YYYY-MM-DD') as date, COUNT(*) as count 
            FROM users 
            WHERE created_at > CURRENT_DATE - INTERVAL '7 days'
            GROUP BY date ORDER BY date ASC
        """).fetchall()
    else:
        user_growth = execute_query(conn, """
            SELECT strftime('%Y-%m-%d', created_at) as date, COUNT(*) as count 
            FROM users 
            WHERE created_at > date('now', '-7 days')
            GROUP BY date ORDER BY date ASC
        """).fetchall()

    # Daily Practices (Last 7 days)
    if is_pg:
        practice_trends = execute_query(conn, """
            SELECT activity_date as date, SUM(practice_count) as count 
            FROM user_activity 
            WHERE activity_date > CURRENT_DATE - INTERVAL '7 days'
            GROUP BY activity_date ORDER BY activity_date ASC
        """).fetchall()
    else:
        practice_trends = execute_query(conn, """
            SELECT activity_date as date, SUM(practice_count) as count 
            FROM user_activity 
            WHERE activity_date > date('now', '-7 days')
            GROUP BY activity_date ORDER BY activity_date ASC
        """).fetchall()

    all_users = execute_query(conn, 'SELECT id, name, email, is_admin, created_at FROM users ORDER BY id DESC').fetchall()
    
    # Calculate Active Users (DAU/WAU)
    if is_pg:
        active_24h = execute_query(conn, "SELECT COUNT(*) as count FROM user_stats WHERE last_active_date >= CURRENT_DATE - INTERVAL '1 day'").fetchone()
        active_7d = execute_query(conn, "SELECT COUNT(*) as count FROM user_stats WHERE last_active_date >= CURRENT_DATE - INTERVAL '7 days'").fetchone()
    else:
        active_24h = execute_query(conn, "SELECT COUNT(*) as count FROM user_stats WHERE last_active_date >= date('now', '-1 day')").fetchone()
        active_7d = execute_query(conn, "SELECT COUNT(*) as count FROM user_stats WHERE last_active_date >= date('now', '-7 days')").fetchone()

    dau = active_24h['count'] if active_24h and 'count' in dict(active_24h) else (active_24h[0] if active_24h else 0)
    wau = active_7d['count'] if active_7d and 'count' in dict(active_7d) else (active_7d[0] if active_7d else 0)

    # Calculate User Growth Percentage (This week vs Last week)
    if is_pg:
        this_week = execute_query(conn, "SELECT COUNT(*) as count FROM users WHERE created_at > CURRENT_DATE - INTERVAL '7 days'").fetchone()
        last_week = execute_query(conn, "SELECT COUNT(*) as count FROM users WHERE created_at BETWEEN CURRENT_DATE - INTERVAL '14 days' AND CURRENT_DATE - INTERVAL '7 days'").fetchone()
    else:
        this_week = execute_query(conn, "SELECT COUNT(*) as count FROM users WHERE created_at > date('now', '-7 days')").fetchone()
        last_week = execute_query(conn, "SELECT COUNT(*) as count FROM users WHERE created_at BETWEEN date('now', '-14 days') AND date('now', '-7 days')").fetchone()
    
    careers = execute_query(conn, "SELECT * FROM careers ORDER BY id DESC").fetchall()
    career_apps = execute_query(conn, """
        SELECT ca.*, c.title as career_title, c.type as career_type
        FROM career_applications ca
        LEFT JOIN careers c ON ca.career_id = c.id
        ORDER BY ca.id DESC
    """).fetchall()
    
    release_db_connection(conn)

    tw_count = this_week['count'] if this_week and 'count' in dict(this_week) else (this_week[0] if this_week else 0)
    lw_count = last_week['count'] if last_week and 'count' in dict(last_week) else (last_week[0] if last_week else 0)
    
    growth_rate = 0
    if lw_count > 0:
        growth_rate = round(((tw_count - lw_count) / lw_count) * 100, 1)
    elif tw_count > 0:
        growth_rate = 100.0

    # Dynamic metrics
    engagement_rate = round((dau / users_count) * 100) if users_count > 0 else 0
    
    top_lang = "N/A"
    if lang_counts:
        max_idx = lang_counts.index(max(lang_counts))
        top_lang = lang_labels[max_idx]
        
    avg_session = 12
    if wau > 0 and practice_trends:
        # Assuming 3 mins per practice, avg over WAU
        total_practice_last_7d = sum(pt['count'] for pt in practice_trends)
        avg_session = max(5, min(60, round((total_practice_last_7d * 3) / wau)))

    analytics = {
        "lang_labels": lang_labels,
        "lang_counts": lang_counts,
        "user_growth": [dict(r) for r in user_growth],
        "practice_trends": [dict(r) for r in practice_trends],
        "user_growth_rate": growth_rate,
        "dau": dau,
        "wau": wau,
        "engagement_rate": engagement_rate,
        "top_lang": top_lang,
        "avg_session": avg_session
    }
    
    return render_template("admin/dashboard.html", 
                           contents=contents, 
                           users_count=users_count, 
                           all_users=all_users,
                           analytics=analytics,
                           careers=careers,
                           career_apps=career_apps)

# Admin Careers Add/Update
@app.route("/admin/add_career", methods=["POST"])
@admin_required
def add_career():
    try:
        data = request.get_json()
        career_id = data.get('id')
        type_ = data.get('type')
        title = data.get('title')
        company = data.get('company')
        location = data.get('location')
        description = data.get('description')
        link = data.get('link')

        if not type_ or not title:
            return jsonify({"message": "Type and Title are required"}), 400

        conn = get_db_connection()
        if career_id:
            execute_query(conn, '''
                UPDATE careers SET type = ?, title = ?, company = ?, location = ?, description = ?, link = ? WHERE id = ?
            ''', (type_, title, company, location, description, link, career_id))
        else:
            execute_query(conn, '''
                INSERT INTO careers (type, title, company, location, description, link)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (type_, title, company, location, description, link))
        conn.commit()
        release_db_connection(conn)
        return jsonify({"message": "Career item added/updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# Admin Careers Delete
@app.route("/admin/delete_career/<int:id>", methods=["POST"])
@admin_required
def delete_career(id):
    try:
        conn = get_db_connection()
        execute_query(conn, 'DELETE FROM careers WHERE id = ?', (id,))
        conn.commit()
        release_db_connection(conn)
        return jsonify({"message": "Career item deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# API endpoint to fetch a specific career (useful for editing)
@app.route("/api/career/<int:id>")
def get_career(id):
    conn = get_db_connection()
    career = execute_query(conn, "SELECT * FROM careers WHERE id = ?", (id,)).fetchone()
    release_db_connection(conn)
    if career:
        return jsonify(dict(career))
    return jsonify({"message": "Career not found"}), 404

@app.route("/admin/add_content", methods=["POST"])
@admin_required
def add_content():
    try:
        data = request.json
        language = data.get('language')
        topic_slug = data.get('topic_slug')
        topic_title = data.get('topic_title')
        content_html = data.get('content_html')
        quiz_json = data.get('quiz_json')
        custom_css = data.get('custom_css')
        custom_js = data.get('custom_js')
        order_index = data.get('order_index', 0)

        conn = get_db_connection()
        execute_query(conn, '''
            INSERT OR REPLACE INTO content (language, topic_slug, topic_title, content_html, quiz_json, custom_css, custom_js, order_index)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (language, topic_slug, topic_title, content_html, quiz_json, custom_css, custom_js, order_index))
        conn.commit()
        release_db_connection(conn)
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
        release_db_connection(conn)
        return jsonify({"message": "Content deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# Content API for dynamic pages
@app.route("/api/content/<language>")
def get_language_content(language):
    user_id = session.get('user_id')
    conn = get_db_connection()
    
    if user_id:
        query = '''
            SELECT c.topic_slug, c.topic_title, 
            CASE WHEN p.user_id IS NOT NULL THEN 1 ELSE 0 END as completed
            FROM content c
            LEFT JOIN user_progress p ON c.language = p.language AND c.topic_slug = p.topic_slug AND p.user_id = ?
            WHERE c.language = ? 
            ORDER BY c.order_index
        '''
        topics = execute_query(conn, query, (user_id, language.lower())).fetchall()
    else:
        topics = execute_query(conn, 'SELECT topic_slug, topic_title, 0 as completed FROM content WHERE language = ? ORDER BY order_index', (language.lower(),)).fetchall()
    
    release_db_connection(conn)
    return jsonify([dict(t) for t in topics])

@app.route("/api/content/<language>/<topic_slug>")
def get_topic_content(language, topic_slug):
    conn = get_db_connection()
    topic = execute_query(conn, 'SELECT id, language, topic_slug, topic_title, content_html, quiz_json, custom_css, custom_js, order_index, created_at FROM content WHERE language = ? AND topic_slug = ?', (language.lower(), topic_slug)).fetchone()
    
    # Get student count who completed this topic
    student_count_res = execute_query(conn, 'SELECT COUNT(*) as count FROM user_progress WHERE language = ? AND topic_slug = ?', (language.lower(), topic_slug)).fetchone()
    student_count = student_count_res['count'] if student_count_res else 0

    # Get started count — distinct users who have started any lesson in this language
    started_count_res = execute_query(conn, 'SELECT COUNT(DISTINCT user_id) as count FROM user_progress WHERE language = ?', (language.lower(),)).fetchone()
    started_count = started_count_res['count'] if started_count_res else 0

    # Check if user has already given feedback
    user_id = session.get('user_id')
    has_given_feedback = False
    if user_id:
        feedback_res = execute_query(conn, 'SELECT id FROM feedback WHERE user_id = ? LIMIT 1', (user_id,)).fetchone()
        has_given_feedback = bool(feedback_res)

    release_db_connection(conn)
    if topic:
        data = dict(topic)
        data['student_count'] = student_count
        data['started_count'] = started_count
        data['has_given_feedback'] = has_given_feedback
        return jsonify(data)
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

        # Use Judge0 API for code execution
        import base64
        import requests

        JUDGE0_URL = "https://judge0-ce.p.rapidapi.com/submissions?base64_encoded=true&wait=true"
        RAPIDAPI_KEY = os.environ.get("JUDGE0_API_KEY")
        RAPIDAPI_HOST = os.environ.get("JUDGE0_API_HOST", "judge0-ce.p.rapidapi.com")

        if not RAPIDAPI_KEY:
            return jsonify({"output": "Judge0 API Key is missing in environment configuration."}), 500

        data = request.get_json()
        source_code = data.get("code", "")
        language_id = data.get("language_id", "71")  # Default to Python
        stdin = data.get("stdin", "")

        # Judge0 expects base64 encoded source code and stdin if base64_encoded=true
        import base64
        encoded_source = base64.b64encode(source_code.encode('utf-8')).decode('utf-8')
        encoded_stdin = base64.b64encode(stdin.encode('utf-8')).decode('utf-8')

        payload = {
            "language_id": int(language_id),
            "source_code": encoded_source,
            "stdin": encoded_stdin
        }

        headers = {
            "content-type": "application/json",
            "Content-Type": "application/json",
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": RAPIDAPI_HOST
        }

        try:
            response = requests.post(JUDGE0_URL, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
            result_data = response.json()

            # Process output
            stdout = base64.b64decode(result_data.get("stdout") or "").decode("utf-8") if result_data.get("stdout") else ""
            stderr = base64.b64decode(result_data.get("stderr") or "").decode("utf-8") if result_data.get("stderr") else ""
            compile_output = base64.b64decode(result_data.get("compile_output") or "").decode("utf-8") if result_data.get("compile_output") else ""
            
            output_result = stdout or compile_output or stderr or result_data.get("message") or "No output"
            
            # If there's a specific status error
            status = result_data.get("status", {})
            if status.get("id") > 3: # Not Accepted
                output_result = f"Status: {status.get('description')}\n{output_result}"

        except requests.exceptions.RequestException as e:
            output_result = f"Judge0 API Error: {str(e)}"
        except Exception as e:
            output_result = f"Unexpected error: {str(e)}"
        
        # Track practice execution
        if 'user_id' in session:
            update_user_activity(session['user_id'], is_practice=True)

        return jsonify({"output": output_result or "No output"})

    except Exception as e:
        return jsonify({"output": f"Server error: {str(e)}"}), 500


# ──────────────────────────────────────────────────────────────
#  AI CHATBOT ENDPOINT  (Gemini 2.0 Flash)
# ──────────────────────────────────────────────────────────────
@app.route('/api/chat', methods=['POST'])
def ai_chat():
    """AI chatbot powered by Gemini. Context-aware for the current language."""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        language = data.get('language', 'programming')  # e.g. 'python', 'java', 'c'

        if not user_message:
            return jsonify({'reply': 'Please type a question first!'}), 400

        if 'user_id' not in session:
            # Grab the page the user was on (sent as Referer header by the browser)
            referrer = request.headers.get('Referer', '/')
            return jsonify({
                'reply': 'Hey ra 😄! AI chat use cheyali ante login avvali. Signin cheyyi ra!',
                'next_url': referrer
            }), 401

        gemini_api_key = os.environ.get('GEMINI_API_KEY', '')
        if not gemini_api_key:
            return jsonify({'reply': '⚠️ AI service not configured. Please set GEMINI_API_KEY in environment variables.'}), 503

        # Telugu casual coding friend system prompt
        system_prompt = f"""You are a friendly coding assistant who explains {language.upper()} programming doubts in a warm, casual, and supportive Telugu style.

Tone & Personality:
- Talk like a close best friend (fun, caring, chill)
- Use mostly Telugu + mix English for coding terms
- Keep it simple, friendly, and engaging
- Use light emojis 😊😄 (don't overuse)

Behavior:
- Always give clear and correct coding explanations
- Break concepts into small, easy steps
- Use examples and code snippets whenever needed
- Explain both "what" and "why"
- Encourage the user ("idi easy ra", "nuvvu chala fast ga nerchukuntav")

Style:
- Start replies casually (like: "Hey ra 😄", "Oye listen...", "Chill bro…")
- Avoid robotic or textbook language
- Keep answers short but useful (not too lengthy)
- Ask small follow-up questions to keep conversation going

When helping:
- If doubt → explain step-by-step
- If error → find mistake and fix it clearly
- If concept → give real-life/simple analogy
- If beginner → explain very simply

Rules:
- Be friendly but not inappropriate
- No rude or offensive language
- Stay focused on {language.upper()} coding help
- Don't give wrong or confusing answers

Example style:

User: function ante enti?
You:  Arey 😄 simple ga cheptha!
Function ante oka reusable block of code.
Okasari rayi, chala sarlu use chey 😄
Easy kada? Inka doubt unda?

User: Code error vastundi
You: Oye 😅 tension padaku ra… code share cheyyi, manam kalisi debug cheddam 💻🔥"""

        full_prompt = f"{system_prompt}\n\nUser: {user_message}\nYou:"

        # Call Gemini REST API directly
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 2048
            }
        }

        # Use a session for better performance
        session_req = requests.Session()
        
        # Models to try in order of preference (limited to 2 for Vercel 10s timeout)
        models_to_try = [
            "gemini-2.0-flash",
            "gemini-1.5-flash"
        ]
        
        resp = None
        last_error = None
        
        for model_name in models_to_try:
            current_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_api_key}"
            try:
                # 7s timeout per attempt to stay within Vercel's 10s function limit
                temp_resp = session_req.post(current_url, json=payload, headers=headers, timeout=7)
                
                # If we get a successful response or a safety/empty response, we're done
                if temp_resp.status_code == 200:
                    resp = temp_resp
                    break
                
                # If it's a 429 (Quota), we might want to try another model, but often quota is per project
                # However, sometimes different models have different quotas
                if temp_resp.status_code == 429:
                    last_error = "QUOTA_EXCEEDED"
                    continue # Try next model
                    
                # For other errors (400, 404, 500, etc.), try the next model
                continue
                
            except Exception as e:
                print(f"Attempt with {model_name} failed: {e}")
                continue

        # If all attempts failed or returned errors
        if resp is None:
            if last_error == "QUOTA_EXCEEDED":
                return jsonify({'reply': '⏳ Free limit reach ayindi ra! Konchem wait chesi malli try cheyyi. 😊'}), 429
            return jsonify({'reply': '❌ AI service temporary ga busy undi ra. Malli try cheyyi! 😅'}), 503

        result = resp.json()
        
        # Check for error in JSON even if status was 200 (rare but possible)
        if 'error' in result:
            return jsonify({'reply': '❌ AI service lo chinna error vachindi. Malli try cheyyi ra!'}), 502

        # Extract text safely
        if 'candidates' in result and len(result['candidates']) > 0:
            candidate = result['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content'] and len(candidate['content']['parts']) > 0:
                reply = candidate['content']['parts'][0].get('text', '')
                if not reply:
                    reply = "Hmm ra, AI response empty vachindi. Malli try cheyyi! 😅"
            else:
                # Check for safety filter or other reasons
                finish_reason = candidate.get('finishReason', 'UNKNOWN')
                if finish_reason == 'SAFETY':
                    reply = "Arey, ee question konchem sensitive ga undi ra. General coding doubts adugu, manam kalisi nerchukundam! 😊"
                else:
                    reply = "Hmm, response structure lo chinna issue vachindi. Malli adugu ra! 😅"
        else:
            reply = "Hmm ra, AI response empty vachindi. Malli try cheyyi! 😅"
        
        return jsonify({'reply': reply})
            
    except requests.exceptions.Timeout:
        return jsonify({'reply': '⏳ The AI is thinking too long. Please try again!'}), 504
    except Exception as e:
        print(f"Chat error: {e}")
        return jsonify({'reply': f'❌ Something went wrong. Please try again later.'}), 500


@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, 'robots.txt')

@app.route('/llms.txt')
def llms_txt():
    return send_from_directory(app.static_folder, 'llms.txt')

@app.route('/sitemap.xml')
def sitemap():
    base_url = "https://codenative.co.in"
    static_pages = [
        "/", "/roadmap.html", "/signin.html", "/videos.html", "/compiler.html",
        "/privacy-policy.html", "/terms-conditions.html", "/cookie-policy.html"
    ]
    
    conn = get_db_connection()
    topics = execute_query(conn, "SELECT language, topic_slug FROM content").fetchall()
    release_db_connection(conn)
    
    pages = []
    for page in static_pages:
        pages.append(f"{base_url}{page}")
    
    # Add tutorial topics
    for topic in topics:
        lang = topic['language']
        slug = topic['topic_slug']
        # Map internal lang codes to page filenames if needed
        filename = lang if lang.endswith('.html') else f"{lang}.html"
        pages.append(f"{base_url}/{filename}#{slug}")

    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for page in pages:
        sitemap_xml += f"  <url><loc>{page}</loc><changefreq>weekly</changefreq></url>\n"
    sitemap_xml += "</urlset>"
    
    return Response(sitemap_xml, mimetype='application/xml')

# Initialize database on startup
init_db()

if __name__ == "__main__":
    app.run(debug=True)
