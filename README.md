# CyberArk Central Credential Provider (CCP) Python Client

[![PyPI version](https://badge.fury.io/py/cyberark-ccp.svg)](https://badge.fury.io/py/cyberark-ccp)
[![Python versions](https://img.shields.io/pypi/pyversions/cyberark-ccp.svg)](https://pypi.org/project/cyberark-ccp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/Tech-Daddy-Digital/CyberarkCCP/workflows/Tests/badge.svg)](https://github.com/Tech-Daddy-Digital/CyberarkCCP/actions)
[![Coverage](https://codecov.io/gh/Tech-Daddy-Digital/CyberarkCCP/branch/main/graph/badge.svg)](https://codecov.io/gh/Tech-Daddy-Digital/CyberarkCCP)

Official Python client library for the CyberArk Central Credential Provider (CCP) Web Service REST API. This library provides a simple and secure way to retrieve passwords and account information from CyberArk Privileged Access Manager (PAM).

## Features

- **Full API Coverage**: Complete implementation of the CyberArk CCP REST API specification
- **Robust Error Handling**: Comprehensive exception handling with specific error types for different scenarios
- **Certificate Authentication**: Support for client certificate-based authentication
- **Parameter Validation**: Built-in validation for all API parameters and character restrictions
- **Type Safety**: Full type hints support for better IDE integration and code quality
- **Production Ready**: Extensive test suite with 95+ tests covering all functionality
- **Python 3.8+**: Compatible with Python 3.8 and above

## Installation

Install the package using pip:

```bash
pip install cyberark-ccp
```

For development dependencies:

```bash
pip install cyberark-ccp[dev]
```

## Quick Start

### Basic Usage

```python
from cyberark_ccp import CyberarkCCPClient

# Initialize the client
client = CyberarkCCPClient(
    base_url="https://your-ccp-server.example.com",
    app_id="MyApplication"
)

# Retrieve a password
password = client.get_password(
    safe="DatabaseCredentials",
    password_object="ProdDB_User",
    reason="Application startup"
)

print(f"Retrieved password: {password}")
```

### Advanced Usage with Certificate Authentication

```python
from cyberark_ccp import CyberarkCCPClient

# Initialize with client certificate
client = CyberarkCCPClient(
    base_url="https://secure-ccp.example.com",
    app_id="SecureApplication",
    cert_path="/path/to/client-cert.p12",
    verify=True,
    timeout=60
)

# Get complete account information
account_info = client.get_account(
    safe="WebServiceCredentials",
    username="api_service",
    address="api.example.com",
    reason="API Integration"
)

print(f"Username: {account_info['UserName']}")
print(f"Address: {account_info['Address']}")
print(f"Password: {account_info['Content']}")
```

### Using Context Manager

```python
from cyberark_ccp import CyberarkCCPClient

# Automatic resource cleanup
with CyberarkCCPClient("https://ccp.example.com", "MyApp") as client:
    password = client.get_password(safe="TestSafe", password_object="TestAccount")
    # Client is automatically closed when exiting the context
```

### Advanced Query with Regular Expressions

```python
from cyberark_ccp import CyberarkCCPClient, QueryFormat

client = CyberarkCCPClient("https://ccp.example.com", "MyApp")

# Use regex patterns for flexible searching
account_info = client.get_account(
    query="Safe=Production,Address=prod-db-.*,Database=prod_.*",
    query_format=QueryFormat.REGEXP,
    reason="Database maintenance"
)
```

## API Reference

### CyberarkCCPClient

The main client class for interacting with the CCP API.

#### Constructor Parameters

- **base_url** (str): The base URL of your CCP server
- **app_id** (str): The Application ID configured in CyberArk
- **cert_path** (str, optional): Path to client certificate file (.p12)
- **verify** (bool, optional): Enable SSL certificate verification (default: True)
- **timeout** (int, optional): Request timeout in seconds (default: 30)

#### Methods

##### get_password()

Retrieve just the password content.

```python
password = client.get_password(
    safe="SafeName",                    # Safe name (optional if using query)
    folder="FolderName",               # Folder name (optional)
    password_object="ObjectName",       # Password object name (optional if using query)
    username="Username",               # Username (optional)
    address="Address",                 # Address (optional)
    database="DatabaseName",           # Database name (optional)
    policy_id="PolicyID",              # Policy ID (optional)
    reason="AccessReason",             # Reason for access (optional)
    query="QueryString",               # Query string (optional, overrides other search criteria)
    query_format=QueryFormat.EXACT,    # Query format (optional)
    connection_timeout=30,             # Connection timeout (optional)
    fail_request_on_password_change=False  # Fail if password change in progress (optional)
)
```

##### get_account()

Retrieve complete account information including password and metadata.

```python
account_info = client.get_account(
    # Same parameters as get_password()
)

# Returns dictionary with:
# - Content: The password
# - UserName: Account username
# - Address: Account address
# - Database: Database name
# - PasswordChangeInProcess: Boolean indicating if password change is in progress
```

### Exception Handling

The library provides specific exception types for different error scenarios:

```python
from cyberark_ccp import (
    CyberarkCCPError,                  # Base exception
    CyberarkCCPValidationError,        # Parameter validation errors
    CyberarkCCPAuthenticationError,    # Authentication failures
    CyberarkCCPAuthorizationError,     # Authorization/permission errors
    CyberarkCCPAccountNotFoundError,   # Account not found errors
    CyberarkCCPConnectionError,        # Network/connection errors
    CyberarkCCPTimeoutError,          # Timeout errors
)

try:
    password = client.get_password(safe="TestSafe", password_object="TestAccount")
except CyberarkCCPAuthenticationError:
    print("Authentication failed - check your App ID and certificate")
except CyberarkCCPAccountNotFoundError:
    print("Account not found - check your search criteria")
except CyberarkCCPValidationError as e:
    print(f"Parameter validation error: {e}")
except CyberarkCCPError as e:
    print(f"General CCP error: {e}")
```

### Query Formats

When using the `query` parameter, you can specify the format:

```python
from cyberark_ccp import QueryFormat

# Exact match (default)
QueryFormat.EXACT

# Regular expression
QueryFormat.REGEXP
```

## Error Codes

The library handles all documented CyberArk CCP error codes:

| HTTP Status | Error Code | Description | Exception Type |
|------------|------------|-------------|----------------|
| 400 | AIMWS030E | Invalid query format | CyberarkCCPValidationError |
| 400 | APPAP227E/228E/229E | Too many objects found | CyberarkCCPAccountNotFoundError |
| 400 | APPAP007E | Connection to Vault failed | CyberarkCCPConnectionError |
| 400 | APPAP081E | Invalid request content | CyberarkCCPValidationError |
| 400 | CASVL010E | Invalid characters in parameter | CyberarkCCPValidationError |
| 400 | AIMWS031E | AppID parameter required | CyberarkCCPValidationError |
| 403 | APPAP306E | Authentication failed | CyberarkCCPAuthenticationError |
| 403 | APPAP008E | User not defined | CyberarkCCPAuthorizationError |
| 404 | APPAP004E | Safe not found | CyberarkCCPAccountNotFoundError |
| 500 | APPAP282E | Password change in progress | CyberarkCCPError |

## Parameter Validation

The library enforces CyberArk's parameter validation rules:

- **Required Parameters**: AppID and at least one other search parameter
- **Character Restrictions**: The following characters are not supported in URL values: `+`, `&`, `%`, `;`, and spaces
- **Query Parameter Behavior**: When `query` is specified, other search criteria are ignored
- **Type Validation**: Proper type checking for integer and boolean parameters

## Configuration

### Environment Variables

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

### SSL Certificate Verification

```python
# Disable SSL verification (not recommended for production)
client = CyberarkCCPClient(
    base_url="https://ccp.example.com",
    app_id="MyApp",
    verify=False
)

# Use custom CA bundle
client = CyberarkCCPClient(
    base_url="https://ccp.example.com",
    app_id="MyApp",
    verify="/path/to/ca-bundle.crt"
)
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/Tech-Daddy-Digital/CyberarkCCP.git
cd CyberarkCCP

# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run tests with coverage
pytest --cov=cyberark_ccp

# Run linting
black cyberark_ccp test/
isort cyberark_ccp test/
flake8 cyberark_ccp test/

# Run type checking
mypy cyberark_ccp
```

### Using Tox

```bash
# Run tests across multiple Python versions
tox

# Run specific test environment
tox -e py311
tox -e lint
tox -e coverage
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Run linting (`tox -e lint`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Security

For security issues, please email security@cyberark.com rather than using the issue tracker.

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/Tech-Daddy-Digital/CyberarkCCP/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Tech-Daddy-Digital/CyberarkCCP/discussions)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes.

## Related Projects

- [CyberArk REST API Documentation](https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/WebServices/Implementing%20Privileged%20Account%20Security%20Web%20Services%20.htm)
- [CyberArk Central Credential Provider](https://docs.cyberark.com/Product-Doc/OnlineHelp/PAS/Latest/en/Content/PASIMP/The-Central-Credential-Provider.htm)