import pytest
import requests
from hypothesis import given, strategies as st, settings, HealthCheck
from bs4 import BeautifulSoup

# Import the helper function from conftest
from tests.conftest import join_url_path

# Mark all tests in this module as fuzz tests
pytestmark = [pytest.mark.fuzz, pytest.mark.webapp]

# We'll need to install beautifulsoup4 for this test
# pip install beautifulsoup4

@pytest.fixture(scope="module")
def webapp_session():
    """Create a requests session for web app tests."""
    session = requests.Session()
    return session

@pytest.fixture(scope="module")
def csrf_token(app_config, webapp_session):
    """Get a CSRF token from the login page."""
    login_url = join_url_path(app_config["base_url"], "auth/login")
    response = webapp_session.get(login_url)
    
    # Parse the page to extract the CSRF token
    soup = BeautifulSoup(response.text, 'html.parser')
    meta_tag = soup.find("meta", {"name": "csrf-token"})
    
    if meta_tag and "content" in meta_tag.attrs:
        # Store at module level for comparison in tests
        token = meta_tag.attrs["content"]
        pytest.valid_csrf_token = token
        return token
    
    pytest.skip("Could not find CSRF token in login page")

@pytest.fixture(scope="module")
def login_webapp(app_config, webapp_session, csrf_token):
    """Login to the web application."""
    login_url = join_url_path(app_config["base_url"], "auth/login")
    
    login_data = {
        "username": app_config["username"],
        "password": app_config["password"],
        "csrf_token": csrf_token
    }
    
    response = webapp_session.post(login_url, data=login_data)
    
    # Check if login was successful
    if "Logged in successfully" in response.text:
        return True
    
    pytest.skip("Could not login to web application")

@settings(
    max_examples=30,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(
    csrf_token=st.one_of(
        st.none(),
        st.just(""),
        st.text(min_size=1, max_size=64),
        st.binary(min_size=1, max_size=32).map(lambda x: x.hex())
    )
)
def test_login_csrf_fuzz(app_config, csrf_token):
    """Test login form with fuzzed CSRF tokens."""
    login_url = join_url_path(app_config["base_url"], "auth/login")
    
    # Create a new session for each test
    session = requests.Session()
    
    # First get the login page to establish a session
    session.get(login_url)
    
    login_data = {
        "username": app_config["username"],
        "password": app_config["password"]
    }
    
    # Add CSRF token if provided
    if csrf_token is not None:
        login_data["csrf_token"] = csrf_token
    
    response = session.post(login_url, data=login_data)
    
    # CSRF failures should either redirect or show an error
    # but should never cause a 500 error
    assert response.status_code != 500, "Server error on CSRF test"
    
    # If we have an invalid CSRF token, we should not be logged in
    # Use the module-level valid token for comparison
    if not hasattr(pytest, 'valid_csrf_token') or csrf_token != pytest.valid_csrf_token:
        assert "Logged in successfully" not in response.text, "Login succeeded with invalid CSRF token"

@settings(
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(
    task_title=st.text(min_size=1, max_size=64).filter(lambda x: x.strip()),
    csrf_token=st.one_of(
        st.none(),
        st.just(""),
        st.text(min_size=1, max_size=64),
    )
)
def test_add_task_csrf_fuzz(app_config, login_webapp, webapp_session, task_title, csrf_token):
    """Test add task form with fuzzed CSRF tokens."""
    add_task_url = join_url_path(app_config["base_url"], "todo/add/")
    
    # First get the add task page
    webapp_session.get(add_task_url)
    
    task_data = {
        "title": task_title,
        "description": "Test description"
    }
    
    # Add CSRF token if provided
    if csrf_token is not None:
        task_data["csrf_token"] = csrf_token
    
    response = webapp_session.post(add_task_url, data=task_data)
    
    # CSRF failures should either redirect or show an error
    # but should never cause a 500 error
    assert response.status_code != 500, "Server error on CSRF test"
    
    # Check for CSRF error page
    # Use the module-level valid token for comparison
    if not hasattr(pytest, 'valid_csrf_token') or csrf_token != pytest.valid_csrf_token:
        assert "Security Error - CSRF Protection" in response.text or "Task created successfully" not in response.text, \
            "Task creation succeeded with invalid CSRF token"

# Store a valid CSRF token for comparison
@pytest.fixture(scope="module", autouse=True)
def setup_module_csrf(request, csrf_token):
    """Store a valid CSRF token at the module level."""
    request.module.valid_csrf_token = csrf_token 