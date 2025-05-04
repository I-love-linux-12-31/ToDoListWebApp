#!/bin/bash

# Run fuzzing tests for the ToDoList web application
# Make sure the application is running before executing this script

# Sanitize URL parts for proper concatenation
join_url_path() {
    local base=$(echo "$1" | sed 's:/*$::')
    local path=$(echo "$2" | sed 's:^/::')
    echo "${base}/${path}"
}

# Set up environment variables for testing
source .env 2>/dev/null || true  # Load .env file if it exists
BASE_URL="http://localhost:5000${URL_PREFIX:-/todo-app}"
# Remove trailing slash for consistent joining
BASE_URL=${BASE_URL%/}
export TEST_BASE_URL="$BASE_URL"
export TEST_API_PREFIX="/api/v1"

# Check if custom username/password were provided
if [ $# -ge 2 ]; then
    export TEST_USERNAME="$1"
    export TEST_PASSWORD="$2"
else
    # Default test user
    export TEST_USERNAME="testuser"
    export TEST_PASSWORD="Test@123!"
fi

# Full URL for token creation endpoint
TOKEN_URL=$(join_url_path "$BASE_URL" "api/v1/token/create")

echo "Using API URL: $TOKEN_URL"

# Verify CSRF configuration
echo "Verifying CSRF configuration..."
python test_api_csrf.py "$BASE_URL" "$TEST_USERNAME" "$TEST_PASSWORD"
if [ $? -ne 0 ]; then
    echo "CSRF configuration verification failed. Please check the API CSRF exemption and web form CSRF protection."
    exit 1
fi

# Create test user if it doesn't exist (requires app to be running)
echo "Checking if test user exists..."
response=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "$TOKEN_URL" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$TEST_USERNAME\",\"password\":\"$TEST_PASSWORD\",\"token_access_level\":3,\"duration\":1}")

echo "API response code: $response"

if [ "$response" != "201" ]; then
    echo "Test user doesn't exist or credentials are incorrect. Please create the user first or check credentials."
    echo "You can use the backend/utils_cmd.py script to create a user:"
    echo "python backend/utils_cmd.py add_user --username $TEST_USERNAME --password $TEST_PASSWORD"
    exit 1
fi

echo "Test user verified. Running fuzzing tests..."

# Run the fuzzing tests
python -m pytest tests/fuzz -v 

# Generate a report if pytest-html is installed
if python -c "import pytest_html" &> /dev/null; then
    echo "Generating HTML report..."
    python -m pytest tests/fuzz -v --html=fuzz_report.html --self-contained-html
fi

echo "Fuzzing tests completed. Check the output for any errors." 