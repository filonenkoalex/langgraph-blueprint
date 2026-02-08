"""Quick smoke-test for the Business Central OData API client.

Reads credentials from .env via pydantic-settings, then exercises every
read-only endpoint with a small page size so you can verify connectivity
and response shapes.

Usage::

    python scripts/debug/debug_business_central_api.py
"""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING

from agentic_app.infrastructure.configs import BusinessCentralODataApiSettings
from agentic_app.infrastructure.business_central_api import (
    BusinessCentralConfig,
    BusinessCentralError,
    create_client,
)

if TYPE_CHECKING:
    from pydantic import BaseModel


def _pretty(label: str, obj: BaseModel) -> None:
    """Print a labelled JSON-friendly representation."""
    print(f"\n{'=' * 60}")  # noqa: T201
    print(f"  {label}")  # noqa: T201
    print(f"{'=' * 60}")  # noqa: T201
    print(json.dumps(obj.model_dump(mode="json"), indent=2, default=str))  # noqa: T201


async def main() -> None:
    """Run read-only API calls against the Business Central OData API."""
    # 1. Load settings from .env and map to infrastructure config
    settings = BusinessCentralODataApiSettings()  # pyright: ignore[reportCallIssue]
    config = BusinessCentralConfig(
        base_url=settings.odata_base_url,
        tenant=settings.odata_tenant,
        username=settings.odata_username,
        password=settings.odata_password,
    )

    print(f"Base URL : {config.base_url}")  # noqa: T201
    print(f"Tenant   : {config.tenant}")  # noqa: T201

    # 2. Create client and run queries
    async with create_client(config) as client:
        # -- Funds --
        try:
            funds = await client.get_funds(top=500)
            _pretty(f"Funds (showing {len(funds.value)})", funds)
        except BusinessCentralError as exc:
            print(f"[ERROR] get_funds: {exc.message}")  # noqa: T201

        # -- Investors --
        try:
            investors = await client.get_investors(top=500)
            _pretty(f"Investors (showing {len(investors.value)})", investors)
        except BusinessCentralError as exc:
            print(f"[ERROR] get_investors: {exc.message}")  # noqa: T201

    print("\nDone.")  # noqa: T201


if __name__ == "__main__":
    asyncio.run(main())
