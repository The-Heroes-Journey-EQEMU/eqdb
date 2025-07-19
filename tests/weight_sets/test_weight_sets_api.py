import requests
import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API base URL
API_BASE = "http://127.0.0.1:5001/api/v1"

# Test credentials
ADMIN_USER = {
    "email": "aepod23@gmail.com",
    "password": "frogluck23"
}

# Sample weight sets for testing
SAMPLE_WEIGHT_SETS = [
    {
        "name": "Tank Weights",
        "description": "Weights optimized for tanking",
        "weights": [
            {"stat": "hp", "value": 2.0},
            {"stat": "ac", "value": 1.5},
            {"stat": "sta", "value": 1.2},
            {"stat": "str", "value": 1.0}
        ]
    },
    {
        "name": "DPS Weights",
        "description": "Weights optimized for damage dealing",
        "weights": [
            {"stat": "damage", "value": 3.0},
            {"stat": "haste", "value": 2.5},
            {"stat": "attack", "value": 2.0},
            {"stat": "str", "value": 1.5}
        ]
    },
    {
        "name": "Caster Weights",
        "description": "Weights optimized for spell casting",
        "weights": [
            {"stat": "mana", "value": 2.5},
            {"stat": "int", "value": 2.0},
            {"stat": "wis", "value": 1.8},
            {"stat": "spelldmg", "value": 3.0}
        ]
    }
]

# --- Utility Functions ---
def json_serial(obj):
    if isinstance(obj, (datetime,)):
        return obj.isoformat()
    raise TypeError("Type not serializable")

def check_attribute(response: dict, attr: str, expected_type: type) -> Tuple[bool, str]:
    if attr not in response:
        return False, f"Missing attribute: {attr}"
    if not isinstance(response[attr], expected_type):
        return False, f"Wrong type for {attr}: expected {expected_type.__name__}, got {type(response[attr]).__name__}"
    return True, ""

def log_result(endpoint: str, test_name: str, passed: bool, msg: str):
    if passed:
        logger.info(f"[GREEN] {endpoint} {test_name} OK")
    else:
        logger.error(f"[RED] {endpoint} {test_name} FAIL: {msg}")

def get_auth_headers(token: str = None, api_key: str = None) -> Dict[str, str]:
    """Get authentication headers for requests"""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if api_key:
        headers["X-API-Key"] = api_key
    return headers

def login_user() -> str:
    """Login and return access token"""
    endpoint = f"{API_BASE}/auth/login"
    try:
        response = requests.post(endpoint, json=ADMIN_USER)
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            logger.error(f"[RED] Login failed: Status {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"[RED] Login failed: {str(e)}")
        return None

# --- Weight Sets Test Functions ---
def test_get_weight_sets(token: str):
    """Test getting all weight sets for the authenticated user"""
    logger.info("Testing GET /user/weight-sets endpoint...")
    
    endpoint = f"{API_BASE}/user/weight-sets"
    
    if not token:
        logger.error("[RED] GET /user/weight-sets FAIL: No token provided")
        return
    
    # Test 1: Authenticated access
    try:
        headers = get_auth_headers(token=token)
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Check required attributes
            for attr, expected_type in [("weight_sets", list)]:
                passed, msg = check_attribute(data, attr, expected_type)
                log_result("GET /user/weight-sets", f"authenticated_{attr}", passed, msg)
            
            # Check weight set structure if any exist
            if data.get("weight_sets"):
                weight_set = data["weight_sets"][0]
                for attr, expected_type in [("id", int), ("name", str), ("description", str), ("weights", list), ("created_at", str), ("updated_at", str)]:
                    passed, msg = check_attribute(weight_set, attr, expected_type)
                    log_result("GET /user/weight-sets", f"weight_set_{attr}", passed, msg)
                
                # Check weight structure
                if weight_set.get("weights"):
                    weight = weight_set["weights"][0]
                    for attr, expected_type in [("stat", str), ("value", (int, float))]:
                        passed, msg = check_attribute(weight, attr, expected_type)
                        log_result("GET /user/weight-sets", f"weight_{attr}", passed, msg)
        else:
            logger.error(f"[RED] GET /user/weight-sets authenticated FAIL: Status {response.status_code}")
    except Exception as e:
        logger.error(f"[RED] GET /user/weight-sets authenticated FAIL: {str(e)}")
    
    # Test 2: Unauthenticated access (should fail)
    try:
        response = requests.get(endpoint)
        if response.status_code == 401:
            logger.info(f"[GREEN] GET /user/weight-sets unauthenticated OK: Correctly rejected")
        else:
            logger.error(f"[RED] GET /user/weight-sets unauthenticated FAIL: Expected 401, got {response.status_code}")
    except Exception as e:
        logger.error(f"[RED] GET /user/weight-sets unauthenticated FAIL: {str(e)}")

def test_create_weight_set(token: str) -> int:
    """Test creating a new weight set"""
    logger.info("Testing POST /user/weight-sets endpoint...")
    
    endpoint = f"{API_BASE}/user/weight-sets"
    
    if not token:
        logger.error("[RED] POST /user/weight-sets FAIL: No token provided")
        return None
    
    # Test 1: Valid weight set creation
    try:
        headers = get_auth_headers(token=token)
        weight_set_data = SAMPLE_WEIGHT_SETS[0]  # Tank Weights
        
        response = requests.post(endpoint, json=weight_set_data, headers=headers)
        if response.status_code in [200, 201]:
            data = response.json()
            # Check required attributes
            for attr, expected_type in [("id", int), ("name", str), ("description", str), ("weights", list), ("created_at", str), ("updated_at", str)]:
                passed, msg = check_attribute(data, attr, expected_type)
                log_result("POST /user/weight-sets", f"valid_create_{attr}", passed, msg)
            
            # Verify the data matches what we sent
            if data.get("name") == weight_set_data["name"]:
                logger.info(f"[GREEN] POST /user/weight-sets name_match OK")
            else:
                logger.error(f"[RED] POST /user/weight-sets name_match FAIL: Expected {weight_set_data['name']}, got {data.get('name')}")
            
            return data.get("id")
        else:
            logger.error(f"[RED] POST /user/weight-sets valid_create FAIL: Status {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"[RED] POST /user/weight-sets valid_create FAIL: {str(e)}")
        return None
    
    # Test 2: Invalid weight set (missing name)
    try:
        headers = get_auth_headers(token=token)
        invalid_data = {
            "description": "Invalid weight set",
            "weights": [{"stat": "hp", "value": 1.0}]
        }
        
        response = requests.post(endpoint, json=invalid_data, headers=headers)
        if response.status_code == 400:
            logger.info(f"[GREEN] POST /user/weight-sets invalid_name OK: Correctly rejected")
        else:
            logger.error(f"[RED] POST /user/weight-sets invalid_name FAIL: Expected 400, got {response.status_code}")
    except Exception as e:
        logger.error(f"[RED] POST /user/weight-sets invalid_name FAIL: {str(e)}")
    
    # Test 3: Invalid weight set (empty weights)
    try:
        headers = get_auth_headers(token=token)
        invalid_data = {
            "name": "Empty Weights",
            "description": "Weight set with no weights",
            "weights": []
        }
        
        response = requests.post(endpoint, json=invalid_data, headers=headers)
        if response.status_code == 400:
            logger.info(f"[GREEN] POST /user/weight-sets empty_weights OK: Correctly rejected")
        else:
            logger.error(f"[RED] POST /user/weight-sets empty_weights FAIL: Expected 400, got {response.status_code}")
    except Exception as e:
        logger.error(f"[RED] POST /user/weight-sets empty_weights FAIL: {str(e)}")

def test_get_weight_set(token: str, weight_set_id: int):
    """Test getting a specific weight set"""
    logger.info(f"Testing GET /user/weight-sets/{weight_set_id} endpoint...")
    
    endpoint = f"{API_BASE}/user/weight-sets/{weight_set_id}"
    
    if not token:
        logger.error("[RED] GET /user/weight-sets/{id} FAIL: No token provided")
        return
    
    if not weight_set_id:
        logger.error("[RED] GET /user/weight-sets/{id} FAIL: No weight set ID provided")
        return
    
    # Test 1: Valid weight set retrieval
    try:
        headers = get_auth_headers(token=token)
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Check required attributes
            for attr, expected_type in [("id", int), ("name", str), ("description", str), ("weights", list), ("created_at", str), ("updated_at", str)]:
                passed, msg = check_attribute(data, attr, expected_type)
                log_result(f"GET /user/weight-sets/{weight_set_id}", f"valid_get_{attr}", passed, msg)
            
            # Verify the ID matches
            if data.get("id") == weight_set_id:
                logger.info(f"[GREEN] GET /user/weight-sets/{weight_set_id} id_match OK")
            else:
                logger.error(f"[RED] GET /user/weight-sets/{weight_set_id} id_match FAIL: Expected {weight_set_id}, got {data.get('id')}")
        else:
            logger.error(f"[RED] GET /user/weight-sets/{weight_set_id} valid_get FAIL: Status {response.status_code}")
    except Exception as e:
        logger.error(f"[RED] GET /user/weight-sets/{weight_set_id} valid_get FAIL: {str(e)}")
    
    # Test 2: Non-existent weight set
    try:
        headers = get_auth_headers(token=token)
        response = requests.get(f"{API_BASE}/user/weight-sets/99999", headers=headers)
        if response.status_code == 404:
            logger.info(f"[GREEN] GET /user/weight-sets/99999 not_found OK: Correctly rejected")
        else:
            logger.error(f"[RED] GET /user/weight-sets/99999 not_found FAIL: Expected 404, got {response.status_code}")
    except Exception as e:
        logger.error(f"[RED] GET /user/weight-sets/99999 not_found FAIL: {str(e)}")
    
    # Test 3: Unauthenticated access (should fail)
    try:
        response = requests.get(endpoint)
        if response.status_code == 401:
            logger.info(f"[GREEN] GET /user/weight-sets/{weight_set_id} unauthenticated OK: Correctly rejected")
        else:
            logger.error(f"[RED] GET /user/weight-sets/{weight_set_id} unauthenticated FAIL: Expected 401, got {response.status_code}")
    except Exception as e:
        logger.error(f"[RED] GET /user/weight-sets/{weight_set_id} unauthenticated FAIL: {str(e)}")

def test_update_weight_set(token: str, weight_set_id: int):
    """Test updating a weight set"""
    logger.info(f"Testing PUT /user/weight-sets/{weight_set_id} endpoint...")
    
    endpoint = f"{API_BASE}/user/weight-sets/{weight_set_id}"
    
    if not token:
        logger.error("[RED] PUT /user/weight-sets/{id} FAIL: No token provided")
        return
    
    if not weight_set_id:
        logger.error("[RED] PUT /user/weight-sets/{id} FAIL: No weight set ID provided")
        return
    
    # Test 1: Valid weight set update
    try:
        headers = get_auth_headers(token=token)
        update_data = {
            "name": "Updated Tank Weights",
            "description": "Updated weights optimized for tanking",
            "weights": [
                {"stat": "hp", "value": 2.5},
                {"stat": "ac", "value": 2.0},
                {"stat": "sta", "value": 1.5},
                {"stat": "str", "value": 1.2},
                {"stat": "haste", "value": 1.0}
            ]
        }
        
        response = requests.put(endpoint, json=update_data, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Check required attributes
            for attr, expected_type in [("id", int), ("name", str), ("description", str), ("weights", list), ("created_at", str), ("updated_at", str)]:
                passed, msg = check_attribute(data, attr, expected_type)
                log_result(f"PUT /user/weight-sets/{weight_set_id}", f"valid_update_{attr}", passed, msg)
            
            # Verify the data was updated
            if data.get("name") == update_data["name"]:
                logger.info(f"[GREEN] PUT /user/weight-sets/{weight_set_id} name_update OK")
            else:
                logger.error(f"[RED] PUT /user/weight-sets/{weight_set_id} name_update FAIL: Expected {update_data['name']}, got {data.get('name')}")
            
            # Verify weights were updated
            if len(data.get("weights", [])) == len(update_data["weights"]):
                logger.info(f"[GREEN] PUT /user/weight-sets/{weight_set_id} weights_count_update OK")
            else:
                logger.error(f"[RED] PUT /user/weight-sets/{weight_set_id} weights_count_update FAIL: Expected {len(update_data['weights'])}, got {len(data.get('weights', []))}")
        else:
            logger.error(f"[RED] PUT /user/weight-sets/{weight_set_id} valid_update FAIL: Status {response.status_code}")
    except Exception as e:
        logger.error(f"[RED] PUT /user/weight-sets/{weight_set_id} valid_update FAIL: {str(e)}")
    
    # Test 2: Partial update (only weights)
    try:
        headers = get_auth_headers(token=token)
        partial_update = {
            "weights": [
                {"stat": "hp", "value": 3.0},
                {"stat": "ac", "value": 2.5}
            ]
        }
        
        response = requests.put(endpoint, json=partial_update, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Verify only weights were updated
            if len(data.get("weights", [])) == len(partial_update["weights"]):
                logger.info(f"[GREEN] PUT /user/weight-sets/{weight_set_id} partial_update OK")
            else:
                logger.error(f"[RED] PUT /user/weight-sets/{weight_set_id} partial_update FAIL: Expected {len(partial_update['weights'])}, got {len(data.get('weights', []))}")
        else:
            logger.error(f"[RED] PUT /user/weight-sets/{weight_set_id} partial_update FAIL: Status {response.status_code}")
    except Exception as e:
        logger.error(f"[RED] PUT /user/weight-sets/{weight_set_id} partial_update FAIL: {str(e)}")
    
    # Test 3: Invalid update (empty weights)
    try:
        headers = get_auth_headers(token=token)
        invalid_update = {
            "weights": []
        }
        
        response = requests.put(endpoint, json=invalid_update, headers=headers)
        if response.status_code == 400:
            logger.info(f"[GREEN] PUT /user/weight-sets/{weight_set_id} invalid_update OK: Correctly rejected")
        else:
            logger.error(f"[RED] PUT /user/weight-sets/{weight_set_id} invalid_update FAIL: Expected 400, got {response.status_code}")
    except Exception as e:
        logger.error(f"[RED] PUT /user/weight-sets/{weight_set_id} invalid_update FAIL: {str(e)}")

def test_delete_weight_set(token: str, weight_set_id: int):
    """Test deleting a weight set"""
    logger.info(f"Testing DELETE /user/weight-sets/{weight_set_id} endpoint...")
    
    endpoint = f"{API_BASE}/user/weight-sets/{weight_set_id}"
    
    if not token:
        logger.error("[RED] DELETE /user/weight-sets/{id} FAIL: No token provided")
        return
    
    if not weight_set_id:
        logger.error("[RED] DELETE /user/weight-sets/{id} FAIL: No weight set ID provided")
        return
    
    # Test 1: Valid weight set deletion
    try:
        headers = get_auth_headers(token=token)
        response = requests.delete(endpoint, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Check required attributes
            for attr, expected_type in [("message", str)]:
                passed, msg = check_attribute(data, attr, expected_type)
                log_result(f"DELETE /user/weight-sets/{weight_set_id}", f"valid_delete_{attr}", passed, msg)
            
            logger.info(f"[GREEN] DELETE /user/weight-sets/{weight_set_id} valid_delete OK")
        else:
            logger.error(f"[RED] DELETE /user/weight-sets/{weight_set_id} valid_delete FAIL: Status {response.status_code}")
    except Exception as e:
        logger.error(f"[RED] DELETE /user/weight-sets/{weight_set_id} valid_delete FAIL: {str(e)}")
    
    # Test 2: Delete non-existent weight set
    try:
        headers = get_auth_headers(token=token)
        response = requests.delete(f"{API_BASE}/user/weight-sets/99999", headers=headers)
        if response.status_code == 404:
            logger.info(f"[GREEN] DELETE /user/weight-sets/99999 not_found OK: Correctly rejected")
        else:
            logger.error(f"[RED] DELETE /user/weight-sets/99999 not_found FAIL: Expected 404, got {response.status_code}")
    except Exception as e:
        logger.error(f"[RED] DELETE /user/weight-sets/99999 not_found FAIL: {str(e)}")
    
    # Test 3: Unauthenticated deletion (should fail)
    try:
        response = requests.delete(endpoint)
        if response.status_code == 401:
            logger.info(f"[GREEN] DELETE /user/weight-sets/{weight_set_id} unauthenticated OK: Correctly rejected")
        else:
            logger.error(f"[RED] DELETE /user/weight-sets/{weight_set_id} unauthenticated FAIL: Expected 401, got {response.status_code}")
    except Exception as e:
        logger.error(f"[RED] DELETE /user/weight-sets/{weight_set_id} unauthenticated FAIL: {str(e)}")

def test_weight_sets_integration():
    """Test the complete weight sets workflow"""
    logger.info("Testing Weight Sets Integration Workflow...")
    
    # Step 1: Login
    token = login_user()
    if not token:
        logger.error("[RED] Weight Sets Integration FAIL: Could not login")
        return
    
    # Step 2: Get initial weight sets
    test_get_weight_sets(token)
    
    # Step 3: Create a new weight set
    weight_set_id = test_create_weight_set(token)
    
    if weight_set_id:
        # Step 4: Get the created weight set
        test_get_weight_set(token, weight_set_id)
        
        # Step 5: Update the weight set
        test_update_weight_set(token, weight_set_id)
        
        # Step 6: Delete the weight set
        test_delete_weight_set(token, weight_set_id)
        
        # Step 7: Verify deletion (should return 404)
        try:
            headers = get_auth_headers(token=token)
            response = requests.get(f"{API_BASE}/user/weight-sets/{weight_set_id}", headers=headers)
            if response.status_code == 404:
                logger.info(f"[GREEN] Weight Sets Integration deletion_verification OK")
            else:
                logger.error(f"[RED] Weight Sets Integration deletion_verification FAIL: Expected 404, got {response.status_code}")
        except Exception as e:
            logger.error(f"[RED] Weight Sets Integration deletion_verification FAIL: {str(e)}")
    
    logger.info("Weight Sets Integration Workflow completed!")

def run_weight_sets_tests():
    """Run all weight sets tests"""
    logger.info("Starting Weight Sets API Tests...")
    
    # Run integration test
    test_weight_sets_integration()
    
    logger.info("Weight Sets API Tests completed!")

if __name__ == "__main__":
    run_weight_sets_tests() 