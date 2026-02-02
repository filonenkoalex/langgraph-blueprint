"""Core LLM decision envelope types.

Provides the universal wrapper for all LLM outputs, ensuring
every decision includes confidence scoring and clarification support.
"""

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class LLMDecisionMeta(BaseModel):
    """Base metadata for all LLM decisions.

    Every LLM interaction produces a decision with confidence
    and reasoning. This base class ensures consistent handling
    of uncertainty and clarification needs across all payloads.

    Attributes:
        confidence: Score between 0.0 and 1.0 indicating LLM certainty.
        reasoning: Step-by-step explanation of how the decision was made.
        needs_clarification: Whether user input is needed to proceed.
        clarification_prompt: Question to ask user if clarification needed.
        timestamp: When the decision was made (UTC).
    """

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0.",
    )
    reasoning: str = Field(
        description="Step-by-step logic explaining how the conclusion was reached.",
    )
    needs_clarification: bool = Field(
        default=False,
        description="True if user input is required to proceed.",
    )
    clarification_prompt: str | None = Field(
        default=None,
        description="Question to ask the user if clarification is needed.",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="UTC timestamp when the decision was made.",
    )

    def is_actionable(self, threshold: float = 0.8) -> bool:
        """Check if this decision can be acted upon without user input.

        A decision is actionable when confidence meets the threshold
        and no clarification is needed.

        Args:
            threshold: Minimum confidence required. Defaults to 0.8.

        Returns:
            True if the decision can proceed without user intervention.
        """
        return self.confidence >= threshold and not self.needs_clarification


class LLMDecision[PayloadT: BaseModel](LLMDecisionMeta):
    """Generic wrapper for LLM decision payloads.

    Combines decision metadata with a strongly-typed payload.
    Use this as the return type for all structured LLM outputs.

    Type Parameters:
        PayloadT: The specific payload type (must be a Pydantic BaseModel).

    Example:
        ```python
        # Define your payload
        class FundQuery(BaseModel):
            ticker: str

        # Use with LLMDecision
        decision: LLMDecision[FundQuery] = llm.invoke(...)
        if decision.is_actionable():
            process(decision.payload.ticker)
        ```
    """

    payload: PayloadT = Field(
        description="The actual content/data of the LLM decision.",
    )
