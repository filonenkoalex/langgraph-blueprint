"""
Business Central service exceptions.

Exception hierarchy:
    BusinessCentralError (base)
    └── TransportError
        └── TransportTimeoutError
"""


class BusinessCentralError(Exception):
    """Base exception for all Business Central service errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class TransportError(BusinessCentralError):
    """Raised when HTTP transport fails."""


class TransportTimeoutError(TransportError):
    """Raised when HTTP request times out."""
