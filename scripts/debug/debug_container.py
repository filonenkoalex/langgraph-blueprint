"""Smoke-test for the DI container and AccountingService.

Boots the full container from .env, initialises async resources,
then exercises the AccountingService (funds, investors, fuzzy search).

Usage::

    python scripts/debug/debug_container.py
"""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING

from agentic_app.container import Container

if TYPE_CHECKING:
    from pydantic import BaseModel


def _pretty(label: str, items: list[BaseModel]) -> None:
    """Print a labelled JSON-friendly list."""
    print(f"\n{'=' * 60}")  # noqa: T201
    print(f"  {label}")  # noqa: T201
    print(f"{'=' * 60}")  # noqa: T201
    for item in items:
        print(json.dumps(item.model_dump(mode="json"), indent=2, default=str))  # noqa: T201


async def main() -> None:
    """Boot container, exercise AccountingService, then shut down."""
    # 1. Create container and initialise async resources (opens HTTP clients)
    container = Container()
    
    try:
        # 2. Obtain service via DI
        svc = container.accounting_service()

        # -- Funds --
        print("\n[service] Fetching funds ...")  # noqa: T201
        funds = await svc.get_all_funds()
        _pretty(f"Funds ({len(funds)} total)", funds)

        # -- Investors --
        print("\n[service] Fetching investors ...")  # noqa: T201
        investors = await svc.get_all_investors()
        _pretty(f"Investors ({len(investors)} total)", investors)

        # -- Fuzzy search --
        if funds:
            query = funds[0].name[:4]  # first 4 chars of first fund name
            print(f"\n[service] Fuzzy-searching funds for '{query}' ...")  # noqa: T201
            results = await svc.search_funds(query, limit=3)
            for hit in results:
                print(f"  {hit.score:5.1f}  {hit.item.name}")  # noqa: T201

        if investors:
            query = investors[0].name[:4]
            print(f"\n[service] Fuzzy-searching investors for '{query}' ...")  # noqa: T201
            results = await svc.search_investors(query, limit=3)
            for hit in results:
                print(f"  {hit.score:5.1f}  {hit.item.name}")  # noqa: T201

    finally:
        # 3. Shutdown resources (closes HTTP clients)
        print("[container] Done.")  # noqa: T201


if __name__ == "__main__":
    asyncio.run(main())
