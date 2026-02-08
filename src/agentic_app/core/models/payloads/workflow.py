"""Workflow payloads for state mutations and dual-intent handling.

Provides models for tracking changes to workflow state when
users confirm and modify data in the same message.
"""

from pydantic import BaseModel, Field

from agentic_app.core.models.enums import ConversationIntent

# Define a union type for mutation values to avoid Any
type MutationValue = str | int | float | bool


class StateMutation[MutationValueT](BaseModel):
    """A single state field mutation.

    Represents a change to one field in the workflow state,
    tracking both the old and new values for audit purposes.

    Type Parameters:
        MutationValueT: The type of the field being mutated.

    Attributes:
        field_name: Name of the state field being changed.
        old_value: Previous value (None if field was unset).
        new_value: New value to set.

    Example:
        ```python
        mutation = StateMutation[int](
            field_name="quantity",
            old_value=50,
            new_value=100,
        )
        ```
    """

    field_name: str = Field(
        description="Name of the state field being changed.",
    )
    old_value: MutationValueT | None = Field(
        default=None,
        description="Previous value of the field (None if unset).",
    )
    new_value: MutationValueT = Field(
        description="New value to set for the field.",
    )


class WorkflowMutationPayload(BaseModel):
    """Payload for handling dual-intent user messages.

    When a user confirms an action but also requests modifications
    (e.g., "Yes, but change the quantity to 100"), this payload
    captures both the intent and the specific changes.

    Attributes:
        user_intent: The primary intent of the user's message.
        mutations: List of state field changes requested.
        workflow_hint: Optional hint about workflow transition.

    Example:
        ```python
        payload = WorkflowMutationPayload(
            user_intent=ConversationIntent.CONFIRM,
            mutations=[
                StateMutation[int](
                    field_name="quantity",
                    old_value=50,
                    new_value=100,
                ),
            ],
            workflow_hint="proceed_with_modifications",
        )
        ```
    """

    user_intent: ConversationIntent = Field(
        description="The primary intent of the user's message.",
    )
    mutations: list[StateMutation[MutationValue]] = Field(
        default_factory=list,
        description="List of state field changes requested by the user.",
    )
    workflow_hint: str | None = Field(
        default=None,
        description="Optional hint about the intended workflow transition.",
    )
