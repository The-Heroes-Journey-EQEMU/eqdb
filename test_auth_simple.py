#!/usr/bin/env python3

import requests
import json

# First, login to get a real token
login_url = "http://localhost:5001/api/v1/auth/login"
login_data = {
    "email": "aepod23@gmail.com",
    "password": "frogluck23"
}

try:
    print("1. Logging in...")
    login_response = requests.post(login_url, json=login_data)
    if login_response.status_code == 200:
        token = login_response.json().get("access_token")
        print(f"Login successful, got token: {token[:20]}...")
    else:
        print(f"Login failed: {login_response.status_code} - {login_response.text}")
        exit(1)
except Exception as e:
    print(f"Login request failed: {e}")
    exit(1)

# Test a simple authenticated endpoint
url = "http://localhost:5001/api/v1/user/weight-sets"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

try:
    print("2. Testing GET endpoint...")
    response = requests.get(url, headers=headers)
    print(f"GET Status Code: {response.status_code}")
    print(f"GET Response: {response.text[:200]}...")
except Exception as e:
    print(f"GET request failed: {e}")

# Test POST with minimal data
try:
    print("3. Testing POST endpoint with minimal data...")
    data = {
        "name": "Test",
        "weights": [{"stat": "hp", "value": 1.0}]
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"POST Status Code: {response.status_code}")
    print(f"POST Response: {response.text}")
except Exception as e:
    print(f"POST request failed: {e}") 