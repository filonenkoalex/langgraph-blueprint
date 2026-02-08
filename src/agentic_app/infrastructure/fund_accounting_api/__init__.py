"""Fund Accounting API Client.

A clean, type-safe HTTP client for the Allvue Fund Accounting API.

Usage::

    from agentic_app.infrastructure.fund_accounting_api import (
        FundAccountingClient,
        FundAccountingConfig,
        create_client,
    )

    config = FundAccountingConfig(
        base_url="https://api.prd.azure.us.allvuecloud.com/fund-accounting",
        tenant_name="allvuesedemo",
        company_name="AltaReturn SE Demo",
        client_id="...",
        client_secret="...",
    )

    async with create_client(config) as client:
        funds = await client.get_funds()
"""

# Client
from .client import FundAccountingClient, create_client

# Configuration
from .config import FundAccountingConfig

# Exceptions
from .exceptions import (
    AuthenticationError,
    FundAccountingError,
    TaskError,
    TaskFailedError,
    TaskTimeoutError,
    TransportError,
    TransportTimeoutError,
)

# Models
from .models import (
    FundResponse,
    GLAccountResponse,
    InvestorResponse,
    SecurityResponse,
    TransactionLineItem,
    TransactionRequest,
    TransactionResponse,
)

__all__ = [
    "AuthenticationError",
    "FundAccountingClient",
    "FundAccountingConfig",
    "FundAccountingError",
    "FundResponse",
    "GLAccountResponse",
    "InvestorResponse",
    "SecurityResponse",
    "TaskError",
    "TaskFailedError",
    "TaskTimeoutError",
    "TransactionLineItem",
    "TransactionRequest",
    "TransactionResponse",
    "TransportError",
    "TransportTimeoutError",
    "create_client",
]
