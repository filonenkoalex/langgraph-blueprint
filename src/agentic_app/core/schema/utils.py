"""Schema preparation utilities for LLM providers.

Provides functions for converting Pydantic models to
provider-compatible JSON schemas, handling quirks like
OpenAI strict mode requirements.
"""

from pydantic import BaseModel

type JsonSchema = dict[str, object]


def prepare_openai_schema[T: BaseModel](response_type: type[T]) -> JsonSchema:
    """Convert a Pydantic model to an OpenAI-compatible JSON schema.

    Handles provider-specific requirements:
    - Sanitizes title (replaces brackets from generic type names)
    - Sets ``additionalProperties: false`` for OpenAI strict mode

    Args:
        response_type: The Pydantic model class to generate a schema for.

    Returns:
        A JSON schema dict ready for OpenAI structured output.

    Example:
        ```python
        from agentic_app.core.schema.utils import prepare_openai_schema

        schema = prepare_openai_schema(LLMDecision[ExtractionPayload[Actor]])
        # schema["title"] == "LLMDecision_ExtractionPayload_Actor_"
        # schema["additionalProperties"] == False
        ```
    """
    schema: JsonSchema = response_type.model_json_schema()

    # Auto-fix: replace invalid chars (brackets) with underscores
    raw_title = str(schema.get("title", "Schema"))
    schema["title"] = raw_title.replace("[", "_").replace("]", "")

    # Required by OpenAI strict mode
    schema["additionalProperties"] = False

    return schema
