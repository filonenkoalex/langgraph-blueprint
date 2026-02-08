"""
Fund Accounting service exceptions.

Exception hierarchy:
    FundAccountingError (base)
    ├── AuthenticationError
    ├── TransportError
    │   └── TransportTimeoutError
    └── TaskError
        ├── TaskFailedError
        └── TaskTimeoutError
"""


class FundAccountingError(Exception):
    """Base exception for all Fund Accounting service errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class AuthenticationError(FundAccountingError):
    """Raised when authentication fails."""


class TransportError(FundAccountingError):
    """Raised when HTTP transport fails."""


class TransportTimeoutError(TransportError):
    """Raised when HTTP request times out."""


class TaskError(FundAccountingError):
    """Base exception for background task errors."""

    def __init__(self, message: str, *, task_id: str) -> None:
        super().__init__(message)
        self.task_id = task_id


class TaskFailedError(TaskError):
    """Raised when a background task fails."""

    def __init__(
        self,
        task_id: str,
        *,
        status: str,
        messages: list[str] | None = None,
    ) -> None:
        super().__init__(
            f"Task {task_id} failed with status: {status}", task_id=task_id
        )
        self.status = status
        self.messages = messages or []


class TaskTimeoutError(TaskError):
    """Raised when task polling exceeds maximum attempts."""

    def __init__(self, task_id: str, *, attempts: int) -> None:
        super().__init__(
            f"Task {task_id} timed out after {attempts} attempts",
            task_id=task_id,
        )
        self.attempts = attempts
