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
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123"
}

ADMIN_USER = {
    "email": "aepod23@gmail.com",
    "password": "frogluck23"
}

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

# --- Authentication Test Cases ---
AUTH_ENDPOINTS = [
    # Login endpoint
    ("/auth/login", [
        {"email": ADMIN_USER["email"], "password": ADMIN_USER["password"]},
        {"email": "nonexistent@example.com", "password": "wrongpassword"},
        {"email": "", "password": ""},
        {"email": "invalid-email", "password": "password"},
    ],
    {"access_token": str, "refresh_token": str, "user": dict}
    ),
    
    # Users endpoint (admin only)
    ("/auth/users", [
        {"email": "newuser@example.com", "password": "newpassword123", "is_admin": False},
        {"email": ADMIN_USER["email"], "password": "password123", "is_admin": False},  # Should fail - user exists
        {"email": "invalid-email", "password": "short", "is_admin": False},  # Should fail - validation
        {"email": "", "password": "", "is_admin": False},  # Should fail - empty fields
    ],
    {"message": str, "user_id": int}
    ),
    
    # Profile endpoint
    ("/auth/profile", [
        {},  # Requires authentication
    ],
    {"id": int, "email": str, "is_admin": bool, "created_at": str, "last_login": str, "preferences": str}
    ),
    
    # Change password endpoint
    ("/auth/change-password", [
        {"current_password": ADMIN_USER["password"], "new_password": "newadmin123"},
        {"current_password": "wrongpassword", "new_password": "newpassword123"},  # Should fail
        {"current_password": "", "new_password": ""},  # Should fail - empty fields
    ],
    {"message": str}
    ),
    
    # API Keys endpoint
    ("/auth/api-keys", [
        {},  # List API keys
    ],
    {"api_keys": list}
    ),
    
    # Create API Key endpoint
    ("/auth/api-keys", [
        {"name": "Test API Key"},
        {"name": ""},  # Should fail - empty name
    ],
    {"id": int, "name": str, "key_prefix": str, "full_key": str, "created_at": str, "is_active": bool}
    ),
]

# --- Test Functions ---
def test_login_endpoint():
    """Test the login endpoint with various scenarios"""
    logger.info("Testing /auth/login endpoint...")
    
    endpoint = f"{API_BASE}/auth/login"
    
    # Test 1: Valid admin login
    try:
        response = requests.post(endpoint, json=ADMIN_USER)
        if response.status_code == 200:
            data = response.json()
            # Check required attributes
            for attr, expected_type in [("access_token", str), ("refresh_token", str), ("user", dict)]:
                passed, msg = check_attribute(data, attr, expected_type)
                log_result("/auth/login", f"valid_admin_{attr}", passed, msg)
            
            # Check user attributes
            if "user" in data:
                user = data["user"]
                for attr, expected_type in [("id", int), ("email", str), ("is_admin", bool)]:
                    passed, msg = check_attribute(user, attr, expected_type)
                    log_result("/auth/login", f"user_{attr}", passed, msg)
            
            return data.get("access_token")
        else:
            logger.error(f"[RED] /auth/login valid_admin FAIL: Status {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"[RED] /auth/login valid_admin FAIL: {str(e)}")
        return None

def test_users_endpoint(token: str):
    """Test the users endpoint with admin authentication"""
    logger.info("Testing /auth/users endpoint...")
    
    endpoint = f"{API_BASE}/auth/users"
    
    if not token:
        logger.error("[RED] /auth/users FAIL: No token provided")
        return
    
    # Test 1: Valid new user creation (admin only)
    import time
    timestamp = int(time.time())
    new_user = {
        "email": f"newuser{timestamp}@example.com",
        "password": "newpassword123",
        "is_admin": False
    }
    
    try:
        headers = get_auth_headers(token=token)
        response = requests.post(endpoint, json=new_user, headers=headers)
        if response.status_code in [200, 201]:
            data = response.json()
            # Check required attributes
            for attr, expected_type in [("message", str), ("user_id", int)]:
                passed, msg = check_attribute(data, attr, expected_type)
                log_result("/auth/users", f"valid_user_{attr}", passed, msg)
        else:
            logger.error(f"[RED] /auth/users valid_user FAIL: Status {response.status_code}")
    except Exception as e:
        logger.error(f"[RED] /auth/users valid_user FAIL: {str(e)}")
    
    # Test 2: Duplicate user creation (should fail)
    try:
        headers = get_auth_headers(token=token)
        response = requests.post(endpoint, json=ADMIN_USER, headers=headers)
        if response.status_code == 409:
            logger.info(f"[GREEN] /auth/users duplicate_user OK: Correctly rejected")
        else:
            logger.error(f"[RED] /auth/users duplicate_user FAIL: Expected 409, got {response.status_code}")
    except Exception as e:
        logger.error(f"[RED] /auth/users duplicate_user FAIL: {str(e)}")

def test_profile_endpoint(token: str):
    """Test the profile endpoint with authentication"""
    logger.info("Testing /auth/profile endpoint...")
    
    endpoint = f"{API_BASE}/auth/profile"
    
    if not token:
        logger.error("[RED] /auth/profile FAIL: No token provided")
        return
    
    # Test 1: Authenticated profile access
    try:
        headers = get_auth_headers(token=token)
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Check required attributes
            for attr, expected_type in [("id", int), ("email", str), ("is_admin", bool), ("created_at", str), ("last_login", str), ("preferences", str)]:
                passed, msg = check_attribute(data, attr, expected_type)
                log_result("/auth/profile", f"authenticated_{attr}", passed, msg)
        else:
            logger.error(f"[RED] /auth/profile authenticated FAIL: Status {response.status_code}")
    except Exception as e:
        logger.error(f"[RED] /auth/profile authenticated FAIL: {str(e)}")
    
    # Test 2: Unauthenticated profile access (should fail)
    try:
        response = requests.get(endpoint)
        if response.status_code == 401:
            logger.info(f"[GREEN] /auth/profile unauthenticated OK: Correctly rejected")
        else:
            logger.error(f"[RED] /auth/profile unauthenticated FAIL: Expected 401, got {response.status_code}")
    except Exception as e:
        logger.error(f"[RED] /auth/profile unauthenticated FAIL: {str(e)}")

def test_change_password_endpoint(token: str):
    """Test the change password endpoint"""
    logger.info("Testing /auth/change-password endpoint...")
    
    endpoint = f"{API_BASE}/auth/change-password"
    
    if not token:
        logger.error("[RED] /auth/change-password FAIL: No token provided")
        return
    
    # Test 1: Valid password change
    try:
        headers = get_auth_headers(token=token)
        data = {
            "current_password": ADMIN_USER["password"],
            "new_password": "newadmin123"
        }
        response = requests.post(endpoint, json=data, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            # Check required attributes
            for attr, expected_type in [("message", str)]:
                passed, msg = check_attribute(response_data, attr, expected_type)
                log_result("/auth/change-password", f"valid_change_{attr}", passed, msg)
            
            # Change password back
            data = {
                "current_password": "newadmin123",
                "new_password": ADMIN_USER["password"]
            }
            requests.post(endpoint, json=data, headers=headers)
        else:
            logger.error(f"[RED] /auth/change-password valid_change FAIL: Status {response.status_code}")
    except Exception as e:
        logger.error(f"[RED] /auth/change-password valid_change FAIL: {str(e)}")
    
    # Test 2: Wrong current password (should fail)
    try:
        headers = get_auth_headers(token=token)
        data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        }
        response = requests.post(endpoint, json=data, headers=headers)
        if response.status_code == 400:
            logger.info(f"[GREEN] /auth/change-password wrong_current OK: Correctly rejected")
        else:
            logger.error(f"[RED] /auth/change-password wrong_current FAIL: Expected 400, got {response.status_code}")
    except Exception as e:
        logger.error(f"[RED] /auth/change-password wrong_current FAIL: {str(e)}")

def test_api_keys_endpoint(token: str):
    """Test the API keys endpoints"""
    logger.info("Testing /auth/api-keys endpoints...")
    
    list_endpoint = f"{API_BASE}/auth/api-keys"
    create_endpoint = f"{API_BASE}/auth/api-keys"
    
    if not token:
        logger.error("[RED] /auth/api-keys FAIL: No token provided")
        return
    
    # Test 1: List API keys
    try:
        headers = get_auth_headers(token=token)
        response = requests.get(list_endpoint, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Check required attributes
            for attr, expected_type in [("api_keys", list)]:
                passed, msg = check_attribute(data, attr, expected_type)
                log_result("/auth/api-keys", f"list_{attr}", passed, msg)
        else:
            logger.error(f"[RED] /auth/api-keys list FAIL: Status {response.status_code}")
    except Exception as e:
        logger.error(f"[RED] /auth/api-keys list FAIL: {str(e)}")
    
    # Test 2: Create API key
    try:
        headers = get_auth_headers(token=token)
        data = {
            "name": "Test API Key"
        }
        response = requests.post(create_endpoint, json=data, headers=headers)
        if response.status_code in [200, 201]:
            response_data = response.json()
            # Check required attributes
            for attr, expected_type in [("id", int), ("name", str), ("key_prefix", str), ("full_key", str), ("created_at", str), ("is_active", bool)]:
                passed, msg = check_attribute(response_data, attr, expected_type)
                log_result("/auth/api-keys", f"create_{attr}", passed, msg)
            
            # Store the API key for later tests
            return response_data.get("full_key")
        else:
            logger.error(f"[RED] /auth/api-keys create FAIL: Status {response.status_code}")
    except Exception as e:
        logger.error(f"[RED] /auth/api-keys create FAIL: {str(e)}")
    
    return None

def test_api_key_authentication(api_key: str):
    """Test API key authentication"""
    logger.info("Testing API key authentication...")
    
    endpoint = f"{API_BASE}/auth/profile"
    
    if not api_key:
        logger.error("[RED] API key authentication FAIL: No API key provided")
        return
    
    # Test 1: API key authentication
    try:
        headers = get_auth_headers(api_key=api_key)
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Check required attributes
            for attr, expected_type in [("id", int), ("email", str), ("is_admin", bool)]:
                passed, msg = check_attribute(data, attr, expected_type)
                log_result("API_KEY_AUTH", f"profile_{attr}", passed, msg)
        else:
            logger.error(f"[RED] API key authentication FAIL: Status {response.status_code}")
    except Exception as e:
        logger.error(f"[RED] API key authentication FAIL: {str(e)}")

def run_auth_tests():
    """Run all authentication tests"""
    logger.info("Starting Authentication API Tests...")
    
    # Test 1: Login to get token
    token = test_login_endpoint()
    
    # Test 2: Create new user (admin only)
    test_users_endpoint(token)
    
    # Test 3: Profile endpoint
    test_profile_endpoint(token)
    
    # Test 4: Change password
    test_change_password_endpoint(token)
    
    # Test 5: API keys
    api_key = test_api_keys_endpoint(token)
    
    # Test 6: API key authentication
    test_api_key_authentication(api_key)
    
    logger.info("Authentication API Tests completed!")

if __name__ == "__main__":
    run_auth_tests() 