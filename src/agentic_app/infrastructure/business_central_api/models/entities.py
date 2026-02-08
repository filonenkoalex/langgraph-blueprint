"""Domain entity models (funds, investors)."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class FundResponse(BaseModel):
    """Fund entity from the Business Central OData API."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., alias="code", description="Unique id of the fund.")
    name: str = Field(..., description="The name of the fund.")
    company_posting_group: str = Field(
        ...,
        alias="companyPostingGroup",
        description="The company posting group of the fund.",
    )
    currency_code: str = Field(
        ..., alias="currencyCode", description="The currency code of the fund."
    )
    is_public: bool = Field(
        ..., alias="public", description="Whether the fund is public."
    )
    listed_date: date | None = Field(
        None, alias="listedDate", description="The listed date of the fund."
    )


class InvestorResponse(BaseModel):
    """Investor entity from the Business Central OData API."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., alias="no", description="Unique id of the investor.")
    name: str = Field(..., description="The name of the investor.")
    currency_code: str = Field(
        ..., alias="currencyCode", description="The currency code of the investor."
    )
