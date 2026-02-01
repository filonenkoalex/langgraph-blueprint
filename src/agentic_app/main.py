from datetime import datetime
from typing import TYPE_CHECKING, cast

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from langchain_core.messages import BaseMessage
    from langchain_core.runnables import Runnable


class Movie(BaseModel):
    """A movie with details."""

    title: str = Field(..., description="The title of the movie")
    year: int = Field(..., description="The year the movie was released")
    director: str = Field(..., description="The director of the movie")
    rating: float = Field(..., description="The movie's rating out of 10")

class Actor(BaseModel):
    """An actor with details."""

    name: str = Field(..., description="The name of the actor")
    birth_date: datetime = Field(..., description="The date of birth of the actor")
    nationality: str = Field(..., description="The nationality of the actor")
    movies: list[Movie] = Field(..., description="The movies the actor has starred in")

# Create LLM
llm = ChatOpenAI()

model_with_structure = cast(
    "Runnable[str, Actor]",
    llm.with_structured_output(Actor),  # pyright: ignore[reportUnknownMemberType]
)

response = model_with_structure.invoke("I want some film tith Leonardo DiCaprio")
print(response)  # noqa: T201

# Create prompt template
prompt = ChatPromptTemplate([
    ("system", "You are a professional {domain} expert"),
    ("human", "Please explain the concept and applications of {topic}"),
])

# Create chain
chain = cast("Runnable[dict[str, str], BaseMessage]", prompt | llm)

# Invoke chain
response = chain.invoke({"domain": "machine learning", "topic": "deep learning"})

content = response.content if hasattr(response, "content") else str(response)  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
print(content)  # pyright: ignore[reportUnknownArgumentType]  # noqa: T201
