# CyberArk CCP API Client Test Suite

This directory contains comprehensive unit tests for the CyberArk Central Credential Provider (CCP) API client, ensuring full compliance with the official API specification.

## Test Structure

### Test Files

- **`test_client.py`** - Core client functionality tests
  - Client initialization and configuration
  - Parameter building and validation
  - Request/response handling
  - Context manager usage
  - Session management

- **`test_exceptions.py`** - Exception handling tests
  - Exception hierarchy validation
  - Error code mapping verification
  - Exception use case scenarios

- **`test_integration.py`** - Integration and real-world scenario tests
  - End-to-end workflows
  - Multiple request scenarios
  - Error recovery patterns
  - Certificate authentication

- **`test_api_compliance.py`** - API specification compliance tests
  - URL format validation
  - Parameter name verification
  - Character restriction enforcement
  - Response structure validation
  - HTTP method compliance

- **`conftest.py`** - Pytest configuration and shared fixtures
  - Common test fixtures
  - Mock response helpers
  - Test utilities

## Test Coverage

### API Specification Coverage

✅ **URL Format**: `https://<IIS_Server_Ip>/AIMWebService/api/Accounts`
✅ **HTTP Method**: GET only
✅ **Content Type**: application/json
✅ **All Query Parameters**:
- AppID (required)
- Safe, Folder, Object, UserName, Address, Database, PolicyID
- Reason, Query, Query Format, Connection Timeout
- FailRequestOnPasswordChange

### Parameter Validation Coverage

✅ **Character Restrictions**: `+`, `&`, `%`, `;`, spaces
✅ **Required Parameters**: AppID + at least one other
✅ **Query Parameter Behavior**: Overrides other search criteria
✅ **Type Validation**: String, Integer, Boolean types
✅ **Default Values**: Per API specification

### Error Code Coverage

✅ **400 Bad Request**:
- AIMWS030E (Invalid query format)
- APPAP227E/228E/229E (Too many objects)
- APPAP007E (Connection to Vault failed)
- APPAP081E (Invalid request content)
- CASVL010E (Invalid characters)
- AIMWS031E (AppID required)

✅ **403 Forbidden**:
- APPAP306E (Authentication failed)
- APPAP008E (User not defined)

✅ **404 Not Found**:
- APPAP004E (Safe not found)

✅ **500 Internal Server Error**:
- APPAP282E (Password change in progress)

### Response Structure Coverage

✅ **Success Response (200)**:
- Content (password)
- UserName, Address, Database
- PasswordChangeInProcess

✅ **Error Response**:
- ErrorCode, ErrorMessage
- HTTP status code mapping

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install -r test/requirements.txt

# Or install from project root
pip install -e .
pip install pytest pytest-mock pytest-cov
```

### Basic Test Execution

```bash
# Run all tests
pytest test/

# Run specific test file
pytest test/test_client.py

# Run with verbose output
pytest -v test/

# Run specific test class
pytest test/test_client.py::TestCyberarkCCPClient

# Run specific test method
pytest test/test_client.py::TestCyberarkCCPClient::test_client_initialization
```

### Coverage Reports

```bash
# Run tests with coverage
pytest --cov=cyberark_ccp test/

# Generate HTML coverage report
pytest --cov=cyberark_ccp --cov-report=html test/

# Generate detailed coverage report
pytest --cov=cyberark_ccp --cov-report=term-missing test/
```

### Test Categories

```bash
# Run only client functionality tests
pytest test/test_client.py

# Run only exception tests
pytest test/test_exceptions.py

# Run only integration tests
pytest test/test_integration.py

# Run only API compliance tests
pytest test/test_api_compliance.py
```

## Test Fixtures

### Available Fixtures

- **`client`** - Basic CCP client instance
- **`secure_client`** - Client with certificate authentication
- **`mock_successful_response`** - Mock successful API response
- **`mock_error_response`** - Configurable mock error response
- **`sample_api_parameters`** - Sample parameters for testing
- **`invalid_characters`** - List of invalid URL characters
- **`api_error_codes`** - Error code to exception mapping
- **`test_helper`** - Helper utilities for tests

### Custom Assertions

```python
# Assert request parameters
test_helper.assert_request_parameters(mock_get, expected_params)

# Assert request URL
test_helper.assert_request_url(mock_get, "https://test.com")
```

## Testing Best Practices

### Mocking Strategy

- **Network Isolation**: All tests use mocked HTTP requests
- **Response Simulation**: Mock responses match API specification
- **Error Simulation**: Test all documented error scenarios
- **State Isolation**: Each test is independent

### Test Organization

- **Unit Tests**: Test individual methods and functions
- **Integration Tests**: Test component interactions
- **Compliance Tests**: Verify API specification adherence
- **Error Tests**: Comprehensive error scenario coverage

### Assertions

- **Explicit Assertions**: Test specific expected behaviors
- **Error Message Validation**: Verify exception messages
- **Parameter Verification**: Check request parameters
- **Response Validation**: Verify response structure

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.7, 3.8, 3.9, 3.10, 3.11]
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        pip install -e .
        pip install -r test/requirements.txt
    - name: Run tests
      run: pytest --cov=cyberark_ccp test/
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Contributing Tests

### Adding New Tests

1. **Follow Naming Convention**: `test_<functionality>.py`
2. **Use Descriptive Names**: Test method names should describe the scenario
3. **Include Docstrings**: Explain what the test validates
4. **Use Fixtures**: Leverage existing fixtures for common setup
5. **Mock External Calls**: Never make real network requests
6. **Test Error Cases**: Include both success and failure scenarios

### Test Guidelines

- **Atomic Tests**: Each test should test one specific behavior
- **Isolated Tests**: Tests should not depend on each other
- **Deterministic**: Tests should always produce the same result
- **Fast Execution**: Tests should run quickly
- **Clear Assertions**: Use specific assertions with helpful messages

### API Specification Updates

When the API specification changes:

1. Update relevant tests in `test_api_compliance.py`
2. Add new error codes to exception mapping
3. Update parameter validation tests
4. Verify response structure changes
5. Update documentation and examples