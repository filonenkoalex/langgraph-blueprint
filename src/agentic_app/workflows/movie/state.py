"""State definition for the movie workflow.

Extends MessagesState with movie-specific fields for
tracking extraction results, search candidates, and
conversational context.
"""

from langgraph.graph import MessagesState  # pyright: ignore[reportMissingTypeStubs]

from agentic_app.models.core.decision import LLMDecision
from agentic_app.models.domain.movie import Movie, MovieQuery
from agentic_app.models.payloads.extraction import ExtractionPayload
from agentic_app.models.payloads.selection import ScoredCandidate


class MovieState(MessagesState):
    """State for the movie search workflow.

    Extends MessagesState to include conversation history
    plus movie-specific fields for tracking the search process.

    Attributes:
        messages: Conversation history (inherited from MessagesState).
        query: Current extracted movie query from user input.
        candidates: List of movies matching the query with scores.
        selected_movie: The final selected movie (if resolved).
        extraction_decision: Full LLM decision from query extraction.
        needs_clarification: Whether clarification is needed from user.
        clarification_count: Number of clarification attempts made.
    """

    query: MovieQuery | None
    candidates: list[ScoredCandidate[Movie]]
    selected_movie: Movie | None
    extraction_decision: LLMDecision[ExtractionPayload[MovieQuery]] | None
    needs_clarification: bool
    clarification_count: int
