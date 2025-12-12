#!/usr/bin/env python3
"""
Simple API Test Script
Tests all the endpoints of the Organization Management Service
"""

import requests
import json
import time
from datetime import datetime
import socket

# Configuration - Auto-detect which port the service is running on
def detect_service_port():
    """Try to detect which port the Organization Management Service is running on."""
    for port in [8000, 8001, 8002]:
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=2)
            if response.status_code == 200:
                # Check if it's our service (even if MongoDB connection fails, server is running)
                data = response.json()
                if "status" in data or "Organization Management Service" in str(data):
                    return port
        except Exception as e:
            continue
    # Default to 8000 if not found (standard FastAPI port)
    print("⚠ Warning: Could not detect server port, defaulting to 8000")
    return 8000

PORT = detect_service_port()
BASE_URL = f"http://localhost:{PORT}"
TEST_ORG_NAME = f"Test Org {datetime.now().strftime('%H%M%S')}"
TEST_EMAIL = f"admin{datetime.now().strftime('%H%M%S')}@test.com"
TEST_PASSWORD = "SecurePass123"

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_success(message):
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message):
    print(f"{RED}✗ {message}{RESET}")


def print_info(message):
    print(f"{BLUE}ℹ {message}{RESET}")


def print_warning(message):
    print(f"{YELLOW}⚠ {message}{RESET}")


def print_section(title):
    print(f"\n{BLUE}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{RESET}\n")


def test_health_check():
    """Test the health check endpoint"""
    print_section("1. Testing Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print_success("Health check passed")
            print_info(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        return False


def test_create_organization():
    """Test organization creation"""
    print_section("2. Testing Organization Creation")
    try:
        data = {
            "organization_name": TEST_ORG_NAME,
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        print_info(f"Creating organization: {TEST_ORG_NAME}")
        response = requests.post(f"{BASE_URL}/org/create", json=data, timeout=10)
        
        if response.status_code == 201:
            print_success("Organization created successfully")
            result = response.json()
            print_info(f"Organization ID: {result.get('id', 'N/A')}")
            print_info(f"Collection Name: {result.get('collection_name', 'N/A')}")
            print_info(f"Admin Email: {result.get('admin_email', 'N/A')}")
            return True, result
        else:
            print_error(f"Failed to create organization: {response.status_code}")
            try:
                error_detail = response.json()
                if 'detail' in error_detail:
                    error_msg = error_detail['detail']
                    print_error(f"Error detail: {error_msg}")
                    # Check if it's a MongoDB connection issue
                    if 'MongoDB' in error_msg or 'connection' in error_msg.lower() or 'authentication' in error_msg.lower():
                        print_warning("⚠️  MongoDB connection issue detected. Please check:")
                        print_warning("   1. MongoDB Atlas password in .env file")
                        print_warning("   2. IP whitelist in MongoDB Atlas Network Access")
                        print_warning("   3. Run: python scripts/ping_mongo.py")
                else:
                    print_error(f"Response: {response.text[:200]}")
            except:
                print_error(f"Response: {response.text[:200]}")
            return False, None
    except requests.exceptions.ConnectionError:
        print_error("Connection error: Server is not running!")
        print_warning("Start the server with: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return False, None
    except Exception as e:
        print_error(f"Error creating organization: {str(e)}")
        return False, None


def test_admin_login():
    """Test admin login"""
    print_section("3. Testing Admin Login")
    try:
        data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        print_info(f"Logging in as: {TEST_EMAIL}")
        response = requests.post(f"{BASE_URL}/admin/login", json=data)
        
        if response.status_code == 200:
            print_success("Login successful")
            result = response.json()
            token = result.get('access_token', '')
            if token:
                print_info(f"Token received: {token[:50]}...")
            print_info(f"Organization: {result.get('organization_name', 'N/A')}")
            return True, token
        else:
            print_error(f"Login failed: {response.status_code}")
            try:
                error_detail = response.json()
                if 'detail' in error_detail:
                    print_error(f"Error detail: {error_detail['detail']}")
                else:
                    print_error(f"Response: {response.text}")
            except:
                print_error(f"Response: {response.text}")
            return False, None
    except Exception as e:
        print_error(f"Error during login: {str(e)}")
        return False, None


def test_get_organization():
    """Test getting organization details"""
    print_section("4. Testing Get Organization")
    try:
        params = {"organization_name": TEST_ORG_NAME}
        
        print_info(f"Fetching organization: {TEST_ORG_NAME}")
        response = requests.get(f"{BASE_URL}/org/get", params=params)
        
        if response.status_code == 200:
            print_success("Organization retrieved successfully")
            result = response.json()
            print_info(f"Organization: {json.dumps(result, indent=2, default=str)}")
            return True
        else:
            print_error(f"Failed to get organization: {response.status_code}")
            try:
                error_detail = response.json()
                if 'detail' in error_detail:
                    print_error(f"Error detail: {error_detail['detail']}")
                else:
                    print_error(f"Response: {response.text}")
            except:
                print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error getting organization: {str(e)}")
        return False


def test_update_organization(token):
    """Test updating organization"""
    print_section("5. Testing Update Organization")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        new_email = f"updated_{TEST_EMAIL}"
        new_password = "UpdatedPassword123!"
        
        data = {
            "organization_name": TEST_ORG_NAME,
            "email": new_email,
            "password": new_password
        }
        
        print_info(f"Updating organization admin email to: {new_email}")
        response = requests.put(f"{BASE_URL}/org/update", json=data, headers=headers)
        
        if response.status_code == 200:
            print_success("Organization updated successfully")
            result = response.json()
            print_info(f"New admin email: {result['admin_email']}")
            return True, new_email, new_password
        else:
            print_error(f"Failed to update organization: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False, None, None
    except Exception as e:
        print_error(f"Error updating organization: {str(e)}")
        return False, None, None


def test_delete_organization(token):
    """Test deleting organization"""
    print_section("6. Testing Delete Organization")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        params = {"organization_name": TEST_ORG_NAME}
        
        print_info(f"Deleting organization: {TEST_ORG_NAME}")
        response = requests.delete(f"{BASE_URL}/org/delete", params=params, headers=headers)
        
        if response.status_code == 200:
            print_success("Organization deleted successfully")
            result = response.json()
            print_info(f"Message: {result['message']}")
            return True
        else:
            print_error(f"Failed to delete organization: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error deleting organization: {str(e)}")
        return False


def main():
    """Main test runner"""
    print(f"\n{BLUE}{'='*60}")
    print("  Organization Management Service - API Test Suite")
    print(f"{'='*60}{RESET}\n")
    
    print_info(f"Testing API at: {BASE_URL}")
    print_info(f"Test Organization: {TEST_ORG_NAME}")
    print_info(f"Test Email: {TEST_EMAIL}")
    
    results = []
    
    # Test 1: Health Check
    results.append(("Health Check", test_health_check()))
    time.sleep(1)
    
    # Test 2: Create Organization
    success, org_data = test_create_organization()
    results.append(("Create Organization", success))
    if not success:
        print_warning("Skipping remaining tests due to creation failure")
        print_summary(results)
        return
    time.sleep(1)
    
    # Test 3: Admin Login
    success, token = test_admin_login()
    results.append(("Admin Login", success))
    if not success:
        print_warning("Skipping authenticated tests due to login failure")
        print_summary(results)
        return
    time.sleep(1)
    
    # Test 4: Get Organization
    results.append(("Get Organization", test_get_organization()))
    time.sleep(1)
    
    # Test 5: Update Organization
    success, new_email, new_password = test_update_organization(token)
    results.append(("Update Organization", success))
    time.sleep(1)
    
    # If update was successful, we need a new token
    if success and new_email and new_password:
        print_info("Getting new token after update...")
        try:
            data = {"email": new_email, "password": new_password}
            response = requests.post(f"{BASE_URL}/admin/login", json=data)
            if response.status_code == 200:
                token = response.json().get('access_token', token)
                print_success("New token obtained")
            else:
                print_warning("Could not get new token, using old token")
        except Exception as e:
            print_warning(f"Could not get new token: {e}, using old token")
        time.sleep(1)
    
    # Test 6: Delete Organization
    results.append(("Delete Organization", test_delete_organization(token)))
    
    # Print summary
    print_summary(results)


def print_summary(results):
    """Print test summary"""
    print_section("Test Summary")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        if success:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    if passed == total:
        print(f"{GREEN}All tests passed! ({passed}/{total}){RESET}")
    else:
        print(f"{YELLOW}Some tests failed: {passed}/{total} passed{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted by user{RESET}")
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")

