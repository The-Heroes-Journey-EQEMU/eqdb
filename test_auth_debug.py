#!/usr/bin/env python3

import requests
import json

# Configuration
BASE_URL = "http://localhost:5001/api/v1"
LOGIN_URL = f"{BASE_URL}/auth/login"

# Test credentials
email = "aepod23@gmail.com"
password = "frogluck23"

def test_auth():
    print("Testing authentication...")
    
    # Step 1: Login to get JWT token
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        print(f"Login Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get('access_token')
            print(f"Got token: {token[:20]}...")
            
            # Step 2: Test a simple authenticated endpoint
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Test GET weight sets first (should work)
            get_response = requests.get(f"{BASE_URL}/user/weight-sets", headers=headers)
            print(f"GET weight-sets Status: {get_response.status_code}")
            print(f"GET Response: {get_response.text}")
            
            # Step 3: Test POST weight sets
            weight_data = {
                "name": "Test Weight Set",
                "description": "Test weight set for debugging",
                "weights": [
                    {"stat": "hp", "value": 1.0},
                    {"stat": "mana", "value": 0.5}
                ]
            }
            
            post_response = requests.post(f"{BASE_URL}/user/weight-sets", 
                                        headers=headers, 
                                        json=weight_data)
            print(f"POST weight-sets Status: {post_response.status_code}")
            print(f"POST Response: {post_response.text}")
            
            if post_response.status_code == 500:
                print("500 error - checking if it's a JSON response...")
                try:
                    error_json = post_response.json()
                    print(f"Error JSON: {json.dumps(error_json, indent=2)}")
                except:
                    print("Not a JSON response")
            
        else:
            print(f"Login failed: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_auth() 