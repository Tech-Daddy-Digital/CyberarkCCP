# CyberArk CCP Python Client Documentation

Welcome to the official documentation for the CyberArk Central Credential Provider (CCP) Python client library.

## Table of Contents

- [Quick Start](quick-start.md)
- [API Reference](api-reference.md)
- [Examples](examples/)
- [Configuration](configuration.md)
- [Error Handling](error-handling.md)
- [Security Best Practices](security.md)
- [Testing](testing.md)
- [Contributing](contributing.md)

## Overview

The CyberArk CCP Python client is a comprehensive library that provides secure access to the CyberArk Central Credential Provider Web Service REST API. It enables applications to retrieve passwords and account information from CyberArk Privileged Access Manager (PAM) in a secure and standardized way.

### Key Features

- **Complete API Coverage**: Full implementation of the CyberArk CCP REST API specification
- **Type Safety**: Comprehensive type hints for better development experience
- **Robust Error Handling**: Specific exception types for different error scenarios
- **Certificate Authentication**: Support for client certificate-based authentication
- **Parameter Validation**: Built-in validation ensuring API compliance
- **Production Ready**: Extensively tested with 95+ unit tests

### Supported Python Versions

- Python 3.7+
- Python 3.8+
- Python 3.9+
- Python 3.10+
- Python 3.11+
- Python 3.12+

### API Compliance

This library is fully compliant with the CyberArk Central Credential Provider REST API specification, supporting all documented parameters, error codes, and response formats.

## Installation

```bash
pip install cyberark-ccp
```

## Quick Example

```python
from cyberark_ccp import CyberarkCCPClient

# Initialize client
client = CyberarkCCPClient(
    base_url="https://ccp.example.com",
    app_id="MyApplication"
)

# Retrieve password
password = client.get_password(
    safe="DatabaseCredentials",
    password_object="ProdDB_User",
    reason="Application startup"
)
```

## Getting Help

- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/Tech-Daddy-Digital/CyberarkCCP/issues)
- **Discussions**: Ask questions and share ideas on [GitHub Discussions](https://github.com/Tech-Daddy-Digital/CyberarkCCP/discussions)
- **Security**: For security issues, email security@cyberark.com

## License

MIT License - see [LICENSE](../LICENSE) for details.