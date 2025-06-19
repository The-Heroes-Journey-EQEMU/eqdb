import requests
import json
from datetime import datetime
import logging
import sys
from pathlib import Path
from typing import Any

# Add parent directory to path so we can import from the main package
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API endpoints
LOCAL_API = "http://127.0.0.1:5001/api/v1"
PROD_API = "https://eqdb.net/api/v1"

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime,)):
        return obj.isoformat()
    raise TypeError("Type not serializable")

def deep_compare(local, prod, path=""):
    """Compare two JSON objects deeply, ignoring value mismatches when types match."""
    if type(local) != type(prod):
        return False, f"Type mismatch at {path}: {type(local)} != {type(prod)}"
    
    if isinstance(local, dict):
        local_keys = set(local.keys())
        prod_keys = set(prod.keys())
        if local_keys != prod_keys:
            return False, f"Key mismatch at {path}: {local_keys - prod_keys}"
        for key in local_keys:
            result, error = deep_compare(local[key], prod[key], f"{path}.{key}" if path else key)
            if not result:
                return False, error
    elif isinstance(local, list):
        if len(local) != len(prod):
            return False, f"List length mismatch at {path}: {len(local)} != {len(prod)}"
        for i, (l, p) in enumerate(zip(local, prod)):
            result, error = deep_compare(l, p, f"{path}[{i}]")
            if not result:
                return False, error
    # For primitive types, we only care about type matching, not values
    return True, None

def compare_responses(local, prod, test_name):
    eq, msg = deep_compare(local, prod)
    if not eq:
        logger.error(f"{test_name}: Response mismatch - {msg}")
        return False
    logger.info(f"{test_name}: Passed")
    return True

def run_tests():
    """Run all API tests."""
    # Spell tests
    test_cases = [
        {
            "name": "Spell by ID",
            "local_url": "http://localhost:5001/api/v1/spells?id=1",
            "prod_url": "https://eqdb.net/api/v1/spells?id=1"
        },
        {
            "name": "Spell by Name",
            "local_url": "http://localhost:5001/api/v1/spells?name=Minor Healing",
            "prod_url": "https://eqdb.net/api/v1/spells?name=Minor Healing"
        },
        {
            "name": "Spell by Class",
            "local_url": "http://localhost:5001/api/v1/spells?class=1",
            "prod_url": "https://eqdb.net/api/v1/spells?class=1"
        }
    ]
    
    total_tests = len(test_cases)
    passed_tests = 0
    
    for test in test_cases:
        try:
            local_response = requests.get(test["local_url"])
            prod_response = requests.get(test["prod_url"])
            
            if compare_responses(local_response, prod_response, test["name"]):
                passed_tests += 1
                logger.info(f"{test['name']}: Passed")
        except Exception as e:
            logger.error(f"{test['name']}: Test failed with error - {str(e)}")
    
    logger.info("\nTest Summary:")
    logger.info(f"Total Tests: {total_tests}")
    logger.info(f"Passed: {passed_tests}")
    logger.info(f"Failed: {total_tests - passed_tests}")

if __name__ == "__main__":
    run_tests() 