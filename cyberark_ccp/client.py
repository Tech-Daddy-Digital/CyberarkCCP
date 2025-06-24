"""CyberArk Central Credential Provider (CCP) REST API client."""

from enum import Enum
from typing import Any, Dict, Optional

import requests

from .exceptions import (
    CyberarkCCPAccountNotFoundError,
    CyberarkCCPAuthenticationError,
    CyberarkCCPAuthorizationError,
    CyberarkCCPConnectionError,
    CyberarkCCPError,
    CyberarkCCPTimeoutError,
    CyberarkCCPValidationError,
)


class QueryFormat(Enum):
    """Query format options for CCP API."""

    EXACT = "Exact"
    REGEXP = "Regexp"


class CyberarkCCPClient:
    """CyberArk CCP API Client for retrieving credentials from the Central Credential Provider.

    This client provides methods to interact with CyberArk's Central Credential Provider
    REST API to securely retrieve passwords and account information.
    """

    def __init__(
        self,
        base_url: str,
        app_id: str,
        cert_path: Optional[str] = None,
        verify: bool = True,
        timeout: int = 30,
    ) -> None:
        """Initialize the CyberArk CCP client.

        Args:
            base_url: Base URL of the CCP web service (e.g., 'https://ccp.example.com')
            app_id: Application ID registered in CyberArk for authentication
            cert_path: Path to client certificate file for certificate-based authentication
            verify: Whether to verify SSL certificates (default: True)
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url.rstrip("/")
        self.app_id = app_id
        self.cert_path = cert_path
        self.verify = verify
        self.timeout = timeout
        self._session = requests.Session()

    def get_password(
        self,
        account: Optional[str] = None,
        safe: Optional[str] = None,
        folder: Optional[str] = None,
        password_object: Optional[str] = None,
        username: Optional[str] = None,
        address: Optional[str] = None,
        database: Optional[str] = None,
        policy_id: Optional[str] = None,
        reason: Optional[str] = None,
        query: Optional[str] = None,
        query_format: Optional[QueryFormat] = None,
        connection_timeout: Optional[int] = None,
        fail_request_on_password_change: Optional[bool] = None,
    ) -> str:
        """Retrieve a password from CyberArk CCP.

        Args:
            account: Account name (required unless using query parameter)
            safe: Safe name where the account is stored
            folder: Folder name where the account is stored (PAM Self-Hosted only)
            password_object: Password object name
            username: Username search criteria according to UserName account property
            address: Address search criteria according to Address account property
            database: Database search criteria according to Database account property
            policy_id: Format used in the setPolicyID method
            reason: Reason for password retrieval (audited in Credential Provider audit log)
            query: Free query using account properties (when specified, other criteria are ignored)
            query_format: Query format (Exact or Regexp, default: Exact)
            connection_timeout: Seconds CCP will try to retrieve password (default: 30)
            fail_request_on_password_change: Return error if called during password change (default: False)

        Returns:
            The password content as a string

        Raises:
            CyberarkCCPError: If the API request fails or returns an error
            CyberarkCCPValidationError: If parameters are invalid
        """
        account_data = self.get_account(
            account=account,
            safe=safe,
            folder=folder,
            password_object=password_object,
            username=username,
            address=address,
            database=database,
            policy_id=policy_id,
            reason=reason,
            query=query,
            query_format=query_format,
            connection_timeout=connection_timeout,
            fail_request_on_password_change=fail_request_on_password_change,
        )
        return account_data.get("Content", "")

    def get_account(
        self,
        account: Optional[str] = None,
        safe: Optional[str] = None,
        folder: Optional[str] = None,
        password_object: Optional[str] = None,
        username: Optional[str] = None,
        address: Optional[str] = None,
        database: Optional[str] = None,
        policy_id: Optional[str] = None,
        reason: Optional[str] = None,
        query: Optional[str] = None,
        query_format: Optional[QueryFormat] = None,
        connection_timeout: Optional[int] = None,
        fail_request_on_password_change: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Retrieve complete account information from CyberArk CCP.

        Args:
            account: Account name (required unless using query parameter)
            safe: Safe name where the account is stored
            folder: Folder name where the account is stored (PAM Self-Hosted only)
            password_object: Password object name
            username: Username search criteria according to UserName account property
            address: Address search criteria according to Address account property
            database: Database search criteria according to Database account property
            policy_id: Format used in the setPolicyID method
            reason: Reason for password retrieval (audited in Credential Provider audit log)
            query: Free query using account properties (when specified, other criteria are ignored)
            query_format: Query format (Exact or Regexp, default: Exact)
            connection_timeout: Seconds CCP will try to retrieve password (default: 30)
            fail_request_on_password_change: Return error if called during password change (default: False)

        Returns:
            Dictionary containing account information including:
            - Content: The password content or empty if error occurs
            - UserName: UserName property or empty if not exists
            - Address: Address property or empty if not exists
            - Database: Database property or empty if not exists
            - PasswordChangeInProcess: Boolean indicating if password change is in progress

        Raises:
            CyberarkCCPError: If the API request fails or returns an error
            CyberarkCCPValidationError: If parameters are invalid
        """
        # Validate that we have AppID and at least one other parameter
        if (
            not query
            and not account
            and not safe
            and not password_object
            and not username
            and not address
            and not database
            and not policy_id
        ):
            raise CyberarkCCPValidationError(
                "The query must contain the AppID and at least one other parameter"
            )

        params = self._build_params(
            account=account,
            safe=safe,
            folder=folder,
            password_object=password_object,
            username=username,
            address=address,
            database=database,
            policy_id=policy_id,
            reason=reason,
            query=query,
            query_format=query_format,
            connection_timeout=connection_timeout,
            fail_request_on_password_change=fail_request_on_password_change,
        )

        url = f"{self.base_url}/AIMWebService/api/Accounts"

        try:
            response = self._session.get(
                url,
                params=params,
                verify=self.verify,
                cert=self.cert_path if self.cert_path else None,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as http_err:
            self._handle_http_error(response, http_err)
        except requests.exceptions.Timeout:
            raise CyberarkCCPTimeoutError(
                f"Request timed out after {self.timeout} seconds"
            ) from None
        except requests.exceptions.ConnectionError as conn_err:
            raise CyberarkCCPConnectionError(
                f"Connection error: {str(conn_err)}"
            ) from conn_err
        except requests.exceptions.RequestException as req_err:
            raise CyberarkCCPError(f"Request failed: {str(req_err)}") from req_err
        except ValueError as json_err:
            raise CyberarkCCPError("Invalid JSON response from server") from json_err

    def _build_params(
        self,
        account: Optional[str] = None,
        safe: Optional[str] = None,
        folder: Optional[str] = None,
        password_object: Optional[str] = None,
        username: Optional[str] = None,
        address: Optional[str] = None,
        database: Optional[str] = None,
        policy_id: Optional[str] = None,
        reason: Optional[str] = None,
        query: Optional[str] = None,
        query_format: Optional[QueryFormat] = None,
        connection_timeout: Optional[int] = None,
        fail_request_on_password_change: Optional[bool] = None,
    ) -> Dict[str, str]:
        """Build query parameters for the API request.

        Args:
            account: Account name
            safe: Safe name
            folder: Folder name
            password_object: Password object name
            username: Username
            address: Address/hostname
            database: Database name
            policy_id: Policy ID
            reason: Reason for retrieval
            query: Free query string
            query_format: Query format (Exact or Regexp)
            connection_timeout: Connection timeout in seconds
            fail_request_on_password_change: Fail if password change in progress

        Returns:
            Dictionary of query parameters with non-None values

        Raises:
            CyberarkCCPValidationError: If parameters contain invalid characters
        """
        params = {
            "AppID": self.app_id,
        }

        # If query is specified, other search criteria are ignored per API spec
        if query:
            self._validate_url_value(query, "Query")
            params["Query"] = query

            if query_format:
                params["Query Format"] = query_format.value
        else:
            # Add standard search parameters
            optional_params = {
                "Safe": safe,
                "Folder": folder,
                "Object": password_object,
                "UserName": username,
                "Address": address,
                "Database": database,
                "PolicyID": policy_id,
            }

            for key, value in optional_params.items():
                if value is not None:
                    self._validate_url_value(value, key)
                    params[key] = value

        # Add additional parameters
        if reason is not None:
            self._validate_url_value(reason, "Reason")
            params["Reason"] = reason

        if connection_timeout is not None:
            if connection_timeout <= 0:
                raise CyberarkCCPValidationError("Connection timeout must be positive")
            params["Connection Timeout"] = str(connection_timeout)

        if fail_request_on_password_change is not None:
            params["FailRequestOnPasswordChange"] = str(
                fail_request_on_password_change
            ).lower()

        return params

    def _validate_url_value(self, value: str, param_name: str) -> None:
        """Validate that URL parameter values don't contain restricted characters.

        Args:
            value: Parameter value to validate
            param_name: Name of the parameter for error messages

        Raises:
            CyberarkCCPValidationError: If value contains invalid characters
        """
        # Check for characters not supported by CCP API (per specification)
        invalid_chars = ["+", "&", "%", ";"]
        for char in invalid_chars:
            if char in value:
                raise CyberarkCCPValidationError(
                    f"Parameter '{param_name}' contains invalid character '{char}'. "
                    f"Characters {invalid_chars} are not supported."
                )

        # Check for spaces (not allowed in URLs per specification)
        if " " in value:
            raise CyberarkCCPValidationError(
                f"Parameter '{param_name}' contains spaces which are not allowed in URLs"
            )

    def _handle_http_error(
        self, response: requests.Response, http_err: requests.exceptions.HTTPError
    ) -> None:
        """Handle HTTP errors from the CCP API according to official specification.

        Args:
            response: The HTTP response object
            http_err: The HTTP error exception

        Raises:
            CyberarkCCPError: With detailed error information mapped to specific exceptions
        """
        status_code = response.status_code

        try:
            error_json = response.json()
            error_code = error_json.get("ErrorCode", "Unknown")
            error_message = error_json.get("ErrorMessage", "No message provided")

            # Map specific CCP error codes per official specification
            if status_code == 400:  # Bad Request
                if error_code in ["AIMWS030E"]:
                    raise CyberarkCCPValidationError(
                        f"Invalid query format ({error_code}): {error_message}"
                    ) from http_err
                elif error_code in ["APPAP227E", "APPAP228E", "APPAP229E"]:
                    raise CyberarkCCPAccountNotFoundError(
                        f"Too many objects ({error_code}): {error_message}"
                    ) from http_err
                elif error_code in ["APPAP007E"]:
                    raise CyberarkCCPConnectionError(
                        f"Connection to Vault failed ({error_code}): {error_message}"
                    ) from http_err
                elif error_code in ["APPAP081E", "CASVL010E", "AIMWS031E"]:
                    raise CyberarkCCPValidationError(
                        f"Request validation error ({error_code}): {error_message}"
                    ) from http_err
                else:
                    raise CyberarkCCPError(
                        f"Bad Request ({error_code}): {error_message}"
                    ) from http_err

            elif status_code == 403:  # Forbidden
                if error_code in ["APPAP306E"]:
                    raise CyberarkCCPAuthenticationError(
                        f"Authentication failed ({error_code}): {error_message}"
                    ) from http_err
                elif error_code in ["APPAP008E"]:
                    raise CyberarkCCPAuthorizationError(
                        f"User not defined ({error_code}): {error_message}"
                    ) from http_err
                else:
                    raise CyberarkCCPAuthorizationError(
                        f"Authorization failed ({error_code}): {error_message}"
                    ) from http_err

            elif status_code == 404:  # Not Found
                if error_code in ["APPAP004E"]:
                    raise CyberarkCCPAccountNotFoundError(
                        f"Safe not found ({error_code}): {error_message}"
                    ) from http_err
                else:
                    raise CyberarkCCPAccountNotFoundError(
                        f"Resource not found ({error_code}): {error_message}"
                    ) from http_err

            elif status_code == 500:  # Internal Server Error
                if error_code in ["APPAP282E"]:
                    raise CyberarkCCPError(
                        f"Password change in progress ({error_code}): {error_message}"
                    ) from http_err
                else:
                    raise CyberarkCCPError(
                        f"Internal server error ({error_code}): {error_message}"
                    ) from http_err

            else:
                raise CyberarkCCPError(
                    f"CCP API error {status_code} ({error_code}): {error_message}"
                ) from http_err

        except ValueError:
            # Response is not JSON - use status code for classification
            error_text = response.text or str(http_err)

            if status_code == 400:
                raise CyberarkCCPValidationError(
                    f"Bad Request (HTTP {status_code}): {error_text}"
                ) from http_err
            elif status_code == 403:
                raise CyberarkCCPAuthenticationError(
                    f"Forbidden (HTTP {status_code}): {error_text}"
                ) from http_err
            elif status_code == 404:
                raise CyberarkCCPAccountNotFoundError(
                    f"Not Found (HTTP {status_code}): {error_text}"
                ) from http_err
            elif status_code == 500:
                raise CyberarkCCPError(
                    f"Internal Server Error (HTTP {status_code}): {error_text}"
                ) from http_err
            else:
                raise CyberarkCCPError(
                    f"HTTP error {status_code}: {error_text}"
                ) from http_err

    def close(self) -> None:
        """Close the HTTP session to free up resources."""
        self._session.close()

    def __enter__(self) -> "CyberarkCCPClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()
