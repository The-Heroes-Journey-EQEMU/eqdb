from flask import Flask
from flask_cors import CORS
from api import init_api, v1
from api.routes import init_routes
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize API with the app
api = init_api(app)

# Initialize API routes
init_routes(api)

if __name__ == '__main__':
    logger.info("Starting API server...")
    app.run(debug=True, host='0.0.0.0', port=5001)
