from flask import Flask
from flask_restx import Api, Namespace
from flask_jwt_extended import JWTManager
import json
from decimal import Decimal
import logging
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create API and namespace with enhanced documentation
api = Api(
    version='1.0',
    title='EQDB API',
    description='A RESTful API for accessing EverQuest game data including items, spells, NPCs, zones, and tradeskills.',
    doc='/api/v1/',
    default='v1',
    default_label='API v1',
    contact='https://wiki.heroesjourneyemu.com/',
    license='MIT',
    license_url='https://opensource.org/licenses/MIT',
    # Enable Swagger UI features
    authorizations={
        'apikey': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'X-API-KEY'
        },
        'bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'JWT Bearer token'
        }
    },
    security='apikey',
    # Swagger UI configuration
    swagger_ui=True,
    swagger_ui_bundle=True,
    swagger_ui_parameters={
        'displayRequestDuration': True,
        'filter': True,
        'tryItOutEnabled': True,
        'persistAuthorization': True,
        'syntaxHighlight.theme': 'monokai'
    }
)

v1 = Namespace('v1', 
    description='API v1 endpoints for EverQuest game data',
    path='/api/v1'
)

# Add v1 namespace to API
api.add_namespace(v1)

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def output_json(data, code, headers=None):
    """Custom JSON output function for Flask-RESTX"""
    if headers is None:
        headers = {}
    dumped = json.dumps(data, cls=CustomJSONEncoder) + '\n'
    resp = Flask.response_class(dumped, mimetype='application/json', status=code)
    resp.headers.extend(headers)
    return resp

def init_api(app):
    """Initialize the API with the Flask app"""
    logger.info("Initializing API")
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Set JWT configuration
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # For development, set to timedelta(hours=1) for production
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = False  # For development, set to timedelta(days=30) for production
    
    # Set custom JSON encoder for Flask-RESTX
    api.representations = {
        'application/json': output_json
    }
    
    # Initialize API with app
    api.init_app(app)
    
    logger.info("API initialization complete")
    return api

# Export v1 namespace and other necessary objects
__all__ = ['v1', 'api', 'init_api'] 