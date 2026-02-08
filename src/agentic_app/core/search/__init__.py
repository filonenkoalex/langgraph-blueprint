"""Fuzzy search utilities built on RapidFuzz.

Provides generic, type-safe containers for fuzzy text matching
with configurable scoring and result filtering.
"""

from agentic_app.core.search.search_hit import SearchHit
from agentic_app.core.search.search_results import SearchResults
from agentic_app.core.search.searchable_list import SearchableList

__all__ = [
    "SearchHit",
    "SearchResults",
    "SearchableList",
]
