"""LCEL-compatible runnables for structured LLM interactions.

Provides LangChain Expression Language (LCEL) components that
can be composed with other runnables via the pipe operator.
"""

from agentic_app.core.runnables.structured_output import StructuredDecisionRunnable

__all__ = ["StructuredDecisionRunnable"]
