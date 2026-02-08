"""LCEL-compatible structured output runnable.

Provides a LangChain Runnable that wraps any BaseChatModel
to return validated Pydantic models, composable via the pipe operator.
"""

from typing import cast, override

from langchain_core.language_models import LanguageModelInput
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import RunnableConfig, RunnableSerializable
from pydantic import BaseModel, ConfigDict

from agentic_app.core.schema.utils import prepare_openai_schema


class StructuredDecisionRunnable(RunnableSerializable[LanguageModelInput, BaseModel]):
    """LCEL-compatible runnable that returns validated Pydantic models.

    Wraps ``BaseChatModel.with_structured_output()`` to provide:
    - Automatic schema generation from Pydantic types
    - Auto-fix for OpenAI strict mode compatibility
    - Type-safe response parsing via Pydantic validation
    - Full LCEL composition via the pipe operator

    Attributes:
        llm: The LangChain chat model to use for generation.
        output_type: The Pydantic model class to parse responses into.

    Example:
        ```python
        from langchain_openai import ChatOpenAI
        from agentic_app.core import (
            StructuredDecisionRunnable,
            LLMDecision,
            ExtractionPayload,
        )

        llm = ChatOpenAI(model="gpt-4o")

        # Direct usage
        runnable = StructuredDecisionRunnable(
            llm=llm,
            output_type=LLMDecision[ExtractionPayload[Actor]],
        )
        decision = runnable.invoke("Tom Hanks is an American actor")

        # LCEL composition with prompt templates
        chain = prompt_template | StructuredDecisionRunnable(
            llm=llm,
            output_type=LLMDecision[ExtractionPayload[Actor]],
        )
        decision = chain.invoke({"text": "Tom Hanks is American"})
        ```
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    llm: BaseChatModel
    output_type: type[BaseModel]

    @override
    def invoke(
        self,
        input: LanguageModelInput,
        config: RunnableConfig | None = None,
        **kwargs: object,
    ) -> BaseModel:
        """Invoke the LLM and return a validated Pydantic model.

        Args:
            input: The input to process (str, messages, PromptValue, etc.).
            config: Optional LangChain runnable config for callbacks/tags.
            **kwargs: Additional keyword arguments (required by Runnable interface).

        Returns:
            Parsed and validated instance of ``output_type``.
        """
        schema = prepare_openai_schema(self.output_type)

        structured_llm = self.llm.with_structured_output(schema=schema)  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]

        result = structured_llm.invoke(input, config=config)  # pyright: ignore[reportUnknownVariableType]

        return self.output_type.model_validate(cast("dict[str, object]", result))
