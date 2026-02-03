# Capital Call Workflow - Architecture Document

## Executive Summary

This document describes the **layered state architecture** for LangGraph workflows, using Capital Call as the reference implementation. The design separates four orthogonal concerns into composable layers, enabling framework reusability while keeping domain logic isolated.

---

## Design Principles

### 1. Separation of Concerns

Each layer has **one reason to change**:

- Conversation layer changes when LangGraph API evolves
- Context layer changes when auth/session model changes
- Workflow layer changes when orchestration patterns evolve
- Domain layer changes when business rules change

### 2. Composition Over Inheritance

While we use inheritance for the state hierarchy, domain data is **composed** as a nested Pydantic model rather than flattened into state fields. This keeps domain logic testable independently.

### 3. Framework-First Thinking

Base layers (`ConversationState`, `ContextState`, `WorkflowState`) are **generic** and reusable. Any new workflow inherits these without modification.

### 4. Pydantic Validation Throughout

All state is Pydantic-validated at runtime, catching type errors early and providing clear error messages.

---

## State Layer Hierarchy

```
┌─────────────────────────────────────────────────────────────────────┐
│                       CapitalCallState                              │
│          (Final composed state for Capital Call workflow)           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌──────────────────────────────────────────────────────────┐     │
│   │                    WorkflowState                          │     │
│   │   status, current_step, error, pending_confirmation       │     │
│   │   (Generic orchestration - reusable for any workflow)     │     │
│   └──────────────────────────┬───────────────────────────────┘     │
│                              │                                      │
│   ┌──────────────────────────┴───────────────────────────────┐     │
│   │                    ContextState                           │     │
│   │   thread_id, user_context                                 │     │
│   │   (Session identity - reusable for any workflow)          │     │
│   └──────────────────────────┬───────────────────────────────┘     │
│                              │                                      │
│   ┌──────────────────────────┴───────────────────────────────┐     │
│   │                 ConversationState                         │     │
│   │   messages (inherited), last_decision                     │     │
│   │   (LLM interaction - extends MessagesState)               │     │
│   └──────────────────────────┬───────────────────────────────┘     │
│                              │                                      │
│   ┌──────────────────────────┴───────────────────────────────┐     │
│   │                   MessagesState                           │     │
│   │   messages: Annotated[list[AnyMessage], add_messages]     │     │
│   │   (LangGraph built-in)                                    │     │
│   └──────────────────────────────────────────────────────────┘     │
│                                                                     │
│   ┌──────────────────────────────────────────────────────────┐     │
│   │                  CapitalCallData                          │     │
│   │   fund, amount, dates, gl_accounts, document              │     │
│   │   (Pure domain model - COMPOSED, not inherited)           │     │
│   └──────────────────────────────────────────────────────────┘     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Layer 1: ConversationState (Framework)

**Purpose**: Extend LangGraph's `MessagesState` with LLM decision tracking.

**Location**: `src/agentic_app/workflows/core/state.py`

```python
from langgraph.graph import MessagesState
from pydantic import Field
from agentic_app.models import LLMDecision

class ConversationState(MessagesState):
    """Base state for all conversational workflows.
    
    Inherits from MessagesState which provides:
        messages: Annotated[list[AnyMessage], add_messages]
    
    The add_messages reducer handles:
        - Appending new messages (not overwriting)
        - Updating existing messages by ID
        - Proper serialization for checkpointing
    
    Attributes:
        last_decision: Most recent LLM decision for routing/debugging.
                       Useful for understanding why a path was taken.
    """
    last_decision: LLMDecision | None = Field(
        default=None,
        description="Most recent LLM decision for routing and debugging.",
    )
```

**Why this layer exists**:

- Every workflow needs conversation history
- `last_decision` enables routing based on LLM confidence/clarification needs
- Consistent pattern for all workflows using your `LLMDecision` model

---

## Layer 2: ContextState (Framework)

**Purpose**: Thread identity and user context passed from the calling system.

**Location**: `src/agentic_app/workflows/core/state.py`

```python
from pydantic import BaseModel, Field

class UserContext(BaseModel):
    """User-specific context from authentication/session.
    
    This model represents WHO is using the system.
    Populated from your auth layer before workflow starts.
    
    Attributes:
        user_id: Unique identifier for the user.
        display_name: Human-readable name for UI.
        permissions: List of permission strings for authorization.
        preferences: User preferences (date format, locale, etc.).
    """
    user_id: str = Field(description="Unique identifier for the user.")
    display_name: str = Field(default="", description="Human-readable name.")
    permissions: list[str] = Field(
        default_factory=list,
        description="Permission strings for authorization checks.",
    )
    preferences: dict[str, str] = Field(
        default_factory=dict,
        description="User preferences like locale, date_format.",
    )
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        return permission in self.permissions


class ContextState(ConversationState):
    """Adds thread and user context to conversation state.
    
    These fields are typically:
        - Set once when workflow starts
        - Read-only during workflow execution
        - Used for authorization, audit logging, personalization
    
    Attributes:
        thread_id: Unique identifier for this conversation thread.
                   Used by LangGraph checkpointer for persistence.
        user_context: Information about the authenticated user.
    """
    thread_id: str = Field(
        default="",
        description="Unique conversation thread ID for checkpointing.",
    )
    user_context: UserContext | None = Field(
        default=None,
        description="Authenticated user context.",
    )
```

**Why this layer exists**:

- `thread_id` is required for LangGraph checkpointing/persistence
- User context enables authorization checks in nodes
- Separating this from workflow logic keeps auth concerns isolated

---

## Layer 3: WorkflowState (Framework)

**Purpose**: Generic orchestration - status tracking, errors, confirmations.

**Location**: `src/agentic_app/workflows/core/state.py`

```python
from enum import StrEnum
from pydantic import Field

class WorkflowStatus(StrEnum):
    """Universal workflow execution status.
    
    These statuses apply to ANY workflow, not just Capital Call.
    """
    IN_PROGRESS = "in_progress"
    """Workflow is actively processing."""
    
    AWAITING_INPUT = "awaiting_input"
    """Waiting for user to provide information."""
    
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    """Waiting for user to confirm an action (human-in-the-loop)."""
    
    COMPLETED = "completed"
    """Workflow finished successfully."""
    
    FAILED = "failed"
    """Workflow failed with an error."""
    
    CANCELLED = "cancelled"
    """User cancelled the workflow."""


class WorkflowState(ContextState):
    """Adds generic workflow orchestration capabilities.
    
    This layer handles the "how" of workflow execution without
    knowing the "what" (domain-specific logic).
    
    Attributes:
        status: Current execution status.
        current_step: Name of the current/last executed node.
        error: Error message if status is FAILED.
        pending_confirmation: Description of action awaiting confirmation.
        step_history: Ordered list of visited nodes (for debugging/audit).
    """
    status: WorkflowStatus = Field(
        default=WorkflowStatus.IN_PROGRESS,
        description="Current workflow execution status.",
    )
    current_step: str = Field(
        default="",
        description="Name of the current or last executed node.",
    )
    error: str | None = Field(
        default=None,
        description="Error message when status is FAILED.",
    )
    pending_confirmation: str | None = Field(
        default=None,
        description="What action is awaiting user confirmation.",
    )
    step_history: list[str] = Field(
        default_factory=list,
        description="Ordered list of visited node names for audit.",
    )
```

**Why this layer exists**:

- Status tracking is universal across all workflows
- Error handling pattern is consistent
- `pending_confirmation` works with LangGraph `interrupt()` for HITL
- `step_history` enables debugging and audit trails

---

## Layer 4: Domain State (Business-Specific)

**Purpose**: Capital Call specific data and selection state.

### Domain Models

**Location**: `src/agentic_app/models/domain/capital_call.py`

```python
from decimal import Decimal
from datetime import date
from enum import StrEnum
from pydantic import BaseModel, Field

class DocumentStatus(StrEnum):
    """Capital Call document lifecycle status."""
    DRAFT = "draft"
    CREATED = "created"
    SUBMITTED = "submitted"
    POSTED = "posted"
    REJECTED = "rejected"


class GLAccount(BaseModel):
    """General Ledger account for capital call allocation.
    
    Represents a G/L account selected for the capital call,
    along with the allocated amount for that account.
    """
    code: str = Field(description="G/L account code.")
    name: str = Field(description="G/L account name.")
    allocated_amount: Decimal | None = Field(
        default=None,
        description="Amount allocated to this account.",
    )


class Investor(BaseModel):
    """Investor in a fund with commitment details.
    
    Read-only reference data loaded from API.
    """
    id: str = Field(description="Investor unique identifier.")
    name: str = Field(description="Investor name.")
    commitment: Decimal = Field(description="Total commitment amount.")
    called_amount: Decimal = Field(
        default=Decimal("0"),
        description="Amount already called.",
    )
    
    @property
    def remaining_commitment(self) -> Decimal:
        """Calculate uncalled commitment."""
        return self.commitment - self.called_amount


class CapitalCallData(BaseModel):
    """Pure domain data for a Capital Call document.
    
    This is the business entity being constructed through
    the conversational workflow. It is COMPOSED into the
    workflow state, not inherited.
    
    Design Decision: This model knows nothing about workflow,
    messages, or UI. It's pure business domain.
    """
    # === Fund Selection ===
    fund_id: str | None = Field(
        default=None,
        description="Selected fund identifier.",
    )
    fund_name: str | None = Field(
        default=None,
        description="Selected fund display name.",
    )
    
    # === Call Details ===
    amount: Decimal | None = Field(
        default=None,
        description="Capital call amount.",
    )
    submit_date: date | None = Field(
        default=None,
        description="Document submission date.",
    )
    posting_date: date | None = Field(
        default=None,
        description="Document posting date.",
    )
    
    # === G/L Accounts ===
    gl_accounts: list[GLAccount] = Field(
        default_factory=list,
        description="Selected G/L accounts with allocations.",
    )
    
    # === Document Lifecycle (set by system) ===
    document_id: str | None = Field(
        default=None,
        description="Created document ID from accounting system.",
    )
    document_status: DocumentStatus | None = Field(
        default=None,
        description="Current document status.",
    )
    
    # === Validation Methods ===
    def missing_fields(self) -> list[str]:
        """Return list of required fields that are not yet set."""
        missing = []
        if not self.fund_id:
            missing.append("fund")
        if not self.amount:
            missing.append("amount")
        if not self.submit_date:
            missing.append("submit_date")
        if not self.posting_date:
            missing.append("posting_date")
        if not self.gl_accounts:
            missing.append("gl_accounts")
        return missing
    
    def is_ready_for_creation(self) -> bool:
        """Check if all required fields are collected."""
        return len(self.missing_fields()) == 0
    
    def total_allocated(self) -> Decimal:
        """Sum of all G/L account allocations."""
        return sum(
            (acc.allocated_amount or Decimal("0"))
            for acc in self.gl_accounts
        )
```

### Final Composed State

**Location**: `src/agentic_app/workflows/capital_call/state.py`

```python
from pydantic import Field

from agentic_app.models import Fund, ScoredCandidate
from agentic_app.models.domain.capital_call import (
    CapitalCallData,
    GLAccount,
    Investor,
)
from agentic_app.workflows.core.state import WorkflowState


class CapitalCallState(WorkflowState):
    """Complete state for the Capital Call workflow.
    
    Inherits (bottom to top):
        From MessagesState:
            - messages: list[AnyMessage] with add_messages reducer
        From ConversationState:
            - last_decision: LLMDecision | None
        From ContextState:
            - thread_id: str
            - user_context: UserContext | None
        From WorkflowState:
            - status: WorkflowStatus
            - current_step: str
            - error: str | None
            - pending_confirmation: str | None
            - step_history: list[str]
    
    Adds (this layer):
        - data: The Capital Call being constructed
        - fund_candidates: For fund selection UI
        - available_accounts: G/L accounts from API
        - investors: Fund investors (read-only display)
    """
    
    # === Domain Data (composed, not flattened) ===
    data: CapitalCallData = Field(
        default_factory=CapitalCallData,
        description="The Capital Call document being constructed.",
    )
    
    # === Selection State ===
    fund_candidates: list[ScoredCandidate[Fund]] = Field(
        default_factory=list,
        description="Fund search results for user selection.",
    )
    
    # === Reference Data (loaded from API) ===
    available_accounts: list[GLAccount] = Field(
        default_factory=list,
        description="Available G/L accounts for selection.",
    )
    investors: list[Investor] = Field(
        default_factory=list,
        description="Investors in selected fund (read-only display).",
    )
```

---

## File Structure

```
src/agentic_app/
├── models/
│   ├── core/
│   │   ├── decision.py          # LLMDecision, LLMDecisionMeta (existing)
│   │   └── enums.py             # Add WorkflowStatus, DocumentStatus
│   │
│   ├── domain/
│   │   ├── fund.py              # Fund, FundQuery (existing)
│   │   ├── movie.py             # Movie, MovieQuery (existing)
│   │   └── capital_call.py      # NEW: CapitalCallData, GLAccount, Investor
│   │
│   └── payloads/                # Existing - reuse as-is
│       ├── extraction.py
│       ├── selection.py
│       └── conversation.py
│
├── workflows/
│   ├── core/                    # NEW: Framework base states
│   │   ├── __init__.py
│   │   └── state.py             # ConversationState, ContextState, WorkflowState
│   │
│   ├── capital_call/
│   │   ├── __init__.py
│   │   ├── architecture.md      # THIS DOCUMENT
│   │   ├── state.py             # CapitalCallState
│   │   ├── nodes.py             # Node functions
│   │   ├── routing.py           # Conditional edge functions
│   │   └── graph.py             # StateGraph definition
│   │
│   └── movie/                   # Can refactor to use core/ later
│       └── ...
│
└── services/
    ├── movie_service.py         # Existing
    └── capital_call_service.py  # NEW: API calls for capital call
```

---

## Node Design

### Node Responsibilities

Each node:

1. Reads from state (type-safe via Pydantic)
2. Performs one logical operation
3. Returns partial state update (dict)
4. Updates only fields it owns

```python
# Example node structure
def node_name(state: CapitalCallState) -> dict:
    """Node description.
    
    Reads: state.field1, state.field2
    Updates: field3, field4
    """
    # 1. Read what you need
    value = state.data.fund_id
    
    # 2. Do work
    result = process(value)
    
    # 3. Return partial update
    return {
        "data": CapitalCallData(
            **state.data.model_dump(),
            field_to_update=result,
        ),
        "current_step": "node_name",
    }
```

### Planned Nodes

| Node | Purpose | Updates |
|------|---------|---------|
| `parse_intent` | Classify user message, extract data | `last_decision` |
| `search_fund` | Search funds via API | `fund_candidates` |
| `confirm_fund` | Resolve fund selection | `data.fund_id`, `data.fund_name` |
| `collect_details` | Extract amount, dates | `data.amount`, `data.submit_date`, `data.posting_date` |
| `load_accounts` | Fetch G/L accounts from API | `available_accounts` |
| `select_accounts` | User selects accounts | `data.gl_accounts` |
| `load_investors` | Fetch fund investors | `investors` |
| `review` | Show summary, await confirmation | `pending_confirmation`, `status` |
| `create_document` | API call to create | `data.document_id`, `data.document_status` |
| `submit_document` | API call to submit | `data.document_status` |
| `post_document` | API call to post | `data.document_status` |
| `handle_error` | Set error state | `error`, `status` |

---

## Graph Flow

```
                    ┌─────────────────┐
                    │     START       │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
            ┌───────│  parse_intent   │───────┐
            │       └────────┬────────┘       │
            │                │                │
     fund_query       has_details       confirmation
            │                │                │
    ┌───────▼───────┐ ┌──────▼──────┐ ┌──────▼──────┐
    │  search_fund  │ │collect_details│ │   review   │
    └───────┬───────┘ └──────┬──────┘ └──────┬──────┘
            │                │                │
    ┌───────▼───────┐        │        ┌──────▼──────┐
    │ confirm_fund  │        │        │create_document│
    └───────┬───────┘        │        └──────┬──────┘
            │                │                │
            └────────────────┼────────────────┤
                             │                │
                    ┌────────▼────────┐       │
                    │  load_accounts  │       │
                    └────────┬────────┘       │
                             │                │
                    ┌────────▼────────┐       │
                    │ select_accounts │       │
                    └────────┬────────┘       │
                             │                │
                    ┌────────▼────────┐       │
                    │ load_investors  │       │
                    └────────┬────────┘       │
                             │                │
                    ┌────────▼────────┐       │
                    │     review      │◄──────┘
                    └────────┬────────┘
                             │ interrupt()
                    ┌────────▼────────┐
                    │create_document  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │submit_document  │
                    └────────┬────────┘
                             │ interrupt()
                    ┌────────▼────────┐
                    │ post_document   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │      END        │
                    └─────────────────┘
```

---

## Human-in-the-Loop Pattern

Using LangGraph's native `interrupt()` for confirmations:

```python
from langgraph.types import interrupt

def review_node(state: CapitalCallState) -> dict:
    """Present summary and await user confirmation."""
    
    # Build summary for UI
    summary = {
        "fund": state.data.fund_name,
        "amount": str(state.data.amount),
        "submit_date": str(state.data.submit_date),
        "posting_date": str(state.data.posting_date),
        "accounts": [acc.model_dump() for acc in state.data.gl_accounts],
        "investors": [inv.model_dump() for inv in state.investors],
    }
    
    # Interrupt for human confirmation
    # Returns when user calls Command(resume=True/False)
    approved = interrupt({
        "action": "confirm_capital_call",
        "summary": summary,
    })
    
    if not approved:
        return {
            "status": WorkflowStatus.AWAITING_INPUT,
            "pending_confirmation": None,
        }
    
    return {
        "status": WorkflowStatus.IN_PROGRESS,
        "pending_confirmation": None,
        "current_step": "review_approved",
    }
```

---

## Service Layer

**Location**: `src/agentic_app/services/capital_call_service.py`

```python
from decimal import Decimal
from agentic_app.models import Fund, ScoredCandidate
from agentic_app.models.domain.capital_call import (
    CapitalCallData,
    GLAccount,
    Investor,
)

class CapitalCallService:
    """Service for Capital Call API operations.
    
    Encapsulates all external API calls related to capital calls.
    Nodes use this service; they don't make API calls directly.
    """
    
    async def search_funds(self, query: str) -> list[ScoredCandidate[Fund]]:
        """Search funds matching query."""
        ...
    
    async def get_gl_accounts(self, fund_id: str) -> list[GLAccount]:
        """Get available G/L accounts for a fund."""
        ...
    
    async def get_investors(self, fund_id: str) -> list[Investor]:
        """Get investors for a fund."""
        ...
    
    async def create_document(self, data: CapitalCallData) -> str:
        """Create capital call document. Returns document_id."""
        ...
    
    async def submit_document(self, document_id: str) -> bool:
        """Submit document for approval."""
        ...
    
    async def post_document(self, document_id: str) -> bool:
        """Post submitted document."""
        ...
```

---

## Summary: Concern Separation

| Layer | Location | Changes When | Reusable? |
|-------|----------|--------------|-----------|
| MessagesState | LangGraph | LangGraph updates | Framework |
| ConversationState | `workflows/core/state.py` | LLM patterns change | All workflows |
| ContextState | `workflows/core/state.py` | Auth/session changes | All workflows |
| WorkflowState | `workflows/core/state.py` | Orchestration patterns | All workflows |
| CapitalCallData | `models/domain/capital_call.py` | Business rules | Capital Call only |
| CapitalCallState | `workflows/capital_call/state.py` | This workflow | Capital Call only |

---

## Next Steps

1. Create `workflows/core/state.py` with base state classes
2. Create `models/domain/capital_call.py` with domain models
3. Update `models/core/enums.py` with new enums
4. Implement `workflows/capital_call/state.py`
5. Implement nodes and graph
