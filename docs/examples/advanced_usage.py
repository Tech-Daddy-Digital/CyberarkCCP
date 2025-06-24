"""Advanced usage examples for CyberArk CCP Python client."""

import os
from cyberark_ccp import (
    CyberarkCCPClient,
    QueryFormat,
    CyberarkCCPError,
    CyberarkCCPAuthenticationError,
    CyberarkCCPAccountNotFoundError,
    CyberarkCCPValidationError
)

def certificate_authentication():
    """Example: Using client certificate authentication."""
    client = CyberarkCCPClient(
        base_url="https://secure-ccp.example.com",
        app_id="SecureApplication",
        cert_path="/path/to/client-cert.p12",
        verify=True,
        timeout=45
    )
    
    try:
        password = client.get_password(
            safe="HighSecuritySafe",
            password_object="CriticalService",
            fail_request_on_password_change=True,
            reason="Critical system access"
        )
        print(f"Secure password retrieved: {password}")
        
    except CyberarkCCPError as e:
        print(f"Security error: {e}")

def regex_query_search():
    """Example: Using regular expressions for flexible searching."""
    client = CyberarkCCPClient(
        base_url="https://ccp.example.com",
        app_id="MyApp"
    )
    
    try:
        # Find all production database accounts
        account_info = client.get_account(
            query="Safe=Production,Address=prod-db-.*,Database=prod_.*",
            query_format=QueryFormat.REGEXP,
            connection_timeout=60,
            reason="Production database maintenance"
        )
        
        print(f"Found production database: {account_info['Address']}")
        print(f"Database: {account_info['Database']}")
        
    except CyberarkCCPError as e:
        print(f"Query error: {e}")

def exact_query_search():
    """Example: Using exact query for precise matching."""
    client = CyberarkCCPClient(
        base_url="https://ccp.example.com",
        app_id="MyApp"
    )
    
    try:
        password = client.get_password(
            query="Safe=WebServices,Object=API_Key_Production",
            query_format=QueryFormat.EXACT,
            reason="API authentication"
        )
        print(f"API key: {password}")
        
    except CyberarkCCPError as e:
        print(f"Error: {e}")

def comprehensive_error_handling():
    """Example: Comprehensive error handling."""
    client = CyberarkCCPClient(
        base_url="https://ccp.example.com",
        app_id="TestApp"
    )
    
    try:
        account_info = client.get_account(
            safe="TestSafe",
            password_object="TestAccount",
            reason="Error handling demo"
        )
        print(f"Success: {account_info['UserName']}")
        
    except CyberarkCCPAuthenticationError as e:
        print(f"Authentication failed: {e}")
        print("Check your App ID and certificate configuration")
        
    except CyberarkCCPAccountNotFoundError as e:
        print(f"Account not found: {e}")
        print("Verify your safe name and object name")
        
    except CyberarkCCPValidationError as e:
        print(f"Parameter validation error: {e}")
        print("Check your parameter values for invalid characters")
        
    except CyberarkCCPError as e:
        print(f"General CCP error: {e}")

def environment_configuration():
    """Example: Using environment variables for configuration."""
    # Set these environment variables:
    # export CYBERARK_CCP_URL="https://ccp.example.com"
    # export CYBERARK_CCP_APP_ID="MyApplication"
    # export CYBERARK_CCP_CERT_PATH="/path/to/cert.p12"
    
    client = CyberarkCCPClient(
        base_url=os.getenv("CYBERARK_CCP_URL"),
        app_id=os.getenv("CYBERARK_CCP_APP_ID"),
        cert_path=os.getenv("CYBERARK_CCP_CERT_PATH")
    )
    
    try:
        password = client.get_password(
            safe=os.getenv("CYBERARK_SAFE", "DefaultSafe"),
            password_object="ServiceAccount",
            reason="Environment-based configuration"
        )
        print(f"Password from environment config: {password}")
        
    except CyberarkCCPError as e:
        print(f"Error: {e}")

def custom_ssl_configuration():
    """Example: Custom SSL configuration."""
    # Disable SSL verification (not recommended for production)
    insecure_client = CyberarkCCPClient(
        base_url="https://dev-ccp.example.com",
        app_id="DevApp",
        verify=False
    )
    
    # Use custom CA bundle
    secure_client = CyberarkCCPClient(
        base_url="https://ccp.example.com",
        app_id="ProdApp",
        verify="/path/to/ca-bundle.crt"
    )
    
    try:
        # Use appropriate client based on environment
        if os.getenv("ENVIRONMENT") == "development":
            client = insecure_client
        else:
            client = secure_client
            
        password = client.get_password(
            safe="ConfigSafe",
            password_object="AppPassword"
        )
        print(f"Password with custom SSL: {password}")
        
    except CyberarkCCPError as e:
        print(f"SSL configuration error: {e}")

def batch_credential_retrieval():
    """Example: Retrieving multiple credentials efficiently."""
    client = CyberarkCCPClient(
        base_url="https://ccp.example.com",
        app_id="BatchApp"
    )
    
    credential_requests = [
        {"safe": "DatabaseCredentials", "password_object": "DB1_User"},
        {"safe": "WebServiceCredentials", "password_object": "API_Service"},
        {"safe": "SystemCredentials", "password_object": "Admin_Account"},
    ]
    
    credentials = {}
    
    for request in credential_requests:
        try:
            password = client.get_password(
                reason="Batch credential retrieval",
                **request
            )
            key = f"{request['safe']}/{request['password_object']}"
            credentials[key] = password
            print(f"Retrieved: {key}")
            
        except CyberarkCCPError as e:
            print(f"Failed to retrieve {request}: {e}")
    
    print(f"Successfully retrieved {len(credentials)} credentials")

def password_change_handling():
    """Example: Handling password change scenarios."""
    client = CyberarkCCPClient(
        base_url="https://ccp.example.com",
        app_id="MyApp"
    )
    
    # First try with fail_request_on_password_change=True
    try:
        password = client.get_password(
            safe="TestSafe",
            password_object="TestAccount",
            fail_request_on_password_change=True,
            reason="Password change handling demo"
        )
        print(f"Password (no change in progress): {password}")
        
    except CyberarkCCPError as e:
        if "password change" in str(e).lower():
            print("Password change in progress, retrying with different setting...")
            
            # Retry with fail_request_on_password_change=False
            try:
                password = client.get_password(
                    safe="TestSafe",
                    password_object="TestAccount",
                    fail_request_on_password_change=False,
                    reason="Password change handling demo - retry"
                )
                print(f"Password (change in progress): {password}")
                print("Note: This password may change soon!")
                
            except CyberarkCCPError as retry_error:
                print(f"Retry failed: {retry_error}")
        else:
            print(f"Other error: {e}")

if __name__ == "__main__":
    print("=== Certificate Authentication ===")
    certificate_authentication()
    
    print("\n=== Regex Query Search ===")
    regex_query_search()
    
    print("\n=== Exact Query Search ===")
    exact_query_search()
    
    print("\n=== Comprehensive Error Handling ===")
    comprehensive_error_handling()
    
    print("\n=== Environment Configuration ===")
    environment_configuration()
    
    print("\n=== Custom SSL Configuration ===")
    custom_ssl_configuration()
    
    print("\n=== Batch Credential Retrieval ===")
    batch_credential_retrieval()
    
    print("\n=== Password Change Handling ===")
    password_change_handling()