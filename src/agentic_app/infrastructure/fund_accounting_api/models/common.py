"""Common shared models for pagination and task handling."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(StrEnum):
    """Background task status values."""

    PENDING = "Pending"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"
    ERROR = "Error"


class PaginatedResponse[T](BaseModel):
    """Generic paginated response wrapper."""

    model_config = ConfigDict(populate_by_name=True)

    items: list[T] = Field(default_factory=list)
    total_count: int = Field(alias="totalCount")
    offset: int
    limit: int
    next_page: str | None = Field(default=None, alias="nextPage")


class BackgroundTaskResponse(BaseModel):
    """Response from endpoints that create background tasks."""

    model_config = ConfigDict(populate_by_name=True)

    task_id: str = Field(alias="taskId")


class TaskResponse(BaseModel):
    """Task status polling response."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    status: TaskStatus
    messages: list[str] = Field(default_factory=list)
    correlation_id: str = Field(alias="correlationId")
    data: dict[str, Any] | None = None
