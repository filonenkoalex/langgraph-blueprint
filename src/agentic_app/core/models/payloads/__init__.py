"""Payload models for LLM decisions.

This module provides specialized payload types that can be
wrapped by LLMDecision for different use cases.
"""

from agentic_app.core.models.payloads.conversation import (
    AgentResponsePayload,
    UserInputPayload,
)
from agentic_app.core.models.payloads.extraction import ExtractionPayload
from agentic_app.core.models.payloads.selection import (
    ScoredCandidate,
    SelectionPayload,
)
from agentic_app.core.models.payloads.workflow import (
    MutationValue,
    StateMutation,
    WorkflowMutationPayload,
)

__all__ = [
    "AgentResponsePayload",
    "ExtractionPayload",
    "MutationValue",
    "ScoredCandidate",
    "SelectionPayload",
    "StateMutation",
    "UserInputPayload",
    "WorkflowMutationPayload",
]
