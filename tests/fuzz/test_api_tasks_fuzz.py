import pytest
import requests
from hypothesis import given, strategies as st, settings, HealthCheck
import datetime
import string

# Import the helper function from conftest
from tests.conftest import join_url_path

# Mark all tests in this module as fuzz tests
pytestmark = [pytest.mark.fuzz, pytest.mark.api]

# Define strategies for generating random task data
task_titles = st.text(
    alphabet=string.printable, 
    min_size=1, 
    max_size=128
).filter(lambda x: x.strip())  # Ensure non-empty titles

task_descriptions = st.one_of(
    st.none(),
    st.text(alphabet=string.printable, min_size=0, max_size=512)
)

task_statuses = st.sampled_from(["DONE", "PENDING", "NONE", "CANCELLED"])

task_access_politics = st.sampled_from([
    "PARENT_SELECT", "PRIVATE", "R_ALL", "R_ONLY_1_LEVELS", 
    "R_ONLY_2_LEVELS", "RW_ALL", "RW_ONLY_1_LEVELS", "RW_ONLY_2_LEVELS"
])

# Strategy for generating random ISO datetime strings
def iso_datetime_strategy():
    return st.builds(
        lambda dt: dt.isoformat(),
        st.datetimes(
            min_value=datetime.datetime(2000, 1, 1),
            max_value=datetime.datetime(2030, 12, 31)
        )
    )

# Task creation strategy
task_creation_data = st.fixed_dictionaries({
    'title': task_titles,
    'description': task_descriptions,
    'status': task_statuses,
    'access_politics': task_access_politics,
    'deadline': st.one_of(st.none(), iso_datetime_strategy())
})

@settings(
    max_examples=50,
    deadline=None,  # Disable deadline since API calls can be slow
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(task_data=task_creation_data)
def test_create_task_fuzz(api_url, auth_headers, task_data):
    """Test creating tasks with fuzzed data."""
    tasks_url = join_url_path(api_url, "tasks")
    
    # Remove None values from the dictionary
    task_data = {k: v for k, v in task_data.items() if v is not None}
    
    # Make the API request
    response = requests.post(tasks_url, json=task_data, headers=auth_headers)
    
    # Check for expected responses
    # Success case
    if response.status_code == 201:
        task = response.json()
        assert task["title"] == task_data["title"]
        if "description" in task_data:
            assert task["description"] == task_data["description"]
        assert task["status"] == task_data["status"]
        if "access_politics" in task_data:
            assert task["access_politics"] == task_data["access_politics"]
        
        # Cleanup
        delete_url = join_url_path(api_url, f"tasks/{task['id']}")
        requests.delete(delete_url, headers=auth_headers)
    
    # Known error cases - these are considered valid test outcomes
    elif response.status_code == 400:
        # Bad request - could be invalid date format or missing fields
        pass
    elif response.status_code == 403:
        # Forbidden - could be insufficient permissions
        pass
    else:
        # Any other response is unexpected and should fail the test
        assert False, f"Unexpected response: {response.status_code} - {response.text}"

@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(
    title=task_titles,
    status=task_statuses
)
def test_update_task_fuzz(api_url, auth_headers, create_task, title, status):
    """Test updating tasks with fuzzed data."""
    # First create a task
    initial_task = create_task({
        "title": "Test task for updating",
        "description": "This task will be updated",
        "status": "PENDING"
    })
    assert initial_task is not None
    
    # Now fuzz the update
    update_data = {
        "title": title,
        "status": status
    }
    
    update_url = join_url_path(api_url, f"tasks/{initial_task['id']}")
    response = requests.put(update_url, json=update_data, headers=auth_headers)
    
    # Check for expected responses
    if response.status_code == 200:
        updated_task = response.json()
        assert updated_task["title"] == title
        assert updated_task["status"] == status
    elif response.status_code in (400, 403):
        # Known error cases - bad request or forbidden
        pass
    else:
        assert False, f"Unexpected response: {response.status_code} - {response.text}"

@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(task_id=st.integers(min_value=-1000, max_value=100000))
def test_get_task_fuzz(api_url, auth_headers, task_id):
    """Test getting tasks with fuzzed task IDs."""
    get_url = join_url_path(api_url, f"tasks/{task_id}")
    response = requests.get(get_url, headers=auth_headers)
    
    # Expected responses:
    # - 200 OK if task exists and user has access
    # - 404 Not Found if task doesn't exist
    # - 403 Forbidden if task exists but user has no access
    assert response.status_code in (200, 404, 403)
    
    if response.status_code == 200:
        task = response.json()
        assert task["id"] == task_id

@settings(
    max_examples=30,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(
    malformed_json=st.one_of(
        st.text().filter(lambda x: x.strip()),
        st.binary().filter(lambda x: len(x) > 0),
        st.dictionaries(
            keys=st.text(alphabet=string.ascii_letters),
            values=st.one_of(
                st.text(),
                st.integers(),
                st.lists(st.integers()),
                st.dictionaries(
                    keys=st.text(alphabet=string.ascii_letters),
                    values=st.text()
                )
            )
        )
    )
)
def test_malformed_json_fuzz(api_url, auth_headers, malformed_json):
    """Test API robustness against malformed JSON."""
    tasks_url = join_url_path(api_url, "tasks")
    
    # Prepare custom headers to bypass Content-Type validation
    headers = auth_headers.copy()
    headers["Content-Type"] = "application/json"
    
    try:
        # Try to send malformed data
        if isinstance(malformed_json, dict):
            response = requests.post(tasks_url, json=malformed_json, headers=headers)
        else:
            # For non-dict data, send as raw data
            headers["Content-Type"] = "text/plain"
            response = requests.post(tasks_url, data=malformed_json, headers=headers)
        
        # API should handle bad requests gracefully (no 500 errors)
        assert response.status_code != 500, f"Server error on malformed input: {response.text}"
    except requests.RequestException:
        # Connection errors are OK - the server might close the connection for very invalid data
        pass 