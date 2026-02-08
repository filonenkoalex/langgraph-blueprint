"""Demo: Using StructuredDecisionRunnable with LCEL."""

from typing import cast

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from agentic_app.core import (
    ExtractionPayload,
    LLMDecision,
    StructuredDecisionRunnable,
)

type ActorDecision = LLMDecision[ExtractionPayload[Actor]]


class Actor(BaseModel):
    """An actor."""

    name: str = Field(..., description="Actor name")
    nationality: str | None = Field(default=None, description="Nationality")


def main() -> None:
    """Run extraction demo."""
    llm = ChatOpenAI(model="gpt-4o")

    # LCEL-compatible runnable: can be used standalone or piped
    runnable = StructuredDecisionRunnable(
        llm=llm,
        output_type=LLMDecision[ExtractionPayload[Actor]],
    )

    # Runnable.invoke returns BaseModel; cast to the concrete type
    decision = cast("ActorDecision", runnable.invoke("Tom Hanks is an American actor"))

    # Use typed response
    print(f"Confidence: {decision.confidence}")  # noqa: T201
    print(f"Success: {decision.payload.is_success}")  # noqa: T201
    if decision.payload.data:
        print(f"Actor: {decision.payload.data.name}")  # noqa: T201


if __name__ == "__main__":
    main()
