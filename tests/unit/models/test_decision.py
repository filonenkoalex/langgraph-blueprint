"""Tests for LLMDecision envelope functionality.

Tests the core decision wrapper including confidence scoring,
actionability checks, and payload handling.
"""

from datetime import UTC, datetime

from pydantic import BaseModel, ValidationError
import pytest

from agentic_app.models.core.decision import LLMDecision, LLMDecisionMeta


class SimplePayload(BaseModel):
    """Simple payload for testing."""

    message: str
    value: int


class TestLLMDecisionMeta:
    """Tests for LLMDecisionMeta base class."""

    def test_valid_confidence_bounds(self) -> None:
        """Confidence must be between 0.0 and 1.0."""
        meta = LLMDecisionMeta(
            confidence=0.5,
            reasoning="Test reasoning",
        )
        assert meta.confidence == 0.5

    def test_confidence_at_zero(self) -> None:
        """Confidence of 0.0 is valid."""
        meta = LLMDecisionMeta(confidence=0.0, reasoning="No confidence")
        assert meta.confidence == 0.0

    def test_confidence_at_one(self) -> None:
        """Confidence of 1.0 is valid."""
        meta = LLMDecisionMeta(confidence=1.0, reasoning="Full confidence")
        assert meta.confidence == 1.0

    def test_confidence_below_zero_raises(self) -> None:
        """Confidence below 0.0 should raise ValidationError."""
        with pytest.raises(ValidationError):
            LLMDecisionMeta(confidence=-0.1, reasoning="Invalid")

    def test_confidence_above_one_raises(self) -> None:
        """Confidence above 1.0 should raise ValidationError."""
        with pytest.raises(ValidationError):
            LLMDecisionMeta(confidence=1.1, reasoning="Invalid")

    def test_timestamp_auto_generated(self) -> None:
        """Timestamp should be auto-generated if not provided."""
        before = datetime.now(UTC)
        meta = LLMDecisionMeta(confidence=0.8, reasoning="Test")
        after = datetime.now(UTC)

        assert meta.timestamp >= before
        assert meta.timestamp <= after

    def test_needs_clarification_default_false(self) -> None:
        """needs_clarification should default to False."""
        meta = LLMDecisionMeta(confidence=0.8, reasoning="Test")
        assert meta.needs_clarification is False

    def test_clarification_prompt_optional(self) -> None:
        """clarification_prompt can be None."""
        meta = LLMDecisionMeta(confidence=0.8, reasoning="Test")
        assert meta.clarification_prompt is None

    def test_clarification_prompt_set(self) -> None:
        """clarification_prompt can be set."""
        meta = LLMDecisionMeta(
            confidence=0.5,
            reasoning="Unclear request",
            needs_clarification=True,
            clarification_prompt="Which movie did you mean?",
        )
        assert meta.clarification_prompt == "Which movie did you mean?"


class TestLLMDecisionMetaActionable:
    """Tests for is_actionable() method."""

    def test_actionable_high_confidence_no_clarification(self) -> None:
        """High confidence + no clarification = actionable."""
        meta = LLMDecisionMeta(
            confidence=0.9,
            reasoning="Clear request",
            needs_clarification=False,
        )
        assert meta.is_actionable() is True

    def test_not_actionable_low_confidence(self) -> None:
        """Low confidence = not actionable (default threshold 0.8)."""
        meta = LLMDecisionMeta(
            confidence=0.7,
            reasoning="Uncertain",
            needs_clarification=False,
        )
        assert meta.is_actionable() is False

    def test_not_actionable_needs_clarification(self) -> None:
        """needs_clarification = not actionable regardless of confidence."""
        meta = LLMDecisionMeta(
            confidence=0.95,
            reasoning="Need more info",
            needs_clarification=True,
        )
        assert meta.is_actionable() is False

    def test_actionable_custom_threshold(self) -> None:
        """Custom threshold changes actionability."""
        meta = LLMDecisionMeta(
            confidence=0.6,
            reasoning="Moderate confidence",
        )
        # Default threshold 0.8 - not actionable
        assert meta.is_actionable() is False
        # Lower threshold 0.5 - actionable
        assert meta.is_actionable(threshold=0.5) is True

    def test_actionable_at_exact_threshold(self) -> None:
        """Confidence exactly at threshold is actionable."""
        meta = LLMDecisionMeta(
            confidence=0.8,
            reasoning="At threshold",
        )
        assert meta.is_actionable(threshold=0.8) is True


class TestLLMDecision:
    """Tests for generic LLMDecision wrapper."""

    def test_create_with_payload(self) -> None:
        """Can create LLMDecision with typed payload."""
        decision = LLMDecision[SimplePayload](
            confidence=0.9,
            reasoning="Test decision",
            payload=SimplePayload(message="Hello", value=42),
        )
        assert decision.payload.message == "Hello"
        assert decision.payload.value == 42

    def test_payload_type_preserved(self) -> None:
        """Payload maintains its type."""
        decision = LLMDecision[SimplePayload](
            confidence=0.85,
            reasoning="Typed payload test",
            payload=SimplePayload(message="Test", value=100),
        )
        assert isinstance(decision.payload, SimplePayload)

    def test_inherits_meta_fields(self) -> None:
        """LLMDecision inherits all LLMDecisionMeta fields."""
        decision = LLMDecision[SimplePayload](
            confidence=0.75,
            reasoning="Inheritance test",
            needs_clarification=True,
            clarification_prompt="Please clarify",
            payload=SimplePayload(message="Test", value=1),
        )
        assert decision.confidence == 0.75
        assert decision.reasoning == "Inheritance test"
        assert decision.needs_clarification is True
        assert decision.clarification_prompt == "Please clarify"

    def test_is_actionable_works(self) -> None:
        """is_actionable() method works on LLMDecision."""
        decision = LLMDecision[SimplePayload](
            confidence=0.9,
            reasoning="Actionable decision",
            payload=SimplePayload(message="Go", value=1),
        )
        assert decision.is_actionable() is True

    def test_serialization_round_trip(self) -> None:
        """LLMDecision can be serialized and deserialized."""
        original = LLMDecision[SimplePayload](
            confidence=0.85,
            reasoning="Serialization test",
            payload=SimplePayload(message="Test", value=99),
        )
        json_str = original.model_dump_json()
        restored = LLMDecision[SimplePayload].model_validate_json(json_str)

        assert restored.confidence == original.confidence
        assert restored.reasoning == original.reasoning
        assert restored.payload.message == original.payload.message
        assert restored.payload.value == original.payload.value

    def test_dict_conversion(self) -> None:
        """LLMDecision can be converted to dict (for LangGraph state)."""
        decision = LLMDecision[SimplePayload](
            confidence=0.8,
            reasoning="Dict test",
            payload=SimplePayload(message="Hello", value=42),
        )
        data = decision.model_dump()

        assert data["confidence"] == 0.8
        assert data["reasoning"] == "Dict test"
        assert data["payload"]["message"] == "Hello"
        assert data["payload"]["value"] == 42
