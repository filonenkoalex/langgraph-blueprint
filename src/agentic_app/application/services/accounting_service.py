"""Accounting service.

Provides an application-level API over the Business Central
infrastructure client, mapping transport DTOs to simplified
application entities and exposing fuzzy search.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agentic_app.application.models import Fund, Investor
from agentic_app.core.search import SearchableList, SearchResults

if TYPE_CHECKING:
    from agentic_app.infrastructure.business_central_api import BusinessCentralClient


class AccountingService:
    """Accounting service.

    Expects a pre-initialized ``BusinessCentralClient``
    (injection solved externally).
    """

    def __init__(  # pyright: ignore[reportMissingSuperCall]
        self,
        business_central_client: BusinessCentralClient,
    ) -> None:
        """Initialize the accounting service with a pre-built client."""
        self._business_central_client = business_central_client

    # -------------------------------------------------------------------------
    # Fuzzy search
    # -------------------------------------------------------------------------

    async def search_funds(
        self, query: str, limit: int = 3
    ) -> SearchResults[Fund]:
        """Look up funds by name using fuzzy search."""
        funds = await self.get_all_funds()
        searchable = SearchableList(funds, key=lambda f: f.name)
        return searchable.search(query, limit)

    async def search_investors(
        self, query: str, limit: int = 3
    ) -> SearchResults[Investor]:
        """Look up investors by name using fuzzy search."""
        investors = await self.get_all_investors()
        searchable = SearchableList(investors, key=lambda i: i.name)
        return searchable.search(query, limit)

    # -------------------------------------------------------------------------
    # Entity retrieval
    # -------------------------------------------------------------------------

    async def get_all_funds(self) -> list[Fund]:
        """Retrieve all funds from Business Central."""
        response = await self._business_central_client.get_funds()
        return [
            Fund(
                id=fund.id,
                name=fund.name,
                currency_code=fund.currency_code,
            )
            for fund in response.value
        ]

    async def get_all_investors(self) -> list[Investor]:
        """Retrieve all investors from Business Central."""
        response = await self._business_central_client.get_investors()
        return [
            Investor(
                id=investor.id,
                name=investor.name,
                currency_code=investor.currency_code,
            )
            for investor in response.value
        ]
