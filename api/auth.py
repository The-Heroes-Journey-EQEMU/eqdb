import os
import secrets
import bcrypt
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from flask import current_app
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
import logging

logger = logging.getLogger(__name__)

class UserAuth:
    def __init__(self, db_path: str = "local_db.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with user and API key tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    preferences TEXT DEFAULT '{}'
                )
            ''')
            
            # Create API keys table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    key_hash TEXT NOT NULL,
                    key_prefix TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_api_key(self) -> tuple[str, str]:
        """Generate a new API key and return (full_key, key_prefix)"""
        full_key = f"eqdb_{secrets.token_urlsafe(32)}"
        key_prefix = full_key[:12]  # First 12 characters for display
        return full_key, key_prefix
    
    def hash_api_key(self, api_key: str) -> str:
        """Hash an API key for storage"""
        return bcrypt.hashpw(api_key.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_api_key(self, api_key: str, hashed: str) -> bool:
        """Verify an API key against its hash"""
        return bcrypt.checkpw(api_key.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_user(self, email: str, password: str, is_admin: bool = False) -> Optional[int]:
        """Create a new user and return user ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (email, password_hash, is_admin)
                VALUES (?, ?, ?)
            ''', (email, password_hash, is_admin))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Created user: {email} (ID: {user_id})")
            return user_id
            
        except sqlite3.IntegrityError:
            logger.warning(f"User already exists: {email}")
            return None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user and return user data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, email, password_hash, is_admin, created_at, last_login, preferences
                FROM users WHERE email = ?
            ''', (email,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            user_id, user_email, password_hash, is_admin, created_at, last_login, preferences = row
            
            if not self.verify_password(password, password_hash):
                return None
            
            # Update last login
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            user_data = {
                'id': user_id,
                'email': user_email,
                'is_admin': bool(is_admin),
                'created_at': created_at,
                'last_login': last_login,
                'preferences': preferences
            }
            
            logger.info(f"User authenticated: {email}")
            return user_data
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user data by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, email, is_admin, created_at, last_login, preferences
                FROM users WHERE id = ?
            ''', (user_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            user_id, email, is_admin, created_at, last_login, preferences = row
            
            return {
                'id': user_id,
                'email': email,
                'is_admin': bool(is_admin),
                'created_at': created_at,
                'last_login': last_login,
                'preferences': preferences
            }
            
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def update_user_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Update user password"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get current password hash
            cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            if not row:
                return False
            
            current_hash = row[0]
            if not self.verify_password(current_password, current_hash):
                return False
            
            # Update password
            new_hash = self.hash_password(new_password)
            cursor.execute('''
                UPDATE users SET password_hash = ?
                WHERE id = ?
            ''', (new_hash, user_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Password updated for user ID: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating password: {e}")
            return False
    
    def update_user_preferences(self, user_id: int, preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        try:
            import json
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            preferences_json = json.dumps(preferences)
            cursor.execute('''
                UPDATE users SET preferences = ?
                WHERE id = ?
            ''', (preferences_json, user_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Preferences updated for user ID: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating preferences: {e}")
            return False
    
    def create_api_key(self, user_id: int, name: str) -> Optional[Dict[str, Any]]:
        """Create a new API key for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            full_key, key_prefix = self.generate_api_key()
            key_hash = self.hash_api_key(full_key)
            
            cursor.execute('''
                INSERT INTO api_keys (user_id, name, key_hash, key_prefix)
                VALUES (?, ?, ?, ?)
            ''', (user_id, name, key_hash, key_prefix))
            
            api_key_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Created API key for user ID: {user_id}")
            
            return {
                'id': api_key_id,
                'name': name,
                'key_prefix': key_prefix,
                'full_key': full_key,
                'created_at': datetime.now().isoformat(),
                'is_active': True
            }
            
        except Exception as e:
            logger.error(f"Error creating API key: {e}")
            return None
    
    def get_user_api_keys(self, user_id: int) -> list[Dict[str, Any]]:
        """Get all API keys for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, key_prefix, created_at, last_used, is_active
                FROM api_keys WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            api_keys = []
            for row in rows:
                api_key_id, name, key_prefix, created_at, last_used, is_active = row
                api_keys.append({
                    'id': api_key_id,
                    'name': name,
                    'key_prefix': key_prefix,
                    'created_at': created_at,
                    'last_used': last_used,
                    'is_active': bool(is_active)
                })
            
            return api_keys
            
        except Exception as e:
            logger.error(f"Error getting API keys: {e}")
            return []
    
    def delete_api_key(self, user_id: int, api_key_id: int) -> bool:
        """Delete an API key"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM api_keys 
                WHERE id = ? AND user_id = ?
            ''', (api_key_id, user_id))
            
            deleted = cursor.rowcount > 0
            conn.commit()
            conn.close()
            
            if deleted:
                logger.info(f"Deleted API key {api_key_id} for user ID: {user_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting API key: {e}")
            return False
    
    def authenticate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Authenticate an API key and return user data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT ak.id, ak.user_id, ak.name, ak.key_hash, ak.is_active,
                       u.email, u.is_admin
                FROM api_keys ak
                JOIN users u ON ak.user_id = u.id
                WHERE ak.is_active = TRUE
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            for row in rows:
                api_key_id, user_id, name, key_hash, is_active, email, is_admin = row
                if self.verify_api_key(api_key, key_hash):
                    # Update last used
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE api_keys SET last_used = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (api_key_id,))
                    conn.commit()
                    conn.close()
                    
                    logger.info(f"API key authenticated for user: {email}")
                    return {
                        'id': user_id,
                        'email': email,
                        'is_admin': bool(is_admin),
                        'api_key_id': api_key_id,
                        'api_key_name': name
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error authenticating API key: {e}")
            return None
    
    def create_default_admin(self):
        """Create the default admin user if it doesn't exist"""
        admin_email = "aepod23@gmail.com"
        admin_password = "frogluck23"
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT id FROM users WHERE email = ?', (admin_email,))
            if cursor.fetchone():
                logger.info("Default admin user already exists")
                conn.close()
                return
            
            conn.close()
            
            user_id = self.create_user(admin_email, admin_password, is_admin=True)
            if user_id:
                logger.info(f"Created default admin user: {admin_email}")
            else:
                logger.error("Failed to create default admin user")
                
        except Exception as e:
            logger.error(f"Error creating default admin: {e}")

# Global instance
auth = UserAuth() 