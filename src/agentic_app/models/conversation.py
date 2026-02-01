from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from typing import Generic, TypeVar, List

HumanMessageConversationIntent = Literal["provide_data", "modify_data", "ask_clarification", "confirm", "cancel", "unknown"]

class ConversationIntent(str, Enum):
    PROVIDE_DATA = "provide_data"
    MODIFY_DATA = "modify_data"
    ASK_CLARIFICATION = "ask_clarification"
    CONFIRM = "confirm"
    CANCEL = "cancel"
    UNKNOWN = "unknown"


class ConversationResponse(BaseModel):
    """
    Generic classification of user message.
    Domain agnostic.
    """

    intent: HumanMessageConversationIntent

    confidence: float = Field(
        ...,
        description="Confidence 0-1 from LLM"
    )

    reasoning: Optional[str] = Field(
        None,
        description="Optional natural language reasoning"
    )

    llm_message: Optional[str] = Field(
        None,
        description="Optional natural language explanation"
    )

T = TypeVar("T")

class EntityExtractionResult(DataExtractionResult, Generic[T]):
    """
    Generic entity extraction + resolution container.
    Works for Fund, Actor, GL Account, Vendor, etc.
    """

    # --- User side ---
    raw_user_value: Optional[str] = None

    normalized_value: Optional[str] = None

    extraction_confidence: Optional[float] = None

    # --- Resolution side ---
    resolution_status: ResolutionStatus = ResolutionStatus.NOT_ATTEMPTED

    resolution_source: Optional[ResolutionSource] = None

    resolved_entity: Optional[T] = None

    candidate_entities: List[T] = Field(default_factory=list)

    # --- Clarification support ---
    clarification_question: Optional[str] = None

    # --- Traceability ---
    resolution_metadata: Dict[str, Any] = Field(default_factory=dict)
    
class Fund(BaseModel):
    id: str
    name: str
    currency: str
    is_active: bool

class FundExtractionResult(EntityExtractionResult[Fund]):
    """
    Fund-specific extraction result.
    Adds fund-specific validation and metadata.
    """

    allowed_for_user: Optional[bool] = None

    open_for_posting: Optional[bool] = None