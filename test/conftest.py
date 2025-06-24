"""Pytest configuration and fixtures for CyberArk CCP API client tests."""

from unittest.mock import Mock

import pytest
import requests

from cyberark_ccp import CyberarkCCPClient


@pytest.fixture
def client():
    """Create a basic CyberArk CCP client for testing."""
    return CyberarkCCPClient(base_url="https://test.example.com", app_id="TestApplication", verify=True, timeout=30)


@pytest.fixture
def secure_client():
    """Create a CyberArk CCP client with certificate authentication for testing."""
    return CyberarkCCPClient(
        base_url="https://secure.example.com",
        app_id="SecureApplication",
        cert_path="/path/to/test-cert.p12",
        verify=True,
        timeout=60,
    )


@pytest.fixture
def mock_successful_response():
    """Create a mock successful API response."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "Content": "test-password-123",
        "UserName": "test-user",
        "Address": "test.example.com",
        "Database": "test-database",
        "PasswordChangeInProcess": False,
    }
    mock_response.raise_for_status.return_value = None
    return mock_response


@pytest.fixture
def mock_minimal_response():
    """Create a mock minimal API response with only Content."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"Content": "simple-password"}
    mock_response.raise_for_status.return_value = None
    return mock_response


@pytest.fixture
def mock_error_response():
    """Create a mock error response with configurable error details."""

    def _create_error_response(status_code, error_code=None, error_message="Test error"):
        mock_response = Mock()
        mock_response.status_code = status_code

        if error_code:
            mock_response.json.return_value = {"ErrorCode": error_code, "ErrorMessage": error_message}
        else:
            mock_response.json.side_effect = ValueError("Not JSON")
            mock_response.text = f"HTTP {status_code} Error: {error_message}"

        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        return mock_response

    return _create_error_response


@pytest.fixture
def sample_api_parameters():
    """Provide sample API parameters for testing."""
    return {
        "safe": "TestSafe",
        "folder": "TestFolder",
        "password_object": "TestObject",
        "username": "test-user",
        "address": "test.example.com",
        "database": "test-db",
        "policy_id": "test-policy",
        "reason": "Unit testing",
        "connection_timeout": 60,
        "fail_request_on_password_change": True,
    }


@pytest.fixture
def invalid_characters():
    """Provide list of invalid characters for testing validation."""
    return ["+", "&", "%", ";"]


@pytest.fixture
def api_error_codes():
    """Provide mapping of API error codes to expected exception types."""
    from cyberark_ccp import (
        CyberarkCCPAccountNotFoundError,
        CyberarkCCPAuthenticationError,
        CyberarkCCPAuthorizationError,
        CyberarkCCPConnectionError,
        CyberarkCCPError,
        CyberarkCCPValidationError,
    )

    return {
        # 400 Bad Request errors
        "AIMWS030E": CyberarkCCPValidationError,
        "APPAP227E": CyberarkCCPAccountNotFoundError,
        "APPAP228E": CyberarkCCPAccountNotFoundError,
        "APPAP229E": CyberarkCCPAccountNotFoundError,
        "APPAP007E": CyberarkCCPConnectionError,
        "APPAP081E": CyberarkCCPValidationError,
        "CASVL010E": CyberarkCCPValidationError,
        "AIMWS031E": CyberarkCCPValidationError,
        # 403 Forbidden errors
        "APPAP306E": CyberarkCCPAuthenticationError,
        "APPAP008E": CyberarkCCPAuthorizationError,
        # 404 Not Found errors
        "APPAP004E": CyberarkCCPAccountNotFoundError,
        # 500 Internal Server Error
        "APPAP282E": CyberarkCCPError,
    }


@pytest.fixture
def api_specification_examples():
    """Provide examples from the API specification for testing."""
    return {
        "valid_response": {
            "Content": "MyPassword123!",
            "UserName": "service_account",
            "Address": "database.example.com",
            "Database": "production_db",
            "PasswordChangeInProcess": False,
        },
        "minimal_response": {"Content": "SimplePassword"},
        "password_change_response": {"Content": "TempPassword", "PasswordChangeInProcess": True},
        "empty_optional_fields": {
            "Content": "Password123",
            "UserName": "",
            "Address": "",
            "Database": "",
            "PasswordChangeInProcess": False,
        },
    }


@pytest.fixture(autouse=True)
def reset_client_state():
    """Ensure client state is reset between tests."""
    # This fixture runs automatically before each test
    # Can be used to reset any global state if needed
    yield
    # Cleanup after test if needed


class TestHelper:
    """Helper class for common test operations."""

    @staticmethod
    def create_mock_response(status_code=200, content=None, error_code=None, error_message=None):
        """Create a mock HTTP response for testing."""
        mock_response = Mock()
        mock_response.status_code = status_code

        if status_code == 200 and content:
            mock_response.json.return_value = content
            mock_response.raise_for_status.return_value = None
        elif error_code:
            mock_response.json.return_value = {"ErrorCode": error_code, "ErrorMessage": error_message or "Test error"}
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        else:
            mock_response.json.side_effect = ValueError("Not JSON")
            mock_response.text = f"HTTP {status_code} Error"
            mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()

        return mock_response

    @staticmethod
    def assert_request_parameters(mock_get, expected_params):
        """Assert that request was made with expected parameters."""
        assert mock_get.called
        call_args = mock_get.call_args
        actual_params = call_args[1]["params"]

        for key, value in expected_params.items():
            assert key in actual_params, f"Parameter {key} not found in request"
            assert actual_params[key] == value, f"Parameter {key}: expected {value}, got {actual_params[key]}"

    @staticmethod
    def assert_request_url(mock_get, expected_base_url):
        """Assert that request was made to expected URL."""
        assert mock_get.called
        call_args = mock_get.call_args
        actual_url = call_args[0][0]
        expected_url = f"{expected_base_url}/AIMWebService/api/Accounts"
        assert actual_url == expected_url


@pytest.fixture
def test_helper():
    """Provide TestHelper instance for tests."""
    return TestHelper
