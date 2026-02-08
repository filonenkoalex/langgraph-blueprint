"""Schema utilities for LLM provider compatibility.

Provides helpers for converting Pydantic models to
provider-specific JSON schemas (e.g., OpenAI strict mode).
"""

from agentic_app.core.schema.utils import prepare_openai_schema

__all__ = ["prepare_openai_schema"]
