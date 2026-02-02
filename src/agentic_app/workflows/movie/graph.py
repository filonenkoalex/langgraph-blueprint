"""LangGraph workflow for movie search conversations.

Compiles the state, nodes, and routing into a runnable
StateGraph that can be used with the LangGraph CLI or
invoked directly.
"""

from langgraph.graph import END, StateGraph  # pyright: ignore[reportMissingTypeStubs]

from agentic_app.workflows.movie.nodes import (
    clarify_node,
    extract_query_node,
    respond_node,
    search_movies_node,
)
from agentic_app.workflows.movie.routing import (
    route_after_extraction,
    route_after_search,
)
from agentic_app.workflows.movie.state import MovieState


def build_movie_graph() -> StateGraph[MovieState]:
    """Build the movie search workflow graph.

    Creates a StateGraph with the following flow:
    1. extract -> Route based on extraction success
    2. search -> Route based on match count/quality
    3. clarify -> Back to extract (user refinement loop)
    4. respond -> END

    Returns:
        Compiled StateGraph ready for invocation.
    """
    # Initialize the graph with MovieState
    graph: StateGraph[MovieState] = StateGraph(MovieState)

    # Add nodes
    graph.add_node("extract", extract_query_node)  # pyright: ignore[reportUnknownMemberType]
    graph.add_node("search", search_movies_node)  # pyright: ignore[reportUnknownMemberType]
    graph.add_node("clarify", clarify_node)  # pyright: ignore[reportUnknownMemberType]
    graph.add_node("respond", respond_node)  # pyright: ignore[reportUnknownMemberType]

    # Set entry point
    graph.set_entry_point("extract")

    # Add conditional edges from extraction
    graph.add_conditional_edges(
        "extract",
        route_after_extraction,
        {
            "search": "search",
            "respond": "respond",
        },
    )

    # Add conditional edges from search
    graph.add_conditional_edges(
        "search",
        route_after_search,
        {
            "respond": "respond",
            "clarify": "clarify",
        },
    )

    # Clarify always goes back to extract for next user input
    graph.add_edge("clarify", END)

    # Respond ends the current turn
    graph.add_edge("respond", END)

    return graph


# Compile the graph for export
movie_graph = build_movie_graph().compile()  # pyright: ignore[reportUnknownMemberType]
"""Compiled movie search workflow graph.

Use this with LangGraph CLI or invoke directly:
    result = movie_graph.invoke({"messages": [HumanMessage(content="...")]})
"""
