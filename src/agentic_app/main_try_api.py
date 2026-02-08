"""Quick smoke-test for the Fund Accounting API client.

Reads credentials from .env via pydantic-settings, then exercises every
read-only endpoint with a small page size so you can verify connectivity
and response shapes.

Usage::

    python -m agentic_app.main_try_api
"""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING

from agentic_app.configs import FundAccountingApiSettings
from agentic_app.infrastructure.fund_accounting_api import (
    FundAccountingConfig,
    FundAccountingError,
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
    """Run read-only API calls against the Fund Accounting API."""
    # 1. Load settings from .env and map to infrastructure config
    settings = FundAccountingApiSettings()  # pyright: ignore[reportCallIssue]
    config = FundAccountingConfig(
        base_url=settings.base_url,
        tenant_name=settings.tenant_name,
        company_name=settings.company_name,
        client_id=settings.client_id,
        client_secret=settings.client_secret,
    )

    print(f"Base URL : {config.base_url}")  # noqa: T201
    print(f"Tenant   : {config.tenant_name}")  # noqa: T201
    print(f"Company  : {config.company_name}")  # noqa: T201

    # 2. Create client and run queries
    async with create_client(config) as client:
        # -- Funds --
        try:
            funds = await client.get_funds(limit=5)
            _pretty(f"Funds (showing {len(funds.items)} of {funds.total_count})", funds)
        except FundAccountingError as exc:
            print(f"[ERROR] get_funds: {exc.message}")  # noqa: T201

        # -- Investors --
        try:
            investors = await client.get_investors(limit=5)
            _pretty(
                f"Investors (showing {len(investors.items)} of {investors.total_count})",
                investors,
            )
        except FundAccountingError as exc:
            print(f"[ERROR] get_investors: {exc.message}")  # noqa: T201

        # -- GL Accounts --
        try:
            gl_accounts = await client.get_gl_accounts(limit=5)
            _pretty(
                f"GL Accounts (showing {len(gl_accounts.items)} of {gl_accounts.total_count})",
                gl_accounts,
            )
        except FundAccountingError as exc:
            print(f"[ERROR] get_gl_accounts: {exc.message}")  # noqa: T201

        # -- Securities --
        try:
            securities = await client.get_securities(limit=5)
            _pretty(
                f"Securities (showing {len(securities.items)} of {securities.total_count})",
                securities,
            )
        except FundAccountingError as exc:
            print(f"[ERROR] get_securities: {exc.message}")  # noqa: T201

    print("\nDone.")  # noqa: T201


if __name__ == "__main__":
    asyncio.run(main())
