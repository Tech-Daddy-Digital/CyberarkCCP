# Quick Start Guide

This guide will help you get up and running with the CyberArk CCP Python client quickly.

## Installation

Install the package using pip:

```bash
pip install cyberark-ccp
```

For development dependencies:

```bash
pip install cyberark-ccp[dev]
```

## Basic Setup

### 1. Import the Client

```python
from cyberark_ccp import CyberarkCCPClient
```

### 2. Initialize the Client

```python
client = CyberarkCCPClient(
    base_url="https://your-ccp-server.example.com",
    app_id="YourApplicationID"
)
```

### 3. Retrieve a Password

```python
password = client.get_password(
    safe="YourSafeName",
    password_object="YourPasswordObject",
    reason="Application startup"
)

print(f"Password: {password}")
```

## Complete Example

Here's a complete working example:

```python
from cyberark_ccp import CyberarkCCPClient, CyberarkCCPError

def main():
    # Initialize the client
    client = CyberarkCCPClient(
        base_url="https://ccp.example.com",
        app_id="MyDatabaseApp"
    )
    
    try:
        # Retrieve database credentials
        account_info = client.get_account(
            safe="DatabaseCredentials",
            username="db_service_user",
            address="database.example.com",
            database="production_db",
            reason="Database connection"
        )
        
        # Use the credentials
        print(f"Database Server: {account_info['Address']}")
        print(f"Username: {account_info['UserName']}")
        print(f"Password: {account_info['Content']}")
        print(f"Database: {account_info['Database']}")
        
    except CyberarkCCPError as e:
        print(f"Error retrieving credentials: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
```

## Using Context Manager

For automatic resource cleanup, use the client as a context manager:

```python
from cyberark_ccp import CyberarkCCPClient

with CyberarkCCPClient("https://ccp.example.com", "MyApp") as client:
    password = client.get_password(
        safe="TestSafe",
        password_object="TestAccount"
    )
    # Client is automatically cleaned up when exiting the context
```

## Certificate Authentication

For environments requiring client certificate authentication:

```python
client = CyberarkCCPClient(
    base_url="https://secure-ccp.example.com",
    app_id="SecureApplication",
    cert_path="/path/to/client-cert.p12",  # Path to your certificate
    verify=True  # Enable SSL verification
)

password = client.get_password(
    safe="HighSecuritySafe",
    password_object="CriticalService"
)
```

## Environment Variables

You can use environment variables for configuration:

```bash
export CYBERARK_CCP_URL="https://ccp.example.com"
export CYBERARK_CCP_APP_ID="MyApplication"
export CYBERARK_CCP_CERT_PATH="/path/to/cert.p12"
```

```python
import os
from cyberark_ccp import CyberarkCCPClient

client = CyberarkCCPClient(
    base_url=os.getenv("CYBERARK_CCP_URL"),
    app_id=os.getenv("CYBERARK_CCP_APP_ID"),
    cert_path=os.getenv("CYBERARK_CCP_CERT_PATH")
)
```

## Next Steps

- Learn about [error handling](error-handling.md)
- Explore [advanced examples](examples/)
- Review [security best practices](security.md)
- Check the complete [API reference](api-reference.md)