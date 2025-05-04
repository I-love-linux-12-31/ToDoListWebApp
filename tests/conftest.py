import os
import pytest
import requests

# Helper function to join URL parts correctly, respecting URL_PREFIX
def join_url_path(base, path):
    """Join URL parts correctly, preserving the full base path."""
    # Remove trailing slash from base and leading slash from path
    base = base.rstrip('/')
    path = path.lstrip('/')
    return f"{base}/{path}"

# Default configuration for the test environment
@pytest.fixture(scope="session")
def app_config():
    """Return the configuration for the test environment."""
    print("TEST CONFIG URL", os.environ.get("TEST_BASE_URL", "http://localhost:5000"))
    return {
        "base_url": os.environ.get("TEST_BASE_URL", "http://localhost:5000"),
        "api_prefix": os.environ.get("TEST_API_PREFIX", "/api/v1"),
        "username": os.environ.get("TEST_USERNAME", "testuser"),
        "password": os.environ.get("TEST_PASSWORD", "Test@123!"),
        "admin_username": os.environ.get("TEST_ADMIN_USERNAME", "admin"),
        "admin_password": os.environ.get("TEST_ADMIN_PASSWORD", "Admin@123!"),
    }

@pytest.fixture(scope="session")
def api_url(app_config):
    """Return the base API URL."""
    full_api_url = join_url_path(app_config["base_url"], app_config["api_prefix"])
    print("Full API URL:", full_api_url)
    return full_api_url

@pytest.fixture(scope="session")
def auth_token(app_config, api_url):
    """Create and return an API authentication token."""
    credentials = {
        "username": app_config["username"],
        "password": app_config["password"],
        "token_access_level": 3,  # EVERYTHING_USER level
        "duration": 1,  # Short duration for tests
    }
    
    token_url = join_url_path(api_url, "token/create")
    print(f"\nAttempting to get auth token from: {token_url}")
    try:
        response = requests.post(
            token_url, 
            json=credentials, 
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 201:
            token_data = response.json()
            print(f"Successfully obtained auth token: {token_data['id'][:10]}...")
            # Store the token at module level for test_api_auth_fuzz.py
            pytest.auth_token_value = token_data["id"]
            return token_data["id"]
        else:
            error_msg = f"Failed to get auth token: {response.status_code}"
            try:
                error_msg += f" - {response.text}"
            except:
                pass
            print(f"Error: {error_msg}")
            pytest.skip(error_msg)
    except requests.RequestException as e:
        error_msg = f"Failed to connect to the API: {e}"
        print(f"Error: {error_msg}")
        pytest.skip(error_msg)

@pytest.fixture(scope="session")
def auth_headers(auth_token):
    """Return headers with authentication token."""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Token {auth_token}"
    }

@pytest.fixture(scope="function")
def create_task(api_url, auth_headers):
    """Fixture to create a task and clean it up after the test."""
    created_tasks = []
    
    def _create_task(task_data):
        tasks_url = join_url_path(api_url, "tasks")
        response = requests.post(tasks_url, json=task_data, headers=auth_headers)
        if response.status_code == 201:
            task = response.json()
            created_tasks.append(task["id"])
            return task
        return None
    
    yield _create_task
    
    # Cleanup - delete all created tasks
    for task_id in created_tasks:
        try:
            delete_url = join_url_path(api_url, f"tasks/{task_id}")
            requests.delete(delete_url, headers=auth_headers)
        except:
            pass  # Ignore cleanup failures 