"""Fund Accounting API client.

Pure HTTP transport with task polling. Contains NO business logic.
Auth is received as a pre-built ``httpx.Auth`` -- the client never
constructs tokens itself.

Use the ``create_client`` factory for standard construction::

    async with create_client(config) as client:
        funds = await client.get_funds()
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any

import httpx
import structlog

from .auth import OAuth2ClientCredentials
from .constants import (
    CONTENT_TYPE_JSON,
    DEFAULT_INTEGRATION_CODE,
    DEFAULT_PAGE_LIMIT,
    DEFAULT_TASK_POLL_INTERVAL_SECONDS,
    DEFAULT_TASK_POLL_MAX_ATTEMPTS,
    DEFAULT_TIMEOUT_SECONDS,
    ENDPOINT_FUNDS,
    ENDPOINT_GL_ACCOUNTS,
    ENDPOINT_INVESTORS,
    ENDPOINT_OAUTH_TOKEN,
    ENDPOINT_SECURITIES,
    ENDPOINT_TASKS,
    ENDPOINT_TRANSACTIONS,
    HEADER_ALLVUE_CLIENT_ID,
    HEADER_ALLVUE_COMPANY_NAME,
    HEADER_ALLVUE_INTEGRATION_CODE,
    HEADER_CONTENT_TYPE,
)
from .exceptions import (
    TaskFailedError,
    TaskTimeoutError,
    TransportError,
    TransportTimeoutError,
)
from .models import (
    BackgroundTaskResponse,
    FundResponse,
    GLAccountResponse,
    InvestorResponse,
    PaginatedResponse,
    SecurityResponse,
    TaskResponse,
    TaskStatus,
    TransactionResponse,
)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from structlog.typing import FilteringBoundLogger

    from .config import FundAccountingConfig
    from .models import TransactionRequest

logger: FilteringBoundLogger = structlog.get_logger(__name__)  # pyright: ignore[reportAny]


# =============================================================================
# Client
# =============================================================================


class FundAccountingClient:
    """Fund Accounting API client.

    Pure HTTP transport. Receives a fully-configured ``httpx.Auth`` --
    never constructs OAuth tokens itself.

    Use ``create_client`` factory for standard construction::

        async with create_client(config) as client:
            funds = await client.get_funds()
    """

    def __init__(  # noqa: PLR0913  # pyright: ignore[reportMissingSuperCall]
        self,
        *,
        base_url: str,
        tenant_name: str,
        company_name: str,
        auth: httpx.Auth,
        integration_code: str = DEFAULT_INTEGRATION_CODE,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        poll_interval_seconds: float = DEFAULT_TASK_POLL_INTERVAL_SECONDS,
        poll_max_attempts: int = DEFAULT_TASK_POLL_MAX_ATTEMPTS,
    ) -> None:
        self._http = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout_seconds,
            headers={
                HEADER_CONTENT_TYPE: CONTENT_TYPE_JSON,
                HEADER_ALLVUE_CLIENT_ID: tenant_name,
                HEADER_ALLVUE_COMPANY_NAME: company_name,
                HEADER_ALLVUE_INTEGRATION_CODE: integration_code,
            },
            auth=auth,
        )

        self._poll_interval = poll_interval_seconds
        self._poll_max_attempts = poll_max_attempts

    async def close(self) -> None:
        """Release all resources."""
        await self._http.aclose()

    # -------------------------------------------------------------------------
    # Entity Retrieval (Paginated)
    # -------------------------------------------------------------------------

    async def get_funds(
        self,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[FundResponse]:
        """Retrieve funds with pagination."""
        data = await self._request(
            "GET", ENDPOINT_FUNDS, params={"limit": limit, "offset": offset}
        )
        return PaginatedResponse[FundResponse].model_validate(data)

    async def get_investors(
        self,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[InvestorResponse]:
        """Retrieve investors with pagination."""
        data = await self._request(
            "GET", ENDPOINT_INVESTORS, params={"limit": limit, "offset": offset}
        )
        return PaginatedResponse[InvestorResponse].model_validate(data)

    async def get_gl_accounts(
        self,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[GLAccountResponse]:
        """Retrieve G/L accounts with pagination."""
        data = await self._request(
            "GET", ENDPOINT_GL_ACCOUNTS, params={"limit": limit, "offset": offset}
        )
        return PaginatedResponse[GLAccountResponse].model_validate(data)

    async def get_securities(
        self,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> PaginatedResponse[SecurityResponse]:
        """Retrieve securities with pagination."""
        data = await self._request(
            "GET", ENDPOINT_SECURITIES, params={"limit": limit, "offset": offset}
        )
        return PaginatedResponse[SecurityResponse].model_validate(data)

    # -------------------------------------------------------------------------
    # Single Entity Lookup
    # -------------------------------------------------------------------------

    async def get_fund_by_code(self, code: str) -> FundResponse | None:
        """Retrieve a single fund by its code."""
        data = await self._request(
            "GET", ENDPOINT_FUNDS, params={"code": code, "limit": 1}
        )
        page = PaginatedResponse[FundResponse].model_validate(data)
        return page.items[0] if page.items else None

    async def get_investor_by_no(self, no: str) -> InvestorResponse | None:
        """Retrieve a single investor by its number."""
        data = await self._request(
            "GET", ENDPOINT_INVESTORS, params={"no": no, "limit": 1}
        )
        page = PaginatedResponse[InvestorResponse].model_validate(data)
        return page.items[0] if page.items else None

    async def get_gl_account_by_no(self, no: str) -> GLAccountResponse | None:
        """Retrieve a single G/L account by its number."""
        data = await self._request(
            "GET", ENDPOINT_GL_ACCOUNTS, params={"no": no, "limit": 1}
        )
        page = PaginatedResponse[GLAccountResponse].model_validate(data)
        return page.items[0] if page.items else None

    async def get_security_by_no(self, no: str) -> SecurityResponse | None:
        """Retrieve a single security by its number."""
        data = await self._request(
            "GET", ENDPOINT_SECURITIES, params={"no": no, "limit": 1}
        )
        page = PaginatedResponse[SecurityResponse].model_validate(data)
        return page.items[0] if page.items else None

    # -------------------------------------------------------------------------
    # Transactions
    # -------------------------------------------------------------------------

    async def create_transaction(
        self, request: TransactionRequest
    ) -> TransactionResponse:
        """Create and post a transaction."""
        data = await self._request(
            "POST",
            ENDPOINT_TRANSACTIONS,
            json_body=request.model_dump(mode="json", by_alias=True, exclude_none=True),
        )
        task = BackgroundTaskResponse.model_validate(data)
        return await self._poll_transaction_task(task.task_id)

    async def submit_post_transaction(self, transaction_id: str) -> TransactionResponse:
        """Submit and post an existing transaction."""
        data = await self._request(
            "POST", f"{ENDPOINT_TRANSACTIONS}/{transaction_id}/submit-post"
        )
        task = BackgroundTaskResponse.model_validate(data)
        return await self._poll_transaction_task(task.task_id)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,  # pyright: ignore[reportExplicitAny]
        json_body: dict[str, Any] | None = None,  # pyright: ignore[reportExplicitAny]
    ) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        """Execute an HTTP request with error handling.

        Auth is handled transparently by httpx via the ``auth=`` parameter
        configured at client construction time.
        """
        try:
            response = await self._http.request(
                method, path, params=params, json=json_body
            )
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

    # -------------------------------------------------------------------------
    # Private: Task Polling
    # -------------------------------------------------------------------------

    async def _poll_transaction_task(self, task_id: str) -> TransactionResponse:
        """Poll transaction task and extract response."""
        task = await self._poll_until_complete(task_id)
        if task.data is None:
            msg = f"Task {task_id} completed but returned no data"
            raise ValueError(msg)
        return TransactionResponse.model_validate(task.data)

    async def _poll_until_complete(self, task_id: str) -> TaskResponse:
        """Poll a background task until completion."""
        for attempt in range(1, self._poll_max_attempts + 1):
            data = await self._request("GET", f"{ENDPOINT_TASKS}/{task_id}")
            task = TaskResponse.model_validate(data)

            if task.status == TaskStatus.COMPLETED:
                logger.info("Task completed", task_id=task_id, attempts=attempt)
                return task

            if task.status in {TaskStatus.FAILED, TaskStatus.ERROR}:
                raise TaskFailedError(
                    task_id, status=task.status, messages=task.messages
                )

            logger.debug(
                "Task pending",
                task_id=task_id,
                status=task.status,
                attempt=attempt,
            )
            await asyncio.sleep(self._poll_interval)

        raise TaskTimeoutError(task_id, attempts=self._poll_max_attempts)


# =============================================================================
# Factory (async context manager)
# =============================================================================


@asynccontextmanager
async def create_client(
    config: FundAccountingConfig,
    *,
    auth: httpx.Auth | None = None,
) -> AsyncIterator[FundAccountingClient]:
    """Create a Fund Accounting client with automatic resource management.

    Builds the default ``OAuth2ClientCredentials`` auth from *config* unless
    a custom *auth* is supplied (useful for testing).

    Args:
        config: Complete configuration including OAuth credentials.
        auth: Optional custom auth (for testing or alternative auth strategies).

    Usage::

        async with create_client(config) as client:
            funds = await client.get_funds()
    """
    resolved_auth = auth or OAuth2ClientCredentials(
        f"{config.base_url}{ENDPOINT_OAUTH_TOKEN}",
        client_id=config.client_id,
        client_secret=config.client_secret,
        early_expiry=config.token_early_expiry_seconds,
    )

    client = FundAccountingClient(
        base_url=config.base_url,
        tenant_name=config.tenant_name,
        company_name=config.company_name,
        auth=resolved_auth,
        integration_code=config.integration_code,
        timeout_seconds=config.timeout_seconds,
        poll_interval_seconds=config.poll_interval_seconds,
        poll_max_attempts=config.poll_max_attempts,
    )
    try:
        yield client
    finally:
        await client.close()
