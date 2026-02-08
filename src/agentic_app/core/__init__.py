"""Agentic Core -- reusable microframework for structured LLM interactions.

Provides a complete toolkit for building type-safe conversational AI:

- **Decision envelope**: ``LLMDecision[PayloadT]`` wraps every LLM output
  with confidence scoring, reasoning, and clarification support.
- **Payload models**: Generic containers for extraction, selection,
  conversation, and workflow mutation results.
- **LCEL runnables**: LangChain-compatible components that compose
  via the pipe operator (``prompt | runnable``).
- **Schema utilities**: Provider-specific schema preparation
  (e.g., OpenAI strict mode).

Example:
    ```python
    from langchain_openai import ChatOpenAI
    from agentic_app.core import (
        LLMDecision,
        ExtractionPayload,
        StructuredDecisionRunnable,
    )

    llm = ChatOpenAI(model="gpt-4o")
    runnable = StructuredDecisionRunnable(
        llm=llm,
        output_type=LLMDecision[ExtractionPayload[MyEntity]],
    )
    decision = runnable.invoke("Extract entity from this text")
    ```
"""

from agentic_app.core.models.decision import LLMDecision, LLMDecisionMeta
from agentic_app.core.models.enums import (
    ConversationIntent,
    ResolutionStatus,
    ResponseType,
    SelectionStrategy,
)
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
from agentic_app.core.runnables.structured_output import StructuredDecisionRunnable
from agentic_app.core.schema.utils import prepare_openai_schema

__all__ = [
    "AgentResponsePayload",
    "ConversationIntent",
    "ExtractionPayload",
    "LLMDecision",
    "LLMDecisionMeta",
    "MutationValue",
    "ResolutionStatus",
    "ResponseType",
    "ScoredCandidate",
    "SelectionPayload",
    "SelectionStrategy",
    "StateMutation",
    "StructuredDecisionRunnable",
    "UserInputPayload",
    "WorkflowMutationPayload",
    "prepare_openai_schema",
]
