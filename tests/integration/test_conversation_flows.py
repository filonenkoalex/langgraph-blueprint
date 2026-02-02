"""Integration tests for end-to-end conversation flows.

Tests realistic conversation scenarios demonstrating the full
pipeline from user input to agent response.
"""


from agentic_app.models.core.decision import LLMDecision
from agentic_app.models.core.enums import (
    ConversationIntent,
    ResponseType,
    SelectionStrategy,
)
from agentic_app.models.domain.movie import Movie, MovieQuery
from agentic_app.models.payloads.conversation import (
    AgentResponsePayload,
    UserInputPayload,
)
from agentic_app.models.payloads.extraction import ExtractionPayload
from agentic_app.models.payloads.selection import ScoredCandidate, SelectionPayload
from agentic_app.models.payloads.workflow import (
    MutationValue,
    StateMutation,
    WorkflowMutationPayload,
)
from agentic_app.services.movie_service import MovieService


class TestFlowASimpleLookup:
    """Flow A: Simple movie lookup with clear request.

    User: "Tell me about Inception"
      → Extraction(title="Inception", confidence=0.95)
      → Selection(selected=Inception, alternatives=[])
      → Response(ANSWER, "Inception (2010)...")
    """

    def test_step1_extract_clear_title(self) -> None:
        """Step 1: Extract movie title from clear request."""
        # Simulate LLM extraction output
        extraction_decision = LLMDecision[ExtractionPayload[MovieQuery]](
            confidence=0.95,
            reasoning="User explicitly mentioned 'Inception' - clear movie title",
            payload=ExtractionPayload[MovieQuery](
                is_success=True,
                data=MovieQuery(title="Inception"),
            ),
        )
        assert extraction_decision.is_actionable()
        assert extraction_decision.payload.is_success
        assert extraction_decision.payload.data is not None
        assert extraction_decision.payload.data.title == "Inception"

    def test_step2_select_single_match(
        self, movie_service: MovieService
    ) -> None:
        """Step 2: Search returns high-confidence match for Inception."""
        query = MovieQuery(title="Inception")
        candidates = movie_service.search(query)

        # First result should be Inception with high score
        assert len(candidates) >= 1
        assert candidates[0].item.title == "Inception"
        assert candidates[0].score >= 0.9
        inception = candidates[0].item

        selection_decision = LLMDecision[SelectionPayload[Movie]](
            confidence=0.95,
            reasoning="Exact match found for 'Inception'",
            payload=SelectionPayload[Movie](
                selected=inception,
                alternatives=[],
                strategy=SelectionStrategy.HIGHEST_SCORE,
                is_ambiguous=False,
                requires_confirmation=False,
            ),
        )
        assert selection_decision.is_actionable()
        assert selection_decision.payload.selected.title == "Inception"
        assert not selection_decision.payload.is_ambiguous

    def test_step3_generate_answer_response(self) -> None:
        """Step 3: Generate informative answer response."""
        response_decision = LLMDecision[AgentResponsePayload](
            confidence=0.95,
            reasoning="Single movie found, providing details",
            payload=AgentResponsePayload(
                response_type=ResponseType.ANSWER,
                content=(
                    "Inception (2010) is a sci-fi thriller directed by "
                    "Christopher Nolan, starring Leonardo DiCaprio. "
                    "Rating: 8.8/10."
                ),
            ),
        )
        assert response_decision.is_actionable()
        assert response_decision.payload.response_type == ResponseType.ANSWER
        assert "Inception" in response_decision.payload.content

    def test_full_flow_a(self, movie_service: MovieService) -> None:
        """Complete Flow A end-to-end."""
        # Step 1: Extract
        extraction = LLMDecision[ExtractionPayload[MovieQuery]](
            confidence=0.95,
            reasoning="Clear title request",
            payload=ExtractionPayload[MovieQuery](
                is_success=True,
                data=MovieQuery(title="Inception"),
            ),
        )

        # Step 2: Search and Select
        assert extraction.payload.data is not None
        candidates = movie_service.search(extraction.payload.data)
        assert len(candidates) >= 1
        assert candidates[0].item.title == "Inception"

        selection = LLMDecision[SelectionPayload[Movie]](
            confidence=0.95,
            reasoning="Single match",
            payload=SelectionPayload[Movie](
                selected=candidates[0].item,
                alternatives=[],
                is_ambiguous=False,
            ),
        )

        # Step 3: Generate Response
        movie = selection.payload.selected
        response = LLMDecision[AgentResponsePayload](
            confidence=0.95,
            reasoning="Providing movie details",
            payload=AgentResponsePayload(
                response_type=ResponseType.ANSWER,
                content=f"{movie.title} ({movie.year}) - {', '.join(movie.genres)}",
            ),
        )

        # Verify full flow
        assert extraction.is_actionable()
        assert selection.is_actionable()
        assert response.is_actionable()
        assert response.payload.response_type == ResponseType.ANSWER


class TestFlowBClarificationLoop:
    """Flow B: Ambiguous request requiring clarification.

    User: "I want to watch a Batman movie"
      → Extraction(title="Batman", confidence=0.65, needs_clarification=true)
      → Selection(3 matches, is_ambiguous=true)
      → Response(CLARIFICATION, "Which Batman movie?...")
    User: "The one with Heath Ledger"
      → Extraction(title="Batman", actor_name="Heath Ledger")
      → Selection(selected="The Dark Knight")
      → Response(ANSWER, "The Dark Knight (2008)...")
    """

    def test_step1_extract_ambiguous_title(self) -> None:
        """Step 1: Extract partial title, flag need for clarification."""
        extraction = LLMDecision[ExtractionPayload[MovieQuery]](
            confidence=0.65,
            reasoning="User mentioned 'Batman' but there are multiple Batman movies",
            needs_clarification=True,
            clarification_prompt="Which Batman movie did you mean?",
            payload=ExtractionPayload[MovieQuery](
                is_success=True,
                data=MovieQuery(title="Batman"),
            ),
        )
        assert not extraction.is_actionable()  # Needs clarification
        assert extraction.needs_clarification
        assert extraction.payload.data is not None
        assert extraction.payload.data.title == "Batman"

    def test_step2_select_multiple_matches(
        self, movie_service: MovieService
    ) -> None:
        """Step 2: Search returns multiple Batman movies."""
        query = MovieQuery(title="Batman")
        candidates = movie_service.search(query)

        # Should have Batman movies as top results
        assert len(candidates) >= 1
        titles = [c.item.title for c in candidates]
        assert "Batman Begins" in titles
        # Dark Knight movies have "Batman" in them via franchise

        selection = LLMDecision[SelectionPayload[Movie]](
            confidence=0.60,
            reasoning="3 Batman movies found, need user to clarify",
            needs_clarification=True,
            clarification_prompt="Did you mean Batman Begins, The Dark Knight, or The Dark Knight Rises?",
            payload=SelectionPayload[Movie](
                selected=candidates[0].item,  # Default to first
                alternatives=[
                    ScoredCandidate[Movie](item=c.item, score=c.score)
                    for c in candidates[1:]
                ],
                is_ambiguous=True,
                requires_confirmation=True,
            ),
        )
        assert not selection.is_actionable()
        assert selection.payload.is_ambiguous
        assert len(selection.payload.alternatives) >= 1

    def test_step3_clarification_response(self) -> None:
        """Step 3: Generate clarification request."""
        response = LLMDecision[AgentResponsePayload](
            confidence=0.90,
            reasoning="Multiple matches, asking user to clarify",
            payload=AgentResponsePayload(
                response_type=ResponseType.CLARIFICATION,
                content="I found 3 Batman movies in the database.",
                clarification_question=(
                    "Did you mean Batman Begins (2005), "
                    "The Dark Knight (2008), or "
                    "The Dark Knight Rises (2012)?"
                ),
            ),
        )
        assert response.is_actionable()
        assert response.payload.response_type == ResponseType.CLARIFICATION
        assert response.payload.clarification_question is not None

    def test_step4_user_clarifies_with_actor(self) -> None:
        """Step 4: User provides clarification with actor name.

        Simulates user saying "The one with Heath Ledger".
        """
        extraction = LLMDecision[ExtractionPayload[MovieQuery]](
            confidence=0.90,
            reasoning="User specified Heath Ledger, narrows to Dark Knight",
            payload=ExtractionPayload[MovieQuery](
                is_success=True,
                data=MovieQuery(title="Batman", actor_name="Heath Ledger"),
            ),
        )
        assert extraction.is_actionable()
        assert extraction.payload.data is not None
        assert extraction.payload.data.actor_name == "Heath Ledger"

    def test_step5_select_after_clarification(
        self, movie_service: MovieService
    ) -> None:
        """Step 5: Search with clarification yields single match."""
        # Heath Ledger was in The Dark Knight
        query = MovieQuery(title="Dark Knight", actor_name="Ledger")
        candidates = movie_service.search(query)

        # The Dark Knight has Heath Ledger
        dark_knight_candidates = [
            c for c in candidates if c.item.title == "The Dark Knight"
        ]
        assert len(dark_knight_candidates) == 1

        selection = LLMDecision[SelectionPayload[Movie]](
            confidence=0.95,
            reasoning="Heath Ledger appeared in The Dark Knight",
            payload=SelectionPayload[Movie](
                selected=dark_knight_candidates[0].item,
                alternatives=[],
                strategy=SelectionStrategy.USER_SPECIFIED,
                is_ambiguous=False,
            ),
        )
        assert selection.is_actionable()
        assert selection.payload.selected.title == "The Dark Knight"


class TestFlowCProgressiveRefinement:
    """Flow C: Progressive refinement with workflow mutations.

    User: "Show me sci-fi movies"
      → Selection(4 movies, no single selection)
      → Response(ANSWER, "Here are sci-fi movies: ...")
    User: "With Leonardo DiCaprio"
      → WorkflowMutation(MODIFY_DATA, add actor filter)
      → Selection(selected="Inception")
      → Response(ANSWER, "Inception matches...")
    """

    def test_step1_genre_search(self, movie_service: MovieService) -> None:
        """Step 1: Genre search returns multiple movies."""
        movies = movie_service.get_by_genre("Sci-Fi")
        assert len(movies) >= 3

        # Present as list, not selection
        titles = [m.title for m in movies]
        assert "Inception" in titles
        assert "Interstellar" in titles

    def test_step2_list_response(self) -> None:
        """Step 2: Respond with list of genre results."""
        response = LLMDecision[AgentResponsePayload](
            confidence=0.90,
            reasoning="Showing sci-fi movie list",
            payload=AgentResponsePayload(
                response_type=ResponseType.ANSWER,
                content=(
                    "Here are sci-fi movies in the database: "
                    "Inception, Interstellar, The Avengers..."
                ),
            ),
        )
        assert response.is_actionable()
        assert response.payload.response_type == ResponseType.ANSWER

    def test_step3_user_adds_filter(self) -> None:
        """Step 3: User refines with actor filter.

        Simulates user saying "With Leonardo DiCaprio".
        """
        mutation = LLMDecision[WorkflowMutationPayload](
            confidence=0.90,
            reasoning="User adding actor filter to existing genre search",
            payload=WorkflowMutationPayload(
                user_intent=ConversationIntent.MODIFY_DATA,
                mutations=[
                    StateMutation[MutationValue](
                        field_name="actor_name",
                        old_value=None,
                        new_value="Leonardo DiCaprio",
                    ),
                ],
            ),
        )
        assert mutation.is_actionable()
        assert mutation.payload.user_intent == ConversationIntent.MODIFY_DATA
        assert len(mutation.payload.mutations) == 1

    def test_step4_refined_search(self, movie_service: MovieService) -> None:
        """Step 4: Search with combined filters."""
        # Combine: genre=Sci-Fi AND actor=DiCaprio
        candidates = movie_service.search(
            MovieQuery(
                genre="Sci-Fi",
                actor_name="DiCaprio",
            )
        )

        # Only Inception matches both criteria
        assert len(candidates) == 1
        assert candidates[0].item.title == "Inception"

    def test_full_flow_c(self, movie_service: MovieService) -> None:
        """Complete Flow C end-to-end."""
        # Initial state: genre=Sci-Fi
        current_query = MovieQuery(genre="Sci-Fi")
        results = movie_service.search(current_query)
        assert len(results) >= 3

        # User modifies: add actor (mutation captured for demonstration)
        _ = WorkflowMutationPayload(
            user_intent=ConversationIntent.MODIFY_DATA,
            mutations=[
                StateMutation[MutationValue](
                    field_name="actor_name",
                    old_value=None,
                    new_value="DiCaprio",
                ),
            ],
        )

        # Apply mutation to query
        updated_query = MovieQuery(
            genre=current_query.genre,
            actor_name="DiCaprio",
        )
        refined_results = movie_service.search(updated_query)

        assert len(refined_results) == 1
        assert refined_results[0].item.title == "Inception"


class TestFlowDGenreDiscovery:
    """Flow D: Genre discovery with confirmation.

    User: "What's a good thriller?"
      → Extraction(genre="Thriller", confidence=0.85)
      → Selection(5 matches, requires_confirmation=true)
      → Response(CONFIRMATION, "How about Inception or The Departed?")
    User: "Departed sounds good"
      → Input(CONFIRM)
      → Response(ANSWER, "The Departed (2006)...")
    """

    def test_step1_extract_genre(self) -> None:
        """Step 1: Extract genre from user request."""
        extraction = LLMDecision[ExtractionPayload[MovieQuery]](
            confidence=0.85,
            reasoning="User asking for thriller recommendations",
            payload=ExtractionPayload[MovieQuery](
                is_success=True,
                data=MovieQuery(genre="Thriller"),
            ),
        )
        assert extraction.is_actionable()
        assert extraction.payload.data is not None
        assert extraction.payload.data.genre == "Thriller"

    def test_step2_find_thrillers(self, movie_service: MovieService) -> None:
        """Step 2: Find thriller movies."""
        candidates = movie_service.search(MovieQuery(genre="Thriller"))
        assert len(candidates) >= 3

        titles = [c.item.title for c in candidates]
        assert "Inception" in titles
        assert "The Departed" in titles

    def test_step3_propose_options(self, movie_service: MovieService) -> None:
        """Step 3: Propose top options for confirmation."""
        candidates = movie_service.search(MovieQuery(genre="Thriller"))
        top_two = candidates[:2]

        response = LLMDecision[AgentResponsePayload](
            confidence=0.85,
            reasoning="Proposing top thriller options",
            payload=AgentResponsePayload(
                response_type=ResponseType.CONFIRMATION,
                content=(
                    f"I'd recommend {top_two[0].item.title} or "
                    f"{top_two[1].item.title}. Both are highly rated thrillers."
                ),
                proposed_action="Select one of the recommended thrillers",
            ),
        )
        assert response.is_actionable()
        assert response.payload.response_type == ResponseType.CONFIRMATION
        assert response.payload.proposed_action is not None

    def test_step4_user_confirms_choice(self) -> None:
        """Step 4: User confirms 'Departed sounds good'."""
        user_input = LLMDecision[UserInputPayload](
            confidence=0.90,
            reasoning="User expressed preference for The Departed",
            payload=UserInputPayload(
                intent=ConversationIntent.CONFIRM,
                entity_hints=["movie:The Departed"],
                raw_query="Departed sounds good",
            ),
        )
        assert user_input.is_actionable()
        assert user_input.payload.intent == ConversationIntent.CONFIRM

    def test_step5_final_response(self, movie_service: MovieService) -> None:
        """Step 5: Provide details on confirmed selection."""
        candidates = movie_service.search(MovieQuery(title="The Departed"))
        assert len(candidates) >= 1
        assert candidates[0].item.title == "The Departed"
        departed = candidates[0].item

        response = LLMDecision[AgentResponsePayload](
            confidence=0.95,
            reasoning="User confirmed The Departed selection",
            payload=AgentResponsePayload(
                response_type=ResponseType.ANSWER,
                content=(
                    f"{departed.title} ({departed.year}) is a "
                    f"{', '.join(departed.genres)} film "
                    f"directed by {departed.director}. Rating: {departed.rating}/10."
                ),
            ),
        )
        assert response.is_actionable()
        assert response.payload.response_type == ResponseType.ANSWER
        assert "The Departed" in response.payload.content


class TestEdgeCases:
    """Edge cases and error scenarios."""

    def test_no_results_response(self, movie_service: MovieService) -> None:
        """Handle case when search returns no results."""
        # Use a completely nonsensical title that won't fuzzy match
        candidates = movie_service.search(MovieQuery(title="Xyzqwerty12345"))
        assert len(candidates) == 0

        response = LLMDecision[AgentResponsePayload](
            confidence=0.90,
            reasoning="No movies found matching query",
            payload=AgentResponsePayload(
                response_type=ResponseType.REJECTION,
                content=(
                    "I couldn't find any movies matching your request. "
                    "Try searching by title, actor, or genre."
                ),
            ),
        )
        assert response.is_actionable()
        assert response.payload.response_type == ResponseType.REJECTION

    def test_vague_request_asks_clarification(self) -> None:
        """Handle vague request by asking for clarification."""
        extraction = LLMDecision[ExtractionPayload[MovieQuery]](
            confidence=0.30,
            reasoning="User request too vague to extract query",
            needs_clarification=True,
            clarification_prompt="What kind of movie are you looking for?",
            payload=ExtractionPayload[MovieQuery](
                is_success=False,
                missing_fields=["title", "genre", "actor_name"],
                error_message="Please specify a movie title, genre, or actor",
            ),
        )
        assert not extraction.is_actionable()
        assert extraction.needs_clarification
        assert not extraction.payload.is_success

    def test_user_cancels_flow(self) -> None:
        """Handle user cancellation."""
        user_input = LLMDecision[UserInputPayload](
            confidence=0.95,
            reasoning="User wants to cancel",
            payload=UserInputPayload(
                intent=ConversationIntent.CANCEL,
                raw_query="Never mind, cancel",
            ),
        )
        assert user_input.payload.intent == ConversationIntent.CANCEL

    def test_confidence_threshold_variations(self) -> None:
        """Different flows may have different confidence thresholds."""
        # High threshold for financial transactions
        high_threshold_decision = LLMDecision[ExtractionPayload[MovieQuery]](
            confidence=0.85,
            reasoning="Moderate confidence",
            payload=ExtractionPayload[MovieQuery](
                is_success=True,
                data=MovieQuery(title="Test"),
            ),
        )
        # Not actionable at 0.9 threshold
        assert not high_threshold_decision.is_actionable(threshold=0.9)
        # Actionable at 0.8 threshold
        assert high_threshold_decision.is_actionable(threshold=0.8)
