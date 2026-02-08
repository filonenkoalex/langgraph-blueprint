"""Fund Accounting API configuration."""

from dataclasses import dataclass

from .constants import (
    DEFAULT_INTEGRATION_CODE,
    DEFAULT_TASK_POLL_INTERVAL_SECONDS,
    DEFAULT_TASK_POLL_MAX_ATTEMPTS,
    DEFAULT_TIMEOUT_SECONDS,
    DEFAULT_TOKEN_EARLY_EXPIRY_SECONDS,
)


@dataclass(frozen=True)
class FundAccountingConfig:
    """Fund Accounting API configuration.

    All required parameters are explicit. Optional settings have defaults.

    Usage::

        config = FundAccountingConfig(
            base_url="https://api.prd.azure.us.allvuecloud.com/fund-accounting",
            tenant_name="allvuesedemo",
            company_name="AltaReturn SE Demo",
            client_id="...",
            client_secret="...",
        )
    """

    # Required
    base_url: str
    """Base URL for the Fund Accounting API."""

    tenant_name: str
    """Tenant identifier (sent as Allvue-Client-Id header)."""

    company_name: str
    """Company name (sent as Allvue-Fund-Acct-Company-Name header)."""

    client_id: str
    """OAuth client ID."""

    client_secret: str
    """OAuth client secret."""

    # Optional with defaults
    integration_code: str = DEFAULT_INTEGRATION_CODE
    """Integration code (sent as Allvue-Fund-Acct-IntegrationCode header)."""

    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    """HTTP request timeout."""

    token_early_expiry_seconds: float = DEFAULT_TOKEN_EARLY_EXPIRY_SECONDS
    """Seconds before token expiry to consider it expired."""

    poll_interval_seconds: float = DEFAULT_TASK_POLL_INTERVAL_SECONDS
    """Interval between task status polls."""

    poll_max_attempts: int = DEFAULT_TASK_POLL_MAX_ATTEMPTS
    """Maximum polling attempts before timeout."""
