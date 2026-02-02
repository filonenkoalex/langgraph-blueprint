"""Pydantic models for conversational AI with LangChain/LangGraph.

This module provides a comprehensive type hierarchy for structured
LLM interactions, including:

- Core decision envelope (LLMDecision) for wrapping all LLM outputs
- Extraction payloads for entity extraction from user input
- Selection payloads for fuzzy matching from API results
- Conversation payloads for user/agent message handling
- Workflow payloads for state mutation tracking

Example usage with LangChain:
    ```python
    from langchain_openai import ChatOpenAI
    from agentic_app.models import (
        LLMDecision,
        ExtractionPayload,
        FundQuery,
        FundExtractionDecision,
    )

    llm = ChatOpenAI(model="gpt-4o")
    structured_llm = llm.with_structured_output(FundExtractionDecision)

    result = structured_llm.invoke("I want to buy VTI")
    if result.is_actionable():
        fund_query = result.payload.data
        # proceed with fund_query.ticker
    ```
"""

from agentic_app.models.aliases import (
    AgentResponseDecision,
    FundExtractionDecision,
    FundSelectionDecision,
    UserInputDecision,
    WorkflowMutationDecision,
)
from agentic_app.models.core.decision import LLMDecision, LLMDecisionMeta
from agentic_app.models.core.enums import (
    ConversationIntent,
    ResolutionStatus,
    ResponseType,
    SelectionStrategy,
)
from agentic_app.models.domain.fund import Fund, FundQuery
from agentic_app.models.payloads.conversation import (
    AgentResponsePayload,
    UserInputPayload,
)
from agentic_app.models.payloads.extraction import ExtractionPayload
from agentic_app.models.payloads.selection import ScoredCandidate, SelectionPayload
from agentic_app.models.payloads.workflow import StateMutation, WorkflowMutationPayload

__all__ = [
    "AgentResponseDecision",
    "AgentResponsePayload",
    "ConversationIntent",
    "ExtractionPayload",
    "Fund",
    "FundExtractionDecision",
    "FundQuery",
    "FundSelectionDecision",
    "LLMDecision",
    "LLMDecisionMeta",
    "ResolutionStatus",
    "ResponseType",
    "ScoredCandidate",
    "SelectionPayload",
    "SelectionStrategy",
    "StateMutation",
    "UserInputDecision",
    "UserInputPayload",
    "WorkflowMutationDecision",
    "WorkflowMutationPayload",
]
