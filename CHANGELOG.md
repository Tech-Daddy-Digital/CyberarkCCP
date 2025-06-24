# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-XX

### Added
- Initial release of the CyberArk CCP Python client
- Full implementation of CyberArk Central Credential Provider REST API
- Support for all API parameters: Safe, Folder, Object, UserName, Address, Database, PolicyID, Reason, Query, Query Format, Connection Timeout, FailRequestOnPasswordChange
- Certificate-based authentication support
- Comprehensive error handling with specific exception types for different scenarios
- Built-in parameter validation and character restriction enforcement
- Context manager support for automatic resource cleanup
- Type hints for better IDE integration
- Extensive test suite with 95+ unit tests
- Support for Python 3.7+

### Features
- **CyberarkCCPClient**: Main client class for API interactions
- **get_password()**: Retrieve password content only
- **get_account()**: Retrieve complete account information including metadata
- **QueryFormat enum**: Support for Exact and Regexp query formats
- **Exception hierarchy**: Specific exceptions for authentication, authorization, validation, connection, and timeout errors
- **Parameter validation**: Automatic validation of URL characters and required parameters
- **SSL/TLS support**: Full SSL certificate verification with custom CA bundle support
- **Session management**: Efficient HTTP session reuse across requests

### Error Handling
- CyberarkCCPError: Base exception class
- CyberarkCCPValidationError: Parameter validation errors (AIMWS030E, APPAP081E, CASVL010E, AIMWS031E)
- CyberarkCCPAuthenticationError: Authentication failures (APPAP306E)
- CyberarkCCPAuthorizationError: Authorization errors (APPAP008E)
- CyberarkCCPAccountNotFoundError: Account not found errors (APPAP004E, APPAP227E, APPAP228E, APPAP229E)
- CyberarkCCPConnectionError: Network and connection errors (APPAP007E)
- CyberarkCCPTimeoutError: Request timeout errors

### API Compliance
- Complete compliance with CyberArk CCP REST API specification
- Support for all documented error codes and response formats
- Proper handling of Query parameter override behavior
- Character restriction validation (+, &, %, ;, spaces)
- Correct parameter type handling (string, integer, boolean)

### Documentation
- Comprehensive README with examples and API reference
- Detailed documentation in docs/ directory
- Code examples for basic and advanced usage scenarios
- Configuration guide with security best practices
- Testing documentation with coverage information

### Development
- Modern Python packaging with pyproject.toml
- Tox configuration for multi-version testing
- GitHub Actions for CI/CD and automated PyPI publishing
- Code quality tools: black, isort, flake8, mypy
- Security scanning with safety and bandit
- 93% code coverage with pytest and pytest-cov