"""Business Central OData API Settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BusinessCentralODataApiSettings(BaseSettings):
    """Business Central OData API Settings (reads from .env)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    odata_base_url: str = Field(..., alias="BUSINESS_CENTRAL_ODATA_BASE_URL")
    odata_username: str = Field(..., alias="BUSINESS_CENTRAL_ODATA_USERNAME")
    odata_password: str = Field(..., alias="BUSINESS_CENTRAL_ODATA_PASSWORD")
    odata_tenant: str = Field(..., alias="BUSINESS_CENTRAL_ODATA_TENANT")
