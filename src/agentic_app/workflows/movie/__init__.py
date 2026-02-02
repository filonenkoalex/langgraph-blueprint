"""Movie domain workflow for conversational movie search.

Provides a LangGraph workflow for:
- Extracting movie queries from user input
- Searching movies with fuzzy matching
- Handling clarification when multiple matches found
- Generating natural language responses
"""

from agentic_app.workflows.movie.graph import movie_graph
from agentic_app.workflows.movie.state import MovieState

__all__ = ["MovieState", "movie_graph"]
