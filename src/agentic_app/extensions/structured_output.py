"""Structured output client for type-safe LLM interactions."""

from typing import cast

from langchain_core.language_models import LanguageModelInput
from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import BaseModel

type JsonSchema = dict[str, object]


class StructuredOutputClient:
    """Type-safe client for structured LLM output.

    Wraps BaseChatModel.with_structured_output() to provide:
    - Automatic schema generation from Pydantic types
    - Auto-fix for OpenAI strict mode compatibility
    - Type-safe response parsing

    Example:
        ```python
        llm = ChatOpenAI(model="gpt-4o")
        client = StructuredOutputClient(llm)
        decision = client.invoke(
            "Tom Hanks is an American actor",
            LLMDecision[ExtractionPayload[Actor]],
        )
        ```
    """

    def __init__(self, model: BaseChatModel) -> None:
        """Initialize the client.

        Args:
            model: The LLM model to use.
        """
        super().__init__()
        self._model = model

    def invoke[T: BaseModel](
        self,
        input_prompt: LanguageModelInput,
        response_type: type[T],
    ) -> T:
        """Send input and get typed response.

        Args:
            input: The input to process (str, messages, etc.).
            response_type: The Pydantic type to parse response into.

        Returns:
            Parsed response as the specified Pydantic type.
        """
        schema = StructuredOutputClient._prepare_schema(response_type)

        structured_llm = self._model.with_structured_output(schema=schema)  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]

        result = structured_llm.invoke(input_prompt)  # pyright: ignore[reportUnknownVariableType]

        return response_type.model_validate(
            cast("dict[str, object]", result)
        )

    @staticmethod
    def _prepare_schema[T: BaseModel](response_type: type[T]) -> JsonSchema:
        """Convert Pydantic type to OpenAI-compatible JSON schema."""
        schema: JsonSchema = response_type.model_json_schema()

        # Auto-fix: replace invalid chars (brackets) with underscores
        raw_title = str(schema.get("title", "Schema"))
        schema["title"] = raw_title.replace("[", "_").replace("]", "")

        # Required by OpenAI strict mode
        schema["additionalProperties"] = False

        return schema
