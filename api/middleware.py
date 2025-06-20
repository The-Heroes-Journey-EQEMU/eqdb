from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from .auth import auth
import logging

logger = logging.getLogger(__name__)

def api_key_required(f):
    """Decorator to require either JWT token or API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for JWT token first
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception:
            pass
        
        # Check for API key
        api_key = request.headers.get('X-API-KEY')
        if not api_key:
            return jsonify({'message': 'Authentication required. Provide either JWT token or X-API-KEY header'}), 401
        
        # Verify API key
        user_data = auth.authenticate_api_key(api_key)
        if not user_data:
            return jsonify({'message': 'Invalid API key'}), 401
        
        # Store user data in request context for later use
        request.current_user = user_data
        return f(*args, **kwargs)
    
    return decorated_function

def optional_auth(f):
    """Decorator to allow anonymous access but provide user data if authenticated"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Try to get user from JWT token
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            user_data = auth.get_user_by_id(int(current_user_id))
            request.current_user = user_data
        except Exception:
            # Try to get user from API key
            api_key = request.headers.get('X-API-KEY')
            if api_key:
                user_data = auth.authenticate_api_key(api_key)
                if user_data:
                    request.current_user = user_data
                else:
                    request.current_user = None
            else:
                request.current_user = None
        
        return f(*args, **kwargs)
    
    return decorated_function

def write_auth_required(f):
    """Decorator to require authentication for write operations (POST, PUT, DELETE)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # For GET requests, allow anonymous access
        if request.method == 'GET':
            return optional_auth(f)(*args, **kwargs)
        
        # For write operations, require authentication
        return api_key_required(f)(*args, **kwargs)
    
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for JWT token first
        try:
            verify_jwt_in_request()
            from flask_jwt_extended import get_jwt_identity
            user_id = get_jwt_identity()
            user_data = auth.get_user_by_id(int(user_id))
        except Exception:
            # Check for API key
            api_key = request.headers.get('X-API-KEY')
            if not api_key:
                return jsonify({'message': 'Authentication required'}), 401
            
            user_data = auth.authenticate_api_key(api_key)
            if not user_data:
                return jsonify({'message': 'Invalid API key'}), 401
        
        if not user_data or not user_data.get('is_admin'):
            return jsonify({'message': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function 