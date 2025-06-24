"""Cyberark CCP API Client Package"""

from .client import CyberarkCCPClient, QueryFormat  # type: ignore
from .exceptions import (  # type: ignore
    CyberarkCCPAccountNotFoundError,
    CyberarkCCPAuthenticationError,
    CyberarkCCPAuthorizationError,
    CyberarkCCPConnectionError,
    CyberarkCCPError,
    CyberarkCCPTimeoutError,
    CyberarkCCPValidationError,
)

__all__ = [
    "CyberarkCCPClient",
    "QueryFormat",
    "CyberarkCCPError",
    "CyberarkCCPAuthenticationError",
    "CyberarkCCPAuthorizationError",
    "CyberarkCCPAccountNotFoundError",
    "CyberarkCCPConnectionError",
    "CyberarkCCPTimeoutError",
    "CyberarkCCPValidationError",
]

__version__ = "0.0.1"
