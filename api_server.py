from flask import Flask
from flask_cors import CORS
import logging
import redis

from api import init_api, v1
from api.routes import init_routes
from api.cache import init_cache

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger('api').setLevel(logging.DEBUG)

app = Flask(__name__)
CORS(app)

# Initialize API with the app
api = init_api(app)

# Initialize API routes
init_routes(api)

# Initialize Redis cache
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()
    init_cache(redis_client)
    logger.info("Redis cache initialized successfully.")
except redis.exceptions.ConnectionError as e:
    logger.error(f"Could not connect to Redis: {e}")
    init_cache(None)

if __name__ == '__main__':
    logger.info("Starting API server...")
    app.run(debug=True, host='0.0.0.0', port=5001)
