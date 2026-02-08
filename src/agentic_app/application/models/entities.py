"""Application-level entity models.

Simplified representations of domain entities used by application services.
These decouple callers from infrastructure-specific response DTOs.
"""

from pydantic import BaseModel


class Fund(BaseModel):
    """Fund entity."""

    id: str
    name: str
    currency_code: str


class Investor(BaseModel):
    """Investor entity."""

    id: str
    name: str
    currency_code: str
