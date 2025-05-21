import sqlite3
import json
from werkzeug.security import generate_password_hash
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Database file
DATABASE = 'app.db'

def init_db():
    """Initialize the database and create tables if they don't exist."""
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('core', 'admin')) DEFAULT 'core'
                )
            ''')
            # Tokens table for revoked JWT tokens
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tokens (
                    jti TEXT PRIMARY KEY,
                    revoked_at TIMESTAMP NOT NULL
                )
            ''')
            # Blueprints table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS blueprints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    filepath TEXT NOT NULL,
                    dimensions TEXT NOT NULL,
                    color TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            conn.commit()
            logger.info("Database initialized successfully")
    except sqlite3.Error as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

def get_db_connection():
    """Get a database connection with row factory set."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def register_user(email, password, role='core'):
    """Register a new user with email, hashed password, and role."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                raise ValueError("Email already registered")
            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users (email, password, role) VALUES (?, ?, ?)",
                (email, hashed_password, role)
            )
            conn.commit()
            logger.debug(f"User registered: {email}")
    except sqlite3.Error as e:
        logger.error(f"User registration failed: {str(e)}")
        raise ValueError(f"Registration failed: {str(e)}")

def get_user_by_email(email):
    """Retrieve a user by email."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, password, role FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            return user
    except sqlite3.Error as e:
        logger.error(f"Get user by email failed: {str(e)}")
        raise ValueError(f"Database error: {str(e)}")

def get_user_by_id(user_id):
    """Retrieve a user by ID."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, password, role FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            return user
    except sqlite3.Error as e:
        logger.error(f"Get user by ID failed: {str(e)}")
        raise ValueError(f"Database error: {str(e)}")

def update_user(user_id, email=None, password=None, role=None):
    """Update user details (email, password, or role)."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if email:
                cursor.execute("SELECT id FROM users WHERE email = ? AND id != ?", (email, user_id))
                if cursor.fetchone():
                    raise ValueError("Email already in use")
                cursor.execute("UPDATE users SET email = ? WHERE id = ?", (email, user_id))
            if password:
                hashed_password = generate_password_hash(password)
                cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
            if role:
                cursor.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
            conn.commit()
            logger.debug(f"User updated: ID {user_id}")
    except sqlite3.Error as e:
        logger.error(f"Update user failed: {str(e)}")
        raise ValueError(f"Update failed: {str(e)}")

def update_user_password(user_id, password):
    """Update a user's password."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            hashed_password = generate_password_hash(password)
            cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
            conn.commit()
            logger.debug(f"Password updated for user ID {user_id}")
    except sqlite3.Error as e:
        logger.error(f"Update password failed: {str(e)}")
        raise ValueError(f"Update failed: {str(e)}")

def update_user_profile(user_id, password=None, role=None):
    """Update user profile (password or role)."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if password:
                hashed_password = generate_password_hash(password)
                cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, user_id))
            if role:
                if role not in ['core', 'admin']:
                    raise ValueError("Invalid role")
                cursor.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))
            conn.commit()
            logger.debug(f"Profile updated for user ID {user_id}")
    except sqlite3.Error as e:
        logger.error(f"Update profile failed: {str(e)}")
        raise ValueError(f"Update failed: {str(e)}")

def delete_user(user_id):
    """Delete a user by ID."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            if cursor.rowcount == 0:
                raise ValueError("User not found")
            conn.commit()
            logger.debug(f"User deleted: ID {user_id}")
    except sqlite3.Error as e:
        logger.error(f"Delete user failed: {str(e)}")
        raise ValueError(f"Delete failed: {str(e)}")

def get_all_users():
    """Retrieve all users."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, role FROM users")
            users = [{'id': row['id'], 'email': row['email'], 'role': row['role']} for row in cursor.fetchall()]
            return users
    except sqlite3.Error as e:
        logger.error(f"Get all users failed: {str(e)}")
        raise ValueError(f"Database error: {str(e)}")

def revoke_token(jti):
    """Revoke a JWT token by adding it to the blocklist."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tokens (jti, revoked_at) VALUES (?, ?)",
                (jti, datetime.utcnow())
            )
            conn.commit()
            logger.debug(f"Token revoked: {jti}")
    except sqlite3.Error as e:
        logger.error(f"Revoke token failed: {str(e)}")
        raise ValueError(f"Revoke failed: {str(e)}")

def is_token_revoked(jti):
    """Check if a JWT token is revoked."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT jti FROM tokens WHERE jti = ?", (jti,))
            return cursor.fetchone() is not None
    except sqlite3.Error as e:
        logger.error(f"Check token revocation failed: {str(e)}")
        raise ValueError(f"Database error: {str(e)}")

def get_dashboard_data(user_id):
    """Retrieve dashboard data for a user."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, role FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
            if not user:
                raise ValueError("User not found")
            return {'id': user['id'], 'email': user['email'], 'role': user['role']}
    except sqlite3.Error as e:
        logger.error(f"Get dashboard data failed: {str(e)}")
        raise ValueError(f"Database error: {str(e)}")

def save_blueprint(user_id, filename, filepath, dimensions, color):
    """Save a blueprint to the database."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO blueprints (user_id, filename, filepath, dimensions, color) VALUES (?, ?, ?, ?, ?)",
                (user_id, filename, filepath, dimensions, color)
            )
            conn.commit()
            blueprint_id = cursor.lastrowid
            logger.debug(f"Blueprint saved: ID {blueprint_id} for user ID {user_id}")
            return blueprint_id
    except sqlite3.Error as e:
        logger.error(f"Save blueprint failed: {str(e)}")
        raise ValueError(f"Save failed: {str(e)}")

def get_blueprint(blueprint_id):
    """Retrieve a blueprint by ID."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, user_id, filename, filepath, dimensions, color FROM blueprints WHERE id = ?",
                (blueprint_id,)
            )
            blueprint = cursor.fetchone()
            if blueprint:
                return {
                    'id': blueprint['id'],
                    'user_id': blueprint['user_id'],
                    'filename': blueprint['filename'],
                    'filepath': blueprint['filepath'],
                    'dimensions': blueprint['dimensions'],
                    'color': blueprint['color']
                }
            return None
    except sqlite3.Error as e:
        logger.error(f"Get blueprint failed: {str(e)}")
        raise ValueError(f"Database error: {str(e)}")

def get_user_blueprints(user_id):
    """Retrieve all blueprints for a user."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, filename, filepath, dimensions, color FROM blueprints WHERE user_id = ?",
                (user_id,)
            )
            blueprints = [
                {
                    'id': row['id'],
                    'filename': row['filename'],
                    'filepath': row['filepath'],
                    'dimensions': row['dimensions'],
                    'color': row['color']
                }
                for row in cursor.fetchall()
            ]
            return blueprints
    except sqlite3.Error as e:
        logger.error(f"Get user blueprints failed: {str(e)}")
        raise ValueError(f"Database error: {str(e)}")

def delete_blueprint(blueprint_id):
    """Delete a blueprint by ID."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM blueprints WHERE id = ?", (blueprint_id,))
            if cursor.rowcount == 0:
                raise ValueError("Blueprint not found")
            conn.commit()
            logger.debug(f"Blueprint deleted: ID {blueprint_id}")
    except sqlite3.Error as e:
        logger.error(f"Delete blueprint failed: {str(e)}")
        raise ValueError(f"Delete failed: {str(e)}")

def update_blueprint_color(blueprint_id, color):
    """Update the color of a blueprint."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE blueprints SET color = ? WHERE id = ?", (color, blueprint_id))
            if cursor.rowcount == 0:
                raise ValueError("Blueprint not found")
            conn.commit()
            logger.debug(f"Blueprint color updated: ID {blueprint_id}")
    except sqlite3.Error as e:
        logger.error(f"Update blueprint color failed: {str(e)}")
        raise ValueError(f"Update failed: {str(e)}")

if __name__ == '__main__':
    init_db()