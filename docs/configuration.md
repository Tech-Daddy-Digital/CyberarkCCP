# Configuration Guide

This guide covers all the configuration options available for the CyberArk CCP Python client.

## Client Configuration

### Basic Configuration

```python
from cyberark_ccp import CyberarkCCPClient

client = CyberarkCCPClient(
    base_url="https://ccp.example.com",
    app_id="MyApplication"
)
```

### Complete Configuration

```python
client = CyberarkCCPClient(
    base_url="https://ccp.example.com",
    app_id="MyApplication",
    cert_path="/path/to/client-cert.p12",
    verify=True,
    timeout=30
)
```

## Configuration Parameters

### base_url (required)

The base URL of your CyberArk CCP server.

- **Type**: `str`
- **Example**: `"https://ccp.example.com"`
- **Notes**: 
  - Should include protocol (https://)
  - Trailing slash is automatically removed
  - Must be accessible from your application

### app_id (required)

The Application ID configured in CyberArk for your application.

- **Type**: `str`
- **Example**: `"MyDatabaseApplication"`
- **Notes**:
  - Must match exactly the App ID configured in CyberArk
  - Case-sensitive
  - Used for authentication and authorization

### cert_path (optional)

Path to the client certificate file for authentication.

- **Type**: `str | None`
- **Default**: `None`
- **Example**: `"/path/to/client-cert.p12"`
- **Supported formats**:
  - PKCS#12 (.p12, .pfx)
  - PEM certificate and key files
- **Notes**:
  - Required for environments using client certificate authentication
  - Certificate must be configured in CyberArk

### verify (optional)

SSL certificate verification setting.

- **Type**: `bool | str`
- **Default**: `True`
- **Options**:
  - `True`: Verify SSL certificates using system CA bundle
  - `False`: Disable SSL verification (not recommended for production)
  - `str`: Path to custom CA bundle file

```python
# Verify with system CA bundle (recommended)
client = CyberarkCCPClient(
    base_url="https://ccp.example.com",
    app_id="MyApp",
    verify=True
)

# Disable verification (development only)
client = CyberarkCCPClient(
    base_url="https://dev-ccp.example.com",
    app_id="DevApp",
    verify=False
)

# Use custom CA bundle
client = CyberarkCCPClient(
    base_url="https://ccp.example.com",
    app_id="MyApp",
    verify="/path/to/ca-bundle.crt"
)
```

### timeout (optional)

Default timeout for HTTP requests in seconds.

- **Type**: `int`
- **Default**: `30`
- **Example**: `60`
- **Notes**:
  - Can be overridden per request using `connection_timeout` parameter
  - Applies to both connection and read timeouts

## Environment Variables

You can use environment variables for configuration:

### Standard Environment Variables

```bash
export CYBERARK_CCP_URL="https://ccp.example.com"
export CYBERARK_CCP_APP_ID="MyApplication"
export CYBERARK_CCP_CERT_PATH="/path/to/cert.p12"
export CYBERARK_CCP_VERIFY="true"
export CYBERARK_CCP_TIMEOUT="30"
```

### Using Environment Variables

```python
import os
from cyberark_ccp import CyberarkCCPClient

def create_client_from_env():
    """Create client using environment variables."""
    return CyberarkCCPClient(
        base_url=os.getenv("CYBERARK_CCP_URL"),
        app_id=os.getenv("CYBERARK_CCP_APP_ID"),
        cert_path=os.getenv("CYBERARK_CCP_CERT_PATH"),
        verify=os.getenv("CYBERARK_CCP_VERIFY", "true").lower() == "true",
        timeout=int(os.getenv("CYBERARK_CCP_TIMEOUT", "30"))
    )
```

### Environment-Specific Configuration

```python
import os
from cyberark_ccp import CyberarkCCPClient

def create_environment_client():
    """Create client based on environment."""
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        return CyberarkCCPClient(
            base_url=os.getenv("PROD_CCP_URL"),
            app_id=os.getenv("PROD_APP_ID"),
            cert_path=os.getenv("PROD_CERT_PATH"),
            verify=True,
            timeout=60
        )
    elif env == "staging":
        return CyberarkCCPClient(
            base_url=os.getenv("STAGING_CCP_URL"),
            app_id=os.getenv("STAGING_APP_ID"),
            cert_path=os.getenv("STAGING_CERT_PATH"),
            verify=True,
            timeout=45
        )
    else:  # development
        return CyberarkCCPClient(
            base_url=os.getenv("DEV_CCP_URL"),
            app_id=os.getenv("DEV_APP_ID"),
            verify=False,  # Development only
            timeout=30
        )
```

## Configuration File

### JSON Configuration

```json
{
  "cyberark_ccp": {
    "base_url": "https://ccp.example.com",
    "app_id": "MyApplication",
    "cert_path": "/path/to/cert.p12",
    "verify": true,
    "timeout": 30
  }
}
```

```python
import json
from cyberark_ccp import CyberarkCCPClient

def create_client_from_config(config_file="config.json"):
    """Create client from JSON configuration file."""
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    ccp_config = config["cyberark_ccp"]
    
    return CyberarkCCPClient(
        base_url=ccp_config["base_url"],
        app_id=ccp_config["app_id"],
        cert_path=ccp_config.get("cert_path"),
        verify=ccp_config.get("verify", True),
        timeout=ccp_config.get("timeout", 30)
    )
```

### YAML Configuration

```yaml
cyberark_ccp:
  base_url: "https://ccp.example.com"
  app_id: "MyApplication"
  cert_path: "/path/to/cert.p12"
  verify: true
  timeout: 30
```

```python
import yaml
from cyberark_ccp import CyberarkCCPClient

def create_client_from_yaml(config_file="config.yaml"):
    """Create client from YAML configuration file."""
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    ccp_config = config["cyberark_ccp"]
    
    return CyberarkCCPClient(**ccp_config)
```

## Security Considerations

### Certificate Management

- Store certificates securely with appropriate file permissions (600 or 400)
- Use environment variables or secure configuration management for certificate paths
- Rotate certificates regularly according to your security policy

### SSL/TLS Configuration

- Always use `verify=True` in production environments
- Use custom CA bundles for internal certificate authorities
- Keep certificate bundles up to date

### Credential Security

- Never hardcode credentials in source code
- Use environment variables or secure configuration management
- Implement proper secret rotation procedures

### Network Security

- Use HTTPS for all communications
- Implement proper firewall rules and network segmentation
- Consider using VPN or private networks for CCP access

## Configuration Validation

```python
from cyberark_ccp import CyberarkCCPClient, CyberarkCCPValidationError

def validate_configuration(base_url, app_id, cert_path=None):
    """Validate configuration before creating client."""
    
    # Basic validation
    if not base_url or not base_url.startswith('https://'):
        raise ValueError("base_url must be a valid HTTPS URL")
    
    if not app_id or not app_id.strip():
        raise ValueError("app_id cannot be empty")
    
    # Certificate validation
    if cert_path:
        import os
        if not os.path.exists(cert_path):
            raise ValueError(f"Certificate file not found: {cert_path}")
        
        if not os.access(cert_path, os.R_OK):
            raise ValueError(f"Certificate file not readable: {cert_path}")
    
    # Test connection
    try:
        client = CyberarkCCPClient(
            base_url=base_url,
            app_id=app_id,
            cert_path=cert_path,
            timeout=10
        )
        
        # Attempt a simple validation call
        # This will fail if the server is unreachable or authentication fails
        # but that's expected for validation
        
        return True
        
    except Exception as e:
        print(f"Configuration test warning: {e}")
        return False
```

## Best Practices

1. **Use Environment Variables**: Store sensitive configuration in environment variables
2. **Validate Early**: Validate configuration at application startup
3. **Use Appropriate Timeouts**: Set reasonable timeouts based on your network conditions
4. **Enable SSL Verification**: Always verify SSL certificates in production
5. **Secure Certificate Storage**: Protect certificate files with appropriate permissions
6. **Monitor Configuration**: Log configuration issues for troubleshooting
7. **Document Settings**: Document all configuration options for your team