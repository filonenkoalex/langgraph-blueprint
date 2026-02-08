"""Immutable, score-sorted container for fuzzy search results."""

from collections.abc import Iterator, Sequence
from typing import overload, override

from .search_hit import SearchHit


class SearchResults[T](Sequence[SearchHit[T]]):
    """An immutable, score-sorted container returned by fuzzy search.

    Provides convenient properties for detecting high-confidence
    matches and filtering candidates above a threshold.
    """

    _super_threshold: float = 0.98
    _super_margin: float = 0.10
    _candidate_threshold: float = 0.80
    _candidate_max: int = 5

    def __init__(self, hits: list[SearchHit[T]]) -> None:  # pyright: ignore[reportMissingSuperCall]
        """Initialize with a list of search hits, sorted by score descending."""
        self._hits = sorted(hits, key=lambda hit: hit.score, reverse=True)

    @override
    def __iter__(self) -> Iterator[SearchHit[T]]:
        """Iterate over hits in descending score order."""
        return iter(self._hits)

    @override
    def __len__(self) -> int:
        """Return the number of hits."""
        return len(self._hits)

    @overload
    def __getitem__(self, idx: int) -> SearchHit[T]: ...
    @overload
    def __getitem__(self, idx: slice) -> Sequence[SearchHit[T]]: ...
    @override
    def __getitem__(self, idx: int | slice) -> SearchHit[T] | Sequence[SearchHit[T]]:
        """Return hit(s) by index or slice."""
        return self._hits[idx]

    @property
    def candidates(self) -> list[T]:
        """Items scoring at or above the candidate threshold (max 5)."""
        return [h.item for h in self._hits if h.score >= self._candidate_threshold][
            : self._candidate_max
        ]

    @property
    def super_match(self) -> SearchHit[T] | None:
        """Top hit if it exceeds the super threshold with sufficient margin."""
        return self._detect_super(self._super_threshold, self._super_margin)

    @property
    def has_super_match(self) -> bool:
        """True if a super match exists."""
        return self.super_match is not None

    @property
    def has_candidate_match(self) -> bool:
        """True if at least one candidate exists."""
        return len(self.candidates) > 0

    @property
    def best(self) -> SearchHit[T] | None:
        """Return the top-scoring hit, or None if empty."""
        return self._hits[0] if self._hits else None

    def _detect_super(
        self,
        threshold: float,
        margin: float,
    ) -> SearchHit[T] | None:
        """Return the top hit if it clears the threshold with enough margin."""
        if not self._hits:
            return None
        top = self._hits[0]
        if top.score < threshold:
            return None
        if len(self._hits) == 1 or top.score - self._hits[1].score >= margin:
            return top
        return None
