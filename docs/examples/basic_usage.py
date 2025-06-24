"""Basic usage examples for CyberArk CCP Python client."""

from cyberark_ccp import CyberarkCCPClient, CyberarkCCPError

def basic_password_retrieval():
    """Example: Basic password retrieval."""
    client = CyberarkCCPClient(
        base_url="https://ccp.example.com",
        app_id="MyApplication"
    )
    
    try:
        password = client.get_password(
            safe="DatabaseCredentials",
            password_object="ProdDB_User",
            reason="Application startup"
        )
        print(f"Retrieved password: {password}")
        
    except CyberarkCCPError as e:
        print(f"Error: {e}")

def get_complete_account_info():
    """Example: Get complete account information."""
    client = CyberarkCCPClient(
        base_url="https://ccp.example.com",
        app_id="MyApplication"
    )
    
    try:
        account_info = client.get_account(
            safe="WebServiceCredentials",
            username="api_service",
            address="api.example.com",
            reason="API Integration"
        )
        
        print(f"Username: {account_info['UserName']}")
        print(f"Address: {account_info['Address']}")
        print(f"Password: {account_info['Content']}")
        print(f"Password Change in Progress: {account_info['PasswordChangeInProcess']}")
        
    except CyberarkCCPError as e:
        print(f"Error: {e}")

def using_context_manager():
    """Example: Using client as context manager."""
    with CyberarkCCPClient("https://ccp.example.com", "MyApp") as client:
        password = client.get_password(
            safe="TestSafe",
            password_object="TestAccount",
            reason="Automated test"
        )
        print(f"Password: {password}")
        # Client is automatically closed when exiting the context

def multiple_search_criteria():
    """Example: Using multiple search criteria."""
    client = CyberarkCCPClient(
        base_url="https://ccp.example.com",
        app_id="DatabaseApp"
    )
    
    try:
        account_info = client.get_account(
            safe="DatabaseCredentials",
            username="db_service_user",
            address="database.example.com",
            database="production_db",
            reason="Database maintenance"
        )
        
        print(f"Found account: {account_info['UserName']}")
        print(f"Database: {account_info.get('Database', 'N/A')}")
        
    except CyberarkCCPError as e:
        print(f"Error: {e}")

def with_connection_timeout():
    """Example: Using custom connection timeout."""
    client = CyberarkCCPClient(
        base_url="https://ccp.example.com",
        app_id="MyApp",
        timeout=60  # 60 second timeout
    )
    
    try:
        password = client.get_password(
            safe="SlowSafe",
            password_object="SlowAccount",
            connection_timeout=120,  # Override default timeout for this request
            reason="Long running process"
        )
        print(f"Password: {password}")
        
    except CyberarkCCPError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("=== Basic Password Retrieval ===")
    basic_password_retrieval()
    
    print("\n=== Complete Account Information ===")
    get_complete_account_info()
    
    print("\n=== Context Manager ===")
    using_context_manager()
    
    print("\n=== Multiple Search Criteria ===")
    multiple_search_criteria()
    
    print("\n=== Custom Timeout ===")
    with_connection_timeout()