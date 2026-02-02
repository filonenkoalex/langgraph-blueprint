"""Core enumerations for conversational AI models.

All string enums used across the models hierarchy are defined here
for reusability and consistency.
"""

from enum import StrEnum


class ConversationIntent(StrEnum):
    """Classification of user message intent.

    Used to determine what action the user wants to perform
    in the conversation flow.
    """

    PROVIDE_DATA = "provide_data"
    """User is providing requested information."""

    MODIFY_DATA = "modify_data"
    """User wants to change previously provided data."""

    CONFIRM = "confirm"
    """User confirms a proposed action or data."""

    CANCEL = "cancel"
    """User wants to cancel the current operation."""

    ASK_CLARIFICATION = "ask_clarification"
    """User is asking for more information."""

    UNKNOWN = "unknown"
    """Intent could not be determined."""


class ResponseType(StrEnum):
    """Type of response the agent should give to the user.

    Determines the conversational act the agent performs.
    """

    ANSWER = "answer"
    """Direct answer to user's question."""

    CLARIFICATION = "clarification"
    """Agent needs more information from user."""

    CONFIRMATION = "confirmation"
    """Agent is asking user to confirm an action."""

    REJECTION = "rejection"
    """Agent cannot fulfill the request."""


class SelectionStrategy(StrEnum):
    """Strategy used to select from multiple candidates.

    Indicates how a selection was made when multiple
    options were available.
    """

    HIGHEST_SCORE = "highest_score"
    """Selected the candidate with highest match score."""

    USER_SPECIFIED = "user_specified"
    """User explicitly specified the selection."""

    LLM_CHOICE = "llm_choice"
    """LLM made the selection based on context."""


class ResolutionStatus(StrEnum):
    """Status of entity resolution against external data.

    Tracks the outcome of attempting to resolve
    an extracted entity to a known record.
    """

    NOT_ATTEMPTED = "not_attempted"
    """Resolution has not been attempted yet."""

    RESOLVED = "resolved"
    """Entity was successfully resolved to a single record."""

    AMBIGUOUS = "ambiguous"
    """Multiple candidates match, user clarification needed."""

    NOT_FOUND = "not_found"
    """No matching records found."""
