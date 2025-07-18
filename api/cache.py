import json
import logging
from functools import wraps
from datetime import datetime, date
from decimal import Decimal

import redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

redis_client = None

def init_cache(client):
    global redis_client
    redis_client = client

def get_redis_client():
    return redis_client

def cache_results(ttl=900):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            client = get_redis_client()
            if not client:
                logger.warning("Redis client not available. Skipping cache.")
                return func(*args, **kwargs)

            # Create a cache key from the function name and arguments, excluding the 'self' argument if it's a method
            key_args = args
            if args and hasattr(args[0], func.__name__):
                key_args = args[1:]

            key = f"{func.__name__}:{json.dumps(key_args, sort_keys=True)}:{json.dumps(kwargs, sort_keys=True)}"
            # logger.info(f"Cache key: {key}")
            
            # Try to get the result from cache
            try:
                cached_result = client.get(key)
                if cached_result:
                    # logger.info(f"Cache hit for key: {key}")
                    return json.loads(cached_result)
            except redis.exceptions.RedisError as e:
                logger.error(f"Redis GET error: {e}")

            # logger.info(f"Cache miss for key: {key}")
            # If not in cache, call the function
            result = func(*args, **kwargs)
            
            # Store the result in cache only if it's not empty
            if result:
                try:
                    client.setex(key, ttl, json.dumps(result, cls=CustomJSONEncoder))
                    # logger.info(f"Set cache for key: {key}")
                except redis.exceptions.RedisError as e:
                    logger.error(f"Redis SETEX error: {e}")

            return result
        return wrapper
    return decorator

def clear_cache():
    client = get_redis_client()
    if client:
        try:
            client.flushdb()
            logger.info("Redis cache cleared.")
            return True
        except redis.exceptions.RedisError as e:
            logger.error(f"Redis FLUSHDB error: {e}")
            return False
    return False
