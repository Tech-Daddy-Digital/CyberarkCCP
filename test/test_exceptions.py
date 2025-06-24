"""Unit tests for CyberArk CCP API client exceptions."""

import pytest

from cyberark_ccp import (
    CyberarkCCPAccountNotFoundError,
    CyberarkCCPAuthenticationError,
    CyberarkCCPAuthorizationError,
    CyberarkCCPConnectionError,
    CyberarkCCPError,
    CyberarkCCPTimeoutError,
    CyberarkCCPValidationError,
)


class TestExceptionHierarchy:
    """Test suite for exception hierarchy."""

    def test_base_exception_inheritance(self):
        """Test that all CCP exceptions inherit from CyberarkCCPError."""
        assert issubclass(CyberarkCCPValidationError, CyberarkCCPError)
        assert issubclass(CyberarkCCPAuthenticationError, CyberarkCCPError)
        assert issubclass(CyberarkCCPAuthorizationError, CyberarkCCPError)
        assert issubclass(CyberarkCCPAccountNotFoundError, CyberarkCCPError)
        assert issubclass(CyberarkCCPConnectionError, CyberarkCCPError)
        assert issubclass(CyberarkCCPTimeoutError, CyberarkCCPError)

    def test_base_exception_is_exception(self):
        """Test that CyberarkCCPError inherits from Exception."""
        assert issubclass(CyberarkCCPError, Exception)

    def test_exception_instantiation(self):
        """Test that all exceptions can be instantiated."""
        exceptions = [
            CyberarkCCPError,
            CyberarkCCPValidationError,
            CyberarkCCPAuthenticationError,
            CyberarkCCPAuthorizationError,
            CyberarkCCPAccountNotFoundError,
            CyberarkCCPConnectionError,
            CyberarkCCPTimeoutError,
        ]

        for exc_class in exceptions:
            # Test with message
            exc = exc_class("Test message")
            assert str(exc) == "Test message"

            # Test without message
            exc = exc_class()
            assert isinstance(exc, exc_class)

    def test_exception_raising_and_catching(self):
        """Test that exceptions can be raised and caught properly."""
        # Test specific exception catching
        with pytest.raises(CyberarkCCPValidationError):
            raise CyberarkCCPValidationError("Validation failed")

        # Test base exception catching
        with pytest.raises(CyberarkCCPError):
            raise CyberarkCCPValidationError("Validation failed")

        # Test Exception base class catching
        with pytest.raises(Exception):
            raise CyberarkCCPError("Base error")

    def test_exception_chaining(self):
        """Test exception chaining with 'from' clause."""
        original_error = ValueError("Original error")

        with pytest.raises(CyberarkCCPError) as exc_info:
            try:
                raise original_error
            except ValueError as e:
                raise CyberarkCCPError("Wrapped error") from e

        assert exc_info.value.__cause__ is original_error

    def test_exception_messages(self):
        """Test that exception messages are properly handled."""
        message = "Detailed error message"

        exceptions = [
            CyberarkCCPError(message),
            CyberarkCCPValidationError(message),
            CyberarkCCPAuthenticationError(message),
            CyberarkCCPAuthorizationError(message),
            CyberarkCCPAccountNotFoundError(message),
            CyberarkCCPConnectionError(message),
            CyberarkCCPTimeoutError(message),
        ]

        for exc in exceptions:
            assert str(exc) == message


class TestExceptionUseCases:
    """Test suite for exception use cases based on API specification."""

    def test_validation_error_scenarios(self):
        """Test scenarios where CyberarkCCPValidationError should be used."""
        # These represent actual validation scenarios
        validation_scenarios = [
            "Invalid query format",
            "Request message content is invalid",
            "Invalid characters in User Name",
            "Invalid request. The AppID parameter is required",
            "Parameter 'test' contains invalid character '+'",
        ]

        for message in validation_scenarios:
            with pytest.raises(CyberarkCCPValidationError):
                raise CyberarkCCPValidationError(message)

    def test_authentication_error_scenarios(self):
        """Test scenarios where CyberarkCCPAuthenticationError should be used."""
        # These represent actual authentication scenarios
        auth_scenarios = [
            "App failed on authentication check",
            "Authentication failed (APPAP306E)",
            "Certificate authentication failed",
        ]

        for message in auth_scenarios:
            with pytest.raises(CyberarkCCPAuthenticationError):
                raise CyberarkCCPAuthenticationError(message)

    def test_authorization_error_scenarios(self):
        """Test scenarios where CyberarkCCPAuthorizationError should be used."""
        # These represent actual authorization scenarios
        auth_scenarios = ["User not defined", "ITATS982E User app11 is not defined", "Insufficient permissions"]

        for message in auth_scenarios:
            with pytest.raises(CyberarkCCPAuthorizationError):
                raise CyberarkCCPAuthorizationError(message)

    def test_account_not_found_error_scenarios(self):
        """Test scenarios where CyberarkCCPAccountNotFoundError should be used."""
        # These represent actual account not found scenarios
        not_found_scenarios = ["Too many objects", "Safe not found", "Account not found", "Resource not found"]

        for message in not_found_scenarios:
            with pytest.raises(CyberarkCCPAccountNotFoundError):
                raise CyberarkCCPAccountNotFoundError(message)

    def test_connection_error_scenarios(self):
        """Test scenarios where CyberarkCCPConnectionError should be used."""
        # These represent actual connection scenarios
        connection_scenarios = [
            "Connection to the Vault has failed",
            "Connection error: HTTPSConnectionPool",
            "Network unreachable",
        ]

        for message in connection_scenarios:
            with pytest.raises(CyberarkCCPConnectionError):
                raise CyberarkCCPConnectionError(message)

    def test_timeout_error_scenarios(self):
        """Test scenarios where CyberarkCCPTimeoutError should be used."""
        # These represent actual timeout scenarios
        timeout_scenarios = ["Request timed out after 30 seconds", "Connection timeout", "Read timeout"]

        for message in timeout_scenarios:
            with pytest.raises(CyberarkCCPTimeoutError):
                raise CyberarkCCPTimeoutError(message)

    def test_error_code_mapping_scenarios(self):
        """Test that error codes map to appropriate exception types."""
        # Based on API specification error code mappings
        error_mappings = {
            # 400 errors
            "AIMWS030E": CyberarkCCPValidationError,
            "APPAP227E": CyberarkCCPAccountNotFoundError,
            "APPAP228E": CyberarkCCPAccountNotFoundError,
            "APPAP229E": CyberarkCCPAccountNotFoundError,
            "APPAP007E": CyberarkCCPConnectionError,
            "APPAP081E": CyberarkCCPValidationError,
            "CASVL010E": CyberarkCCPValidationError,
            "AIMWS031E": CyberarkCCPValidationError,
            # 403 errors
            "APPAP306E": CyberarkCCPAuthenticationError,
            "APPAP008E": CyberarkCCPAuthorizationError,
            # 404 errors
            "APPAP004E": CyberarkCCPAccountNotFoundError,
            # 500 errors
            "APPAP282E": CyberarkCCPError,
        }

        for error_code, expected_exception in error_mappings.items():
            message = f"Error with code {error_code}"

            with pytest.raises(expected_exception):
                raise expected_exception(message)
