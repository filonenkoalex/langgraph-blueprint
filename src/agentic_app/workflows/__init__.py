"""LangGraph workflows for conversational agents.

Provides compiled graph workflows for different domains,
each implementing structured conversational flows.
"""

from agentic_app.workflows.movie.graph import movie_graph

__all__ = ["movie_graph"]
