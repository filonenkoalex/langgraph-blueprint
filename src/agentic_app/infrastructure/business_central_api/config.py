"""Business Central OData API configuration."""

from dataclasses import dataclass

from .constants import DEFAULT_MAX_TOP, DEFAULT_TIMEOUT_SECONDS


@dataclass(frozen=True)
class BusinessCentralConfig:
    """Business Central OData API configuration.

    All required parameters are explicit. Optional settings have defaults.

    Usage::

        config = BusinessCentralConfig(
            base_url="https://bc.example.com/ODataV4",
            tenant="my-tenant",
            username="...",
            password="...",
        )
    """

    # Required
    base_url: str
    """OData base URL for the Business Central API."""

    tenant: str
    """Tenant identifier (sent as ``tenant`` query parameter)."""

    username: str
    """Username for Digest authentication."""

    password: str
    """Password for Digest authentication."""

    # Optional with defaults
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    """HTTP request timeout."""

    max_top: int = DEFAULT_MAX_TOP
    """Maximum value for OData ``$top`` parameter."""
