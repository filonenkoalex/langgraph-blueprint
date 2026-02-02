"""Type aliases for common LLM decision types.

Provides convenient, strongly-typed shortcuts for common use cases
when working with LLMDecision and various payloads.
"""

from agentic_app.models.core.decision import LLMDecision
from agentic_app.models.domain.fund import Fund, FundQuery
from agentic_app.models.payloads.conversation import (
    AgentResponsePayload,
    UserInputPayload,
)
from agentic_app.models.payloads.extraction import ExtractionPayload
from agentic_app.models.payloads.selection import SelectionPayload
from agentic_app.models.payloads.workflow import WorkflowMutationPayload

# Extraction decisions
type FundExtractionDecision = LLMDecision[ExtractionPayload[FundQuery]]
"""Decision wrapping fund query extraction from user input."""

# Selection decisions
type FundSelectionDecision = LLMDecision[SelectionPayload[Fund]]
"""Decision wrapping fund selection from multiple candidates."""

# Conversation decisions
type UserInputDecision = LLMDecision[UserInputPayload]
"""Decision wrapping user input classification."""

type AgentResponseDecision = LLMDecision[AgentResponsePayload]
"""Decision wrapping agent response generation."""

# Workflow decisions
type WorkflowMutationDecision = LLMDecision[WorkflowMutationPayload]
"""Decision wrapping state mutation from dual-intent messages."""
