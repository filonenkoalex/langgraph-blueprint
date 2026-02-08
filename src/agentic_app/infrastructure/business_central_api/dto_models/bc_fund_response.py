"""Fund model."""

from datetime import date

from pydantic import BaseModel, Field


class FundResponse(BaseModel):
    """Fund model."""

    id: str = Field(..., alias="code", description="Unique id of the fund.")
    name: str = Field(..., description="The name of the fund.")
    companyPostingGroup: str = Field(
        ..., description="The company posting group of the fund."
    )
    currencyCode: str = Field(..., description="The currency code of the fund.")
    is_public: bool = Field(
        ..., alias="public", description="Whether the fund is public."
    )
    listedDate: date | None = Field(None, description="The listed date of the fund.")
