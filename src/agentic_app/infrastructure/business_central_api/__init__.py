"""Business Central OData API Client.

A clean, type-safe HTTP client for the Business Central OData API.

Usage::

    from agentic_app.infrastructure.business_central_api import (
        BusinessCentralClient,
        BusinessCentralConfig,
        create_client,
    )

    config = BusinessCentralConfig(
        base_url="https://bc.example.com/ODataV4",
        tenant="my-tenant",
        username="...",
        password="...",
    )

    async with create_client(config) as client:
        funds = await client.get_funds()
"""

# Client
from .client import BusinessCentralClient, create_client

# Configuration
from .config import BusinessCentralConfig

# Exceptions
from .exceptions import (
    BusinessCentralError,
    TransportError,
    TransportTimeoutError,
)

# Models
from .models import FundResponse, InvestorResponse, ODataResponse

__all__ = [
    "BusinessCentralClient",
    "BusinessCentralConfig",
    "BusinessCentralError",
    "FundResponse",
    "InvestorResponse",
    "ODataResponse",
    "TransportError",
    "TransportTimeoutError",
    "create_client",
]
