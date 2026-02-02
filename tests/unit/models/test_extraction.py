"""Tests for ExtractionPayload with MovieQuery scenarios.

Tests the generic extraction container including success/failure
states, validation, and realistic movie extraction scenarios.
"""

from pydantic import ValidationError
import pytest

from agentic_app.models.core.decision import LLMDecision
from agentic_app.models.domain.movie import MovieQuery
from agentic_app.models.payloads.extraction import ExtractionPayload


class TestExtractionPayloadBasics:
    """Basic ExtractionPayload functionality tests."""

    def test_successful_extraction(self) -> None:
        """Successful extraction has data and is_success=True."""
        payload = ExtractionPayload[MovieQuery](
            is_success=True,
            data=MovieQuery(title="Inception"),
        )
        assert payload.is_success is True
        assert payload.data is not None
        assert payload.data.title == "Inception"
        assert payload.missing_fields == []

    def test_failed_extraction_with_missing_fields(self) -> None:
        """Failed extraction lists missing fields."""
        payload = ExtractionPayload[MovieQuery](
            is_success=False,
            missing_fields=["title", "actor_name", "genre"],
            error_message="Could not determine what movie you're looking for",
        )
        assert payload.is_success is False
        assert payload.data is None
        assert "title" in payload.missing_fields
        assert len(payload.missing_fields) == 3

    def test_success_requires_data_validator(self) -> None:
        """is_success=True requires data to be present."""
        with pytest.raises(ValidationError) as exc_info:
            ExtractionPayload[MovieQuery](
                is_success=True,
                data=None,
            )
        assert "Data cannot be null if is_success is True" in str(exc_info.value)

    def test_failure_allows_none_data(self) -> None:
        """is_success=False allows data to be None."""
        payload = ExtractionPayload[MovieQuery](
            is_success=False,
            missing_fields=["title"],
        )
        assert payload.data is None

    def test_error_message_optional(self) -> None:
        """error_message is optional even on failure."""
        payload = ExtractionPayload[MovieQuery](
            is_success=False,
            missing_fields=["title"],
        )
        assert payload.error_message is None


class TestMovieExtractionScenarios:
    """Realistic movie extraction scenarios."""

    def test_clear_title_extraction(self) -> None:
        """Scenario: User says 'Inception movie info'."""
        payload = ExtractionPayload[MovieQuery](
            is_success=True,
            data=MovieQuery(title="Inception"),
        )
        assert payload.is_success
        assert payload.data is not None
        assert payload.data.title == "Inception"

    def test_actor_search_extraction(self) -> None:
        """Scenario: User says 'Movies with DiCaprio'."""
        payload = ExtractionPayload[MovieQuery](
            is_success=True,
            data=MovieQuery(actor_name="DiCaprio"),
        )
        assert payload.data is not None
        assert payload.data.actor_name == "DiCaprio"

    def test_genre_browse_extraction(self) -> None:
        """Scenario: User says 'Show me sci-fi movies'."""
        payload = ExtractionPayload[MovieQuery](
            is_success=True,
            data=MovieQuery(genre="Sci-Fi"),
        )
        assert payload.data is not None
        assert payload.data.genre == "Sci-Fi"

    def test_multi_criteria_extraction(self) -> None:
        """Scenario: User says '90s drama with Tom Hanks'."""
        payload = ExtractionPayload[MovieQuery](
            is_success=True,
            data=MovieQuery(
                genre="Drama",
                actor_name="Tom Hanks",
                year_from=1990,
                year_to=1999,
            ),
        )
        assert payload.data is not None
        assert payload.data.genre == "Drama"
        assert payload.data.actor_name == "Tom Hanks"
        assert payload.data.year_from == 1990
        assert payload.data.year_to == 1999

    def test_partial_info_extraction(self) -> None:
        """Scenario: User says 'That Batman movie' - partial but usable."""
        payload = ExtractionPayload[MovieQuery](
            is_success=True,
            data=MovieQuery(title="Batman"),
            missing_fields=[],  # We got something, but it's ambiguous
        )
        assert payload.data is not None
        assert payload.data.title == "Batman"

    def test_vague_request_extraction_fails(self) -> None:
        """Scenario: User says 'Something good to watch' - too vague."""
        payload = ExtractionPayload[MovieQuery](
            is_success=False,
            missing_fields=["title", "genre", "actor_name"],
            error_message="Please specify a movie title, genre, or actor",
        )
        assert payload.is_success is False
        assert len(payload.missing_fields) == 3

    def test_typo_handling_extraction(self) -> None:
        """Scenario: User says 'Incpetion' - typo but recognizable."""
        # In real scenario, LLM would correct the typo
        payload = ExtractionPayload[MovieQuery](
            is_success=True,
            data=MovieQuery(title="Inception"),  # Corrected by LLM
        )
        assert payload.data is not None
        assert payload.data.title == "Inception"


class TestExtractionWithLLMDecision:
    """Tests for ExtractionPayload wrapped in LLMDecision."""

    def test_high_confidence_clear_extraction(self) -> None:
        """Clear title extraction should have high confidence."""
        decision = LLMDecision[ExtractionPayload[MovieQuery]](
            confidence=0.95,
            reasoning="User explicitly mentioned 'Inception' movie title",
            payload=ExtractionPayload[MovieQuery](
                is_success=True,
                data=MovieQuery(title="Inception"),
            ),
        )
        assert decision.is_actionable()
        assert decision.payload.is_success
        assert decision.payload.data is not None
        assert decision.payload.data.title == "Inception"

    def test_moderate_confidence_partial_extraction(self) -> None:
        """Partial info should have moderate confidence."""
        decision = LLMDecision[ExtractionPayload[MovieQuery]](
            confidence=0.65,
            reasoning="User mentioned 'Batman' but there are multiple Batman movies",
            needs_clarification=True,
            clarification_prompt="Which Batman movie did you mean?",
            payload=ExtractionPayload[MovieQuery](
                is_success=True,
                data=MovieQuery(title="Batman"),
            ),
        )
        assert not decision.is_actionable()  # Needs clarification
        assert decision.payload.is_success
        assert decision.clarification_prompt is not None

    def test_low_confidence_vague_extraction(self) -> None:
        """Vague request should have low confidence."""
        decision = LLMDecision[ExtractionPayload[MovieQuery]](
            confidence=0.30,
            reasoning="User request too vague - no specific movie, actor, or genre",
            needs_clarification=True,
            clarification_prompt="What kind of movie are you looking for?",
            payload=ExtractionPayload[MovieQuery](
                is_success=False,
                missing_fields=["title", "genre", "actor_name"],
            ),
        )
        assert not decision.is_actionable()
        assert not decision.payload.is_success
        assert len(decision.payload.missing_fields) == 3

    def test_actionable_when_confident_and_successful(self) -> None:
        """Decision is actionable only when confident AND extraction succeeded."""
        decision = LLMDecision[ExtractionPayload[MovieQuery]](
            confidence=0.90,
            reasoning="Clear actor search request",
            payload=ExtractionPayload[MovieQuery](
                is_success=True,
                data=MovieQuery(actor_name="DiCaprio"),
            ),
        )
        assert decision.is_actionable()
        assert decision.payload.is_success
        assert decision.payload.data is not None

    def test_serialization_preserves_nested_structure(self) -> None:
        """Serialization should preserve the nested structure."""
        original = LLMDecision[ExtractionPayload[MovieQuery]](
            confidence=0.88,
            reasoning="Multi-criteria extraction",
            payload=ExtractionPayload[MovieQuery](
                is_success=True,
                data=MovieQuery(
                    genre="Drama",
                    actor_name="Tom Hanks",
                    year_from=1990,
                    year_to=1999,
                ),
            ),
        )
        json_str = original.model_dump_json()
        # Verify JSON structure is valid
        data = original.model_dump()
        assert data["payload"]["is_success"] is True
        assert data["payload"]["data"]["genre"] == "Drama"
        assert data["payload"]["data"]["actor_name"] == "Tom Hanks"
        # Verify round-trip works
        restored = LLMDecision[ExtractionPayload[MovieQuery]].model_validate_json(
            json_str
        )
        assert restored.payload.data is not None
        assert original.payload.data is not None  # Already asserted via is_success
        assert restored.payload.data.genre == original.payload.data.genre
