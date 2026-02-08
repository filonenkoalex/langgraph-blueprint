"""OAuth2 Client Credentials auth -- credentials sent as POST body.

Uses the idiomatic httpx ``auth_flow`` generator pattern:

1. When the cached token is missing or expired, yield a token request
   (with ``client_id`` / ``client_secret`` as form body fields).
2. httpx sends the request and feeds the response back into the generator.
3. Cache the token with a monotonic-clock expiry.
4. Set ``Authorization: Bearer <token>`` on the original request and yield it.

No separate ``httpx.Client`` is created -- the same async/sync transport
that sends the API request also handles the token fetch.
"""

from __future__ import annotations

import asyncio
import threading
import time
from typing import TYPE_CHECKING, override

import httpx

from .exceptions import AuthenticationError

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

_DEFAULT_EARLY_EXPIRY: float = 30.0
_DEFAULT_EXPIRES_IN: int = 3600


class OAuth2ClientCredentials(httpx.Auth):
    """OAuth2 Client Credentials Grant -- credentials sent as POST body.

    Production-safe:

    * ``time.monotonic()`` for expiry tracking (immune to NTP drift).
    * ``asyncio.Lock`` / ``threading.Lock`` with double-check pattern to
      prevent thundering-herd token refreshes.
    * ``requires_response_body = True`` so the base ``auth_flow`` fallback
      reads the response body; the sync/async overrides read explicitly.
    """

    requires_response_body = True

    def __init__(  # pyright: ignore[reportMissingSuperCall]
        self,
        token_url: str,
        client_id: str,
        client_secret: str,
        *,
        early_expiry: float = _DEFAULT_EARLY_EXPIRY,
    ) -> None:
        self._token_url = token_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._early_expiry = early_expiry

        self._token: str | None = None
        self._token_expiry: float = 0.0  # monotonic timestamp

        self._sync_lock = threading.Lock()
        self._async_lock = asyncio.Lock()

    # -----------------------------------------------------------------
    # httpx auth flow overrides
    # -----------------------------------------------------------------

    @override
    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        """Base auth flow (no concurrency protection)."""
        if self._is_expired():
            token_response: httpx.Response = yield self._build_token_request()
            self._update_token(token_response)

        request.headers["Authorization"] = f"Bearer {self._token}"
        yield request

    @override
    def sync_auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        """Sync auth flow with threading lock + double-check."""
        if self._is_expired():
            with self._sync_lock:
                if self._is_expired():
                    token_response: httpx.Response = yield self._build_token_request()
                    token_response.read()
                    self._update_token(token_response)

        request.headers["Authorization"] = f"Bearer {self._token}"
        yield request

    @override
    async def async_auth_flow(
        self, request: httpx.Request
    ) -> AsyncGenerator[httpx.Request, httpx.Response]:
        """Async auth flow with asyncio lock + double-check."""
        if self._is_expired():
            async with self._async_lock:
                if self._is_expired():
                    token_response: httpx.Response = yield self._build_token_request()
                    await token_response.aread()
                    self._update_token(token_response)

        request.headers["Authorization"] = f"Bearer {self._token}"
        yield request

    # -----------------------------------------------------------------
    # Private helpers
    # -----------------------------------------------------------------

    def _is_expired(self) -> bool:
        return self._token is None or time.monotonic() >= self._token_expiry

    def _build_token_request(self) -> httpx.Request:
        return httpx.Request(
            "POST",
            self._token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
        )

    def _update_token(self, response: httpx.Response) -> None:
        if response.is_error:
            raise AuthenticationError(
                f"Token request failed: HTTP {response.status_code}"
            )

        data = response.json()  # pyright: ignore[reportAny]
        token: str | None = data.get("access_token")  # pyright: ignore[reportAny]
        if not token:
            raise AuthenticationError("No access_token in token response")

        raw_expires: int | str = data.get("expires_in", _DEFAULT_EXPIRES_IN)  # pyright: ignore[reportAny]
        expires_in = int(raw_expires)
        self._token = token
        self._token_expiry = time.monotonic() + expires_in - self._early_expiry
