"""Single match result from a fuzzy search operation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SearchHit[T]:
    """A single fuzzy search match holding the score and matched item.

    Attributes:
        score: Similarity score between 0.0 and 1.0.
        item: The matched item from the searchable collection.
    """

    score: float
    item: T
