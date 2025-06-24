"""API specification compliance tests for CyberArk CCP API client.

These tests verify that the client implementation strictly follows the
CyberArk Central Credential Provider REST API specification.
"""

import pytest
from unittest.mock import patch

from cyberark_ccp import (
    CyberarkCCPClient,
    QueryFormat,
    CyberarkCCPValidationError,
)


class TestAPISpecificationCompliance:
    """Test suite to verify strict compliance with the API specification."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = CyberarkCCPClient("https://ccp.example.com", "TestApp")

    def test_url_format_compliance(self):
        """Test URL format matches specification exactly."""
        with patch("cyberark_ccp.client.requests.Session.get") as mock_get:
            # Mock successful response
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"Content": "test"}
            mock_get.return_value.raise_for_status.return_value = None

            self.client.get_account(safe="TestSafe")

            # Verify URL matches specification: https://<IIS_Server_Ip>/AIMWebService/api/Accounts
            call_args = mock_get.call_args
            url = call_args[0][0]
            assert url == "https://ccp.example.com/AIMWebService/api/Accounts"

    def test_http_method_compliance(self):
        """Test that only GET method is used as per specification."""
        with patch("cyberark_ccp.client.requests.Session.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"Content": "test"}
            mock_get.return_value.raise_for_status.return_value = None

            self.client.get_account(safe="TestSafe")

            # Verify only GET method is called
            mock_get.assert_called_once()

    def test_query_parameter_names_compliance(self):
        """Test that parameter names match specification exactly."""
        # Test standard parameters (without Query to avoid override)
        params = self.client._build_params(
            safe="TestSafe",
            folder="TestFolder",
            password_object="TestObject",
            username="TestUser",
            address="TestAddress",
            database="TestDatabase",
            policy_id="TestPolicy",
            reason="TestReason",
            connection_timeout=60,
            fail_request_on_password_change=True,
        )

        # Verify exact parameter names from specification
        assert "AppID" in params
        assert "Safe" in params
        assert "Folder" in params
        assert "Object" in params  # Not "password_object"
        assert "UserName" in params  # Not "username"
        assert "Address" in params
        assert "Database" in params
        assert "PolicyID" in params  # Not "policy_id"
        assert "Reason" in params
        assert "Connection Timeout" in params  # Note: space in parameter name
        assert "FailRequestOnPasswordChange" in params

        # Test Query parameters separately (since Query overrides others)
        query_params = self.client._build_params(query="TestQuery", query_format=QueryFormat.EXACT)
        assert "Query" in query_params
        assert "Query Format" in query_params  # Note: space in parameter name

    def test_appid_required_compliance(self):
        """Test AppID requirement per specification."""
        # AppID should always be present
        params = self.client._build_params(safe="TestSafe")
        assert "AppID" in params
        assert params["AppID"] == "TestApp"

    def test_at_least_one_other_parameter_compliance(self):
        """Test 'AppID and at least one other parameter' requirement."""
        # Per specification: "The query must contain the AppID and at least one other parameter"
        with pytest.raises(CyberarkCCPValidationError, match="AppID and at least one other parameter"):
            self.client.get_account()

    def test_query_parameter_overrides_compliance(self):
        """Test Query parameter behavior per specification."""
        # Per specification: "When this method is specified, all other search criteria
        # (Safe/Folder/Object/UserName/Address/PolicyID/Database) are ignored"
        params = self.client._build_params(
            query="Safe=TestSafe",
            safe="IgnoredSafe",
            folder="IgnoredFolder",
            password_object="IgnoredObject",
            username="IgnoredUser",
            address="IgnoredAddress",
            database="IgnoredDatabase",
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

    def test_query_format_values_compliance(self):
        """Test Query Format values match specification exactly."""
        # Per specification: Possible values: Exact, Regexp
        assert QueryFormat.EXACT.value == "Exact"
        assert QueryFormat.REGEXP.value == "Regexp"

        # Test parameter usage
        params = self.client._build_params(query="Test", query_format=QueryFormat.EXACT)
        assert params["Query Format"] == "Exact"

        params = self.client._build_params(query="Test.*", query_format=QueryFormat.REGEXP)
        assert params["Query Format"] == "Regexp"

    def test_character_restrictions_compliance(self):
        """Test character restrictions per specification."""
        # Per specification: "The following characters are not supported in URL values: +, &, %"
        # Plus additional note: "such as ; (semi-colon)"
        restricted_chars = ["+", "&", "%", ";"]

        for char in restricted_chars:
            with pytest.raises(CyberarkCCPValidationError):
                self.client._validate_url_value(f"test{char}value", "TestParam")

        # Per specification: "Make sure there are no spaces in the URL"
        with pytest.raises(CyberarkCCPValidationError):
            self.client._validate_url_value("test value", "TestParam")

    def test_connection_timeout_type_compliance(self):
        """Test Connection Timeout parameter type per specification."""
        # Per specification: Type = Int, Default = 30
        params = self.client._build_params(safe="TestSafe", connection_timeout=45)

        # Should be converted to string for URL parameter
        assert params["Connection Timeout"] == "45"
        assert isinstance(params["Connection Timeout"], str)

    def test_fail_request_on_password_change_type_compliance(self):
        """Test FailRequestOnPasswordChange parameter type per specification."""
        # Per specification: Type = Boolean, Default = False

        # Test True value
        params = self.client._build_params(safe="TestSafe", fail_request_on_password_change=True)
        assert params["FailRequestOnPasswordChange"] == "true"

        # Test False value
        params = self.client._build_params(safe="TestSafe", fail_request_on_password_change=False)
        assert params["FailRequestOnPasswordChange"] == "false"

    def test_response_structure_compliance(self):
        """Test expected response structure per specification."""
        with patch("cyberark_ccp.client.requests.Session.get") as mock_get:
            # Mock response matching specification structure
            spec_response = {
                "Content": "MyPassword",
                "UserName": "myuser",
                "Address": "myaddress",
                "Database": "MyDatabase",
                "PasswordChangeInProcess": False,
            }

            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = spec_response
            mock_get.return_value.raise_for_status.return_value = None

            result = self.client.get_account(safe="TestSafe")

            # Verify all fields from specification are accessible
            assert "Content" in result
            assert "UserName" in result
            assert "Address" in result
            assert "Database" in result
            assert "PasswordChangeInProcess" in result

            # Verify field types per specification
            assert isinstance(result["Content"], str)
            assert isinstance(result["UserName"], str)
            assert isinstance(result["Address"], str)
            assert isinstance(result["Database"], str)
            assert isinstance(result["PasswordChangeInProcess"], bool)

    def test_http_status_code_compliance(self):
        """Test HTTP status code handling per specification."""
        with patch("cyberark_ccp.client.requests.Session.get") as mock_get:
            # Test successful response (Status Code: 200)
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"Content": "test"}
            mock_get.return_value.raise_for_status.return_value = None

            result = self.client.get_account(safe="TestSafe")
            assert isinstance(result, dict)

    def test_default_values_compliance(self):
        """Test default values per specification."""
        # Per specification defaults:
        # - Folder: Root (only in PAM Self-Hosted)
        # - Query Format: Exact
        # - Connection Timeout: 30
        # - FailRequestOnPasswordChange: False

        # These defaults are handled by the server, not the client
        # Client only sends non-None values
        params = self.client._build_params(safe="TestSafe")

        # Default values should not be explicitly sent by client
        assert "Folder" not in params  # Only sent if explicitly provided
        assert "Query Format" not in params  # Only sent with Query
        assert "Connection Timeout" not in params  # Only sent if explicitly provided
        assert "FailRequestOnPasswordChange" not in params  # Only sent if explicitly provided

    def test_parameter_purpose_compliance(self):
        """Test parameter purposes match specification."""
        # Test AppID purpose: "Specifies the unique ID of the application issuing the password request"
        params = self.client._build_params(safe="TestSafe")
        assert params["AppID"] == "TestApp"

        # Test Safe purpose: "Specifies the name of the Safe where the password is stored"
        params = self.client._build_params(safe="ProductionSafe")
        assert params["Safe"] == "ProductionSafe"

        # Test Reason purpose: "The reason for retrieving the password. This reason will be audited"
        params = self.client._build_params(safe="TestSafe", reason="ApplicationStartup")
        assert params["Reason"] == "ApplicationStartup"

    def test_folder_pam_self_hosted_note_compliance(self):
        """Test Folder parameter note compliance."""
        # Per specification: "Folders are only supported in PAM - Self-Hosted"
        # Client should still accept and send the parameter if provided
        params = self.client._build_params(safe="TestSafe", folder="SubFolder")
        assert params["Folder"] == "SubFolder"

    def test_content_type_expectation_compliance(self):
        """Test content type expectation per specification."""
        # Per specification: Content type = application/json
        with patch("cyberark_ccp.client.requests.Session.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"Content": "test"}
            mock_get.return_value.raise_for_status.return_value = None

            self.client.get_account(safe="TestSafe")

            # Client should expect JSON response (verified by calling .json())
            mock_get.return_value.json.assert_called_once()

    def test_single_password_return_compliance(self):
        """Test that API returns single password per specification."""
        # Per specification: "This REST API returns a single password"
        with patch("cyberark_ccp.client.requests.Session.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {"Content": "SinglePassword"}
            mock_get.return_value.raise_for_status.return_value = None

            password = self.client.get_password(safe="TestSafe")

            # Should return single password string
            assert isinstance(password, str)
            assert password == "SinglePassword"

    def test_url_space_restriction_compliance(self):
        """Test URL space restriction per specification."""
        # Per specification: "Make sure there are no spaces in the URL"
        with pytest.raises(CyberarkCCPValidationError, match="spaces which are not allowed in URLs"):
            self.client._validate_url_value("value with spaces", "TestParam")

    def test_semicolon_restriction_compliance(self):
        """Test semicolon restriction per specification."""
        # Per specification: "such as ; (semi-colon)"
        with pytest.raises(CyberarkCCPValidationError, match="invalid character ';'"):
            self.client._validate_url_value("value;with;semicolon", "TestParam")
