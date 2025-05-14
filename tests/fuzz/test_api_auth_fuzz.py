import pytest
import requests
from urllib.parse import urljoin
from hypothesis import given, strategies as st, settings, HealthCheck
import string

# Import the helper function from conftest
from tests.conftest import join_url_path

# Mark all tests in this module as fuzz tests
pytestmark = [pytest.mark.fuzz, pytest.mark.api]

# Define strategies for auth data
usernames = st.text(
    alphabet=string.ascii_letters + string.digits + "_-",
    min_size=1,
    max_size=64
).filter(lambda x: x.strip())

passwords = st.text(
    alphabet=string.printable,
    min_size=1,
    max_size=50
).filter(lambda x: x.strip())

token_access_levels = st.integers(min_value=0, max_value=5)
durations = st.integers(min_value=1, max_value=150)


@settings(
    max_examples=30,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(
    username=usernames,
    password=passwords,
    token_access_level=token_access_levels,
    duration=durations
)
def test_token_creation_fuzz(api_url, username, password, token_access_level, duration):
    """Test token creation with fuzzed credentials."""
    token_url = join_url_path(api_url, "token/create")

    credentials = {
        "username": username,
        "password": password,
        "token_access_level": token_access_level,
        "duration": duration
    }

    response = requests.post(token_url, json=credentials)

    # We don't expect 500 errors regardless of input
    assert response.status_code != 500, f"Server error on token creation: {response.text}"

    # For user credentials we know are valid, we can be more specific
    if username == "testuser" and password == "Test@123!":
        # Should succeed with known good credentials
        assert response.status_code == 201, f"Failed with valid credentials: {response.text}"
        token_data = response.json()
        assert "id" in token_data
        assert "user_id" in token_data
        assert "valid_until" in token_data
        assert "access_level" in token_data

        # Validate the received token
        validate_url = join_url_path(api_url, "tasks")
        headers = {"Authorization": f"Token {token_data['id']}"}
        validate_response = requests.get(validate_url, headers=headers)
        assert validate_response.status_code in (200, 403), "Token validation failed"


@settings(
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(
    auth_header=st.one_of(
        st.none(),
        st.just(""),
        st.just("Bearer "),
        st.just("Token "),
        # Filter out control characters and invalid header characters
        st.text(
            alphabet=string.ascii_letters + string.digits + "-._~+/=",
            min_size=1, 
            max_size=20
        ).map(lambda x: f"Bearer {x}"),
        st.text(
            alphabet=string.ascii_letters + string.digits + "-._~+/=",
            min_size=1, 
            max_size=64
        ).map(lambda x: f"Token {x}"),
        st.text(
            alphabet=string.ascii_letters + string.digits + "-._~+/=",
            min_size=1, 
            max_size=20
        )
    )
)
def test_malformed_auth_headers_fuzz(api_url, auth_headers, auth_header):
    """Test API robustness against malformed authentication headers."""
    tasks_url = join_url_path(api_url, "tasks")

    headers = {"Content-Type": "application/json"}
    if auth_header is not None:
        try:
            headers["Authorization"] = auth_header
            response = requests.get(tasks_url, headers=headers)
        
            # We don't expect 500 errors regardless of input
            assert response.status_code != 500, f"Server error on malformed auth header: {response.text}"
        
            # For valid auth patterns with invalid tokens, we expect 401
            if auth_header and auth_header.startswith("Token ") and len(auth_header) > 6:
                # Get the valid token from the auth_headers fixture
                valid_token = auth_headers.get("Authorization", "").replace("Token ", "")
                
                # Only for non-existing tokens
                if auth_header != f"Token {valid_token}" and valid_token:
                    assert response.status_code == 401, f"Expected 401 for invalid token but got {response.status_code}"
        except requests.exceptions.InvalidHeader:
            # Skip validation if the header is invalid for requests library
            pass
    else:
        # Handles the None case
        response = requests.get(tasks_url, headers=headers)
        assert response.status_code != 500


@pytest.fixture(scope="module")
def auth_token_value(request):
    """Store the auth token for the fuzz tests."""
    if hasattr(request.module, "auth_token_value"):
        return request.module.auth_token_value

    # Get a valid token to compare against
    app_config = request.getfixturevalue("app_config")
    api_url = request.getfixturevalue("api_url")

    credentials = {
        "username": app_config["username"],
        "password": app_config["password"],
        "token_access_level": 3,
        "duration": 1
    }

    token_url = urljoin(api_url, "/token/create")
    try:
        response = requests.post(token_url, json=credentials)
        if response.status_code == 201:
            token = response.json()["id"]
            request.module.auth_token_value = token
            return token
    except Exception as e:
        print(e)
        pass
    return None


# This will be called once at the module level to store the token
@pytest.fixture(scope="module", autouse=True)
def setup_module_token(request, auth_token_value):
    """Setup module with auth token."""
    request.module.auth_token_value = auth_token_value