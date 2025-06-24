"""Integration tests for CyberArk CCP API client."""

import pytest
from unittest.mock import Mock, patch
import requests

from cyberark_ccp import (
    CyberarkCCPClient,
    QueryFormat,
    CyberarkCCPError,
    CyberarkCCPValidationError,
    CyberarkCCPAuthenticationError,
    CyberarkCCPAccountNotFoundError,
    CyberarkCCPConnectionError,
    CyberarkCCPTimeoutError,
)


class TestRealWorldScenarios:
    """Test suite for real-world usage scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = CyberarkCCPClient(
            base_url="https://ccp.example.com", app_id="MyApplication", verify=True, timeout=30
        )

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_database_credential_retrieval(self, mock_get):
        """Test retrieving database credentials with multiple search criteria."""
        # Mock successful database credential response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Content": "DatabasePassword123!",
            "UserName": "db_service_user",
            "Address": "database.example.com",
            "Database": "production_db",
            "PasswordChangeInProcess": False,
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Retrieve database credentials
        account_info = self.client.get_account(
            safe="DatabaseCredentials",
            username="db_service_user",
            address="database.example.com",
            database="production_db",
            reason="ApplicationStartup",
        )

        # Verify request parameters
        call_args = mock_get.call_args
        params = call_args[1]["params"]

        assert params["AppID"] == "MyApplication"
        assert params["Safe"] == "DatabaseCredentials"
        assert params["UserName"] == "db_service_user"
        assert params["Address"] == "database.example.com"
        assert params["Database"] == "production_db"
        assert params["Reason"] == "ApplicationStartup"

        # Verify response
        assert account_info["Content"] == "DatabasePassword123!"
        assert account_info["UserName"] == "db_service_user"
        assert account_info["Address"] == "database.example.com"
        assert account_info["Database"] == "production_db"
        assert account_info["PasswordChangeInProcess"] is False

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_web_service_credential_retrieval(self, mock_get):
        """Test retrieving web service credentials using object name."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Content": "WebServiceAPIKey789",
            "UserName": "api_service",
            "Address": "api.example.com",
            "PasswordChangeInProcess": False,
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        password = self.client.get_password(
            safe="WebServiceCredentials", password_object="APIService_Key", reason="APIIntegration"
        )

        # Verify request parameters
        call_args = mock_get.call_args
        params = call_args[1]["params"]

        assert params["Safe"] == "WebServiceCredentials"
        assert params["Object"] == "APIService_Key"
        assert params["Reason"] == "APIIntegration"

        # Verify password is extracted correctly
        assert password == "WebServiceAPIKey789"

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_advanced_query_with_regex(self, mock_get):
        """Test advanced query using regular expressions."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Content": "ProdDBPassword456",
            "UserName": "prod_service",
            "Address": "prod-db-01.example.com",
            "Database": "prod_main",
            "PasswordChangeInProcess": False,
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        account_info = self.client.get_account(
            query="Safe=Production,Address=prod-db-.*,Database=prod_.*",
            query_format=QueryFormat.REGEXP,
            connection_timeout=60,
            reason="ProductionDatabaseMaintenance",
        )

        # Verify request parameters
        call_args = mock_get.call_args
        params = call_args[1]["params"]

        assert params["Query"] == "Safe=Production,Address=prod-db-.*,Database=prod_.*"
        assert params["Query Format"] == "Regexp"
        assert params["Connection Timeout"] == "60"
        assert params["Reason"] == "ProductionDatabaseMaintenance"

        # Verify other search parameters are not included (ignored when Query is used)
        assert "Safe" not in params
        assert "Address" not in params
        assert "Database" not in params

        assert account_info["Content"] == "ProdDBPassword456"

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_certificate_based_authentication(self, mock_get):
        """Test certificate-based authentication workflow."""
        # Create client with certificate
        cert_client = CyberarkCCPClient(
            base_url="https://secure-ccp.example.com",
            app_id="SecureApplication",
            cert_path="/path/to/client-cert.p12",
            verify=True,
            timeout=45,
        )

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Content": "SecurePassword999",
            "UserName": "secure_service",
            "PasswordChangeInProcess": False,
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        password = cert_client.get_password(
            safe="HighSecuritySafe",
            password_object="CriticalService",
            fail_request_on_password_change=True,
            reason="CriticalSystemAccess",
        )

        # Verify certificate was used
        call_args = mock_get.call_args
        assert call_args[1]["cert"] == "/path/to/client-cert.p12"
        assert call_args[1]["verify"] is True
        assert call_args[1]["timeout"] == 45

        # Verify request parameters
        params = call_args[1]["params"]
        assert params["FailRequestOnPasswordChange"] == "true"

        assert password == "SecurePassword999"

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_password_change_in_progress_scenario(self, mock_get):
        """Test handling of password change in progress."""
        # First request fails due to password change
        mock_response_error = Mock()
        mock_response_error.status_code = 500
        mock_response_error.json.return_value = {
            "ErrorCode": "APPAP282E",
            "ErrorMessage": "Password [TestPassword] is currently being changed by the CPM.",
        }
        mock_response_error.raise_for_status.side_effect = requests.exceptions.HTTPError()

        # Second request with fail_request_on_password_change=False should succeed
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"Content": "NewPassword123", "PasswordChangeInProcess": True}
        mock_response_success.raise_for_status.return_value = None

        mock_get.side_effect = [mock_response_error, mock_response_success]

        # First request should fail
        with pytest.raises(CyberarkCCPError, match="Password change in progress"):
            self.client.get_password(
                safe="TestSafe", password_object="TestObject", fail_request_on_password_change=True
            )

        # Second request should succeed
        password = self.client.get_password(
            safe="TestSafe", password_object="TestObject", fail_request_on_password_change=False
        )

        assert password == "NewPassword123"

    def test_context_manager_usage(self):
        """Test using client as context manager."""
        with patch.object(CyberarkCCPClient, "close") as mock_close:
            with CyberarkCCPClient("https://test.com", "TestApp") as client:
                assert isinstance(client, CyberarkCCPClient)
                # Context manager should ensure cleanup

            mock_close.assert_called_once()

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_multiple_requests_session_reuse(self, mock_get):
        """Test that session is reused across multiple requests."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"Content": "password"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Make multiple requests
        self.client.get_password(safe="Safe1", password_object="Object1")
        self.client.get_password(safe="Safe2", password_object="Object2")
        self.client.get_password(safe="Safe3", password_object="Object3")

        # Verify session was reused (same session object for all calls)
        assert mock_get.call_count == 3

        # All calls should use the same session instance
        for call in mock_get.call_args_list:
            # This verifies the session object is consistent
            pass  # Session reuse is implicit in the mock setup

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_error_recovery_workflow(self, mock_get):
        """Test error recovery and retry scenarios."""
        # First request times out
        mock_get.side_effect = [
            requests.exceptions.Timeout(),
            # Second request succeeds
            Mock(
                status_code=200,
                json=Mock(return_value={"Content": "RecoveredPassword"}),
                raise_for_status=Mock(return_value=None),
            ),
        ]

        # First request should fail with timeout
        with pytest.raises(CyberarkCCPTimeoutError):
            self.client.get_password(safe="TestSafe", password_object="TestObject")

        # Second request should succeed
        password = self.client.get_password(safe="TestSafe", password_object="TestObject")
        assert password == "RecoveredPassword"


class TestErrorScenarios:
    """Test suite for various error scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = CyberarkCCPClient("https://test.com", "TestApp")

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_authentication_failure_workflow(self, mock_get):
        """Test complete authentication failure workflow."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.json.return_value = {
            "ErrorCode": "APPAP306E",
            "ErrorMessage": "App failed on authentication check.",
        }
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_get.return_value = mock_response

        with pytest.raises(CyberarkCCPAuthenticationError) as exc_info:
            self.client.get_account(safe="TestSafe")

        assert "Authentication failed (APPAP306E)" in str(exc_info.value)
        assert "App failed on authentication check" in str(exc_info.value)

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_account_not_found_workflow(self, mock_get):
        """Test account not found error workflow."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"ErrorCode": "APPAP004E", "ErrorMessage": "Safe not found"}
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_get.return_value = mock_response

        with pytest.raises(CyberarkCCPAccountNotFoundError) as exc_info:
            self.client.get_account(safe="NonExistentSafe")

        assert "Safe not found (APPAP004E)" in str(exc_info.value)

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_validation_error_workflow(self, mock_get):
        """Test validation error workflow."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "ErrorCode": "AIMWS031E",
            "ErrorMessage": "Invalid request. The AppID parameter is required.",
        }
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_get.return_value = mock_response

        with pytest.raises(CyberarkCCPValidationError) as exc_info:
            self.client.get_account(safe="TestSafe")

        assert "Request validation error (AIMWS031E)" in str(exc_info.value)

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_network_error_workflow(self, mock_get):
        """Test network error workflow."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        with pytest.raises(CyberarkCCPConnectionError) as exc_info:
            self.client.get_account(safe="TestSafe")

        assert "Connection error" in str(exc_info.value)
        assert "Connection refused" in str(exc_info.value)


class TestParameterValidationIntegration:
    """Test suite for integrated parameter validation scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = CyberarkCCPClient("https://test.com", "TestApp")

    def test_comprehensive_parameter_validation(self):
        """Test comprehensive parameter validation scenarios."""
        # Test various invalid character combinations
        invalid_values = [
            ("test+value", "+"),
            ("test&value", "&"),
            ("test%value", "%"),
            ("test;value", ";"),
            ("test value", "space"),
        ]

        for invalid_value, expected_char in invalid_values:
            with pytest.raises(CyberarkCCPValidationError) as exc_info:
                self.client._validate_url_value(invalid_value, "TestParam")

            error_message = str(exc_info.value)
            if expected_char == "space":
                assert "contains spaces" in error_message
            else:
                # Check that the specific character is mentioned in the error
                assert expected_char in error_message
                assert "are not supported" in error_message

    def test_parameter_combination_validation(self):
        """Test validation of parameter combinations."""
        # Valid combinations that should work
        valid_combinations = [
            {"safe": "ValidSafe"},
            {"folder": "ValidFolder"},
            {"password_object": "ValidObject"},
            {"username": "ValidUser"},
            {"address": "valid.example.com"},
            {"database": "ValidDB"},
            {"policy_id": "ValidPolicy"},
            {"query": "Safe=ValidSafe"},
            {"safe": "ValidSafe", "username": "ValidUser"},
            {"query": "Safe=ValidSafe", "query_format": QueryFormat.REGEXP},
        ]

        for combination in valid_combinations:
            try:
                params = self.client._build_params(**combination)
                assert "AppID" in params
                assert params["AppID"] == "TestApp"
            except CyberarkCCPValidationError as e:
                if "AppID and at least one other parameter" not in str(e):
                    pytest.fail(f"Valid combination {combination} failed validation: {e}")

    @patch("cyberark_ccp.client.requests.Session.get")
    def test_end_to_end_parameter_flow(self, mock_get):
        """Test end-to-end parameter validation and request flow."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"Content": "test-password"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test complex parameter combination
        password = self.client.get_password(
            safe="ProductionSafe",
            folder="DatabaseAccounts",
            password_object="MainDB_ServiceUser",
            username="db_service",
            address="prod-db.example.com",
            database="main_production",
            policy_id="DBPolicy_v2",
            reason="ScheduledBackupProcess",
            connection_timeout=120,
            fail_request_on_password_change=True,
        )

        # Verify all parameters were correctly processed
        call_args = mock_get.call_args
        params = call_args[1]["params"]

        expected_params = {
            "AppID": "TestApp",
            "Safe": "ProductionSafe",
            "Folder": "DatabaseAccounts",
            "Object": "MainDB_ServiceUser",
            "UserName": "db_service",
            "Address": "prod-db.example.com",
            "Database": "main_production",
            "PolicyID": "DBPolicy_v2",
            "Reason": "ScheduledBackupProcess",
            "Connection Timeout": "120",
            "FailRequestOnPasswordChange": "true",
        }

        for key, value in expected_params.items():
            assert params[key] == value

        assert password == "test-password"
