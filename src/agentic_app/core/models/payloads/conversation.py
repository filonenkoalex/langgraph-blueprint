"""Conversation payloads for user input and agent responses.

Provides models for classifying user intent and structuring
agent responses in conversational flows.
"""

from pydantic import BaseModel, Field

from agentic_app.core.models.enums import ConversationIntent, ResponseType


class UserInputPayload(BaseModel):
    """Classification of user message input.

    Represents the parsed understanding of what the user
    said and what they want to accomplish.

    Attributes:
        intent: The classified intent of the user's message.
        entity_hints: Potential entity references detected in the message.
        raw_query: The original user message text.

    Example:
        ```python
        payload = UserInputPayload(
            intent=ConversationIntent.PROVIDE_DATA,
            entity_hints=["fund:VANGUARD", "action:buy"],
            raw_query="I want to buy some Vanguard fund",
        )
        ```
    """

    intent: ConversationIntent = Field(
        description="The classified intent of the user's message.",
    )
    entity_hints: list[str] = Field(
        default_factory=list,
        description="Potential entity references detected (e.g., 'fund:VTI').",
    )
    raw_query: str | None = Field(
        default=None,
        description="The original user message text.",
    )


class AgentResponsePayload(BaseModel):
    """Structured response from agent to user.

    Defines what the agent should say and how it should
    be presented to the user.

    Attributes:
        response_type: The type of conversational act.
        content: The natural language text to show the user.
        proposed_action: Action being proposed if asking for confirmation.
        clarification_question: Specific question if asking for clarification.

    Example:
        ```python
        # Answer response
        response = AgentResponsePayload(
            response_type=ResponseType.ANSWER,
            content="Your portfolio is up 5% this month.",
        )

        # Clarification response
        response = AgentResponsePayload(
            response_type=ResponseType.CLARIFICATION,
            content="I found multiple Vanguard funds.",
            clarification_question="Did you mean VTI, VOO, or VXUS?",
        )
        ```
    """

    response_type: ResponseType = Field(
        description="The type of conversational response.",
    )
    content: str = Field(
        description="The natural language text to show the user.",
    )
    proposed_action: str | None = Field(
        default=None,
        description="If response_type is CONFIRMATION, what action are we confirming?",
    )
    clarification_question: str | None = Field(
        default=None,
        description="If response_type is CLARIFICATION, what specific question to ask?",
    )
