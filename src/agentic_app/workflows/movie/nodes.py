"""Node functions for the movie workflow.

Each node represents a step in the conversational flow:
- Extract: Parse user intent into MovieQuery
- Search: Find matching movies from the service
- Clarify: Generate clarification prompts
- Respond: Generate final response to user
"""

from collections.abc import Sequence
from functools import lru_cache
from typing import TYPE_CHECKING, cast

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from agentic_app.models.core.decision import LLMDecision
from agentic_app.models.domain.movie import Movie, MovieQuery
from agentic_app.models.payloads.conversation import AgentResponsePayload
from agentic_app.models.payloads.extraction import ExtractionPayload
from agentic_app.services.movie_service import MovieService

if TYPE_CHECKING:
    from langchain_core.runnables import Runnable

    from agentic_app.workflows.movie.state import MovieState

# =============================================================================
# Constants
# =============================================================================

HIGH_CONFIDENCE_THRESHOLD = 0.8
"""Score threshold for automatic movie selection."""


# =============================================================================
# LLM Configuration (Lazy-loaded)
# =============================================================================


@lru_cache(maxsize=1)
def _get_llm() -> ChatOpenAI:
    """Get or create the ChatOpenAI instance (lazy-loaded)."""
    return ChatOpenAI(model="gpt-4o-mini", temperature=0)


@lru_cache(maxsize=1)
def _get_extraction_model() -> "Runnable[list[HumanMessage | AIMessage], LLMDecision[ExtractionPayload[MovieQuery]]]":
    """Get or create the extraction model (lazy-loaded)."""
    return cast(
        "Runnable[list[HumanMessage | AIMessage], LLMDecision[ExtractionPayload[MovieQuery]]]",
        _get_llm().with_structured_output(  # pyright: ignore[reportUnknownMemberType]
            LLMDecision[ExtractionPayload[MovieQuery]]
        ),
    )


@lru_cache(maxsize=1)
def _get_response_model() -> "Runnable[list[HumanMessage | AIMessage], LLMDecision[AgentResponsePayload]]":
    """Get or create the response model (lazy-loaded)."""
    return cast(
        "Runnable[list[HumanMessage | AIMessage], LLMDecision[AgentResponsePayload]]",
        _get_llm().with_structured_output(  # pyright: ignore[reportUnknownMemberType]
            LLMDecision[AgentResponsePayload]
        ),
    )


# Shared movie service instance (can be eagerly loaded)
_movie_service = MovieService()


# =============================================================================
# Extraction Prompt Schema
# =============================================================================


class ExtractionPromptContext(BaseModel):
    """Context for the extraction prompt."""

    conversation_history: str = Field(description="Recent conversation messages")
    current_query: str | None = Field(
        default=None, description="Current extracted query if any"
    )


EXTRACTION_SYSTEM_PROMPT = """You are a movie search assistant. Extract search criteria from the user's message.

Your task:
1. Identify any movie search criteria mentioned (title, actor, genre, director, year range, rating)
2. If the user is refining a previous search, merge the new criteria with existing ones
3. Set confidence based on how clear the user's intent is
4. Request clarification if the query is too vague

Current search context:
{context}

Extract the movie query and wrap it in an LLMDecision with appropriate confidence and reasoning.
"""


# =============================================================================
# Node Functions
# =============================================================================


def extract_query_node(state: "MovieState") -> dict[str, object]:
    """Extract movie query from user's latest message.

    Uses structured output to parse user intent into a MovieQuery,
    wrapped in an LLMDecision with confidence scoring.

    Args:
        state: Current workflow state with messages.

    Returns:
        State update with extracted query and decision metadata.
    """
    messages = state.get("messages", [])
    if not messages:
        return {
            "query": None,
            "extraction_decision": None,
            "needs_clarification": True,
        }

    # Build context for extraction
    current_query = state.get("query")
    context = ExtractionPromptContext(
        conversation_history=_format_messages(messages[-5:]),
        current_query=current_query.model_dump_json() if current_query else None,
    )

    # Prepare messages for LLM
    prompt_messages: list[HumanMessage | AIMessage] = [
        HumanMessage(content=EXTRACTION_SYSTEM_PROMPT.format(context=context.model_dump_json())),
        *[_convert_message(m) for m in messages[-3:]],
    ]

    # Get structured extraction
    decision = _get_extraction_model().invoke(prompt_messages)

    # Extract query from payload
    extracted_query: MovieQuery | None = None
    if decision.payload.is_success and decision.payload.data is not None:
        extracted_query = decision.payload.data

    return {
        "query": extracted_query,
        "extraction_decision": decision,
        "needs_clarification": decision.needs_clarification,
    }


def search_movies_node(state: "MovieState") -> dict[str, object]:
    """Search for movies matching the extracted query.

    Calls the MovieService with the current query and
    returns scored candidates.

    Args:
        state: Current workflow state with query.

    Returns:
        State update with search candidates.
    """
    query = state.get("query")
    if query is None:
        return {"candidates": [], "selected_movie": None}

    candidates = _movie_service.search(query)

    # If exactly one match with high score, select it
    selected: Movie | None = None
    if len(candidates) == 1 and candidates[0].score >= HIGH_CONFIDENCE_THRESHOLD:
        selected = candidates[0].item

    return {
        "candidates": candidates,
        "selected_movie": selected,
    }


def clarify_node(state: "MovieState") -> dict[str, object]:
    """Generate clarification message for ambiguous matches.

    When multiple movies match, asks the user to specify
    which one they meant.

    Args:
        state: Current workflow state with candidates.

    Returns:
        State update with clarification message.
    """
    candidates = state.get("candidates", [])
    clarification_count = state.get("clarification_count", 0)

    if not candidates:
        message = AIMessage(
            content=(
                "I couldn't find any movies matching your criteria. "
                "Could you try a different search? You can specify a title, "
                "actor, genre, director, or year range."
            )
        )
    else:
        # Build options list
        options = [
            f"{i + 1}. {c.item.title} ({c.item.year}) - {c.item.director}"
            for i, c in enumerate(candidates[:5])
        ]
        options_text = "\n".join(options)

        message = AIMessage(
            content=(
                f"I found {len(candidates)} movies matching your search. "
                f"Which one did you mean?\n\n{options_text}\n\n"
                "You can say the number, the title, or add more details to narrow it down."
            )
        )

    return {
        "messages": [message],
        "needs_clarification": True,
        "clarification_count": clarification_count + 1,
    }


def respond_node(state: "MovieState") -> dict[str, object]:
    """Generate final response to the user.

    Creates a natural language response based on the
    search results and conversation context.

    Args:
        state: Current workflow state.

    Returns:
        State update with response message.
    """
    selected = state.get("selected_movie")
    candidates = state.get("candidates", [])

    # Build response based on state
    if selected is not None:
        response = _generate_movie_response(selected)
    elif not candidates:
        response = _generate_not_found_response(state)
    else:
        # Single match but low confidence - still respond
        response = _generate_movie_response(candidates[0].item)

    return {
        "messages": [AIMessage(content=response.payload.content)],
        "needs_clarification": False,
    }


# =============================================================================
# Helper Functions
# =============================================================================


def _format_messages(messages: Sequence[AnyMessage]) -> str:
    """Format messages for prompt context."""
    formatted: list[str] = []
    for msg in messages:
        msg_content = msg.content  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        content: str = msg_content if isinstance(msg_content, str) else str(msg_content)  # pyright: ignore[reportUnknownArgumentType]
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        formatted.append(f"{role}: {content}")
    return "\n".join(formatted)


def _convert_message(msg: AnyMessage) -> HumanMessage | AIMessage:
    """Convert a message to HumanMessage or AIMessage."""
    if isinstance(msg, HumanMessage):
        return msg
    if isinstance(msg, AIMessage):
        return msg
    # Default to HumanMessage for unknown types
    msg_content = msg.content  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    content: str = msg_content if isinstance(msg_content, str) else str(msg_content)  # pyright: ignore[reportUnknownArgumentType]
    return HumanMessage(content=content)


def _generate_movie_response(
    movie: Movie,
) -> LLMDecision[AgentResponsePayload]:
    """Generate a response about a specific movie."""
    # Build context
    context = (
        f"Movie found: {movie.title} ({movie.year})\n"
        f"Director: {movie.director}\n"
        f"Genres: {', '.join(movie.genres)}\n"
        f"Rating: {movie.rating}/10\n"
        f"Cast: {', '.join(a.name for a in movie.cast)}"
    )

    prompt_messages: list[HumanMessage | AIMessage] = [
        HumanMessage(
            content=(
                f"Generate a helpful response about this movie:\n{context}\n\n"
                "Be conversational and informative. Include key details."
            )
        ),
    ]

    return _get_response_model().invoke(prompt_messages)


def _generate_not_found_response(
    state: "MovieState",
) -> LLMDecision[AgentResponsePayload]:
    """Generate a response when no movies match."""
    query = state.get("query")
    query_desc = ""
    if query is not None:
        parts: list[str] = []
        if query.title:
            parts.append(f"title '{query.title}'")
        if query.actor_name:
            parts.append(f"actor '{query.actor_name}'")
        if query.genre:
            parts.append(f"genre '{query.genre}'")
        if query.director_name:
            parts.append(f"director '{query.director_name}'")
        query_desc = ", ".join(parts) if parts else "your criteria"

    prompt_messages: list[HumanMessage | AIMessage] = [
        HumanMessage(
            content=(
                f"No movies found matching {query_desc}. "
                "Generate a helpful response suggesting alternatives or asking "
                "for different search criteria."
            )
        ),
    ]

    return _get_response_model().invoke(prompt_messages)
