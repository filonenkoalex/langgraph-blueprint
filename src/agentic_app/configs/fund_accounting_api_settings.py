"""Settings for the Fund Accounting API."""

from pydantic import Field
from pydantic_settings import BaseSettings


class FundAccountingApiSettings(BaseSettings):
    """Settings for the Fund Accounting API."""

    base_url: str = Field(..., alias="FUND_ACCOUNTING_API_BASE_URL")
    client_id: str = Field(..., alias="FUND_ACCOUNTING_API_CLIENT_ID")
    client_secret: str = Field(..., alias="FUND_ACCOUNTING_API_CLIENT_SECRET")
    company_name: str = Field(..., alias="FUND_ACCOUNTING_API_COMPANY_NAME")
    tenant_name: str = Field(..., alias="FUND_ACCOUNTING_API_TENANT_NAME")
