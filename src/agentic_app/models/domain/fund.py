"""Fund domain models for investment fund entities.

Provides models for both resolved fund entities and
extraction queries for fund identification.
"""

from pydantic import BaseModel, Field


class Fund(BaseModel):
    """A resolved investment fund entity.

    Represents a fully identified fund from the system's
    fund master data.

    Attributes:
        id: Unique identifier in the system.
        name: Full name of the fund.
        ticker: Trading ticker symbol.
        isin: International Securities Identification Number.
        currency: Base currency of the fund.
        is_active: Whether the fund is currently active.

    Example:
        ```python
        fund = Fund(
            id="fund_001",
            name="Vanguard Total Stock Market Index Fund",
            ticker="VTI",
            isin="US9229087690",
            currency="USD",
            is_active=True,
        )
        ```
    """

    id: str = Field(
        description="Unique identifier in the system.",
    )
    name: str = Field(
        description="Full name of the fund.",
    )
    ticker: str | None = Field(
        default=None,
        description="Trading ticker symbol.",
    )
    isin: str | None = Field(
        default=None,
        description="International Securities Identification Number.",
    )
    currency: str = Field(
        default="USD",
        description="Base currency of the fund.",
    )
    is_active: bool = Field(
        default=True,
        description="Whether the fund is currently active.",
    )


class FundQuery(BaseModel):
    """Query parameters for fund extraction/search.

    Represents partial fund information extracted from
    user input, used to search for matching funds.

    Attributes:
        name: Partial or full fund name from user input.
        ticker: Ticker symbol if mentioned.
        isin: ISIN code if mentioned.

    Example:
        ```python
        # User said "I want to buy VTI"
        query = FundQuery(ticker="VTI")

        # User said "Vanguard Total Stock fund"
        query = FundQuery(name="Vanguard Total Stock")
        ```
    """

    name: str | None = Field(
        default=None,
        description="Partial or full fund name from user input.",
    )
    ticker: str | None = Field(
        default=None,
        description="Ticker symbol if mentioned by user.",
    )
    isin: str | None = Field(
        default=None,
        description="ISIN code if mentioned by user.",
    )
