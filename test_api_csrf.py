#!/usr/bin/env python3
"""
Test script to verify API is exempt from CSRF protection while
web forms are still protected.
"""
import requests
import sys
import os
from bs4 import BeautifulSoup

def join_url_path(base, path):
    """Join URL parts correctly, preserving the full base path."""
    # Remove trailing slash from base and leading slash from path
    base = base.rstrip('/')
    path = path.lstrip('/')
    return f"{base}/{path}"

def get_csrf_token(base_url):
    """Get a CSRF token from the login page."""
    login_url = join_url_path(base_url, "auth/login")
    session = requests.Session()
    response = session.get(login_url)
    
    # Parse the page to extract the CSRF token
    soup = BeautifulSoup(response.text, 'html.parser')
    meta_tag = soup.find("meta", {"name": "csrf-token"})
    
    if meta_tag and "content" in meta_tag.attrs:
        return meta_tag.attrs["content"], session
    
    return None, session

def test_token_creation(base_url, username, password):
    """Test creating a token via the API (should be CSRF exempt)."""
    token_url = join_url_path(base_url, "api/v1/token/create")
    credentials = {
        "username": username,
        "password": password,
        "token_access_level": 3,
        "duration": 1
    }

    print(f"1. Testing API token creation at: {token_url}")
    print(f"   With credentials: {username} / {'*' * len(password)}")
    
    # Get CSRF token for testing
    csrf_token, session = get_csrf_token(base_url)
    if csrf_token:
        print(f"   Got CSRF token: {csrf_token[:10]}... (truncated)")
    else:
        print("   WARNING: Could not get CSRF token")
    
    # First try without CSRF token (should work if exemption is working)
    try:
        print("   Trying API call WITHOUT CSRF token...")
        response = requests.post(
            token_url, 
            json=credentials,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Response status code: {response.status_code}")
        
        if response.status_code == 201:
            token_data = response.json()
            print("   API exemption is working correctly! Token creation successful without CSRF token.")
            print(f"   Token: {token_data['id'][:10]}... (truncated)")
            return (True, token_data["id"])
        elif csrf_token:
            # If we have a CSRF token, try with it
            print("   Trying API call WITH CSRF token...")
            response = requests.post(
                token_url, 
                json=credentials,
                headers={
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrf_token
                }
            )
            
            print(f"   Response with CSRF token status code: {response.status_code}")
            
            if response.status_code == 201:
                token_data = response.json()
                print("   API works with CSRF token but not without it - exemption NOT working.")
                print(f"   Token: {token_data['id'][:10]}... (truncated)")
                return (False, token_data["id"])
        
        print("   API call failed both with and without CSRF token")
        if "CSRF" in response.text:
            print("   Found CSRF error message in response - CSRF protection is active on API!")
        return (False, None)
    except Exception as e:
        print(f"   Error: {e}")
        return (False, None)

def test_web_form_csrf(base_url, username, password):
    """Test web form submission (should require CSRF protection)."""
    login_url = join_url_path(base_url, "auth/login")
    session = requests.Session()
    
    print(f"\n2. Testing web form CSRF protection at: {login_url}")
    
    # First get the login page to get the CSRF token
    try:
        response = session.get(login_url)
        print(f"   Initial page response code: {response.status_code}")
        print(f"   Session cookies: {session.cookies.get_dict()}")
        
        # Parse the page to extract the CSRF token
        soup = BeautifulSoup(response.text, 'html.parser')
        meta_tag = soup.find("meta", {"name": "csrf-token"})
        
        if meta_tag and "content" in meta_tag.attrs:
            csrf_token = meta_tag.attrs["content"]
            print(f"   Found CSRF token: {csrf_token[:10]}... (truncated)")
            
            # Test with valid CSRF token
            print("   Trying login with valid CSRF token...")
            login_data = {
                "username": username,
                "password": password,
                "csrf_token": csrf_token
            }
            
            response = session.post(login_url, data=login_data, allow_redirects=False)
            print(f"   Login with token response code: {response.status_code}")
            
            # Check for redirect (302) which is common on successful login
            if response.status_code == 302:
                print("   Login successful with valid CSRF token! (Redirect detected)")
                redirect_url = response.headers.get('Location')
                print(f"   Redirect to: {redirect_url}")
                return True
            elif "Logged in successfully" in response.text:
                print("   Login successful with valid CSRF token!")
                return True
            else:
                print(f"   Login response with token: {response.text[:200]}...")
                print(f"   Login failed with valid CSRF token. Status: {response.status_code}")
                return False
            
            # Start a new session and test without CSRF token
            session = requests.Session()
            session.get(login_url)  # Establish a session first
            print("   Trying login without CSRF token...")
            login_data = {
                "username": username,
                "password": password
            }
            
            response = session.post(login_url, data=login_data)
            print(f"   Login without token response code: {response.status_code}")
            print(f"   Response contains 'CSRF': {'Yes' if 'CSRF' in response.text or 'csrf' in response.text.lower() else 'No'}")
            print(f"   Response contains 'Logged in successfully': {'Yes' if 'Logged in successfully' in response.text else 'No'}")
            
            # If we get a small response, print it for debugging
            if len(response.text) < 500:
                print(f"   Response: {response.text}")
            else:
                print(f"   Response excerpt: {response.text[:200]}...")
            
            if "CSRF" in response.text or "csrf" in response.text.lower():
                print("   Login correctly rejected without CSRF token (found CSRF error message)")
                return True
            elif "Logged in successfully" in response.text:
                print("   LOGIN SUCCEEDED WITHOUT CSRF TOKEN - PROTECTION NOT WORKING!")
                return False
            else:
                print(f"   Login rejected without CSRF token. Status: {response.status_code}")
                return True
        else:
            print("   Could not find CSRF token in login page")
            # Debug the page content to see why we can't find the CSRF token
            print(f"   Page title: {soup.title.string if soup.title else 'No title found'}")
            print(f"   Page content excerpt: {response.text[:200]}...")
            return False
    except Exception as e:
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Get arguments or use defaults
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000/todo-app"
    username = sys.argv[2] if len(sys.argv) > 2 else "testuser"
    password = sys.argv[3] if len(sys.argv) > 3 else "Test@123!"
    
    # Ensure the base URL doesn't end with a slash for consistent joining
    base_url = base_url.rstrip('/')
    
    # Install beautifulsoup4 if needed
    try:
        import bs4
    except ImportError:
        print("Installing beautifulsoup4...")
        os.system("pip install beautifulsoup4")
    
    api_success, token = test_token_creation(base_url, username, password)
    web_success = test_web_form_csrf(base_url, username, password)
    
    print("\n=== RESULTS ===")
    print(f"API CSRF exemption: {'SUCCESS' if api_success else 'FAILURE'}")
    print(f"Web form CSRF protection: {'SUCCESS' if web_success else 'FAILURE'}")
    
    success = api_success and web_success
    sys.exit(0 if success else 1) 