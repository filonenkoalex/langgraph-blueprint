"""List-like container with fuzzy search capabilities."""

from collections.abc import Callable, Iterable, Iterator, Sequence
from typing import overload, override

from rapidfuzz import fuzz, process

from .search_hit import SearchHit
from .search_results import SearchResults


class SearchableList[T](Sequence[T]):
    """A list-like container with built-in fuzzy search.

    Wraps a collection of items and enables fuzzy text matching
    via RapidFuzz. A key function extracts searchable text from each item.

    Args:
        items: The underlying data.
        key: Extracts comparable text from each item.
        scorer: RapidFuzz scorer function (default: ``fuzz.partial_ratio``).
    """

    def __init__(  # pyright: ignore[reportMissingSuperCall]
        self,
        items: Iterable[T],
        key: Callable[[T], str],
        scorer: Callable[..., float] = fuzz.partial_ratio,
    ) -> None:
        """Initialize the searchable list with items and a key extractor."""
        self._items: list[T] = list(items)
        self._key = key
        self._scorer = scorer
        self._texts = [key(it) for it in self._items]

    @override
    def __iter__(self) -> Iterator[T]:
        """Iterate over the underlying items."""
        return iter(self._items)

    @override
    def __len__(self) -> int:
        """Return the number of items."""
        return len(self._items)

    @overload
    def __getitem__(self, idx: int) -> T: ...
    @overload
    def __getitem__(self, idx: slice) -> Sequence[T]: ...
    @override
    def __getitem__(self, idx: int | slice) -> T | Sequence[T]:
        """Return item(s) by index or slice."""
        return self._items[idx]

    def search(self, query: str, limit: int = 3) -> SearchResults[T]:
        """Return up to *limit* best matches, score-sorted high to low."""
        raw = process.extract(
            query,
            self._texts,
            scorer=self._scorer,
            limit=limit,
        )

        hits = [
            SearchHit(
                score=round(score / 100.0, 4),
                item=self._items[idx],
            )
            for _, score, idx in raw
        ]

        hits.sort(key=lambda h: h.score, reverse=True)
        return SearchResults(hits)

    def best(self, query: str) -> SearchHit[T] | None:
        """Shortcut for the single highest-scoring match."""
        return self.search(query, limit=1).best
