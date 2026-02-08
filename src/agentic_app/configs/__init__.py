"""Application configuration settings (bridge from .env to infrastructure configs)."""

from .business_central_odata_api_settings import BusinessCentralODataApiSettings
from .fund_accounting_api_settings import FundAccountingApiSettings

__all__ = [
    "BusinessCentralODataApiSettings",
    "FundAccountingApiSettings",
]
