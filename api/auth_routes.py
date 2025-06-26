from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
from .auth import auth
from .models import create_models
import logging

logger = logging.getLogger(__name__)

# Create namespace
auth_ns = Namespace('auth', description='Authentication operations')

# Get models
def get_auth_models(api):
    models = create_models(api, auth_ns)
    return models

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(auth_ns.model('UserLogin', {
        'email': fields.String(required=True, description='User email'),
        'password': fields.String(required=True, description='User password')
    }))
    @auth_ns.response(200, 'Login successful', auth_ns.model('LoginResponse', {
        'access_token': fields.String(description='JWT access token'),
        'refresh_token': fields.String(description='JWT refresh token'),
        'user': fields.Nested(auth_ns.model('User', {
            'id': fields.Integer(description='User ID'),
            'email': fields.String(description='User email'),
            'is_admin': fields.Boolean(description='Admin status'),
            'created_at': fields.DateTime(description='Account creation date'),
            'last_login': fields.DateTime(description='Last login date'),
            'preferences': fields.Raw(description='User preferences')
        }))
    }))
    @auth_ns.response(401, 'Invalid credentials')
    def post(self):
        """User login"""
        try:
            data = request.get_json()
            if not data:
                return {'message': 'No data provided'}, 400
            
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return {'message': 'Email and password required'}, 400
            
            # Authenticate user
            user_data = auth.authenticate_user(email, password)
            if not user_data:
                return {'message': 'Invalid credentials'}, 401
            
            # Create tokens
            access_token = create_access_token(identity=str(user_data['id']))
            refresh_token = create_refresh_token(identity=str(user_data['id']))
            
            logger.info(f"User logged in: {email}")
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user_data
            }, 200
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return {'message': 'Internal server error'}, 500

@auth_ns.route('/refresh')
class Refresh(Resource):
    @jwt_required(refresh=True)
    @auth_ns.response(200, 'Token refreshed')
    def post(self):
        """Refresh access token"""
        try:
            current_user_id = get_jwt_identity()
            access_token = create_access_token(identity=str(current_user_id))
            
            return {
                'access_token': access_token
            }, 200
            
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return {'message': 'Internal server error'}, 500

@auth_ns.route('/profile')
class Profile(Resource):
    @jwt_required()
    @auth_ns.response(200, 'Profile retrieved')
    @auth_ns.response(404, 'User not found')
    def get(self):
        """Get current user profile"""
        try:
            current_user_id = get_jwt_identity()
            user_data = auth.get_user_by_id(int(current_user_id))
            
            if not user_data:
                return {'message': 'User not found'}, 404
            
            return user_data, 200
            
        except Exception as e:
            logger.error(f"Profile retrieval error: {e}")
            return {'message': 'Internal server error'}, 500
    
    @jwt_required()
    @auth_ns.expect(auth_ns.model('UserUpdate', {
        'email': fields.String(description='User email'),
        'is_admin': fields.Boolean(description='Admin status')
    }))
    @auth_ns.response(200, 'Profile updated')
    def put(self):
        """Update user profile (admin only)"""
        try:
            current_user_id = get_jwt_identity()
            user_data = auth.get_user_by_id(int(current_user_id))
            
            if not user_data or not user_data['is_admin']:
                return {'message': 'Admin access required'}, 403
            
            data = request.get_json()
            if not data:
                return {'message': 'No data provided'}, 400
            
            # For now, only allow admin to update other users
            # This could be expanded to allow users to update their own email
            return {'message': 'Profile update not implemented yet'}, 501
            
        except Exception as e:
            logger.error(f"Profile update error: {e}")
            return {'message': 'Internal server error'}, 500

@auth_ns.route('/change-password')
class ChangePassword(Resource):
    @jwt_required()
    @auth_ns.expect(auth_ns.model('PasswordChange', {
        'current_password': fields.String(required=True, description='Current password'),
        'new_password': fields.String(required=True, description='New password')
    }))
    @auth_ns.response(200, 'Password changed successfully')
    @auth_ns.response(400, 'Invalid current password')
    def post(self):
        """Change user password"""
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data:
                return {'message': 'No data provided'}, 400
            
            current_password = data.get('current_password')
            new_password = data.get('new_password')
            
            if not current_password or not new_password:
                return {'message': 'Current and new password required'}, 400
            
            if len(new_password) < 8:
                return {'message': 'New password must be at least 8 characters'}, 400
            
            success = auth.update_user_password(current_user_id, current_password, new_password)
            
            if success:
                logger.info(f"Password changed for user ID: {current_user_id}")
                return {'message': 'Password changed successfully'}, 200
            else:
                return {'message': 'Invalid current password'}, 400
            
        except Exception as e:
            logger.error(f"Password change error: {e}")
            return {'message': 'Internal server error'}, 500

@auth_ns.route('/preferences')
class Preferences(Resource):
    @jwt_required()
    @auth_ns.response(200, 'Preferences retrieved')
    def get(self):
        """Get user preferences"""
        try:
            current_user_id = get_jwt_identity()
            user_data = auth.get_user_by_id(int(current_user_id))
            
            if not user_data:
                return {'message': 'User not found'}, 404
            
            import json
            preferences = json.loads(user_data['preferences']) if user_data['preferences'] else {}
            
            return preferences, 200
            
        except Exception as e:
            logger.error(f"Preferences retrieval error: {e}")
            return {'message': 'Internal server error'}, 500
    
    @jwt_required()
    @auth_ns.expect(fields.Raw(description='User preferences'))
    @auth_ns.response(200, 'Preferences updated')
    def put(self):
        """Update user preferences"""
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data:
                return {'message': 'No data provided'}, 400
            
            success = auth.update_user_preferences(current_user_id, data)
            
            if success:
                logger.info(f"Preferences updated for user ID: {current_user_id}")
                return {'message': 'Preferences updated successfully'}, 200
            else:
                return {'message': 'Failed to update preferences'}, 500
            
        except Exception as e:
            logger.error(f"Preferences update error: {e}")
            return {'message': 'Internal server error'}, 500

@auth_ns.route('/api-keys')
class ApiKeys(Resource):
    @jwt_required()
    @auth_ns.response(200, 'API keys retrieved')
    def get(self):
        """Get user's API keys"""
        try:
            current_user_id = get_jwt_identity()
            api_keys = auth.get_user_api_keys(current_user_id)
            
            return {'api_keys': api_keys}, 200
            
        except Exception as e:
            logger.error(f"API keys retrieval error: {e}")
            return {'message': 'Internal server error'}, 500
    
    @jwt_required()
    @auth_ns.expect(auth_ns.model('ApiKeyCreate', {
        'name': fields.String(required=True, description='API Key name')
    }))
    @auth_ns.response(201, 'API key created')
    def post(self):
        """Create new API key"""
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data:
                return {'message': 'No data provided'}, 400
            
            name = data.get('name')
            if not name:
                return {'message': 'API key name required'}, 400
            
            api_key_data = auth.create_api_key(current_user_id, name)
            
            if api_key_data:
                logger.info(f"API key created for user ID: {current_user_id}")
                return api_key_data, 201
            else:
                return {'message': 'Failed to create API key'}, 500
            
        except Exception as e:
            logger.error(f"API key creation error: {e}")
            return {'message': 'Internal server error'}, 500

@auth_ns.route('/api-keys/<int:api_key_id>')
class ApiKeyDetail(Resource):
    @jwt_required()
    @auth_ns.response(200, 'API key deleted')
    @auth_ns.response(404, 'API key not found')
    def delete(self, api_key_id):
        """Delete API key"""
        try:
            current_user_id = get_jwt_identity()
            success = auth.delete_api_key(current_user_id, api_key_id)
            
            if success:
                logger.info(f"API key {api_key_id} deleted for user ID: {current_user_id}")
                return {'message': 'API key deleted successfully'}, 200
            else:
                return {'message': 'API key not found'}, 404
            
        except Exception as e:
            logger.error(f"API key deletion error: {e}")
            return {'message': 'Internal server error'}, 500

@auth_ns.route('/users')
class Users(Resource):
    @jwt_required()
    @auth_ns.response(200, 'Users retrieved')
    @auth_ns.response(403, 'Admin access required')
    def get(self):
        """Get all users (admin only)"""
        try:
            current_user_id = get_jwt_identity()
            user_data = auth.get_user_by_id(int(current_user_id))
            
            if not user_data or not user_data['is_admin']:
                return {'message': 'Admin access required'}, 403
            
            # This would require adding a method to get all users
            # For now, return a placeholder
            return {'message': 'User listing not implemented yet'}, 501
            
        except Exception as e:
            logger.error(f"Users retrieval error: {e}")
            return {'message': 'Internal server error'}, 500
    
    @jwt_required()
    @auth_ns.expect(auth_ns.model('UserCreate', {
        'email': fields.String(required=True, description='User email'),
        'password': fields.String(required=True, description='User password'),
        'is_admin': fields.Boolean(description='Admin status', default=False)
    }))
    @auth_ns.response(201, 'User created')
    @auth_ns.response(403, 'Admin access required')
    def post(self):
        """Create new user (admin only)"""
        try:
            current_user_id = get_jwt_identity()
            user_data = auth.get_user_by_id(int(current_user_id))
            
            if not user_data or not user_data['is_admin']:
                return {'message': 'Admin access required'}, 403
            
            data = request.get_json()
            if not data:
                return {'message': 'No data provided'}, 400
            
            email = data.get('email')
            password = data.get('password')
            is_admin = data.get('is_admin', False)
            
            if not email or not password:
                return {'message': 'Email and password required'}, 400
            
            if len(password) < 8:
                return {'message': 'Password must be at least 8 characters'}, 400
            
            user_id = auth.create_user(email, password, is_admin)
            
            if user_id:
                logger.info(f"User created by admin {current_user_id}: {email}")
                return {'message': 'User created successfully', 'user_id': user_id}, 201
            else:
                return {'message': 'User already exists'}, 409
            
        except Exception as e:
            logger.error(f"User creation error: {e}")
            return {'message': 'Internal server error'}, 500 