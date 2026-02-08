"""Business Central OData API client.

Pure HTTP transport. Contains NO business logic.
Auth is received as a pre-built ``httpx.Auth`` -- the client never
constructs credentials itself.

Use the ``create_client`` factory for standard construction::

    async with create_client(config) as client:
        funds = await client.get_funds()
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any

import httpx
import structlog

from .constants import (
    CONTENT_TYPE_JSON,
    DEFAULT_MAX_TOP,
    DEFAULT_TIMEOUT_SECONDS,
    DIGEST_ALGORITHM,
    ENDPOINT_INVESTMENT_COMPANIES,
    ENDPOINT_INVESTORS,
    HEADER_ACCEPT,
    HEADER_ALGORITHM,
    ODATA_FILTER_FUNDS,
    ODATA_FILTER_INVESTORS,
    ODATA_SELECT_FUNDS,
    ODATA_SELECT_INVESTORS,
)
from .exceptions import TransportError, TransportTimeoutError
from .models import FundResponse, InvestorResponse, ODataResponse

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from structlog.typing import FilteringBoundLogger

    from .config import BusinessCentralConfig

logger: FilteringBoundLogger = structlog.get_logger(__name__)  # pyright: ignore[reportAny]


# =============================================================================
# Client
# =============================================================================


class BusinessCentralClient:
    """Business Central OData API client.

    Pure HTTP transport. Receives a fully-configured ``httpx.Auth`` --
    never constructs Digest credentials itself.

    Use ``create_client`` factory for standard construction::

        async with create_client(config) as client:
            funds = await client.get_funds()
    """

    def __init__(  # pyright: ignore[reportMissingSuperCall]
        self,
        *,
        base_url: str,
        tenant: str,
        auth: httpx.Auth,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._tenant = tenant
        self._http = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout_seconds,
            headers={
                HEADER_ACCEPT: CONTENT_TYPE_JSON,
                HEADER_ALGORITHM: DIGEST_ALGORITHM,
            },
            auth=auth,
        )

    async def close(self) -> None:
        """Release all resources."""
        await self._http.aclose()

    # -------------------------------------------------------------------------
    # Entity Retrieval (OData)
    # -------------------------------------------------------------------------

    async def get_funds(
        self,
        *,
        top: int = DEFAULT_MAX_TOP,
    ) -> ODataResponse[FundResponse]:
        """Retrieve investment companies filtered by type ``Fund``."""
        data = await self._request(
            "GET",
            ENDPOINT_INVESTMENT_COMPANIES,
            params={
                "tenant": self._tenant,
                "$top": str(top),
                "$filter": ODATA_FILTER_FUNDS,
                "$select": ODATA_SELECT_FUNDS,
            },
        )
        return ODataResponse[FundResponse].model_validate(data)

    async def get_investors(
        self,
        *,
        top: int = DEFAULT_MAX_TOP,
    ) -> ODataResponse[InvestorResponse]:
        """Retrieve investors filtered by type ``LP``."""
        data = await self._request(
            "GET",
            ENDPOINT_INVESTORS,
            params={
                "tenant": self._tenant,
                "$top": str(top),
                "$filter": ODATA_FILTER_INVESTORS,
                "$select": ODATA_SELECT_INVESTORS,
            },
        )
        return ODataResponse[InvestorResponse].model_validate(data)

    # -------------------------------------------------------------------------
    # Private: HTTP transport
    # -------------------------------------------------------------------------

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,  # pyright: ignore[reportExplicitAny]
    ) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        """Execute an HTTP request with error handling.

        Auth is handled transparently by httpx via the ``auth=`` parameter
        configured at client construction time.
        """
        try:
            response = await self._http.request(method, path, params=params)
            response.raise_for_status()
            return response.json()  # pyright: ignore[reportAny]

        except httpx.TimeoutException as e:
            logger.error("HTTP timeout", method=method, path=path)
            raise TransportTimeoutError(f"Request to {path} timed out") from e

        except httpx.HTTPStatusError as e:
            logger.error(
                "HTTP error",
                method=method,
                path=path,
                status=e.response.status_code,
            )
            raise TransportError(
                f"HTTP {e.response.status_code} from {method} {path}"
            ) from e

        except httpx.RequestError as e:
            logger.error("HTTP request failed", method=method, path=path, error=str(e))
            raise TransportError(f"Request to {path} failed: {e}") from e


# =============================================================================
# Factory (async context manager)
# =============================================================================


@asynccontextmanager
async def create_client(
    config: BusinessCentralConfig,
    *,
    auth: httpx.Auth | None = None,
) -> AsyncIterator[BusinessCentralClient]:
    """Create a Business Central client with automatic resource management.

    Builds the default ``httpx.DigestAuth`` from *config* unless a custom
    *auth* is supplied (useful for testing).

    Args:
        config: Complete configuration including Digest credentials.
        auth: Optional custom auth (for testing or alternative auth strategies).

    Usage::

        async with create_client(config) as client:
            funds = await client.get_funds()
    """
    resolved_auth = auth or httpx.DigestAuth(
        username=config.username,
        password=config.password,
    )

    client = BusinessCentralClient(
        base_url=config.base_url,
        tenant=config.tenant,
        auth=resolved_auth,
        timeout_seconds=config.timeout_seconds,
    )
    try:
        yield client
    finally:
        await client.close()
