#!/usr/bin/env python3
"""
Comprehensive test suite for Authentication and Weight Sets API endpoints.
This script tests both authentication functionality and weight sets management.
"""

import sys
import os
import logging
import requests
from datetime import datetime

# Add the parent directory to the path so we can import our test modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our test modules
from auth.test_auth_api import run_auth_tests
from weight_sets.test_weight_sets_api import run_weight_sets_tests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API base URL
API_BASE = "http://127.0.0.1:5001/api/v1"

def check_api_server():
    """Check if the API server is running"""
    try:
        response = requests.get(f"{API_BASE}/", timeout=5)
        if response.status_code == 200:
            logger.info("[GREEN] API server is running and accessible")
            return True
        else:
            logger.error(f"[RED] API server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        logger.error("[RED] Could not connect to API server. Make sure it's running on http://127.0.0.1:5001")
        return False
    except Exception as e:
        logger.error(f"[RED] Error checking API server: {str(e)}")
        return False

def test_swagger_documentation():
    """Test that Swagger documentation is accessible"""
    logger.info("Testing Swagger documentation...")
    
    try:
        # Test Swagger UI (served at /api/v1/)
        response = requests.get(f"{API_BASE}/", timeout=5)
        if response.status_code == 200:
            logger.info("[GREEN] Swagger UI is accessible at /api/v1/")
        else:
            logger.warning(f"[YELLOW] Swagger UI returned status {response.status_code}")
        
        # Test Swagger JSON
        response = requests.get(f"{API_BASE}/swagger.json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "paths" in data:
                logger.info(f"[GREEN] Swagger JSON is valid with {len(data['paths'])} endpoints")
                
                # Check for auth endpoints
                auth_endpoints = [path for path in data["paths"].keys() if "auth" in path]
                if auth_endpoints:
                    logger.info(f"[GREEN] Found {len(auth_endpoints)} auth endpoints in Swagger")
                    for endpoint in auth_endpoints:
                        logger.info(f"  - {endpoint}")
                else:
                    logger.warning("[YELLOW] No auth endpoints found in Swagger")
                
                # Check for weight sets endpoints
                weight_endpoints = [path for path in data["paths"].keys() if "weight" in path]
                if weight_endpoints:
                    logger.info(f"[GREEN] Found {len(weight_endpoints)} weight sets endpoints in Swagger")
                    for endpoint in weight_endpoints:
                        logger.info(f"  - {endpoint}")
                else:
                    logger.warning("[YELLOW] No weight sets endpoints found in Swagger")
                
                # Check for other important endpoints
                other_endpoints = [path for path in data["paths"].keys() if "auth" not in path and "weight" not in path]
                logger.info(f"[GREEN] Found {len(other_endpoints)} other endpoints in Swagger")
            else:
                logger.warning("[YELLOW] Swagger JSON missing 'paths' section")
        else:
            logger.warning(f"[YELLOW] Swagger JSON returned status {response.status_code}")
    except Exception as e:
        logger.error(f"[RED] Error testing Swagger documentation: {str(e)}")

def run_all_tests():
    """Run all authentication and weight sets tests"""
    logger.info("=" * 80)
    logger.info("Starting Comprehensive Authentication and Weight Sets API Tests")
    logger.info("=" * 80)
    
    start_time = datetime.now()
    
    # Step 1: Check if API server is running
    if not check_api_server():
        logger.error("[RED] Cannot proceed with tests - API server is not accessible")
        return False
    
    # Step 2: Test Swagger documentation
    test_swagger_documentation()
    
    # Step 3: Run authentication tests
    logger.info("\n" + "=" * 60)
    logger.info("RUNNING AUTHENTICATION TESTS")
    logger.info("=" * 60)
    
    try:
        run_auth_tests()
        logger.info("[GREEN] Authentication tests completed successfully")
    except Exception as e:
        logger.error(f"[RED] Authentication tests failed: {str(e)}")
        return False
    
    # Step 4: Run weight sets tests
    logger.info("\n" + "=" * 60)
    logger.info("RUNNING WEIGHT SETS TESTS")
    logger.info("=" * 60)
    
    try:
        run_weight_sets_tests()
        logger.info("[GREEN] Weight sets tests completed successfully")
    except Exception as e:
        logger.error(f"[RED] Weight sets tests failed: {str(e)}")
        return False
    
    # Step 5: Summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Total test duration: {duration}")
    logger.info(f"API server: http://127.0.0.1:5001")
    logger.info(f"Swagger UI: http://127.0.0.1:5001/swagger")
    logger.info(f"API base: {API_BASE}")
    logger.info("=" * 80)
    
    return True

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "auth":
            logger.info("Running only authentication tests...")
            if check_api_server():
                run_auth_tests()
            else:
                logger.error("[RED] Cannot proceed - API server is not accessible")
        elif sys.argv[1] == "weights":
            logger.info("Running only weight sets tests...")
            if check_api_server():
                run_weight_sets_tests()
            else:
                logger.error("[RED] Cannot proceed - API server is not accessible")
        elif sys.argv[1] == "swagger":
            logger.info("Testing only Swagger documentation...")
            if check_api_server():
                test_swagger_documentation()
            else:
                logger.error("[RED] Cannot proceed - API server is not accessible")
        else:
            logger.error(f"Unknown test type: {sys.argv[1]}")
            logger.info("Available options: auth, weights, swagger, or no argument for all tests")
    else:
        # Run all tests
        success = run_all_tests()
        if success:
            logger.info("[GREEN] All tests completed successfully!")
            sys.exit(0)
        else:
            logger.error("[RED] Some tests failed!")
            sys.exit(1)

if __name__ == "__main__":
    main() 