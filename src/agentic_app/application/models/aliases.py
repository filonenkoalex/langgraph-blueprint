"""Type aliases for common LLM decision types.

Provides convenient, strongly-typed shortcuts for common use cases
when working with LLMDecision and various payloads.
"""

from agentic_app.core import (
    AgentResponsePayload,
    LLMDecision,
    UserInputPayload,
    WorkflowMutationPayload,
)

# Conversation decisions
type UserInputDecision = LLMDecision[UserInputPayload]
"""Decision wrapping user input classification."""

type AgentResponseDecision = LLMDecision[AgentResponsePayload]
"""Decision wrapping agent response generation."""

# Workflow decisions
type WorkflowMutationDecision = LLMDecision[WorkflowMutationPayload]
"""Decision wrapping state mutation from dual-intent messages."""
