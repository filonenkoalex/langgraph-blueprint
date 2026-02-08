"""
Business Central OData API constants.

All magic numbers, strings, and default values are defined here.
This makes the codebase easier to audit and modify.
"""

from typing import Final

# =============================================================================
# API Endpoints
# =============================================================================

ENDPOINT_INVESTMENT_COMPANIES: Final[str] = "/investmentCompanies"
ENDPOINT_INVESTORS: Final[str] = "/investors"

# =============================================================================
# HTTP Headers
# =============================================================================

HEADER_ACCEPT: Final[str] = "Accept"
HEADER_ALGORITHM: Final[str] = "algorithm"
CONTENT_TYPE_JSON: Final[str] = "application/json"
DIGEST_ALGORITHM: Final[str] = "MD5-SESS"

# =============================================================================
# OData Query Defaults
# =============================================================================

ODATA_FILTER_FUNDS: Final[str] = "type eq 'Fund'"
ODATA_FILTER_INVESTORS: Final[str] = "type eq 'LP'"
ODATA_SELECT_FUNDS: Final[str] = (
    "code,name,companyPostingGroup,currencyCode,public,listedDate"
)
ODATA_SELECT_INVESTORS: Final[str] = "no,name,currencyCode"

# =============================================================================
# Default Configuration Values
# =============================================================================

DEFAULT_TIMEOUT_SECONDS: Final[float] = 30.0
DEFAULT_MAX_TOP: Final[int] = 10000
