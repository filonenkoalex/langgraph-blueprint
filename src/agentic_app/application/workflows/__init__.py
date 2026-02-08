"""LangGraph workflows for conversational agents.

Provides compiled graph workflows for different domains,
each implementing structured conversational flows.
"""

from .capital_call.graph import graph

__all__ = ["graph"]
