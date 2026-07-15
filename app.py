
# ─────────────────────────────────────────────────────────────────────────────
#  CodeNative  —  FastAPI Backend
#  Migrated from Flask.  All routes, logic and DB code preserved.
# ─────────────────────────────────────────────────────────────────────────────
import os
import time
import sqlite3
import csv
import io
import hashlib          # kept for migrating existing SHA-256 hashed passwords
import random
import tempfile
import smtplib
import base64
import threading
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

import psycopg2
import psycopg2.extras
import requests as http_requests

from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.security import generate_password_hash, check_password_hash

from fastapi import (
    FastAPI, Request, Response, Depends, HTTPException,
    UploadFile, File, Form
)
from fastapi.responses import (
    HTMLResponse, RedirectResponse, StreamingResponse
)
from starlette.responses import JSONResponse as _StarletteJSONResponse
import json as _json
import datetime as _dt_module
from decimal import Decimal as _Decimal


class _DateAwareEncoder(_json.JSONEncoder):
    """JSON encoder that handles date/datetime and Decimal from PostgreSQL."""
    def default(self, obj):
        if isinstance(obj, (_dt_module.datetime, _dt_module.date)):
            return obj.isoformat()
        if isinstance(obj, _Decimal):
            return float(obj)
        return super().default(obj)


class JSONResponse(_StarletteJSONResponse):
    """Drop-in JSONResponse that never crashes on PostgreSQL date/datetime columns."""
    def render(self, content) -> bytes:
        return _json.dumps(
            content,
            cls=_DateAwareEncoder,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

# Google OAuth imports
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

load_dotenv()

# ─── App setup ───────────────────────────────────────────────────────────────
app = FastAPI()

SECRET_KEY = os.environ.get('SECRET_KEY', 'codenative_fallback_secret_key_secure_12345')
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=60 * 60 * 24 * 30,  # 30 days
    https_only=False,
)

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
# Make ga_id available globally in every template
templates.env.globals["ga_id"] = "G-YHH2J3PXVZ"

# ── Flask-compatible url_for shim ─────────────────────────────────────────────
# Templates use url_for('static', filename='...') which is Flask syntax.
# Starlette injects its own url_for into the template context via request,
# which raises NoMatchFound for 'static' + filename param.
# We override it globally AND per-request in _render().
def _flask_url_for(name: str, **path_params) -> str:
    if name == "static":
        filename = path_params.get("filename", "")
        return f"/static/{filename}"
    return f"/{name}"

templates.env.globals["url_for"] = _flask_url_for


# Allow HTTP for OAuth in development
if not os.environ.get('DATABASE_URL') or '127.0.0.1' in os.environ.get('GOOGLE_REDIRECT_URI', ''):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# ─── Database configuration ──────────────────────────────────────────────────
DATABASE = 'users.db'


def get_db_connection():
    """Open one fresh connection per request."""
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

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def release_db_connection(conn):
    if conn:
        try:
            conn.close()
        except Exception:
            pass


def execute_query(conn, query, params=None):
    """Abstraction layer to handle different SQL placeholders (?, %s)"""
    is_pg = hasattr(conn, 'cursor_factory')
    if is_pg:
        query = query.replace('?', '%s')
        if 'INSERT OR REPLACE' in query:
            query = query.replace('INSERT OR REPLACE INTO content', 'INSERT INTO content')
            query += (
                ' ON CONFLICT (language, topic_slug) DO UPDATE SET '
                'topic_title = EXCLUDED.topic_title, content_html = EXCLUDED.content_html, '
                'quiz_json = EXCLUDED.quiz_json, custom_css = EXCLUDED.custom_css, '
                'custom_js = EXCLUDED.custom_js, order_index = EXCLUDED.order_index'
            )

    cursor = conn.cursor()
    cursor.execute(query, params or ())
    return cursor


def hash_password(password):
    return generate_password_hash(password, method='pbkdf2:sha256')


def check_and_verify_referral(referred_user_id, conn=None):
    """
    Check if the referred user meets verification criteria:
    - Registered (inherent)
    - Started at least one course (has >=1 entries in user_progress) OR
    - Spent at least 5 minutes learning (study_minutes >= 5 in user_stats)
    If yes, mark their referral record as 'Verified' and update referrer's verified_referrals.
    """
    close_conn = False
    if not conn:
        conn = get_db_connection()
        close_conn = True
    try:
        # Check user's referral status in referrals table
        ref_record = execute_query(conn, "SELECT referrer_id, status FROM referrals WHERE referred_user_id = ?", (referred_user_id,)).fetchone()
        if not ref_record or ref_record['status'] == 'Verified':
            if close_conn:
                release_db_connection(conn)
            return False

        referrer_id = ref_record['referrer_id']

        # Check progress
        progress_count = execute_query(conn, "SELECT COUNT(*) as count FROM user_progress WHERE user_id = ?", (referred_user_id,)).fetchone()
        progress_count = progress_count['count'] if progress_count else 0

        # Check study minutes
        stats = execute_query(conn, "SELECT study_minutes FROM user_stats WHERE user_id = ?", (referred_user_id,)).fetchone()
        study_minutes = stats['study_minutes'] if stats else 0

        if progress_count >= 1 or study_minutes >= 5:
            # Verify referral
            execute_query(conn, "UPDATE referrals SET status = 'Verified', verified_at = ? WHERE referred_user_id = ?", (datetime.now(), referred_user_id))
            execute_query(conn, "UPDATE users SET referral_verified = 1 WHERE id = ?", (referred_user_id,))
            
            # Recalculate referrer's count
            verified_count = execute_query(conn, "SELECT COUNT(*) as count FROM referrals WHERE referrer_id = ? AND status = 'Verified'", (referrer_id,)).fetchone()
            count = verified_count['count'] if verified_count else 0
            
            execute_query(conn, "UPDATE users SET verified_referrals = ? WHERE id = ?", (count, referrer_id))
            conn.commit()
            print(f"[Referral] Verified referral: user {referred_user_id} referred by {referrer_id}")
            return True
    except Exception as e:
        print(f"[Referral] Error verifying referral: {e}")
    finally:
        if close_conn:
            release_db_connection(conn)


def refresh_all_referrals_for_user(referrer_id, conn=None):
    """
    Check and update all pending referrals for the given referrer.
    """
    close_conn = False
    if not conn:
        conn = get_db_connection()
        close_conn = True
    try:
        pending_users = execute_query(conn, "SELECT referred_user_id FROM referrals WHERE referrer_id = ? AND status = 'Pending'", (referrer_id,)).fetchall()
        for pu in pending_users:
            check_and_verify_referral(pu['referred_user_id'], conn)
            
        # Re-sync referrer's count
        verified_count = execute_query(conn, "SELECT COUNT(*) as count FROM referrals WHERE referrer_id = ? AND status = 'Verified'", (referrer_id,)).fetchone()
        count = verified_count['count'] if verified_count else 0
        execute_query(conn, "UPDATE users SET verified_referrals = ? WHERE id = ?", (count, referrer_id))
        conn.commit()
    except Exception as e:
        print(f"[Referral] Error refreshing referrals: {e}")
    finally:
        if close_conn:
            release_db_connection(conn)


# ─── Database initialisation ─────────────────────────────────────────────────
def init_db():
    """Initialize the database with users and content tables"""
    conn = get_db_connection()
    is_pg = hasattr(conn, 'cursor_factory')

    users_sql = '''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            mobile TEXT,
            password TEXT,
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
            password TEXT,
            google_id TEXT UNIQUE,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    '''

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

    progress_sql = '''
        CREATE TABLE IF NOT EXISTS user_progress (
            user_id INTEGER,
            language TEXT,
            topic_slug TEXT,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, language, topic_slug)
        )
    '''

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

    careers_sql = '''
        CREATE TABLE IF NOT EXISTS careers (
            id SERIAL PRIMARY KEY,
            type TEXT NOT NULL,
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
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            company TEXT,
            location TEXT,
            description TEXT,
            link TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    '''

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

    referrals_sql = '''
        CREATE TABLE IF NOT EXISTS referrals (
            id SERIAL PRIMARY KEY,
            referrer_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            referred_user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            verified_at TIMESTAMP
        )
    ''' if is_pg else '''
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            referred_user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            verified_at TIMESTAMP
        )
    '''

    if is_pg:
        cursor = conn.cursor()
        for sql in [users_sql, content_sql, stats_sql, activity_sql, progress_sql,
                    feedback_sql, careers_sql, career_applications_sql, referrals_sql]:
            cursor.execute(sql)

        for idx_sql in [
            "CREATE INDEX IF NOT EXISTS idx_user_progress_language ON user_progress(language)",
            "CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON feedback(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_career_applications_career_id ON career_applications(career_id)",
            "CREATE INDEX IF NOT EXISTS idx_referrals_referrer_id ON referrals(referrer_id)",
        ]:
            cursor.execute(idx_sql)

        def _pg_add_col(table, col, col_type):
            cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table}' AND column_name='{col}'")
            if not cursor.fetchone():
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")

        for col, t in [('is_admin','INTEGER DEFAULT 0'),('mobile','TEXT'),('otp_code','TEXT'),
                       ('otp_expiry','TIMESTAMP'),('google_id','TEXT UNIQUE'),
                       ('referral_code','TEXT UNIQUE'),('referred_by','INTEGER'),
                       ('verified_referrals','INTEGER DEFAULT 0'),('referral_verified','INTEGER DEFAULT 0')]:
            _pg_add_col('users', col, t)
        for col, t in [('mobile','TEXT'),('college','TEXT')]:
            _pg_add_col('feedback', col, t)
        for col, t in [('quiz_json','TEXT'),('custom_css','TEXT'),('custom_js','TEXT')]:
            _pg_add_col('content', col, t)
        for col, t in [('whatsapp','TEXT'),('college','TEXT'),('passout_year','TEXT')]:
            _pg_add_col('career_applications', col, t)
        conn.commit()
    else:
        for sql in [users_sql, content_sql, stats_sql, activity_sql, progress_sql,
                    feedback_sql, careers_sql, career_applications_sql, referrals_sql]:
            conn.execute(sql)
        for idx_sql in [
            "CREATE INDEX IF NOT EXISTS idx_user_progress_language ON user_progress(language)",
            "CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON feedback(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_career_applications_career_id ON career_applications(career_id)",
            "CREATE INDEX IF NOT EXISTS idx_referrals_referrer_id ON referrals(referrer_id)",
        ]:
            conn.execute(idx_sql)

        cur = conn.execute("PRAGMA table_info(users)")
        cols = [c[1] for c in cur.fetchall()]
        for col, t in [('is_admin','INTEGER DEFAULT 0'),('mobile','TEXT'),('otp_code','TEXT'),
                       ('otp_expiry','TIMESTAMP'),('google_id','TEXT'),
                       ('referral_code','TEXT'),('referred_by','INTEGER'),
                       ('verified_referrals','INTEGER DEFAULT 0'),('referral_verified','INTEGER DEFAULT 0')]:
            if col not in cols:
                conn.execute(f"ALTER TABLE users ADD COLUMN {col} {t}")

        cur = conn.execute("PRAGMA table_info(content)")
        cols = [c[1] for c in cur.fetchall()]
        for col in ['custom_css','custom_js','quiz_json']:
            if col not in cols:
                conn.execute(f"ALTER TABLE content ADD COLUMN {col} TEXT")

        cur = conn.execute("PRAGMA table_info(career_applications)")
        cols = [c[1] for c in cur.fetchall()]
        for col in ['whatsapp','college','passout_year']:
            if col not in cols:
                conn.execute(f"ALTER TABLE career_applications ADD COLUMN {col} TEXT")
        conn.commit()

    # Sync existing referred users into the referrals table if not already present
    try:
        if is_pg:
            cursor = conn.cursor()
            cursor.execute("SELECT id, referred_by, referral_verified, created_at FROM users WHERE referred_by IS NOT NULL")
            referred_users = cursor.fetchall()
            for ru in referred_users:
                cursor.execute("SELECT id FROM referrals WHERE referred_user_id = %s", (ru['id'],))
                if not cursor.fetchone():
                    status = 'Verified' if ru['referral_verified'] else 'Pending'
                    verified_at = ru['created_at'] if ru['referral_verified'] else None
                    cursor.execute(
                        "INSERT INTO referrals (referrer_id, referred_user_id, status, created_at, verified_at) VALUES (%s, %s, %s, %s, %s)",
                        (ru['referred_by'], ru['id'], status, ru['created_at'], verified_at)
                    )
            conn.commit()
        else:
            cursor = conn.execute("SELECT id, referred_by, referral_verified, created_at FROM users WHERE referred_by IS NOT NULL")
            referred_users = cursor.fetchall()
            for ru in referred_users:
                check = conn.execute("SELECT id FROM referrals WHERE referred_user_id = ?", (ru['id'],)).fetchone()
                if not check:
                    status = 'Verified' if ru['referral_verified'] else 'Pending'
                    verified_at = ru['created_at'] if ru['referral_verified'] else None
                    conn.execute(
                        "INSERT INTO referrals (referrer_id, referred_user_id, status, created_at, verified_at) VALUES (?, ?, ?, ?, ?)",
                        (ru['referred_by'], ru['id'], status, ru['created_at'], verified_at)
                    )
            conn.commit()
    except Exception as e:
        print(f"Error syncing referrals in app: {e}")

    release_db_connection(conn)
    print("Database initialized successfully!")


# ─── In-memory rate limiter ───────────────────────────────────────────────────
_rate_store: dict = defaultdict(list)
_rate_lock = threading.Lock()


def _check_rate(key: str, limit: int, window_seconds: int) -> bool:
    now = time.time()
    with _rate_lock:
        timestamps = _rate_store[key]
        timestamps[:] = [t for t in timestamps if now - t < window_seconds]
        if len(timestamps) >= limit:
            return False
        timestamps.append(now)
        return True


def rate_limit(limit: int, window_seconds: int):
    def dependency(request: Request):
        ip = request.client.host if request.client else "unknown"
        key = f"{request.url.path}:{ip}"
        if not _check_rate(key, limit, window_seconds):
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please wait a moment and try again."
            )
    return Depends(dependency)


rl_5_per_hour  = rate_limit(5, 3600)
rl_3_per_hour  = rate_limit(3, 3600)
rl_10_per_min  = rate_limit(10, 60)
rl_20_per_min  = rate_limit(20, 60)


# ─── JSON-safe date serializer ───────────────────────────────────────────────
import datetime as _dt

def _jsonify_dates(obj):
    """Recursively convert date/datetime objects to ISO strings so Jinja2
    tojson filter never chokes on PostgreSQL date columns."""
    if isinstance(obj, list):
        return [_jsonify_dates(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _jsonify_dates(v) for k, v in obj.items()}
    if isinstance(obj, (_dt.datetime, _dt.date)):
        return obj.isoformat()
    return obj


# ─── Template/redirect helpers ───────────────────────────────────────────────
def _render(request: Request, template_name: str, context: dict = None):
    ctx = context or {}
    ctx["request"] = request
    ctx["session"] = request.session
    # Override url_for per-request so Starlette's built-in doesn't shadow our shim
    ctx["url_for"] = _flask_url_for
    return templates.TemplateResponse(request=request, name=template_name, context=ctx)


def _redirect(url: str, status_code: int = 302) -> RedirectResponse:
    return RedirectResponse(url=url, status_code=status_code)


# ─── Override 302 / 429 HTTPExceptions ───────────────────────────────────────
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 302:
        return RedirectResponse(url=exc.detail, status_code=302)
    if exc.status_code == 429:
        return JSONResponse(status_code=429, content={"error": exc.detail, "status": 429})
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


# ─── Email helper ────────────────────────────────────────────────────────────
def send_email(to_email: str, subject: str, body: str) -> bool:
    smtp_server   = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port     = int(os.environ.get('SMTP_PORT', 587))
    smtp_user     = os.environ.get('SMTP_USER')
    smtp_password = os.environ.get('SMTP_PASSWORD')

    if not smtp_user or not smtp_password:
        print("ERROR: SMTP credentials not set in .env")
        return False

    try:
        msg = MIMEMultipart()
        sender_name = os.environ.get('SENDER_NAME', 'Code Native')
        msg['From']    = f"{sender_name} <{smtp_user}>"
        msg['To']      = to_email
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


# ─── User activity helper ────────────────────────────────────────────────────
def update_user_activity(user_id: int, is_practice: bool = False):
    conn = get_db_connection()
    today_str = datetime.today().strftime('%Y-%m-%d')
    try:
        act = execute_query(conn,
            "SELECT practice_count FROM user_activity WHERE user_id = ? AND activity_date = ?",
            (user_id, today_str)).fetchone()
        practice_inc = 1 if is_practice else 0
        if act:
            execute_query(conn,
                "UPDATE user_activity SET practice_count = practice_count + ? WHERE user_id = ? AND activity_date = ?",
                (practice_inc, user_id, today_str))
        else:
            execute_query(conn,
                "INSERT INTO user_activity (user_id, activity_date, practice_count) VALUES (?, ?, ?)",
                (user_id, today_str, practice_inc))

        stats = execute_query(conn, "SELECT * FROM user_stats WHERE user_id = ?", (user_id,)).fetchone()
        study_inc = 1 if not is_practice else 0

        if not stats:
            execute_query(conn,
                "INSERT INTO user_stats (user_id, study_minutes, certificates, current_streak, max_streak, last_active_date) VALUES (?, ?, 0, 1, 1, ?)",
                (user_id, study_inc, today_str))
        else:
            last_date = stats['last_active_date']
            if isinstance(last_date, str):
                try:
                    last_date = datetime.strptime(last_date.split(' ')[0], '%Y-%m-%d').date()
                except Exception:
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

            execute_query(conn,
                "UPDATE user_stats SET study_minutes = study_minutes + ?, current_streak = ?, max_streak = ?, last_active_date = ? WHERE user_id = ?",
                (study_inc, new_streak, new_max, today_str, user_id))

        check_and_verify_referral(user_id, conn)
        conn.commit()
    except Exception as e:
        print("Error tracking activity:", e)
    finally:
        release_db_connection(conn)


# ─── Google OAuth config ──────────────────────────────────────────────────────
GOOGLE_CLIENT_ID     = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI  = os.environ.get("GOOGLE_REDIRECT_URI", "http://127.0.0.1:8000/login/google/callback")


# ══════════════════════════════════════════════════════════════════════════════
#  ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.get('/robots.txt')
async def robots(request: Request):
    path = os.path.join("static", "robots.txt")
    with open(path, 'r') as f:
        content = f.read()
    return Response(content=content, media_type="text/plain")


@app.get('/llms.txt')
async def llms_txt(request: Request):
    path = os.path.join("static", "llms.txt")
    with open(path, 'r') as f:
        content = f.read()
    return Response(content=content, media_type="text/plain")


@app.get('/sitemap.xml')
async def sitemap(request: Request):
    base_url = "https://codenative.co.in"
    static_pages = [
        "/", "/roadmap.html", "/signin.html", "/videos.html", "/compiler.html",
        "/privacy-policy.html", "/terms-conditions.html", "/cookie-policy.html"
    ]
    conn = get_db_connection()
    topics = execute_query(conn, "SELECT language, topic_slug FROM content").fetchall()
    release_db_connection(conn)

    pages = [f"{base_url}{p}" for p in static_pages]
    for topic in topics:
        lang = topic['language']
        slug = topic['topic_slug']
        filename = lang if lang.endswith('.html') else f"{lang}.html"
        pages.append(f"{base_url}/{filename}#{slug}")

    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for page in pages:
        sitemap_xml += f"  <url><loc>{page}</loc><changefreq>weekly</changefreq></url>\n"
    sitemap_xml += "</urlset>"
    return Response(content=sitemap_xml, media_type="application/xml")


# ─── Authentication Routes ───────────────────────────────────────────────────
@app.get("/signin.html", response_class=HTMLResponse)
async def signin_page(request: Request):
    return _render(request, "signin.html")


@app.post("/signup")
async def signup(request: Request, _rl=rl_5_per_hour):
    try:
        data     = await request.json()
        name     = data.get('name')
        email    = data.get('email')
        mobile   = data.get('mobile')
        password = data.get('password')
        ref_code = data.get('ref')

        if not name or not email or not password:
            return JSONResponse({"message": "All fields are required"}, status_code=400)

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        conn = get_db_connection()
        referred_by_id = None
        if ref_code:
            try:
                # Basic validation: check code starts with CN
                if ref_code.startswith("CN"):
                    ref_user = execute_query(conn, "SELECT id, email FROM users WHERE referral_code = ?", (ref_code,)).fetchone()
                    if ref_user:
                        # Prevent self-referrals
                        if ref_user['email'].lower() != email.lower():
                            referred_by_id = ref_user['id']
            except Exception as e:
                print(f"[Referral] Error parsing ref_code: {e}")

        try:
            is_pg = hasattr(conn, 'cursor_factory')
            cursor = conn.cursor()
            if is_pg:
                cursor.execute(
                    'INSERT INTO users (name, email, mobile, password, referred_by) VALUES (%s, %s, %s, %s, %s) RETURNING id',
                    (name, email, mobile, hashed_password, referred_by_id)
                )
                new_user_id = cursor.fetchone()['id']
            else:
                cursor.execute(
                    'INSERT INTO users (name, email, mobile, password, referred_by) VALUES (?, ?, ?, ?, ?)',
                    (name, email, mobile, hashed_password, referred_by_id)
                )
                new_user_id = cursor.lastrowid
            
            # Generate and save referral code
            new_ref_code = f"CN{10000 + new_user_id}"
            cursor.execute(
                "UPDATE users SET referral_code = ? WHERE id = ?".replace('?', '%s' if is_pg else '?'),
                (new_ref_code, new_user_id)
            )
            
            # Record referral history if referred by someone
            if referred_by_id:
                cursor.execute(
                    "INSERT INTO referrals (referrer_id, referred_user_id, status) VALUES (?, ?, 'Pending')".replace('?', '%s' if is_pg else '?'),
                    (referred_by_id, new_user_id)
                )

            conn.commit()
            release_db_connection(conn)
            return JSONResponse({"message": "Account created successfully"}, status_code=201)
        except (sqlite3.IntegrityError, psycopg2.IntegrityError):
            release_db_connection(conn)
            return JSONResponse({"message": "Email already exists"}, status_code=409)
    except Exception as e:
        return JSONResponse({"message": f"Server error: {str(e)}"}, status_code=500)


@app.post("/signin")
async def signin(request: Request, _rl=rl_10_per_min):
    try:
        data     = await request.json()
        email    = data.get('email')
        password = data.get('password')
        next_url = request.query_params.get('next', '/')

        if not email or not password:
            return JSONResponse({"message": "Email and password are required"}, status_code=400)

        conn = get_db_connection()
        user = execute_query(conn, 'SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if not user or not user['password']:
            release_db_connection(conn)
            return JSONResponse({"message": "Invalid email or password"}, status_code=401)

        stored_password = user['password']
        password_valid  = False

        old_sha256 = hashlib.sha256(password.encode()).hexdigest()
        if stored_password == old_sha256:
            password_valid = True
            new_hash = generate_password_hash(password, method='pbkdf2:sha256')
            execute_query(conn, 'UPDATE users SET password = ? WHERE email = ?', (new_hash, email))
            conn.commit()
        elif check_password_hash(stored_password, password):
            password_valid = True

        if not password_valid:
            release_db_connection(conn)
            return JSONResponse({"message": "Invalid email or password"}, status_code=401)

        user = execute_query(conn, 'SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        release_db_connection(conn)

        if user:
            if email == 'racharlamohan16@gmail.com' and not user['is_admin']:
                conn = get_db_connection()
                execute_query(conn, 'UPDATE users SET is_admin = 1 WHERE id = ?', (user['id'],))
                conn.commit()
                release_db_connection(conn)
                user = dict(user)
                user['is_admin'] = 1

            request.session['user_id']    = user['id']
            request.session['user_name']  = user['name']
            request.session['user_email'] = user['email']
            request.session['is_admin']   = bool(user['is_admin'])

            admin_next = "/admin" if user['is_admin'] else next_url
            return JSONResponse({
                "message": "Sign in successful",
                "user": {"name": user['name'], "email": user['email'], "is_admin": bool(user['is_admin'])},
                "next": admin_next
            }, status_code=200)
        else:
            return JSONResponse({"message": "Invalid email or password"}, status_code=401)
    except Exception as e:
        return JSONResponse({"message": f"Server error: {str(e)}"}, status_code=500)


@app.post("/forgot-password")
async def forgot_password(request: Request, _rl=rl_3_per_hour):
    data  = await request.json()
    email = data.get("email")
    conn  = get_db_connection()
    user  = execute_query(conn, "SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if not user:
        release_db_connection(conn)
        return JSONResponse({"message": "Email not found"}, status_code=404)

    otp    = str(random.randint(100000, 999999))
    expiry = datetime.now() + timedelta(minutes=10)
    execute_query(conn, "UPDATE users SET otp_code = ?, otp_expiry = ? WHERE email = ?", (otp, expiry, email))
    conn.commit()
    release_db_connection(conn)

    subject = "Your Code Native Password Reset OTP"
    body = (f"Hello,\n\nYour OTP for password reset is: {otp}\n\n"
            "This code will expire in 10 minutes.\n\n"
            "If you did not request this, please ignore this email.")
    if send_email(email, subject, body):
        return JSONResponse({"message": "OTP sent successfully to your email."})
    return JSONResponse({"message": "Failed to send email. Please check SMTP settings."}, status_code=500)


@app.post("/verify-otp")
async def verify_otp(request: Request):
    data  = await request.json()
    email = data.get("email")
    otp   = data.get("otp")
    conn  = get_db_connection()
    user  = execute_query(conn, "SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if not user:
        release_db_connection(conn)
        return JSONResponse({"message": "User not found"}, status_code=404)
    db_otp    = user['otp_code']
    db_expiry = user['otp_expiry']
    if isinstance(db_expiry, str):
        try:
            db_expiry = datetime.strptime(db_expiry.split('.')[0], '%Y-%m-%d %H:%M:%S')
        except Exception:
            db_expiry = datetime.strptime(db_expiry, '%Y-%m-%dT%H:%M:%S')
    release_db_connection(conn)
    if db_otp == otp and datetime.now() < db_expiry:
        return JSONResponse({"message": "OTP verified successfully"})
    return JSONResponse({"message": "Invalid or expired OTP"}, status_code=400)


@app.post("/reset-password")
async def reset_password(request: Request, _rl=rl_3_per_hour):
    data         = await request.json()
    email        = data.get("email")
    otp          = data.get("otp")
    new_password = data.get("new_password")
    conn = get_db_connection()
    user = execute_query(conn, "SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if not user:
        release_db_connection(conn)
        return JSONResponse({"message": "User not found"}, status_code=404)
    db_otp    = user['otp_code']
    db_expiry = user['otp_expiry']
    if isinstance(db_expiry, str):
        try:
            db_expiry = datetime.strptime(db_expiry.split('.')[0], '%Y-%m-%d %H:%M:%S')
        except Exception:
            db_expiry = datetime.strptime(db_expiry, '%Y-%m-%dT%H:%M:%S')
    if db_otp == otp and datetime.now() < db_expiry:
        hashed_pw = generate_password_hash(new_password, method='pbkdf2:sha256')
        execute_query(conn, "UPDATE users SET password = ?, otp_code = NULL, otp_expiry = NULL WHERE email = ?",
                      (hashed_pw, email))
        conn.commit()
        release_db_connection(conn)
        return JSONResponse({"message": "Password reset successfully!"})
    release_db_connection(conn)
    return JSONResponse({"message": "Session expired or invalid. Please try again."}, status_code=400)


# ─── Google OAuth ─────────────────────────────────────────────────────────────
@app.get("/login/google")
async def login_google(request: Request):
    flow = Flow.from_client_config(
        {"web": {"client_id": GOOGLE_CLIENT_ID, "client_secret": GOOGLE_CLIENT_SECRET,
                 "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                 "token_uri": "https://oauth2.googleapis.com/token"}},
        scopes=["https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/userinfo.email", "openid"],
        redirect_uri=GOOGLE_REDIRECT_URI
    )
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    request.session['oauth_state']   = state
    request.session['code_verifier'] = flow.code_verifier
    request.session['oauth_next']    = request.query_params.get('next', '')
    ref = request.query_params.get('ref')
    if ref:
        request.session['oauth_ref'] = ref
    return _redirect(authorization_url)


@app.get("/login/google/callback")
async def google_callback(request: Request):
    state = request.session.get('oauth_state')
    flow = Flow.from_client_config(
        {"web": {"client_id": GOOGLE_CLIENT_ID, "client_secret": GOOGLE_CLIENT_SECRET,
                 "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                 "token_uri": "https://oauth2.googleapis.com/token"}},
        scopes=["https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/userinfo.email", "openid"],
        state=state,
        redirect_uri=GOOGLE_REDIRECT_URI
    )
    flow.code_verifier = request.session.get('code_verifier')
    try:
        flow.fetch_token(authorization_response=str(request.url))
    except Exception as e:
        print(f"Error fetching token: {e}")
        return _redirect("/signin.html?error=oauth_failed")

    credentials = flow.credentials
    try:
        id_info = id_token.verify_oauth2_token(
            credentials.id_token, google_requests.Request(), GOOGLE_CLIENT_ID)
    except ValueError:
        return _redirect("/signin.html?error=invalid_token")

    google_id = id_info.get('sub')
    email     = id_info.get('email')
    name      = id_info.get('name')
    if not email:
        return _redirect("/signin.html?error=no_email")

    conn = get_db_connection()
    user = execute_query(conn, "SELECT * FROM users WHERE google_id = ?", (google_id,)).fetchone()
    if not user:
        user = execute_query(conn, "SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user:
            execute_query(conn, "UPDATE users SET google_id = ? WHERE id = ?", (google_id, user['id']))
            conn.commit()
        else:
            ref_code = request.session.pop('oauth_ref', None)
            referred_by_id = None
            if ref_code:
                try:
                    ref_user = execute_query(conn, "SELECT id, email FROM users WHERE referral_code = ?", (ref_code,)).fetchone()
                    if ref_user and ref_user['email'].lower() != email.lower():
                        referred_by_id = ref_user['id']
                except Exception as e:
                    print(f"[Referral] Google callback ref lookup error: {e}")
            
            is_pg = hasattr(conn, 'cursor_factory')
            cursor = conn.cursor()
            if is_pg:
                cursor.execute(
                    "INSERT INTO users (name, email, google_id, referred_by) VALUES (%s, %s, %s, %s) RETURNING id",
                    (name, email, google_id, referred_by_id)
                )
                new_user_id = cursor.fetchone()['id']
            else:
                cursor.execute(
                    "INSERT INTO users (name, email, google_id, referred_by) VALUES (?, ?, ?, ?)",
                    (name, email, google_id, referred_by_id)
                )
                new_user_id = cursor.lastrowid
                
            new_ref_code = f"CN{10000 + new_user_id}"
            cursor.execute(
                "UPDATE users SET referral_code = ? WHERE id = ?".replace('?', '%s' if is_pg else '?'),
                (new_ref_code, new_user_id)
            )
            
            if referred_by_id:
                cursor.execute(
                    "INSERT INTO referrals (referrer_id, referred_user_id, status) VALUES (?, ?, 'Pending')".replace('?', '%s' if is_pg else '?'),
                    (referred_by_id, new_user_id)
                )
                
            conn.commit()
            
            user = execute_query(conn, "SELECT * FROM users WHERE id = ?", (new_user_id,)).fetchone()
    release_db_connection(conn)

    request.session['user_id']    = user['id']
    request.session['user_name']  = user['name']
    request.session['user_email'] = user['email']
    request.session['is_admin']   = bool(user['is_admin'])

    next_url = request.session.pop('oauth_next', None)
    if next_url and next_url.startswith('http') and 'codenative' in next_url:
        return _redirect(next_url)
    elif next_url and next_url.startswith('/'):
        return _redirect(next_url)
    return _redirect("/admin" if user['is_admin'] else "/dashboard")


@app.get("/logout")
async def logout(request: Request):
    user_name = request.session.get('user_name', 'User')
    request.session.clear()
    request.session['logout_message'] = f"Goodbye {user_name}! You have been logged out successfully. See you soon! 👋"
    return _redirect("/")


@app.get("/register")
async def register_page_redirect(request: Request):
    ref = request.query_params.get('ref')
    if ref:
        return _redirect(f"/signin.html?ref={ref}")
    return _redirect("/signin.html")


# ─── Dashboard ────────────────────────────────────────────────────────────────
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if 'user_id' not in request.session:
        return _redirect("/signin.html")

    user_id = request.session.get('user_id')
    conn = get_db_connection()
    check_and_verify_referral(user_id, conn)
    stats = execute_query(conn, "SELECT * FROM user_stats WHERE user_id = ?", (user_id,)).fetchone()
    stats_existed = stats is not None
    if stats:
        stats = dict(stats)
        stats['study_hours'] = round(stats['study_minutes'] / 60, 1)
    else:
        stats = {'study_hours': 0.0, 'study_minutes': 0, 'certificates': 0, 'current_streak': 0, 'max_streak': 0}

    activities = execute_query(conn,
        "SELECT activity_date, practice_count FROM user_activity WHERE user_id = ? ORDER BY activity_date ASC",
        (user_id,)).fetchall()

    courses = [
        {'id': 'python', 'name': 'Python Core',       'icon': 'fab fa-python',    'bg': 'python-bg', 'header_bg': '#3776ab', 'link': '/python.html'},
        {'id': 'c',      'name': 'C Architecture',    'icon': 'fas fa-code-branch','bg': 'c-bg',      'header_bg': '#00599c', 'link': '/c.html'},
        {'id': 'java',   'name': 'Java Masterclass',  'icon': 'fab fa-java',      'bg': 'java-bg',   'header_bg': '#ed8b00', 'link': '/java.html'},
        {'id': 'web',    'name': 'Web Development',   'icon': 'fab fa-html5',     'bg': 'web-bg',    'header_bg': '#e34f26', 'link': '/web.html'},
        {'id': 'js',     'name': 'JavaScript Expert', 'icon': 'fab fa-js',        'bg': 'js-bg',     'header_bg': '#f7df1e', 'link': '/js.html'},
    ]

    total_topics_map     = {row['language']: row['count'] for row in execute_query(conn, "SELECT language, COUNT(*) as count FROM content GROUP BY language").fetchall()}
    completed_topics_map = {row['language']: row['count'] for row in execute_query(conn, "SELECT language, COUNT(*) as count FROM user_progress WHERE user_id = ? GROUP BY language", (user_id,)).fetchall()}
    last_topic_map       = {row['language']: row['topic_title'] for row in execute_query(conn, """
        WITH ranked_progress AS (
            SELECT p.language, c.topic_title,
                   ROW_NUMBER() OVER (PARTITION BY p.language ORDER BY p.completed_at DESC) as rn
            FROM user_progress p JOIN content c ON p.topic_slug = c.topic_slug AND p.language = c.language
            WHERE p.user_id = ?
        )
        SELECT language, topic_title FROM ranked_progress WHERE rn = 1
    """, (user_id,)).fetchall()}

    user_courses = []
    for course in courses:
        total = total_topics_map.get(course['id'], 0)
        if total > 0:
            done = completed_topics_map.get(course['id'], 0)
            d = course.copy()
            d['progress']   = int((done / total) * 100)
            d['last_topic'] = last_topic_map.get(course['id'], "Not started yet")
            user_courses.append(d)

    completed_certs = sum(1 for c in user_courses if c.get('progress', 0) >= 100)
    stats['certificates'] = completed_certs
    if stats_existed:
        execute_query(conn, "UPDATE user_stats SET certificates = ? WHERE user_id = ?", (completed_certs, user_id))
    else:
        execute_query(conn, "INSERT INTO user_stats (user_id, study_minutes, certificates, current_streak, max_streak) VALUES (?, 0, ?, 0, 0)", (user_id, completed_certs))
    conn.commit()
    release_db_connection(conn)

    total_practices  = sum([a['practice_count'] for a in activities])
    total_days_active = len(activities)
    today_date  = datetime.today().date()
    year_start  = today_date.replace(month=1, day=1)
    days_elapsed = max((today_date - year_start).days + 1, 1)
    consistency = min(int((total_days_active / days_elapsed) * 100), 100)

    return _render(request, "dashboard.html", dict(
        stats=_jsonify_dates(stats),
        total_practices=total_practices,
        consistency=consistency,
        activity_data=_jsonify_dates([dict(a) for a in activities]),
        user_courses=user_courses
    ))


@app.get("/referrals", response_class=HTMLResponse)
async def referrals_page_redirect(request: Request):
    return _redirect("/my-referrals")


@app.get("/my-referrals", response_class=HTMLResponse)
async def referrals_page(request: Request):
    if 'user_id' not in request.session:
        return _redirect("/signin.html")
    
    user_id = request.session.get('user_id')
    conn = get_db_connection()
    try:
        # Check and verify if there are any pending referrals for this user that can be verified now
        refresh_all_referrals_for_user(user_id, conn)

        # Get user details
        user_info = execute_query(conn, "SELECT referral_code, verified_referrals FROM users WHERE id = ?", (user_id,)).fetchone()
        
        referral_code = user_info['referral_code'] if user_info and user_info['referral_code'] else None
        if not referral_code:
            referral_code = f"CN{10000 + user_id}"
            execute_query(conn, "UPDATE users SET referral_code = ? WHERE id = ?", (referral_code, user_id))
            conn.commit()
            
        verified_referrals = user_info['verified_referrals'] if user_info and user_info['verified_referrals'] else 0
        
        # Get referred users list from referrals table
        referred_users = execute_query(conn, """
            SELECT u.name, u.email, r.status, r.created_at 
            FROM referrals r 
            JOIN users u ON r.referred_user_id = u.id 
            WHERE r.referrer_id = ? 
            ORDER BY r.created_at DESC
        """, (user_id,)).fetchall()
        
        # Mask details for privacy
        masked_users = []
        for u in referred_users:
            name_parts = u['name'].split()
            masked_name = " ".join([p[0] + "*"*max(1, len(p)-1) for p in name_parts]) if name_parts else "User"
            
            email_parts = u['email'].split('@')
            masked_email = email_parts[0][:2] + "*"*max(1, len(email_parts[0])-2) + "@" + email_parts[1] if len(email_parts) == 2 else "user@example.com"
            
            # Format date
            date_str = u['created_at']
            date_display = date_str
            if isinstance(date_str, str):
                try:
                    dt = datetime.strptime(date_str[:19], '%Y-%m-%d %H:%M:%S')
                    date_display = dt.strftime('%d %b %Y')
                except Exception:
                    pass
            elif hasattr(date_str, 'strftime'):
                date_display = date_str.strftime('%d %b %Y')
                
            masked_users.append({
                'name': masked_name,
                'email': masked_email,
                'verified': u['status'] == 'Verified',
                'date': date_display
            })

        referral_link = str(request.base_url).rstrip('/') + f"/register?ref={referral_code}"
        
        remaining = max(0, 3 - verified_referrals)
        progress_pct = min(100, int((verified_referrals / 3) * 100))
        
        # Get active courses for sidebar
        courses = [
            {'id': 'python', 'name': 'Python Core', 'icon': 'fab fa-python', 'bg': 'python-bg', 'header_bg': '#3776ab', 'link': '/python.html'},
            {'id': 'c', 'name': 'C Architecture', 'icon': 'fas fa-code-branch', 'bg': 'c-bg', 'header_bg': '#00599c', 'link': '/c.html'},
            {'id': 'java', 'name': 'Java Masterclass', 'icon': 'fab fa-java', 'bg': 'java-bg', 'header_bg': '#ed8b00', 'link': '/java.html'},
            {'id': 'web', 'name': 'Web Development', 'icon': 'fab fa-html5', 'bg': 'web-bg', 'header_bg': '#e34f26', 'link': '/web.html'},
            {'id': 'js', 'name': 'JavaScript Expert', 'icon': 'fab fa-js', 'bg': 'js-bg', 'header_bg': '#f7df1e', 'link': '/js.html'}
        ]
        
        total_topics_rows = execute_query(conn, "SELECT language, COUNT(*) as count FROM content GROUP BY language").fetchall()
        total_topics_map = {row['language']: row['count'] for row in total_topics_rows}

        completed_topics_rows = execute_query(conn, "SELECT language, COUNT(*) as count FROM user_progress WHERE user_id = ? GROUP BY language", (user_id,)).fetchall()
        completed_topics_map = {row['language']: row['count'] for row in completed_topics_rows}

        user_courses = []
        for course in courses:
            total_topics = total_topics_map.get(course['id'], 0)
            if total_topics > 0:
                completed_count = completed_topics_map.get(course['id'], 0)
                course_data = course.copy()
                course_data['progress'] = int((completed_count / total_topics) * 100)
                user_courses.append(course_data)
                
        release_db_connection(conn)
        return _render(request, "referrals.html", dict(
            referral_code=referral_code, 
            referral_link=referral_link, 
            verified_referrals=verified_referrals, 
            remaining=remaining, 
            progress_pct=progress_pct, 
            masked_users=masked_users, 
            user_courses=user_courses
        ))
    except Exception as e:
        release_db_connection(conn)
        return HTMLResponse(content=str(e), status_code=500)


@app.get("/referral-status")
async def referral_status(request: Request):
    if 'user_id' not in request.session:
        return JSONResponse({"message": "Unauthorized"}, status_code=401)
        
    user_id = request.session['user_id']
    conn = get_db_connection()
    try:
        # Auto-refresh first
        refresh_all_referrals_for_user(user_id, conn)
        
        user_info = execute_query(conn, "SELECT referral_code, verified_referrals FROM users WHERE id = ?", (user_id,)).fetchone()
        referral_code = user_info['referral_code'] if user_info and user_info['referral_code'] else f"CN{10000 + user_id}"
        verified_referrals = user_info['verified_referrals'] if user_info and user_info['verified_referrals'] else 0
        
        referred_users = execute_query(conn, """
            SELECT u.name, u.email, r.status, r.created_at 
            FROM referrals r 
            JOIN users u ON r.referred_user_id = u.id 
            WHERE r.referrer_id = ? 
            ORDER BY r.created_at DESC
        """, (user_id,)).fetchall()
        
        masked_users = []
        for u in referred_users:
            name_parts = u['name'].split()
            masked_name = " ".join([p[0] + "*"*max(1, len(p)-1) for p in name_parts]) if name_parts else "User"
            
            email_parts = u['email'].split('@')
            masked_email = email_parts[0][:2] + "*"*max(1, len(email_parts[0])-2) + "@" + email_parts[1] if len(email_parts) == 2 else "user@example.com"
            
            date_str = u['created_at']
            date_display = date_str
            if isinstance(date_str, str):
                try:
                    dt = datetime.strptime(date_str[:19], '%Y-%m-%d %H:%M:%S')
                    date_display = dt.strftime('%d %b %Y')
                except Exception:
                    pass
            elif hasattr(date_str, 'strftime'):
                date_display = date_str.strftime('%d %b %Y')
                
            masked_users.append({
                'name': masked_name,
                'email': masked_email,
                'status': u['status'],
                'date': date_display
            })
            
        referral_link = str(request.base_url).rstrip('/') + f"/register?ref={referral_code}"
        remaining = max(0, 3 - verified_referrals)
        progress_pct = min(100, int((verified_referrals / 3) * 100))
        
        release_db_connection(conn)
        return JSONResponse({
            "referral_code": referral_code,
            "referral_link": referral_link,
            "verified_referrals": verified_referrals,
            "remaining": remaining,
            "progress_pct": progress_pct,
            "referrals": masked_users
        })
    except Exception as e:
        release_db_connection(conn)
        return JSONResponse({"message": str(e)}, status_code=500)


@app.get("/certificate-status")
async def certificate_status(request: Request):
    if 'user_id' not in request.session:
        return JSONResponse({"message": "Unauthorized"}, status_code=401)
        
    user_id = request.session['user_id']
    conn = get_db_connection()
    try:
        user_info = execute_query(conn, "SELECT verified_referrals FROM users WHERE id = ?", (user_id,)).fetchone()
        verified_referrals = user_info['verified_referrals'] if user_info and user_info['verified_referrals'] else 0
        unlocked = verified_referrals >= 3
        release_db_connection(conn)
        return JSONResponse({
            "unlocked": unlocked,
            "verified_referrals": verified_referrals
        })
    except Exception as e:
        release_db_connection(conn)
        return JSONResponse({"message": str(e)}, status_code=500)


@app.post("/verify-referral")
async def verify_referral(request: Request):
    if 'user_id' not in request.session:
        return JSONResponse({"message": "Unauthorized"}, status_code=401)
        
    try:
        data = await request.json()
        referred_user_id = data.get("referred_user_id")
        if not referred_user_id:
            return JSONResponse({"message": "Missing referred_user_id"}, status_code=400)
            
        conn = get_db_connection()
        verified = check_and_verify_referral(referred_user_id, conn)
        release_db_connection(conn)
        
        return JSONResponse({
            "verified": verified,
            "message": "Referral verified successfully." if verified else "Criteria not met yet or already verified."
        })
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=500)


@app.post("/refresh-referrals")
async def refresh_referrals(request: Request):
    if 'user_id' not in request.session:
        return JSONResponse({"message": "Unauthorized"}, status_code=401)
        
    user_id = request.session['user_id']
    conn = get_db_connection()
    try:
        refresh_all_referrals_for_user(user_id, conn)
        user_info = execute_query(conn, "SELECT verified_referrals FROM users WHERE id = ?", (user_id,)).fetchone()
        verified_referrals = user_info['verified_referrals'] if user_info and user_info['verified_referrals'] else 0
        remaining = max(0, 3 - verified_referrals)
        progress_pct = min(100, int((verified_referrals / 3) * 100))
        release_db_connection(conn)
        
        return JSONResponse({
            "verified_referrals": verified_referrals,
            "remaining": remaining,
            "progress_pct": progress_pct,
            "message": "Referrals refreshed successfully."
        })
    except Exception as e:
        release_db_connection(conn)
        return JSONResponse({"message": str(e)}, status_code=500)


@app.post("/api/complete_topic")
async def complete_topic(request: Request):
    if 'user_id' not in request.session:
        return JSONResponse({"message": "Please sign in to access this page."}, status_code=401)
    try:
        data       = await request.json()
        user_id    = request.session['user_id']
        language   = data.get('language')
        topic_slug = data.get('topic_slug')
        if not language or not topic_slug:
            return JSONResponse({"message": "Missing language or slug"}, status_code=400)
        conn = get_db_connection()
        execute_query(conn, """
            INSERT INTO user_progress (user_id, language, topic_slug) VALUES (?, ?, ?)
            ON CONFLICT (user_id, language, topic_slug) DO NOTHING
        """, (user_id, language, topic_slug))
        conn.commit()
        release_db_connection(conn)
        update_user_activity(user_id, is_practice=False)
        return JSONResponse({"message": "Progress saved"}, status_code=200)
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=500)


@app.post("/api/log_study")
async def log_study(request: Request):
    if 'user_id' in request.session:
        update_user_activity(request.session['user_id'], is_practice=False)
        return JSONResponse({"status": "ok"})
    return JSONResponse({"status": "unauthorized"}, status_code=401)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    logout_msg = request.session.pop('logout_message', None)
    conn   = get_db_connection()
    counts = {l: 0 for l in ['c', 'java', 'python', 'web', 'js']}
    for row in execute_query(conn, 'SELECT language, COUNT(DISTINCT user_id) as count FROM user_progress GROUP BY language').fetchall():
        if row['language'] in counts:
            counts[row['language']] = row['count']
    release_db_connection(conn)

    reviews = [
        {"name": "Sagar",           "rating": 5, "message": "Great platform for learning coding in Telugu! Clear tutorials, interactive compiler, and covers all major languages. Highly recommended for beginners!", "role": "Independent Scholar",             "date": "2026-05-05", "initial": "S"},
        {"name": "Kanna Vemula",    "rating": 5, "message": "I like the interface and it's good platform to learn java or any other language from scratch in Telugu! 😊",                                            "role": "Sree Chaitanya Institute of Tech", "date": "2026-05-04", "initial": "K"},
        {"name": "Shivateja",       "rating": 5, "message": "Great innovative work by the CodeNative team! Wishing you all more success and growth ahead. 🔥",                                                      "role": "Independent Scholar",             "date": "2026-05-04", "initial": "S"},
        {"name": "Deva",            "rating": 5, "message": "Good Web for beginners, such good idea it is. Content is in Telugu, and the AI is next level asalu! Good Initiative.",                                "role": "Independent Scholar",             "date": "2026-05-04", "initial": "D"},
        {"name": "Srikar Manchala", "rating": 5, "message": "Very useful platform for native speakers. Everything is explained clearly in Telugu. 🚀",                                                             "role": "Bharath Institute of Higher Ed",   "date": "2026-05-04", "initial": "S"},
        {"name": "PapaRao Rapuri",  "rating": 5, "message": "CodeNative is very helpful for beginners. The step-by-step approach makes learning programming easy to follow. Highly recommended!",                  "role": "Independent Scholar",             "date": "2026-05-01", "initial": "P"},
        {"name": "Tutorial User",   "rating": 5, "message": "Oh chala useful and simply understanding. Best platform for Telugu students. 😊",                                                                     "role": "Independent Scholar",             "date": "2026-04-25", "initial": "T"},
        {"name": "Venkatesh",       "rating": 5, "message": "All good, UI is good. The platform is consistent and easy to navigate. Keep it up!",                                                                  "role": "MLRIT",                           "date": "2026-05-04", "initial": "V"},
        {"name": "Vaishu",          "rating": 5, "message": "Excellent Platform. Friendly Content and very easy to understand for beginners. 🌟",                                                                  "role": "Independent Scholar",             "date": "2026-05-04", "initial": "V"},
        {"name": "Ajay Patel Boppa","rating": 5, "message": "Such a good website to prepare for courses in Telugu easily. Concepts are explained very well.",                                                      "role": "Jyothismathi Institute of Tech",   "date": "2026-05-04", "initial": "A"},
        {"name": "Zuck",            "rating": 5, "message": "This initiative is impactful because it removes language barriers in tech education. Teaching programming in Telugu helps thousands build real skills.", "role": "CBIT",                            "date": "2026-05-04", "initial": "Z"},
        {"name": "Tutorial User",   "rating": 5, "message": "Ui is Good, Easy understanding content. Very helpful for beginners.",                                                                                 "role": "Independent Scholar",             "date": "2026-04-26", "initial": "T"},
        {"name": "Sri Harshitha K", "rating": 5, "message": "Your website is really impressive and beginner-friendly, especially because you are teaching programming in Telugu, which makes learning much easier and more comfortable for Telugu learners.", "role": "Woxsen University", "date": "2026-05-19", "initial": "S"},
    ]
    return _render(request, "index.html", dict(logout_message=logout_msg, course_counts=counts, reviews=reviews))


@app.get("/c.html",       response_class=HTMLResponse)
async def c_page(request: Request):
    if 'user_id' not in request.session: return _redirect("/signin.html")
    return _render(request, "c.html")

@app.get("/java.html",    response_class=HTMLResponse)
async def java_page(request: Request):
    if 'user_id' not in request.session: return _redirect("/signin.html")
    return _render(request, "java.html")

@app.get("/python.html",  response_class=HTMLResponse)
async def python_page(request: Request):
    if 'user_id' not in request.session: return _redirect("/signin.html")
    return _render(request, "python.html")

@app.get("/compiler.html",    response_class=HTMLResponse)
async def compiler_page(request: Request):   return _render(request, "compiler.html")

@app.get("/roadmap.html",     response_class=HTMLResponse)
async def roadmap_page(request: Request):    return _render(request, "roadmap.html")

@app.get("/start-learning.html", response_class=HTMLResponse)
async def start_learning_page(request: Request):
    conn   = get_db_connection()
    counts = {l: 0 for l in ['c', 'java', 'python', 'web', 'js']}
    for row in execute_query(conn, 'SELECT language, COUNT(DISTINCT user_id) as count FROM user_progress GROUP BY language').fetchall():
        if row['language'] in counts: counts[row['language']] = row['count']
    release_db_connection(conn)
    return _render(request, "start-learning.html", dict(course_counts=counts))

@app.get("/terms-conditions.html", response_class=HTMLResponse)
async def terms_conditions(request: Request): return _render(request, "terms-conditions.html")

@app.get("/privacy-policy.html",   response_class=HTMLResponse)
async def privacy_policy(request: Request):   return _render(request, "privacy-policy.html")

@app.get("/cookie-policy.html",    response_class=HTMLResponse)
async def cookie_policy(request: Request):    return _render(request, "cookie-policy.html")

@app.get("/web.html", response_class=HTMLResponse)
async def web_page(request: Request):
    if 'user_id' not in request.session: return _redirect("/signin.html")
    return _render(request, "web.html")

@app.get("/js.html", response_class=HTMLResponse)
async def js_page(request: Request):
    if 'user_id' not in request.session: return _redirect("/signin.html")
    return _render(request, "js.html")

@app.get("/videos.html",   response_class=HTMLResponse)
async def videos_page(request: Request):  return _render(request, "videos.html")

@app.get("/feedback.html", response_class=HTMLResponse)
async def feedback_page(request: Request): return _render(request, "feedback.html")


@app.get("/careers.html", response_class=HTMLResponse)
async def careers_page(request: Request):
    if 'user_id' not in request.session: return _redirect("/signin.html")
    conn    = get_db_connection()
    careers = execute_query(conn, "SELECT * FROM careers ORDER BY id DESC").fetchall()
    release_db_connection(conn)
    return _render(request, "careers.html", dict(careers=careers))


@app.get("/apply/{career_id}", response_class=HTMLResponse)
async def apply_page(career_id: int, request: Request):
    if 'user_id' not in request.session: return _redirect("/signin.html")
    conn   = get_db_connection()
    career = execute_query(conn, "SELECT * FROM careers WHERE id = ?", (career_id,)).fetchone()
    release_db_connection(conn)
    if not career:
        return Response(content="Career post not found", status_code=404)
    return _render(request, "apply.html", dict(
        career=career,
        user_name=request.session.get('user_name', ''),
        user_email=request.session.get('user_email', '')
    ))


@app.post("/apply_submit")
async def apply_submit(
    request: Request,
    career_id:    str                  = Form(None),
    name:         str                  = Form(None),
    email:        str                  = Form(None),
    whatsapp:     Optional[str]        = Form(None),
    college:      Optional[str]        = Form(None),
    passout_year: Optional[str]        = Form(None),
    cover_letter: Optional[str]        = Form(None),
    resume_link:  Optional[str]        = Form(None),
    resume:       Optional[UploadFile] = File(None),
):
    if 'user_id' not in request.session:
        return JSONResponse({"message": "Please sign in."}, status_code=401)
    try:
        final_resume_link = resume_link or ""
        if resume and resume.filename:
            file_bytes = await resume.read()
            encoded    = base64.b64encode(file_bytes).decode('utf-8')
            ct         = resume.content_type or 'application/octet-stream'
            final_resume_link = f"data:{ct};base64,{encoded}"
        if not final_resume_link:
            return JSONResponse({"message": "Please upload a resume file or provide a public link."}, status_code=400)
        if not career_id or not name or not email:
            return JSONResponse({"message": "Career, Name and Email are required"}, status_code=400)
        conn = get_db_connection()
        execute_query(conn, '''
            INSERT INTO career_applications (career_id, name, email, whatsapp, college, passout_year, resume_link, cover_letter)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (career_id, name, email, whatsapp, college, passout_year, final_resume_link, cover_letter))
        conn.commit()
        release_db_connection(conn)
        return JSONResponse({"message": "Application submitted successfully"}, status_code=200)
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=500)


@app.get("/uploads/resumes/{filename:path}")
async def serve_resume(filename: str, request: Request):
    conn = get_db_connection()
    if filename.isdigit():
        app_data = execute_query(conn, "SELECT resume_link FROM career_applications WHERE id = ?", (int(filename),)).fetchone()
    else:
        app_data = execute_query(conn, "SELECT resume_link FROM career_applications WHERE resume_link LIKE ?", (f"%{filename}%",)).fetchone()
    release_db_connection(conn)
    if not app_data or not app_data['resume_link']:
        return Response(content="File not found", status_code=404)
    val = app_data['resume_link']
    if val.startswith("data:"):
        try:
            header, b64_str = val.split(",", 1)
            ct = header.split(";")[0].replace("data:", "")
            return Response(content=base64.b64decode(b64_str), media_type=ct)
        except Exception as e:
            return Response(content=f"Error: {str(e)}", status_code=500)
    elif val.startswith("http://") or val.startswith("https://"):
        return _redirect(val)
    else:
        clean_name = os.path.basename(val)
        for d in [os.path.join('static', 'uploads', 'resumes'), os.path.join(tempfile.gettempdir(), 'codenative_resumes')]:
            p = os.path.join(d, clean_name)
            if os.path.exists(p):
                with open(p, 'rb') as f: return Response(content=f.read())
        return Response(content="File not found", status_code=404)


@app.post("/api/submit_feedback")
async def submit_feedback(request: Request):
    try:
        data    = await request.json()
        name    = data.get('name')
        email   = data.get('email')
        college = data.get('college')
        rating  = data.get('rating')
        message = data.get('message')
        user_id = request.session.get('user_id')
        if user_id:
            sess_name  = request.session.get('user_name')
            sess_email = request.session.get('user_email')
            if not sess_name or not sess_email:
                conn = get_db_connection()
                try:
                    row = execute_query(conn, "SELECT name, email FROM users WHERE id = ?", (user_id,)).fetchone()
                    if row: sess_name, sess_email = row['name'], row['email']
                except Exception as ex:
                    print(f"Error querying user info for feedback: {ex}")
                finally:
                    release_db_connection(conn)
            if not name or name == 'Tutorial User': name  = sess_name or name
            if not email:                           email = sess_email or email
        if not message and not rating:
            return JSONResponse({"message": "Either a rating or a message is required"}, status_code=400)
        conn = get_db_connection()
        execute_query(conn, "INSERT INTO feedback (user_id, name, email, college, rating, message) VALUES (?, ?, ?, ?, ?, ?)",
                      (user_id, name, email, college, rating, message))
        conn.commit()
        release_db_connection(conn)
        return JSONResponse({"message": "Feedback submitted successfully! Thank you. 😊"}, status_code=200)
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=500)


@app.get("/certificate/{course_id}", response_class=HTMLResponse)
async def certificate_page(course_id: str, request: Request):
    if 'user_id' not in request.session: return _redirect("/signin.html")
    user_id   = request.session.get('user_id')
    user_name = request.session.get('user_name', 'Student')
    course_name_map = {
        'python': 'Python Core Lesson Suite', 'c': 'C Architecture Suite',
        'java': 'Java Masterclass', 'web': 'Web Development Basics', 'js': 'JavaScript Expert Roadmap'
    }
    if course_id not in course_name_map:
        return Response(content="Course not found", status_code=404)
    conn = get_db_connection()
    try:
        total = execute_query(conn, "SELECT COUNT(*) as count FROM content WHERE language = ?", (course_id,)).fetchone()
        total_topics = total['count'] if total else 0
        if total_topics == 0:
            release_db_connection(conn)
            return Response(content="No content for this course.", status_code=400)
        done = execute_query(conn, "SELECT COUNT(*) as count FROM user_progress WHERE user_id = ? AND language = ?", (user_id, course_id)).fetchone()
        completed_count = done['count'] if done else 0
        progress = int((completed_count / total_topics) * 100) if total_topics > 0 else 0
        if progress < 100:
            release_db_connection(conn)
            return _redirect("/dashboard")
        last = execute_query(conn, "SELECT completed_at FROM user_progress WHERE user_id = ? AND language = ? ORDER BY completed_at DESC LIMIT 1", (user_id, course_id)).fetchone()
        formatted_date = None
        if last and last['completed_at']:
            dt_val = last['completed_at']
            if isinstance(dt_val, str):
                try:    formatted_date = datetime.strptime(dt_val[:19], '%Y-%m-%d %H:%M:%S').strftime('%B %d, %Y')
                except Exception:
                    try: formatted_date = datetime.fromisoformat(dt_val.replace('Z', '+00:00')).strftime('%B %d, %Y')
                    except Exception: formatted_date = dt_val
            else:
                formatted_date = dt_val.strftime('%B %d, %Y')
        if not formatted_date:
            formatted_date = datetime.today().strftime('%B %d, %Y')
        # Get referral details
        refresh_all_referrals_for_user(user_id, conn)
        user_info = execute_query(conn, "SELECT verified_referrals, referral_code FROM users WHERE id = ?", (user_id,)).fetchone()
        verified_referrals = user_info['verified_referrals'] if user_info and user_info['verified_referrals'] else 0
        referral_code = user_info['referral_code'] if user_info and user_info['referral_code'] else None
        if not referral_code:
            referral_code = f"CN{10000 + user_id}"
            execute_query(conn, "UPDATE users SET referral_code = ? WHERE id = ?", (referral_code, user_id))
            conn.commit()
            
        referral_link = str(request.base_url).rstrip('/') + f"/register?ref={referral_code}"
            
        release_db_connection(conn)
        return _render(request, "certificate.html", dict(
            course_id=course_id, course_name=course_name_map[course_id],
            student_name=user_name, date=formatted_date,
            verified_referrals=verified_referrals, referral_code=referral_code,
            referral_link=referral_link
        ))
    except Exception as e:
        release_db_connection(conn)
        return Response(content=str(e), status_code=500)


# ─── Admin Routes ─────────────────────────────────────────────────────────────
def _admin_check(request: Request):
    return 'user_id' in request.session and request.session.get('is_admin')


@app.get("/admin/feedback", response_class=HTMLResponse)
async def admin_feedback(request: Request):
    if not _admin_check(request): return _redirect("/")
    conn      = get_db_connection()
    feedbacks = execute_query(conn, "SELECT * FROM feedback ORDER BY created_at DESC").fetchall()
    release_db_connection(conn)
    total = len(feedbacks)
    s, vc = 0, 0
    for f in feedbacks:
        if f['rating']:
            try: s += int(f['rating']); vc += 1
            except Exception: pass
    avg  = round(s / vc, 1) if vc > 0 else 0
    sat  = round((avg / 5) * 100, 1) if avg > 0 else 0
    return _render(request, "admin/feedback.html", dict(feedbacks=feedbacks, stats={'total': total, 'avg': avg, 'satisfaction': sat}))


@app.get("/admin/certificates", response_class=HTMLResponse)
async def admin_certificates(request: Request):
    if not _admin_check(request): return _redirect("/")
    conn = get_db_connection()
    users_with_stats = execute_query(conn, """
        SELECT u.id, u.name, u.email, COALESCE(s.certificates, 0) as certificates
        FROM users u LEFT JOIN user_stats s ON u.id = s.user_id ORDER BY u.name ASC
    """).fetchall()
    release_db_connection(conn)
    return _render(request, "admin/certificates.html", dict(users=users_with_stats))


@app.post("/admin/increment_certificate")
async def admin_increment_certificate(request: Request):
    if not _admin_check(request): return JSONResponse({"message": "Admin access required."}, status_code=403)
    try:
        data    = await request.json()
        user_id = data.get('user_id')
        if not user_id: return JSONResponse({"message": "User ID is required"}, status_code=400)
        conn = get_db_connection()
        if not execute_query(conn, "SELECT * FROM user_stats WHERE user_id = ?", (user_id,)).fetchone():
            execute_query(conn, "INSERT INTO user_stats (user_id, study_minutes, certificates, current_streak, max_streak) VALUES (?, 0, 1, 0, 0)", (user_id,))
        else:
            execute_query(conn, "UPDATE user_stats SET certificates = certificates + 1 WHERE user_id = ?", (user_id,))
        conn.commit(); release_db_connection(conn)
        return JSONResponse({"message": "Certificate count incremented successfully"}, status_code=200)
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=500)


@app.get("/admin/export_users")
async def export_users(request: Request):
    if not _admin_check(request):
        return RedirectResponse(url="/", status_code=303)
    
    conn = get_db_connection()
    users = execute_query(conn, "SELECT id, name, email, mobile, is_admin, referral_code, referred_by, verified_referrals, created_at FROM users ORDER BY id ASC").fetchall()
    release_db_connection(conn)
    
    output = io.StringIO()
    # Write UTF-8 BOM to support Unicode in Excel
    output.write('\ufeff')
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "User ID", "Name", "Email", "Mobile", "Role", "Referral Code", "Referred By ID", "Verified Referrals", "Joined At"
    ])
    
    # Rows
    for u in users:
        role = "Admin" if u['is_admin'] else "User"
        writer.writerow([
            u['id'],
            u['name'],
            u['email'],
            u['mobile'] or '',
            role,
            u['referral_code'] or '',
            u['referred_by'] or '',
            u['verified_referrals'] or 0,
            u['created_at']
        ])
    
    output.seek(0)
    
    response = StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv"
    )
    response.headers["Content-Disposition"] = "attachment; filename=users_export.csv"
    return response


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    if not _admin_check(request): return _redirect("/")
    conn     = get_db_connection()
    contents = execute_query(conn, 'SELECT id, language, topic_slug, topic_title, content_html, quiz_json, custom_css, custom_js, order_index, created_at FROM content ORDER BY language, order_index').fetchall()
    users_count_res = execute_query(conn, 'SELECT COUNT(*) as count FROM users').fetchone()
    users_count = users_count_res['count'] if hasattr(users_count_res, '__getitem__') else users_count_res[0]
    lang_dist   = execute_query(conn, 'SELECT language, COUNT(*) as count FROM content GROUP BY language').fetchall()
    lang_labels = [r['language'].capitalize() for r in lang_dist]
    lang_counts = [r['count'] for r in lang_dist]
    is_pg = hasattr(conn, 'cursor_factory')
    if is_pg:
        user_growth      = execute_query(conn, "SELECT TO_CHAR(created_at, 'YYYY-MM-DD') as date, COUNT(*) as count FROM users WHERE created_at > CURRENT_DATE - INTERVAL '7 days' GROUP BY date ORDER BY date ASC").fetchall()
        practice_trends  = execute_query(conn, "SELECT activity_date as date, SUM(practice_count) as count FROM user_activity WHERE activity_date > CURRENT_DATE - INTERVAL '7 days' GROUP BY activity_date ORDER BY activity_date ASC").fetchall()
        active_24h = execute_query(conn, "SELECT COUNT(*) as count FROM user_stats WHERE last_active_date >= CURRENT_DATE - INTERVAL '1 day'").fetchone()
        active_7d  = execute_query(conn, "SELECT COUNT(*) as count FROM user_stats WHERE last_active_date >= CURRENT_DATE - INTERVAL '7 days'").fetchone()
        this_week  = execute_query(conn, "SELECT COUNT(*) as count FROM users WHERE created_at > CURRENT_DATE - INTERVAL '7 days'").fetchone()
        last_week  = execute_query(conn, "SELECT COUNT(*) as count FROM users WHERE created_at BETWEEN CURRENT_DATE - INTERVAL '14 days' AND CURRENT_DATE - INTERVAL '7 days'").fetchone()
    else:
        user_growth      = execute_query(conn, "SELECT strftime('%Y-%m-%d', created_at) as date, COUNT(*) as count FROM users WHERE created_at > date('now', '-7 days') GROUP BY date ORDER BY date ASC").fetchall()
        practice_trends  = execute_query(conn, "SELECT activity_date as date, SUM(practice_count) as count FROM user_activity WHERE activity_date > date('now', '-7 days') GROUP BY activity_date ORDER BY activity_date ASC").fetchall()
        active_24h = execute_query(conn, "SELECT COUNT(*) as count FROM user_stats WHERE last_active_date >= date('now', '-1 day')").fetchone()
        active_7d  = execute_query(conn, "SELECT COUNT(*) as count FROM user_stats WHERE last_active_date >= date('now', '-7 days')").fetchone()
        this_week  = execute_query(conn, "SELECT COUNT(*) as count FROM users WHERE created_at > date('now', '-7 days')").fetchone()
        last_week  = execute_query(conn, "SELECT COUNT(*) as count FROM users WHERE created_at BETWEEN date('now', '-14 days') AND date('now', '-7 days')").fetchone()
    all_users   = execute_query(conn, 'SELECT id, name, email, mobile, is_admin, created_at FROM users ORDER BY id DESC').fetchall()
    careers     = execute_query(conn, "SELECT * FROM careers ORDER BY id DESC").fetchall()
    career_apps = execute_query(conn, "SELECT ca.*, c.title as career_title, c.type as career_type FROM career_applications ca LEFT JOIN careers c ON ca.career_id = c.id ORDER BY ca.id DESC").fetchall()
    release_db_connection(conn)

    def _cnt(r):
        if r is None: return 0
        try:    return r['count']
        except Exception: return r[0] if r else 0

    dau, wau = _cnt(active_24h), _cnt(active_7d)
    tw, lw   = _cnt(this_week), _cnt(last_week)
    growth_rate = 0
    if lw > 0:   growth_rate = round(((tw - lw) / lw) * 100, 1)
    elif tw > 0: growth_rate = 100.0
    engagement_rate = round((dau / users_count) * 100) if users_count > 0 else 0
    top_lang = lang_labels[lang_counts.index(max(lang_counts))] if lang_counts else "N/A"
    avg_session = 12
    if wau > 0 and practice_trends:
        total_p = sum(pt['count'] for pt in practice_trends)
        avg_session = max(5, min(60, round((total_p * 3) / wau)))

    analytics = {
        "lang_labels": lang_labels, "lang_counts": lang_counts,
        "user_growth":     _jsonify_dates([dict(r) for r in user_growth]),
        "practice_trends": _jsonify_dates([dict(r) for r in practice_trends]),
        "user_growth_rate": growth_rate, "dau": dau, "wau": wau,
        "engagement_rate": engagement_rate, "top_lang": top_lang, "avg_session": avg_session
    }
    return _render(request, "admin/dashboard.html", dict(
        contents=_jsonify_dates([dict(c) for c in contents]),
        users_count=users_count,
        all_users=_jsonify_dates([dict(u) for u in all_users]),
        analytics=analytics,
        careers=_jsonify_dates([dict(c) for c in careers]),
        career_apps=_jsonify_dates([dict(ca) for ca in career_apps])
    ))



@app.post("/admin/add_career")
async def add_career(request: Request):
    if not _admin_check(request): return JSONResponse({"message": "Admin access required."}, status_code=403)
    try:
        data = await request.json()
        career_id, type_, title = data.get('id'), data.get('type'), data.get('title')
        company, location, description, link = data.get('company'), data.get('location'), data.get('description'), data.get('link')
        if not type_ or not title:
            return JSONResponse({"message": "Type and Title are required"}, status_code=400)
        conn = get_db_connection()
        if career_id:
            execute_query(conn, 'UPDATE careers SET type = ?, title = ?, company = ?, location = ?, description = ?, link = ? WHERE id = ?',
                          (type_, title, company, location, description, link, career_id))
        else:
            execute_query(conn, 'INSERT INTO careers (type, title, company, location, description, link) VALUES (?, ?, ?, ?, ?, ?)',
                          (type_, title, company, location, description, link))
        conn.commit(); release_db_connection(conn)
        return JSONResponse({"message": "Career item added/updated successfully"}, status_code=200)
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=500)


@app.post("/admin/delete_career/{id}")
async def delete_career(id: int, request: Request):
    if not _admin_check(request): return JSONResponse({"message": "Admin access required."}, status_code=403)
    try:
        conn = get_db_connection()
        execute_query(conn, 'DELETE FROM careers WHERE id = ?', (id,))
        conn.commit(); release_db_connection(conn)
        return JSONResponse({"message": "Career item deleted successfully"}, status_code=200)
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=500)


@app.get("/api/career/{id}")
async def get_career(id: int, request: Request):
    conn   = get_db_connection()
    career = execute_query(conn, "SELECT * FROM careers WHERE id = ?", (id,)).fetchone()
    release_db_connection(conn)
    if career: return JSONResponse(dict(career))
    return JSONResponse({"message": "Career not found"}, status_code=404)


@app.post("/admin/add_content")
async def add_content(request: Request):
    if not _admin_check(request): return JSONResponse({"message": "Admin access required."}, status_code=403)
    try:
        data = await request.json()
        conn = get_db_connection()
        execute_query(conn, '''
            INSERT OR REPLACE INTO content (language, topic_slug, topic_title, content_html, quiz_json, custom_css, custom_js, order_index)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data.get('language'), data.get('topic_slug'), data.get('topic_title'), data.get('content_html'),
              data.get('quiz_json'), data.get('custom_css'), data.get('custom_js'), data.get('order_index', 0)))
        conn.commit(); release_db_connection(conn)
        return JSONResponse({"message": "Content added/updated successfully"}, status_code=200)
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=500)


@app.post("/admin/delete_content/{id}")
async def delete_content(id: int, request: Request):
    if not _admin_check(request): return JSONResponse({"message": "Admin access required."}, status_code=403)
    try:
        conn = get_db_connection()
        execute_query(conn, 'DELETE FROM content WHERE id = ?', (id,))
        conn.commit(); release_db_connection(conn)
        return JSONResponse({"message": "Content deleted successfully"}, status_code=200)
    except Exception as e:
        return JSONResponse({"message": str(e)}, status_code=500)


@app.get("/api/content/{language}")
async def get_language_content(language: str, request: Request):
    user_id = request.session.get('user_id')
    conn    = get_db_connection()
    if user_id:
        topics = execute_query(conn, '''
            SELECT c.topic_slug, c.topic_title,
            CASE WHEN p.user_id IS NOT NULL THEN 1 ELSE 0 END as completed
            FROM content c LEFT JOIN user_progress p ON c.language = p.language AND c.topic_slug = p.topic_slug AND p.user_id = ?
            WHERE c.language = ? ORDER BY c.order_index
        ''', (user_id, language.lower())).fetchall()
    else:
        topics = execute_query(conn, 'SELECT topic_slug, topic_title, 0 as completed FROM content WHERE language = ? ORDER BY order_index', (language.lower(),)).fetchall()
    release_db_connection(conn)
    return JSONResponse([dict(t) for t in topics])


@app.get("/api/content/{language}/{topic_slug}")
async def get_topic_content(language: str, topic_slug: str, request: Request):
    conn  = get_db_connection()
    topic = execute_query(conn, 'SELECT id, language, topic_slug, topic_title, content_html, quiz_json, custom_css, custom_js, order_index, created_at FROM content WHERE language = ? AND topic_slug = ?', (language.lower(), topic_slug)).fetchone()
    student_count = (execute_query(conn, 'SELECT COUNT(*) as count FROM user_progress WHERE language = ? AND topic_slug = ?', (language.lower(), topic_slug)).fetchone() or {}).get('count', 0)
    started_count = (execute_query(conn, 'SELECT COUNT(DISTINCT user_id) as count FROM user_progress WHERE language = ?', (language.lower(),)).fetchone() or {}).get('count', 0)
    user_id = request.session.get('user_id')
    has_given_feedback = bool(user_id and execute_query(conn, 'SELECT id FROM feedback WHERE user_id = ? LIMIT 1', (user_id,)).fetchone())
    release_db_connection(conn)
    if topic:
        d = dict(topic)
        d['student_count'] = student_count
        d['started_count'] = started_count
        d['has_given_feedback'] = has_given_feedback
        return JSONResponse(d)
    return JSONResponse({"message": "Not found"}, status_code=404)


@app.post("/run")
async def run(request: Request, _rl=rl_10_per_min):
    try:
        data = await request.json()
        if not data: return JSONResponse({"output": "No input data received"}, status_code=400)
        source      = data.get("code", "")
        language_id = str(data.get("language_id", ""))
        if not source or not language_id: return JSONResponse({"output": "Missing code or language_id"}, status_code=400)
        JUDGE0_URL    = "https://judge0-ce.p.rapidapi.com/submissions?base64_encoded=true&wait=true"
        RAPIDAPI_KEY  = os.environ.get("JUDGE0_API_KEY")
        RAPIDAPI_HOST = os.environ.get("JUDGE0_API_HOST", "judge0-ce.p.rapidapi.com")
        if not RAPIDAPI_KEY: return JSONResponse({"output": "Judge0 API Key is missing in environment configuration."}, status_code=500)
        source_code    = data.get("code", "")
        language_id    = data.get("language_id", "71")
        stdin          = data.get("stdin", "")
        encoded_source = base64.b64encode(source_code.encode('utf-8')).decode('utf-8')
        encoded_stdin  = base64.b64encode(stdin.encode('utf-8')).decode('utf-8')
        payload = {"language_id": int(language_id), "source_code": encoded_source, "stdin": encoded_stdin}
        headers = {"Content-Type": "application/json", "X-RapidAPI-Key": RAPIDAPI_KEY, "X-RapidAPI-Host": RAPIDAPI_HOST}
        try:
            resp = http_requests.post(JUDGE0_URL, json=payload, headers=headers, timeout=15)
            resp.raise_for_status()
            rd = resp.json()
            stdout  = base64.b64decode(rd.get("stdout") or "").decode("utf-8") if rd.get("stdout") else ""
            stderr  = base64.b64decode(rd.get("stderr") or "").decode("utf-8") if rd.get("stderr") else ""
            compile_output = base64.b64decode(rd.get("compile_output") or "").decode("utf-8") if rd.get("compile_output") else ""
            output_result  = stdout or compile_output or stderr or rd.get("message") or "No output"
            status = rd.get("status", {})
            if status.get("id") > 3:
                output_result = f"Status: {status.get('description')}\n{output_result}"
        except http_requests.exceptions.RequestException as e:
            output_result = f"Judge0 API Error: {str(e)}"
        except Exception as e:
            output_result = f"Unexpected error: {str(e)}"
        if 'user_id' in request.session:
            update_user_activity(request.session['user_id'], is_practice=True)
        return JSONResponse({"output": output_result or "No output"})
    except Exception as e:
        return JSONResponse({"output": f"Server error: {str(e)}"}, status_code=500)


@app.post("/api/chat")
async def ai_chat(request: Request, _rl=rl_20_per_min):
    try:
        data         = await request.json()
        user_message = data.get('message', '').strip()
        language     = data.get('language', 'programming')
        if not user_message: return JSONResponse({'reply': 'Please type a question first!'}, status_code=400)
        if 'user_id' not in request.session:
            referrer = request.headers.get('Referer', '/')
            return JSONResponse({'reply': 'Hey ra 😄! AI chat use cheyali ante login avvali. Signin cheyyi ra!', 'next_url': referrer}, status_code=401)
        gemini_api_key = os.environ.get('GEMINI_API_KEY', '')
        if not gemini_api_key: return JSONResponse({'reply': '⚠️ AI service not configured. Please set GEMINI_API_KEY in environment variables.'}, status_code=503)
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
- Don't give wrong or confusing answers"""

        full_prompt = f"{system_prompt}\n\nUser: {user_message}\nYou:"
        gemini_headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": full_prompt}]}], "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2048}}
        session_req = http_requests.Session()
        models_to_try = ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.0-flash-lite", "gemini-2.5-flash-lite", "gemini-flash-latest"]
        resp, last_error = None, None
        for model_name in models_to_try:
            try:
                temp_resp = session_req.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_api_key}", json=payload, headers=gemini_headers, timeout=6)
                if temp_resp.status_code == 200: resp = temp_resp; break
                if temp_resp.status_code == 429: last_error = "QUOTA_EXCEEDED"; continue
                continue
            except Exception as e:
                print(f"Attempt with {model_name} failed: {e}"); continue
        if resp is None:
            if last_error == "QUOTA_EXCEEDED": return JSONResponse({'reply': '⏳ Free limit reach ayindi ra! Konchem wait chesi malli try cheyyi. 😊'}, status_code=429)
            return JSONResponse({'reply': '❌ AI service temporary ga busy undi ra. Malli try cheyyi! 😅'}, status_code=503)
        result = resp.json()
        if 'error' in result: return JSONResponse({'reply': '❌ AI service lo chinna error vachindi. Malli try cheyyi ra!'}, status_code=502)
        if 'candidates' in result and len(result['candidates']) > 0:
            cand = result['candidates'][0]
            if 'content' in cand and 'parts' in cand['content'] and len(cand['content']['parts']) > 0:
                reply = cand['content']['parts'][0].get('text', '') or "Hmm ra, AI response empty vachindi. Malli try cheyyi! 😅"
            else:
                finish_reason = cand.get('finishReason', 'UNKNOWN')
                reply = ("Arey, ee question konchem sensitive ga undi ra. General coding doubts adugu, manam kalisi nerchukundam! 😊"
                         if finish_reason == 'SAFETY' else "Hmm, response structure lo chinna issue vachindi. Malli adugu ra! 😅")
        else:
            reply = "Hmm ra, AI response empty vachindi. Malli try cheyyi! 😅"
        return JSONResponse({'reply': reply})
    except http_requests.exceptions.Timeout:
        return JSONResponse({'reply': '⏳ The AI is thinking too long. Please try again!'}, status_code=504)
    except Exception as e:
        print(f"Chat error: {e}")
        return JSONResponse({'reply': '❌ Something went wrong. Please try again later.'}, status_code=500)


# ─── Startup (lifespan) ───────────────────────────────────────────────────────
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(application: FastAPI):
    init_db()
    yield

app.router.lifespan_context = lifespan


# ─── Entrypoint ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print("")
    print("  *  CodeNative FastAPI server starting...")
    print(f"  *  Listening on  http://127.0.0.1:{port}")
    print("  *  Press Ctrl+C to stop")
    print("")

    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)

