"""Comprehensive unit tests for CyberArk CCP API client."""

import pytest
from unittest.mock import Mock, patch
import requests

from cyberark_ccp import (
    CyberarkCCPClient,
    QueryFormat,
    CyberarkCCPError,
    CyberarkCCPValidationError,
    CyberarkCCPAuthenticationError,
    CyberarkCCPAuthorizationError,
    CyberarkCCPAccountNotFoundError,
    CyberarkCCPConnectionError,
    CyberarkCCPTimeoutError,
)


class TestCyberarkCCPClient:
    """Test suite for CyberarkCCPClient class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.base_url = "https://ccp.example.com"
        self.app_id = "TestApp"
        self.client = CyberarkCCPClient(base_url=self.base_url, app_id=self.app_id, verify=True, timeout=30)

    def test_client_initialization(self):
        """Test client initialization with various parameters."""
        # Test basic initialization
        client = CyberarkCCPClient("https://test.com", "MyApp")
        assert client.base_url == "https://test.com"
        assert client.app_id == "MyApp"
        assert client.verify is True
        assert client.timeout == 30
        assert client.cert_path is None

        # Test with all parameters
        client = CyberarkCCPClient(
            base_url="https://test.com/",  # With trailing slash
            app_id="MyApp",
            cert_path="/path/to/cert.p12",
            verify=False,
            timeout=60,
        )
        assert client.base_url == "https://test.com"  # Trailing slash removed
        assert client.app_id == "MyApp"
        assert client.cert_path == "/path/to/cert.p12"
        assert client.verify is False
        assert client.timeout == 60

    def test_context_manager(self):
        """Test client as context manager."""
        with patch.object(self.client, "close") as mock_close:
            with self.client as client:
                assert client is self.client
            mock_close.assert_called_once()

    def test_build_params_basic(self):
        """Test parameter building with basic parameters."""
        params = self.client._build_params(safe="TestSafe", password_object="TestObject")

        expected = {"AppID": "TestApp", "Safe": "TestSafe", "Object": "TestObject"}
        assert params == expected

    def test_build_params_all_standard_parameters(self):
        """Test parameter building with all standard parameters."""
        params = self.client._build_params(
            safe="TestSafe",
            folder="TestFolder",
            password_object="TestObject",
            username="TestUser",
            address="test.example.com",
            database="TestDB",
            policy_id="TestPolicy",
            reason="TestReason",
        )

        expected = {
            "AppID": "TestApp",
            "Safe": "TestSafe",
            "Folder": "TestFolder",
            "Object": "TestObject",
            "UserName": "TestUser",
            "Address": "test.example.com",
            "Database": "TestDB",
            "PolicyID": "TestPolicy",
            "Reason": "TestReason",
        }
        assert params == expected

    def test_build_params_query_overrides_others(self):
        """Test that Query parameter overrides other search criteria per API spec."""
        params = self.client._build_params(
            query="Safe=TestSafe,Object=TestObject",
            query_format=QueryFormat.EXACT,
            safe="IgnoredSafe",  # Should be ignored
            password_object="IgnoredObject",  # Should be ignored
            reason="TestReason",  # Should still be included
        )

        expected = {
            "AppID": "TestApp",
            "Query": "Safe=TestSafe,Object=TestObject",
            "Query Format": "Exact",
            "Reason": "TestReason",
        }
        assert params == expected
        # Verify ignored parameters are not present
        assert "Safe" not in params
        assert "Object" not in params

    def test_build_params_query_format_exact(self):
        """Test Query Format parameter with Exact value."""
        params = self.client._build_params(query="Safe=TestSafe", query_format=QueryFormat.EXACT)

        assert params["Query Format"] == "Exact"

    def test_build_params_query_format_regexp(self):
        """Test Query Format parameter with Regexp value."""
        params = self.client._build_params(query="Safe=Test.*", query_format=QueryFormat.REGEXP)

        assert params["Query Format"] == "Regexp"

    def test_build_params_connection_timeout(self):
        """Test Connection Timeout parameter."""
        params = self.client._build_params(safe="TestSafe", connection_timeout=60)

        assert params["Connection Timeout"] == "60"

    def test_build_params_connection_timeout_validation(self):
        """Test Connection Timeout parameter validation."""
        with pytest.raises(CyberarkCCPValidationError, match="Connection timeout must be positive"):
            self.client._build_params(safe="TestSafe", connection_timeout=0)

        with pytest.raises(CyberarkCCPValidationError, match="Connection timeout must be positive"):
            self.client._build_params(safe="TestSafe", connection_timeout=-1)

    def test_build_params_fail_request_on_password_change(self):
        """Test FailRequestOnPasswordChange parameter."""
        # Test True value
        params = self.client._build_params(safe="TestSafe", fail_request_on_password_change=True)
        assert params["FailRequestOnPasswordChange"] == "true"

        # Test False value
        params = self.client._build_params(safe="TestSafe", fail_request_on_password_change=False)
        assert params["FailRequestOnPasswordChange"] == "false"

    def test_validate_url_value_valid(self):
        """Test URL value validation with valid inputs."""
        # These should not raise exceptions
        self.client._validate_url_value("ValidValue", "Test")
        self.client._validate_url_value("Valid123", "Test")
        self.client._validate_url_value("Valid_Value", "Test")
        self.client._validate_url_value("Valid-Value", "Test")

    def test_validate_url_value_invalid_characters(self):
        """Test URL value validation with invalid characters per API spec."""
        invalid_chars = ["+", "&", "%", ";"]

        for char in invalid_chars:
            with pytest.raises(CyberarkCCPValidationError) as exc_info:
                self.client._validate_url_value(f"test{char}value", "TestParam")

            assert f"invalid character '{char}'" in str(exc_info.value)
            assert "are not supported" in str(exc_info.value)

    def test_validate_url_value_spaces(self):
        """Test URL value validation with spaces."""
        with pytest.raises(CyberarkCCPValidationError) as exc_info:
            self.client._validate_url_value("test value", "TestParam")

        assert "contains spaces" in str(exc_info.value)
        assert "not allowed in URLs" in str(exc_info.value)

    def test_appid_and_one_other_parameter_validation(self):
        """Test that AppID and at least one other parameter is required per API spec."""
        with pytest.raises(CyberarkCCPValidationError) as exc_info:
            self.client.get_account()

        assert "AppID and at least one other parameter" in str(exc_info.value)

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_successful_request(self, mock_get):
        """Test successful API request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Content": "test-password",
            "UserName": "test-user",
            "Address": "test.example.com",
            "Database": "test-db",
            "PasswordChangeInProcess": False,
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.client.get_account(safe="TestSafe")

        # Verify request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args

        assert call_args[1]["params"]["AppID"] == "TestApp"
        assert call_args[1]["params"]["Safe"] == "TestSafe"
        assert call_args[1]["verify"] is True
        assert call_args[1]["timeout"] == 30

        # Verify response
        assert result["Content"] == "test-password"
        assert result["UserName"] == "test-user"
        assert result["Address"] == "test.example.com"
        assert result["Database"] == "test-db"
        assert result["PasswordChangeInProcess"] is False

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_get_password_method(self, mock_get):
        """Test get_password method returns only Content field."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"Content": "test-password", "UserName": "test-user"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        password = self.client.get_password(safe="TestSafe")
        assert password == "test-password"

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_certificate_authentication(self, mock_get):
        """Test certificate-based authentication."""
        client = CyberarkCCPClient(base_url="https://test.com", app_id="TestApp", cert_path="/path/to/cert.p12")

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"Content": "test-password"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        client.get_password(safe="TestSafe")

        # Verify cert parameter was passed
        call_args = mock_get.call_args
        assert call_args[1]["cert"] == "/path/to/cert.p12"


class TestErrorHandling:
    """Test suite for error handling according to API specification."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = CyberarkCCPClient("https://test.com", "TestApp")

    def create_mock_error_response(self, status_code, error_code=None, error_message="Test error"):
        """Create a mock error response."""
        mock_response = Mock()
        mock_response.status_code = status_code

        if error_code:
            mock_response.json.return_value = {"ErrorCode": error_code, "ErrorMessage": error_message}
        else:
            mock_response.json.side_effect = ValueError("Not JSON")
            mock_response.text = f"HTTP {status_code} Error"

        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        return mock_response

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_400_error_aimws030e_invalid_query_format(self, mock_get):
        """Test 400 error with AIMWS030E (Invalid query format)."""
        mock_get.return_value = self.create_mock_error_response(400, "AIMWS030E", "Invalid query format")

        with pytest.raises(CyberarkCCPValidationError) as exc_info:
            self.client.get_account(safe="TestSafe")

        assert "Invalid query format (AIMWS030E)" in str(exc_info.value)

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_400_error_appap227e_too_many_objects(self, mock_get):
        """Test 400 error with APPAP227E (Too many objects)."""
        mock_get.return_value = self.create_mock_error_response(400, "APPAP227E", "Too many objects")

        with pytest.raises(CyberarkCCPAccountNotFoundError) as exc_info:
            self.client.get_account(safe="TestSafe")

        assert "Too many objects (APPAP227E)" in str(exc_info.value)

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_400_error_appap228e_too_many_objects(self, mock_get):
        """Test 400 error with APPAP228E (Too many objects)."""
        mock_get.return_value = self.create_mock_error_response(400, "APPAP228E", "Too many objects")

        with pytest.raises(CyberarkCCPAccountNotFoundError) as exc_info:
            self.client.get_account(safe="TestSafe")

        assert "Too many objects (APPAP228E)" in str(exc_info.value)

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_400_error_appap229e_too_many_objects(self, mock_get):
        """Test 400 error with APPAP229E (Too many objects)."""
        mock_get.return_value = self.create_mock_error_response(400, "APPAP229E", "Too many objects")

        with pytest.raises(CyberarkCCPAccountNotFoundError) as exc_info:
            self.client.get_account(safe="TestSafe")

        assert "Too many objects (APPAP229E)" in str(exc_info.value)

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_400_error_appap007e_connection_to_vault_failed(self, mock_get):
        """Test 400 error with APPAP007E (Connection to Vault failed)."""
        mock_get.return_value = self.create_mock_error_response(400, "APPAP007E", "Connection to the Vault has failed")

        with pytest.raises(CyberarkCCPConnectionError) as exc_info:
            self.client.get_account(safe="TestSafe")

        assert "Connection to Vault failed (APPAP007E)" in str(exc_info.value)

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_400_error_appap081e_invalid_request_content(self, mock_get):
        """Test 400 error with APPAP081E (Invalid request message content)."""
        mock_get.return_value = self.create_mock_error_response(400, "APPAP081E", "Request message content is invalid")

        with pytest.raises(CyberarkCCPValidationError) as exc_info:
            self.client.get_account(safe="TestSafe")

        assert "Request validation error (APPAP081E)" in str(exc_info.value)

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_400_error_casvl010e_invalid_characters(self, mock_get):
        """Test 400 error with CASVL010E (Invalid characters in User Name)."""
        mock_get.return_value = self.create_mock_error_response(400, "CASVL010E", "Invalid characters in User Name")

        with pytest.raises(CyberarkCCPValidationError) as exc_info:
            self.client.get_account(safe="TestSafe")

        assert "Request validation error (CASVL010E)" in str(exc_info.value)

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_400_error_aimws031e_appid_required(self, mock_get):
        """Test 400 error with AIMWS031E (AppID parameter required)."""
        mock_get.return_value = self.create_mock_error_response(
            400, "AIMWS031E", "Invalid request. The AppID parameter is required"
        )

        with pytest.raises(CyberarkCCPValidationError) as exc_info:
            self.client.get_account(safe="TestSafe")

        assert "Request validation error (AIMWS031E)" in str(exc_info.value)

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_403_error_appap306e_authentication_failed(self, mock_get):
        """Test 403 error with APPAP306E (App failed on authentication check)."""
        mock_get.return_value = self.create_mock_error_response(403, "APPAP306E", "App failed on authentication check")

        with pytest.raises(CyberarkCCPAuthenticationError) as exc_info:
            self.client.get_account(safe="TestSafe")

        assert "Authentication failed (APPAP306E)" in str(exc_info.value)

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_403_error_appap008e_user_not_defined(self, mock_get):
        """Test 403 error with APPAP008E (User not defined)."""
        mock_get.return_value = self.create_mock_error_response(403, "APPAP008E", "ITATS982E User app11 is not defined")

        with pytest.raises(CyberarkCCPAuthorizationError) as exc_info:
            self.client.get_account(safe="TestSafe")

        assert "User not defined (APPAP008E)" in str(exc_info.value)

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_404_error_appap004e_safe_not_found(self, mock_get):
        """Test 404 error with APPAP004E (Safe not found)."""
        mock_get.return_value = self.create_mock_error_response(404, "APPAP004E", "Safe not found")

        with pytest.raises(CyberarkCCPAccountNotFoundError) as exc_info:
            self.client.get_account(safe="TestSafe")

        assert "Safe not found (APPAP004E)" in str(exc_info.value)

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_500_error_appap282e_password_change_in_progress(self, mock_get):
        """Test 500 error with APPAP282E (Password change in progress)."""
        mock_get.return_value = self.create_mock_error_response(
            500, "APPAP282E", "Password [password] is currently being changed by the CPM"
        )

        with pytest.raises(CyberarkCCPError) as exc_info:
            self.client.get_account(safe="TestSafe")

        assert "Password change in progress (APPAP282E)" in str(exc_info.value)

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_400_error_no_json_response(self, mock_get):
        """Test 400 error with non-JSON response."""
        mock_get.return_value = self.create_mock_error_response(400)

        with pytest.raises(CyberarkCCPValidationError) as exc_info:
            self.client.get_account(safe="TestSafe")

        assert "Bad Request (HTTP 400)" in str(exc_info.value)

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_403_error_no_json_response(self, mock_get):
        """Test 403 error with non-JSON response."""
        mock_get.return_value = self.create_mock_error_response(403)

        with pytest.raises(CyberarkCCPAuthenticationError) as exc_info:
            self.client.get_account(safe="TestSafe")

        assert "Forbidden (HTTP 403)" in str(exc_info.value)

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_404_error_no_json_response(self, mock_get):
        """Test 404 error with non-JSON response."""
        mock_get.return_value = self.create_mock_error_response(404)

        with pytest.raises(CyberarkCCPAccountNotFoundError) as exc_info:
            self.client.get_account(safe="TestSafe")

        assert "Not Found (HTTP 404)" in str(exc_info.value)

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_500_error_no_json_response(self, mock_get):
        """Test 500 error with non-JSON response."""
        mock_get.return_value = self.create_mock_error_response(500)

        with pytest.raises(CyberarkCCPError) as exc_info:
            self.client.get_account(safe="TestSafe")

        assert "Internal Server Error (HTTP 500)" in str(exc_info.value)

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_timeout_error(self, mock_get):
        """Test timeout error handling."""
        mock_get.side_effect = requests.exceptions.Timeout()

        with pytest.raises(CyberarkCCPTimeoutError) as exc_info:
            self.client.get_account(safe="TestSafe")

        assert "Request timed out after 30 seconds" in str(exc_info.value)

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_connection_error(self, mock_get):
        """Test connection error handling."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        with pytest.raises(CyberarkCCPConnectionError) as exc_info:
            self.client.get_account(safe="TestSafe")

        assert "Connection error" in str(exc_info.value)

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_generic_request_error(self, mock_get):
        """Test generic request error handling."""
        mock_get.side_effect = requests.exceptions.RequestException("Generic error")

        with pytest.raises(CyberarkCCPError) as exc_info:
            self.client.get_account(safe="TestSafe")

        assert "Request failed" in str(exc_info.value)

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_invalid_json_response(self, mock_get):
        """Test invalid JSON response handling."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with pytest.raises(CyberarkCCPError) as exc_info:
            self.client.get_account(safe="TestSafe")

        assert "Invalid JSON response from server" in str(exc_info.value)


class TestQueryFormat:
    """Test suite for QueryFormat enum."""

    def test_query_format_values(self):
        """Test QueryFormat enum values."""
        assert QueryFormat.EXACT.value == "Exact"
        assert QueryFormat.REGEXP.value == "Regexp"

    def test_query_format_usage(self):
        """Test QueryFormat enum usage in client."""
        client = CyberarkCCPClient("https://test.com", "TestApp")

        # Test with EXACT
        params = client._build_params(query="Safe=Test", query_format=QueryFormat.EXACT)
        assert params["Query Format"] == "Exact"

        # Test with REGEXP
        params = client._build_params(query="Safe=Test.*", query_format=QueryFormat.REGEXP)
        assert params["Query Format"] == "Regexp"


class TestAPISpecificationCompliance:
    """Test suite to verify compliance with API specification."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = CyberarkCCPClient("https://test.com", "TestApp")

    def test_url_construction(self):
        """Test URL construction matches API specification."""
        with patch("cyberark_ccp.client.requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"Content": "test"}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            self.client.get_account(safe="TestSafe")

            # Verify URL matches specification
            call_args = mock_get.call_args
            url = call_args[0][0]
            assert url == "https://test.com/AIMWebService/api/Accounts"

    def test_http_method_and_version(self):
        """Test HTTP method is GET as per specification."""
        with patch("cyberark_ccp.client.requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"Content": "test"}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            self.client.get_account(safe="TestSafe")

            # Verify GET method was used
            mock_get.assert_called_once()

    def test_content_type_expectation(self):
        """Test that we expect application/json content type."""
        # The client expects JSON responses, which is tested through json() calls
        # This is implicitly tested in other tests, but we can verify the expectation
        with patch("cyberark_ccp.client.requests.Session.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"Content": "test"}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = self.client.get_account(safe="TestSafe")

            # Verify we successfully parse JSON response
            assert isinstance(result, dict)
            mock_response.json.assert_called_once()

    def test_parameter_name_compliance(self):
        """Test that parameter names match API specification exactly."""
        # Test standard parameters (without Query to avoid override)
        params = self.client._build_params(
            safe="Safe",
            folder="Folder",
            password_object="Object",
            username="UserName",
            address="Address",
            database="Database",
            policy_id="PolicyID",
            reason="Reason",
            connection_timeout=60,
            fail_request_on_password_change=True,
        )

        # Verify exact parameter names from specification
        assert "AppID" in params
        assert "Safe" in params
        assert "Folder" in params
        assert "Object" in params
        assert "UserName" in params
        assert "Address" in params
        assert "Database" in params
        assert "PolicyID" in params
        assert "Reason" in params
        assert "Connection Timeout" in params  # Note: with space as per spec
        assert "FailRequestOnPasswordChange" in params

        # Test Query parameters separately (since Query overrides others)
        query_params = self.client._build_params(query="TestQuery", query_format=QueryFormat.EXACT, reason="TestReason")
        assert "Query" in query_params
        assert "Query Format" in query_params  # Note: with space as per spec

    def test_response_structure_compliance(self):
        """Test response structure matches API specification."""
        with patch("cyberark_ccp.client.requests.Session.get") as mock_get:
            # Mock response matching API specification
            api_response = {
                "Content": "test-password",
                "UserName": "test-user",
                "Address": "test.example.com",
                "Database": "test-db",
                "PasswordChangeInProcess": False,
            }

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = api_response
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = self.client.get_account(safe="TestSafe")

            # Verify all expected fields from specification
            assert "Content" in result
            assert "UserName" in result
            assert "Address" in result
            assert "Database" in result
            assert "PasswordChangeInProcess" in result

            # Verify data types match specification
            assert isinstance(result["Content"], str)
            assert isinstance(result["UserName"], str)
            assert isinstance(result["Address"], str)
            assert isinstance(result["Database"], str)
            assert isinstance(result["PasswordChangeInProcess"], bool)

    def test_character_restrictions_compliance(self):
        """Test character restrictions match API specification exactly."""
        # Test all restricted characters from specification: +, &, %, ;
        restricted_chars = ["+", "&", "%", ";"]

        for char in restricted_chars:
            with pytest.raises(CyberarkCCPValidationError):
                self.client._validate_url_value(f"test{char}value", "TestParam")

        # Test space restriction
        with pytest.raises(CyberarkCCPValidationError):
            self.client._validate_url_value("test value", "TestParam")

    def test_required_parameter_compliance(self):
        """Test AppID + at least one other parameter requirement."""
        # This should fail per specification
        with pytest.raises(CyberarkCCPValidationError, match="AppID and at least one other parameter"):
            self.client.get_account()

        # These should work (AppID + one other parameter)
        valid_combinations = [
            {"safe": "TestSafe"},
            {"folder": "TestFolder"},
            {"password_object": "TestObject"},
            {"username": "TestUser"},
            {"address": "TestAddress"},
            {"database": "TestDB"},
            {"policy_id": "TestPolicy"},
            {"query": "TestQuery"},
        ]

        for combo in valid_combinations:
            # Should not raise validation error (will raise connection error due to mocking)
            try:
                self.client._build_params(**combo)
            except CyberarkCCPValidationError as e:
                if "AppID and at least one other parameter" in str(e):
                    pytest.fail(f"Valid combination {combo} incorrectly rejected")

    def test_query_parameter_behavior_compliance(self):
        """Test Query parameter behavior per API specification."""
        # When Query is specified, other search criteria should be ignored
        params = self.client._build_params(
            query="Safe=TestSafe",
            safe="IgnoredSafe",
            folder="IgnoredFolder",
            password_object="IgnoredObject",
            username="IgnoredUser",
            address="IgnoredAddress",
            database="IgnoredDB",
            policy_id="IgnoredPolicy",
        )

        # Only Query should be present, others should be ignored
        assert "Query" in params
        assert "Safe" not in params
        assert "Folder" not in params
        assert "Object" not in params
        assert "UserName" not in params
        assert "Address" not in params
        assert "Database" not in params
        assert "PolicyID" not in params

    def test_default_values_compliance(self):
        """Test default values match API specification."""
        # Query Format default should be "Exact" if not specified
        params = self.client._build_params(query="Safe=Test")
        # When query_format is not specified, "Query Format" should not be in params
        # The default is handled by the API server, not the client
        assert "Query Format" not in params

        # Connection Timeout default is 30 (handled by server)
        params = self.client._build_params(safe="TestSafe")
        assert "Connection Timeout" not in params

        # FailRequestOnPasswordChange default is False (handled by server)
        params = self.client._build_params(safe="TestSafe")
        assert "FailRequestOnPasswordChange" not in params
