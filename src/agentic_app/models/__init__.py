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
    from agentic_app.core import (
        LLMDecision,
        ExtractionPayload,
        StructuredDecisionRunnable,
    )
    from agentic_app.models import FundQuery

    llm = ChatOpenAI(model="gpt-4o")
    runnable = StructuredDecisionRunnable(
        llm=llm,
        output_type=LLMDecision[ExtractionPayload[FundQuery]],
    )
    result = runnable.invoke("I want to buy VTI")
    if result.is_actionable():
        fund_query = result.payload.data
        # proceed with fund_query.ticker
    ```
"""

from agentic_app.core import (
    AgentResponsePayload,
    ConversationIntent,
    ExtractionPayload,
    LLMDecision,
    LLMDecisionMeta,
    ResolutionStatus,
    ResponseType,
    ScoredCandidate,
    SelectionPayload,
    SelectionStrategy,
    StateMutation,
    UserInputPayload,
    WorkflowMutationPayload,
)
from agentic_app.models.aliases import (
    AgentResponseDecision,
    FundExtractionDecision,
    FundSelectionDecision,
    UserInputDecision,
    WorkflowMutationDecision,
)
from agentic_app.models.domain.fund import Fund, FundQuery

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
