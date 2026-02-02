"""Selection payload for choosing from multiple candidates.

Provides models for handling fuzzy matching results from APIs
where multiple candidates may match a user's query.
"""

from pydantic import BaseModel, Field

from agentic_app.models.core.enums import SelectionStrategy


class ScoredCandidate[CandidateT: BaseModel](BaseModel):
    """A single candidate with its match score.

    Represents one option from a set of possible matches,
    along with metadata about why it matched.

    Type Parameters:
        CandidateT: The type of the candidate entity.

    Attributes:
        item: The candidate entity.
        score: Match score between 0.0 and 1.0.
        match_reason: Explanation of why this candidate matched.
    """

    item: CandidateT = Field(
        description="The candidate entity.",
    )
    score: float = Field(
        ge=0.0,
        le=1.0,
        description="Match score between 0.0 and 1.0.",
    )
    match_reason: str | None = Field(
        default=None,
        description="Explanation of why this candidate matched the query.",
    )


class SelectionPayload[CandidateT: BaseModel](BaseModel):
    """Result of selecting from multiple candidates.

    Encapsulates the outcome of a selection process where
    one item is chosen from multiple possibilities.

    Type Parameters:
        CandidateT: The type of entities being selected from.

    Attributes:
        selected: The chosen candidate entity.
        alternatives: Other candidates that were considered, ranked by score.
        strategy: How the selection was made.
        is_ambiguous: True if multiple candidates had similar scores.
        requires_confirmation: True if user should confirm the selection.

    Example:
        ```python
        class Fund(BaseModel):
            ticker: str
            name: str

        result = SelectionPayload[Fund](
            selected=Fund(ticker="VTI", name="Vanguard Total Stock"),
            alternatives=[
                ScoredCandidate(
                    item=Fund(ticker="VOO", name="Vanguard S&P 500"),
                    score=0.72,
                    match_reason="Partial name match",
                ),
            ],
            strategy=SelectionStrategy.HIGHEST_SCORE,
            is_ambiguous=False,
        )
        ```
    """

    selected: CandidateT = Field(
        description="The chosen candidate entity.",
    )
    alternatives: list[ScoredCandidate[CandidateT]] = Field(
        default_factory=list,
        description="Other candidates considered, ranked by score descending.",
    )
    strategy: SelectionStrategy = Field(
        default=SelectionStrategy.HIGHEST_SCORE,
        description="The strategy used to make the selection.",
    )
    is_ambiguous: bool = Field(
        default=False,
        description="True if multiple candidates had similar scores.",
    )
    requires_confirmation: bool = Field(
        default=False,
        description="True if user should confirm the selection before proceeding.",
    )
