"""Business Central OData API Settings."""

from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BusinessCentralODataApiSettings(BaseSettings):
    """Business Central OData API Settings (reads from .env)."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    odata_base_url: str = Field(..., alias="BUSINESS_CENTRAL_ODATA_BASE_URL")
    odata_username: str = Field(..., alias="BUSINESS_CENTRAL_ODATA_USERNAME")
    odata_password: str = Field(..., alias="BUSINESS_CENTRAL_ODATA_PASSWORD")
    odata_tenant: str = Field(..., alias="BUSINESS_CENTRAL_ODATA_TENANT")

    def to_client_kwargs(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        """Return kwargs for BusinessCentralHttpClient constructor."""
        return {
            "odata_base_url": self.odata_base_url,
            "odata_username": self.odata_username,
            "odata_password": self.odata_password,
            "odata_tenant": self.odata_tenant,
        }
