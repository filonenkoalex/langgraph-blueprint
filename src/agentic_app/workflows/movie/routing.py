"""Routing logic for the movie workflow.

Defines conditional edge functions that determine
the next step in the conversational flow based on
the current state.
"""

from typing import Literal

from agentic_app.workflows.movie.state import MovieState

# Constants for routing decisions
MAX_CLARIFICATION_ATTEMPTS = 3
HIGH_CONFIDENCE_THRESHOLD = 0.8
AMBIGUITY_THRESHOLD = 0.1  # Score difference to consider ambiguous


def route_after_extraction(
    state: MovieState,
) -> Literal["search", "respond"]:
    """Determine next step after query extraction.

    Routes to search if extraction was successful,
    or to respond if clarification is needed or extraction failed.

    Args:
        state: Current workflow state with extraction decision.

    Returns:
        "search" if query is ready, "respond" if not.
    """
    extraction_decision = state.get("extraction_decision")
    query = state.get("query")

    # No extraction decision - something went wrong
    if extraction_decision is None:
        return "respond"

    # Extraction failed or needs clarification
    if extraction_decision.needs_clarification:
        return "respond"

    # No query extracted
    if query is None:
        return "respond"

    # Empty query - no filters set
    if query.is_empty():
        return "respond"

    return "search"


def route_after_search(
    state: MovieState,
) -> Literal["respond", "clarify"]:
    """Determine next step after movie search.

    Routes based on the number and quality of matches:
    - Single high-confidence match -> respond
    - No matches -> respond (with "not found" message)
    - Multiple matches or low confidence -> clarify

    Args:
        state: Current workflow state with search candidates.

    Returns:
        "respond" for clear results, "clarify" for ambiguous.
    """
    candidates = state.get("candidates", [])
    clarification_count = state.get("clarification_count", 0)

    # No matches - respond with not found
    if not candidates:
        return "respond"

    # Too many clarification attempts - just respond with best match
    if clarification_count >= MAX_CLARIFICATION_ATTEMPTS:
        return "respond"

    # Single match - check confidence
    if len(candidates) == 1:
        if candidates[0].score >= HIGH_CONFIDENCE_THRESHOLD:
            return "respond"
        # Low confidence single match - ask for confirmation
        return "clarify"

    # Multiple matches - check if top result is clearly better
    top_score = candidates[0].score
    second_score = candidates[1].score if len(candidates) > 1 else 0.0

    # Clear winner with high confidence
    if top_score >= HIGH_CONFIDENCE_THRESHOLD and (top_score - second_score) > AMBIGUITY_THRESHOLD:
        return "respond"

    # Ambiguous - need clarification
    return "clarify"


def route_after_clarification(
    _state: MovieState,
) -> Literal["extract"]:
    """Route back to extraction after clarification.

    After presenting options to the user, we need to
    process their response through extraction again.

    Args:
        _state: Current workflow state (unused, but required by LangGraph).

    Returns:
        Always "extract" to process user's clarifying response.
    """
    return "extract"


def should_end_conversation(state: MovieState) -> bool:
    """Check if the conversation should end.

    Returns True if we have a selected movie and
    have responded to the user.

    Args:
        state: Current workflow state.

    Returns:
        True if conversation is complete.
    """
    selected = state.get("selected_movie")
    needs_clarification = state.get("needs_clarification", True)

    return selected is not None and not needs_clarification
