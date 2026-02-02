"""Tests for SelectionPayload with Movie scenarios.

Tests the selection container including single/multiple matches,
ambiguity detection, and confirmation requirements.
"""

import pytest

from agentic_app.models.core.decision import LLMDecision
from agentic_app.models.core.enums import SelectionStrategy
from agentic_app.models.domain.movie import Actor, Movie
from agentic_app.models.payloads.selection import ScoredCandidate, SelectionPayload


@pytest.fixture
def inception_movie() -> Movie:
    """Provide Inception movie for tests."""
    return Movie(
        id="mov_001",
        title="Inception",
        year=2010,
        director="Christopher Nolan",
        genres=["Sci-Fi", "Thriller"],
        cast=[Actor(id="a1", name="Leonardo DiCaprio")],
        rating=8.8,
    )


@pytest.fixture
def dark_knight_movie() -> Movie:
    """Provide The Dark Knight movie for tests."""
    return Movie(
        id="mov_002",
        title="The Dark Knight",
        year=2008,
        director="Christopher Nolan",
        genres=["Action", "Crime"],
        cast=[Actor(id="a2", name="Christian Bale")],
        rating=9.0,
    )


@pytest.fixture
def batman_begins_movie() -> Movie:
    """Provide Batman Begins movie for tests."""
    return Movie(
        id="mov_003",
        title="Batman Begins",
        year=2005,
        director="Christopher Nolan",
        genres=["Action"],
        cast=[Actor(id="a2", name="Christian Bale")],
        rating=8.2,
    )


@pytest.fixture
def dark_knight_rises_movie() -> Movie:
    """Provide The Dark Knight Rises movie for tests."""
    return Movie(
        id="mov_004",
        title="The Dark Knight Rises",
        year=2012,
        director="Christopher Nolan",
        genres=["Action"],
        cast=[Actor(id="a2", name="Christian Bale")],
        rating=8.4,
    )


class TestScoredCandidate:
    """Tests for ScoredCandidate wrapper."""

    def test_create_scored_candidate(self, inception_movie: Movie) -> None:
        """Can create a scored candidate with movie."""
        candidate = ScoredCandidate[Movie](
            item=inception_movie,
            score=0.95,
            match_reason="Exact title match",
        )
        assert candidate.item.title == "Inception"
        assert candidate.score == 0.95
        assert candidate.match_reason == "Exact title match"

    def test_score_bounds(self, inception_movie: Movie) -> None:
        """Score must be between 0.0 and 1.0."""
        # Valid bounds
        ScoredCandidate[Movie](item=inception_movie, score=0.0)
        ScoredCandidate[Movie](item=inception_movie, score=1.0)

        # Invalid bounds
        with pytest.raises(Exception):  # noqa: B017
            ScoredCandidate[Movie](item=inception_movie, score=-0.1)
        with pytest.raises(Exception):  # noqa: B017
            ScoredCandidate[Movie](item=inception_movie, score=1.1)

    def test_match_reason_optional(self, inception_movie: Movie) -> None:
        """match_reason is optional."""
        candidate = ScoredCandidate[Movie](
            item=inception_movie,
            score=0.9,
        )
        assert candidate.match_reason is None


class TestSelectionPayloadBasics:
    """Basic SelectionPayload functionality tests."""

    def test_single_selection_no_alternatives(self, inception_movie: Movie) -> None:
        """Single match returns selected with no alternatives."""
        payload = SelectionPayload[Movie](
            selected=inception_movie,
            alternatives=[],
            strategy=SelectionStrategy.HIGHEST_SCORE,
        )
        assert payload.selected.title == "Inception"
        assert len(payload.alternatives) == 0
        assert payload.is_ambiguous is False

    def test_selection_with_alternatives(
        self,
        dark_knight_movie: Movie,
        batman_begins_movie: Movie,
        dark_knight_rises_movie: Movie,
    ) -> None:
        """Selection with multiple alternatives."""
        payload = SelectionPayload[Movie](
            selected=dark_knight_movie,
            alternatives=[
                ScoredCandidate[Movie](
                    item=dark_knight_rises_movie,
                    score=0.85,
                    match_reason="Partial title match",
                ),
                ScoredCandidate[Movie](
                    item=batman_begins_movie,
                    score=0.70,
                    match_reason="Same franchise",
                ),
            ],
            strategy=SelectionStrategy.HIGHEST_SCORE,
        )
        assert payload.selected.title == "The Dark Knight"
        assert len(payload.alternatives) == 2

    def test_ambiguous_selection(
        self,
        dark_knight_movie: Movie,
        batman_begins_movie: Movie,
        dark_knight_rises_movie: Movie,
    ) -> None:
        """Ambiguous selection when multiple high-scoring matches."""
        payload = SelectionPayload[Movie](
            selected=dark_knight_movie,
            alternatives=[
                ScoredCandidate[Movie](
                    item=batman_begins_movie,
                    score=0.88,
                    match_reason="Contains 'Batman'",
                ),
                ScoredCandidate[Movie](
                    item=dark_knight_rises_movie,
                    score=0.87,
                    match_reason="Contains 'Batman'",
                ),
            ],
            strategy=SelectionStrategy.HIGHEST_SCORE,
            is_ambiguous=True,
            requires_confirmation=True,
        )
        assert payload.is_ambiguous is True
        assert payload.requires_confirmation is True

    def test_default_strategy(self, inception_movie: Movie) -> None:
        """Default strategy is HIGHEST_SCORE."""
        payload = SelectionPayload[Movie](
            selected=inception_movie,
        )
        assert payload.strategy == SelectionStrategy.HIGHEST_SCORE


class TestMovieSelectionScenarios:
    """Realistic movie selection scenarios."""

    def test_exact_match_scenario(self, inception_movie: Movie) -> None:
        """Scenario: User searches for 'Inception' - exact match."""
        payload = SelectionPayload[Movie](
            selected=inception_movie,
            alternatives=[],
            strategy=SelectionStrategy.HIGHEST_SCORE,
            is_ambiguous=False,
            requires_confirmation=False,
        )
        assert payload.selected.title == "Inception"
        assert not payload.is_ambiguous
        assert not payload.requires_confirmation

    def test_multiple_batman_matches_scenario(
        self,
        dark_knight_movie: Movie,
        batman_begins_movie: Movie,
        dark_knight_rises_movie: Movie,
    ) -> None:
        """Scenario: User searches for 'Batman' - 3 matches."""
        payload = SelectionPayload[Movie](
            selected=dark_knight_movie,  # Highest rated
            alternatives=[
                ScoredCandidate[Movie](
                    item=dark_knight_rises_movie,
                    score=0.90,
                    match_reason="Title contains 'Dark Knight'",
                ),
                ScoredCandidate[Movie](
                    item=batman_begins_movie,
                    score=0.85,
                    match_reason="Title contains 'Batman'",
                ),
            ],
            strategy=SelectionStrategy.HIGHEST_SCORE,
            is_ambiguous=True,
            requires_confirmation=True,
        )
        assert payload.is_ambiguous
        assert payload.requires_confirmation
        assert len(payload.alternatives) == 2

    def test_fuzzy_match_scenario(self, dark_knight_movie: Movie) -> None:
        """Scenario: User searches for 'Dark Night' (typo) - fuzzy match."""
        payload = SelectionPayload[Movie](
            selected=dark_knight_movie,
            alternatives=[],
            strategy=SelectionStrategy.HIGHEST_SCORE,
            is_ambiguous=False,
            requires_confirmation=True,  # Confirm due to typo
        )
        assert payload.selected.title == "The Dark Knight"
        assert payload.requires_confirmation  # Should confirm typo correction

    def test_user_specified_selection(self, batman_begins_movie: Movie) -> None:
        """Scenario: User explicitly selects after clarification."""
        payload = SelectionPayload[Movie](
            selected=batman_begins_movie,
            alternatives=[],
            strategy=SelectionStrategy.USER_SPECIFIED,
            is_ambiguous=False,
            requires_confirmation=False,
        )
        assert payload.strategy == SelectionStrategy.USER_SPECIFIED
        assert not payload.requires_confirmation


class TestSelectionWithLLMDecision:
    """Tests for SelectionPayload wrapped in LLMDecision."""

    def test_high_confidence_single_match(self, inception_movie: Movie) -> None:
        """Single match should have high confidence."""
        decision = LLMDecision[SelectionPayload[Movie]](
            confidence=0.95,
            reasoning="Exact title match for 'Inception'",
            payload=SelectionPayload[Movie](
                selected=inception_movie,
                alternatives=[],
                is_ambiguous=False,
            ),
        )
        assert decision.is_actionable()
        assert not decision.payload.is_ambiguous

    def test_low_confidence_ambiguous_match(
        self,
        dark_knight_movie: Movie,
        batman_begins_movie: Movie,
        dark_knight_rises_movie: Movie,
    ) -> None:
        """Ambiguous matches should trigger clarification."""
        decision = LLMDecision[SelectionPayload[Movie]](
            confidence=0.60,
            reasoning="Multiple Batman movies found, user needs to clarify",
            needs_clarification=True,
            clarification_prompt="Did you mean Batman Begins, The Dark Knight, or The Dark Knight Rises?",
            payload=SelectionPayload[Movie](
                selected=dark_knight_movie,
                alternatives=[
                    ScoredCandidate[Movie](item=batman_begins_movie, score=0.85),
                    ScoredCandidate[Movie](item=dark_knight_rises_movie, score=0.82),
                ],
                is_ambiguous=True,
                requires_confirmation=True,
            ),
        )
        assert not decision.is_actionable()
        assert decision.needs_clarification
        assert decision.payload.is_ambiguous

    def test_moderate_confidence_with_confirmation(
        self,
        dark_knight_movie: Movie,
    ) -> None:
        """Fuzzy match should request confirmation."""
        decision = LLMDecision[SelectionPayload[Movie]](
            confidence=0.80,
            reasoning="Fuzzy matched 'Dark Night' to 'The Dark Knight'",
            payload=SelectionPayload[Movie](
                selected=dark_knight_movie,
                alternatives=[],
                is_ambiguous=False,
                requires_confirmation=True,
            ),
        )
        assert decision.is_actionable()
        assert decision.payload.requires_confirmation

    def test_genre_results_no_single_selection(self) -> None:
        """Genre search returns list without single selection logic."""
        # When user asks for "sci-fi movies", we show all results
        # This is a list response, not a selection
        movies = [
            Movie(
                id="m1",
                title="Inception",
                year=2010,
                director="Nolan",
                genres=["Sci-Fi"],
                rating=8.8,
            ),
            Movie(
                id="m2",
                title="Interstellar",
                year=2014,
                director="Nolan",
                genres=["Sci-Fi"],
                rating=8.7,
            ),
        ]
        # For a list response, we pick the highest rated as "selected"
        # but set requires_confirmation since user might want to browse
        decision = LLMDecision[SelectionPayload[Movie]](
            confidence=0.85,
            reasoning="Found 2 sci-fi movies, showing top rated",
            payload=SelectionPayload[Movie](
                selected=movies[0],  # Highest rated
                alternatives=[ScoredCandidate[Movie](item=movies[1], score=0.87)],
                strategy=SelectionStrategy.HIGHEST_SCORE,
                is_ambiguous=False,  # Not ambiguous, just multiple results
                requires_confirmation=False,  # Just displaying results
            ),
        )
        assert decision.is_actionable()
        assert len(decision.payload.alternatives) == 1

    def test_serialization_with_nested_movies(
        self,
        dark_knight_movie: Movie,
        batman_begins_movie: Movie,
    ) -> None:
        """Serialization preserves all nested movie data."""
        original = LLMDecision[SelectionPayload[Movie]](
            confidence=0.75,
            reasoning="Batman search",
            payload=SelectionPayload[Movie](
                selected=dark_knight_movie,
                alternatives=[
                    ScoredCandidate[Movie](
                        item=batman_begins_movie,
                        score=0.80,
                        match_reason="Same franchise",
                    ),
                ],
                is_ambiguous=True,
            ),
        )
        json_str = original.model_dump_json()
        restored = LLMDecision[SelectionPayload[Movie]].model_validate_json(json_str)

        assert restored.payload.selected.title == "The Dark Knight"
        assert len(restored.payload.alternatives) == 1
        assert restored.payload.alternatives[0].item.title == "Batman Begins"
