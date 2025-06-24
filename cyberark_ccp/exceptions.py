"""Custom exceptions for CyberArk CCP API client."""


class CyberarkCCPError(Exception):
    """Base exception for CyberArk CCP API errors."""


class CyberarkCCPAuthenticationError(CyberarkCCPError):
    """Raised when authentication fails."""


class CyberarkCCPAuthorizationError(CyberarkCCPError):
    """Raised when authorization fails (insufficient permissions)."""


class CyberarkCCPAccountNotFoundError(CyberarkCCPError):
    """Raised when the requested account is not found."""


class CyberarkCCPConnectionError(CyberarkCCPError):
    """Raised when connection to CCP service fails."""


class CyberarkCCPTimeoutError(CyberarkCCPError):
    """Raised when request times out."""


class CyberarkCCPValidationError(CyberarkCCPError):
    """Raised when request validation fails."""
