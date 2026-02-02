"""Demo: Using StructuredOutputClient extension."""

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from agentic_app.extensions import StructuredOutputClient
from agentic_app.models.core.decision import LLMDecision
from agentic_app.models.payloads.extraction import ExtractionPayload


class Actor(BaseModel):
    """An actor."""

    name: str = Field(..., description="Actor name")
    nationality: str | None = Field(default=None, description="Nationality")


def main() -> None:
    """Run extraction demo."""
    llm = ChatOpenAI(model="gpt-4o")
    llm.invoke("Tom Hanks is an American actor")
    client = StructuredOutputClient(llm)

    # Type comes from invoke, not constructor
    decision = client.invoke(
        "Tom Hanks is an American actor",
        LLMDecision[ExtractionPayload[Actor]],
    )

    # Use typed response
    print(f"Confidence: {decision.confidence}")  # noqa: T201
    print(f"Success: {decision.payload.is_success}")  # noqa: T201
    if decision.payload.data:
        print(f"Actor: {decision.payload.data.name}")  # noqa: T201


if __name__ == "__main__":
    main()
