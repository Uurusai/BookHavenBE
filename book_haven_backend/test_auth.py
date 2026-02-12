"""
Simple test script for authentication endpoints
Run this after starting the Flask server to test login/register functionality
"""

import requests
import json

BASE_URL = "http://localhost:5000/api/users"

def test_register():
    """Test user registration"""
    print("\n=== Testing User Registration ===")
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123",
        "full_name": "Test User"
    }
    
    response = requests.post(f"{BASE_URL}/register", json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        return response.json().get('token')
    return None

def test_login():
    """Test user login"""
    print("\n=== Testing User Login ===")
    data = {
        "username": "testuser",
        "password": "TestPass123"
    }
    
    response = requests.post(f"{BASE_URL}/login", json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        return response.json().get('token')
    return None

def test_get_current_user(token):
    """Test getting current user info"""
    print("\n=== Testing Get Current User ===")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(f"{BASE_URL}/me", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_update_current_user(token):
    """Test updating current user"""
    print("\n=== Testing Update Current User ===")
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "city": "San Francisco",
        "country": "USA"
    }
    
    response = requests.patch(f"{BASE_URL}/me", json=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_protected_route_without_token():
    """Test accessing protected route without token"""
    print("\n=== Testing Protected Route Without Token ===")
    response = requests.get(f"{BASE_URL}/me")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_invalid_credentials():
    """Test login with invalid credentials"""
    print("\n=== Testing Invalid Login ===")
    data = {
        "username": "testuser",
        "password": "WrongPassword123"
    }
    
    response = requests.post(f"{BASE_URL}/login", json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    print("Starting Authentication Tests...")
    print("Make sure the Flask server is running!")
    
    # Test registration
    token = test_register()
    
    if not token:
        # If registration fails (user might already exist), try login
        token = test_login()
    
    if token:
        # Test authenticated endpoints
        test_get_current_user(token)
        test_update_current_user(token)
    
    # Test error cases
    test_protected_route_without_token()
    test_invalid_credentials()
    
    print("\n=== Tests Complete ===")
