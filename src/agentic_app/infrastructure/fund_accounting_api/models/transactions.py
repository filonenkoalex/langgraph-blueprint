"""Transaction request and response models."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TransactionLineItem(BaseModel):
    """Single line item in a transaction."""

    model_config = ConfigDict(populate_by_name=True)

    company_code: str = Field(..., alias="companyCode", description="Fund code")
    description: str = Field(..., description="Transaction description")
    amount_scy: Decimal = Field(
        ..., alias="amountScy", description="Amount in security currency"
    )
    security_external_id: str = Field(..., alias="securityExternalId")
    settlement_date: date = Field(..., alias="settlementDate")
    trade_date: date = Field(..., alias="tradeDate")
    transaction_code: str = Field(
        ..., alias="transactionCode", description="e.g., BUY, SELL"
    )


class TransactionRequest(BaseModel):
    """Request payload for creating a transaction."""

    model_config = ConfigDict(populate_by_name=True)

    transaction_id: str | None = Field(default=None, alias="transactionId")
    integration_code: str = Field(default="API", alias="integrationCode")
    is_auto_submit_and_post: bool = Field(default=True, alias="isAutoSubmitAndPost")
    line_items: list[TransactionLineItem] = Field(..., alias="lineItems")


class TransactionResponse(BaseModel):
    """Response after transaction creation/posting."""

    model_config = ConfigDict(populate_by_name=True)

    transaction_id: str = Field(..., alias="TransactionId")
