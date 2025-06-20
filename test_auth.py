#!/usr/bin/env python3
"""
Test script for the EQDB authentication system
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:5001"
API_BASE = f"{BASE_URL}/api/v1"

def test_login():
    """Test user login"""
    print("🔐 Testing user login...")
    
    login_data = {
        "email": "aepod23@gmail.com",
        "password": "frogluck23"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"   User: {data['user']['email']}")
            print(f"   Admin: {data['user']['is_admin']}")
            print(f"   Access Token: {data['access_token'][:20]}...")
            return data['access_token'], data['refresh_token']
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None, None

def test_profile(access_token):
    """Test getting user profile"""
    print("\n👤 Testing user profile...")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(f"{API_BASE}/auth/profile", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Profile retrieved successfully!")
            print(f"   User ID: {data['id']}")
            print(f"   Email: {data['email']}")
            print(f"   Admin: {data['is_admin']}")
            print(f"   Created: {data['created_at']}")
        else:
            print(f"❌ Profile retrieval failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Profile error: {e}")

def test_api_keys(access_token):
    """Test API key management"""
    print("\n🔑 Testing API key management...")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        # Get existing API keys
        response = requests.get(f"{API_BASE}/auth/api-keys", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API keys retrieved successfully!")
            print(f"   Number of keys: {len(data['api_keys'])}")
            
            # Create a new API key
            key_data = {"name": "Test API Key"}
            response = requests.post(f"{API_BASE}/auth/api-keys", json=key_data, headers=headers)
            
            if response.status_code == 201:
                new_key_data = response.json()
                print("✅ API key created successfully!")
                print(f"   Key name: {new_key_data['name']}")
                print(f"   Key prefix: {new_key_data['key_prefix']}")
                print(f"   Full key: {new_key_data['full_key']}")
                
                # Test using the API key
                test_api_key_usage(new_key_data['full_key'])
                
                # Delete the test API key
                response = requests.delete(f"{API_BASE}/auth/api-keys/{new_key_data['id']}", headers=headers)
                
                if response.status_code == 200:
                    print("✅ Test API key deleted successfully!")
                else:
                    print(f"❌ Failed to delete test API key: {response.status_code}")
                    
            else:
                print(f"❌ API key creation failed: {response.status_code}")
                print(f"   Response: {response.text}")
        else:
            print(f"❌ API keys retrieval failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ API key error: {e}")

def test_api_key_usage(api_key):
    """Test using an API key to access protected endpoints"""
    print("\n🔑 Testing API key usage...")
    
    headers = {"X-API-KEY": api_key}
    
    try:
        # Test accessing a protected endpoint
        response = requests.get(f"{API_BASE}/items?name=dagger", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API key authentication successful!")
            print(f"   Retrieved {len(data)} items")
        else:
            print(f"❌ API key authentication failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ API key usage error: {e}")

def test_preferences(access_token):
    """Test user preferences"""
    print("\n⚙️ Testing user preferences...")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        # Get current preferences
        response = requests.get(f"{API_BASE}/auth/preferences", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Preferences retrieved successfully!")
            print(f"   Current preferences: {data}")
            
            # Update preferences
            new_prefs = {
                "theme": "dark",
                "default_expansion": 0,
                "items_per_page": 25
            }
            
            response = requests.put(f"{API_BASE}/auth/preferences", json=new_prefs, headers=headers)
            
            if response.status_code == 200:
                print("✅ Preferences updated successfully!")
                
                # Verify the update
                response = requests.get(f"{API_BASE}/auth/preferences", headers=headers)
                if response.status_code == 200:
                    updated_data = response.json()
                    print(f"   Updated preferences: {updated_data}")
            else:
                print(f"❌ Preferences update failed: {response.status_code}")
                print(f"   Response: {response.text}")
        else:
            print(f"❌ Preferences retrieval failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Preferences error: {e}")

def test_protected_endpoints(access_token):
    """Test accessing protected API endpoints"""
    print("\n🛡️ Testing protected endpoints...")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        # Test items endpoint
        response = requests.get(f"{API_BASE}/items?name=dagger", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Items endpoint accessible!")
            print(f"   Retrieved {len(data)} items")
        else:
            print(f"❌ Items endpoint failed: {response.status_code}")
            
        # Test spells endpoint
        response = requests.get(f"{API_BASE}/spells?name=heal", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Spells endpoint accessible!")
            print(f"   Retrieved {len(data)} spells")
        else:
            print(f"❌ Spells endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Protected endpoints error: {e}")

def main():
    """Run all authentication tests"""
    print("🧪 EQDB Authentication System Test")
    print("=" * 50)
    
    # Test login
    access_token, refresh_token = test_login()
    
    if not access_token:
        print("\n❌ Cannot proceed without valid authentication")
        sys.exit(1)
    
    # Test various features
    test_profile(access_token)
    test_preferences(access_token)
    test_api_keys(access_token)
    test_protected_endpoints(access_token)
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main() 