"""Investor model."""

from pydantic import BaseModel, Field


class InvestorResponse(BaseModel):
    """Investor model."""

    id: str = Field(..., alias="no", description="Unique id of the investor.")
    name: str = Field(..., description="The name of the investor.")
    currencyCode: str = Field(..., description="The currency code of the investor.")
