"""
Fund Accounting API constants.

All magic numbers, strings, and default values are defined here.
This makes the codebase easier to audit and modify.
"""

from typing import Final

# =============================================================================
# API Endpoints
# =============================================================================

ENDPOINT_OAUTH_TOKEN: Final[str] = "/v1/oauth2/token"  # noqa: S105
ENDPOINT_FUNDS: Final[str] = "/v1/funds"
ENDPOINT_INVESTORS: Final[str] = "/v1/investors"
ENDPOINT_GL_ACCOUNTS: Final[str] = "/v1/gl-accounts"
ENDPOINT_SECURITIES: Final[str] = "/v1/securities"
ENDPOINT_TRANSACTIONS: Final[str] = "/v1/transactions"
ENDPOINT_TASKS: Final[str] = "/v1/tasks"

# =============================================================================
# HTTP Headers - Standard
# =============================================================================

HEADER_AUTHORIZATION: Final[str] = "Authorization"
HEADER_CONTENT_TYPE: Final[str] = "Content-Type"
CONTENT_TYPE_JSON: Final[str] = "application/json"
CONTENT_TYPE_FORM: Final[str] = "application/x-www-form-urlencoded"
AUTH_SCHEME_BEARER: Final[str] = "Bearer"

# =============================================================================
# HTTP Headers - Allvue Custom
# =============================================================================

HEADER_ALLVUE_CLIENT_ID: Final[str] = "Allvue-Client-Id"
HEADER_ALLVUE_COMPANY_NAME: Final[str] = "Allvue-Fund-Acct-Company-Name"
HEADER_ALLVUE_INTEGRATION_CODE: Final[str] = "Allvue-Fund-Acct-IntegrationCode"
HEADER_ALLVUE_CORRELATION_ID: Final[str] = "Allvue-Correlation-Id"

# =============================================================================
# Default Configuration Values
# =============================================================================

DEFAULT_INTEGRATION_CODE: Final[str] = "API"
DEFAULT_TIMEOUT_SECONDS: Final[float] = 30.0
DEFAULT_TOKEN_EARLY_EXPIRY_SECONDS: Final[float] = 30.0
DEFAULT_PAGE_LIMIT: Final[int] = 100
DEFAULT_MAX_PAGE_LIMIT: Final[int] = 10000
DEFAULT_TASK_POLL_INTERVAL_SECONDS: Final[float] = 1.0
DEFAULT_TASK_POLL_MAX_ATTEMPTS: Final[int] = 60
