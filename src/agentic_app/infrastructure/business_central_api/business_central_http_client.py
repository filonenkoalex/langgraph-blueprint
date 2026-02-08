"""Business Central HTTP Client."""

import httpx

from .dto_models import (
    FundResponse,
    InvestorResponse,
    ODataResponse,
)


class BusinessCentralHttpClient:
    """Business Central HTTP Client."""

    MAX_TOP = 10000

    def __init__(
        self,
        odata_base_url: str,
        odata_tenant: str,
        odata_username: str,
        odata_password: str,
    ) -> None:
        """Initialize the client."""
        self._odata_tenant = odata_tenant
        self._client = httpx.AsyncClient(
            base_url=odata_base_url,
            auth=httpx.DigestAuth(odata_username, odata_password),
            headers={"Accept": "application/json", "algorithm": "MD5-SESS"},
            timeout=30.0,
        )

    async def get_funds(self, top: int = MAX_TOP) -> ODataResponse[FundResponse]:
        """Retrieve investment companies filtered by *type* (default: "Fund")."""
        params = {
            "tenant": self._odata_tenant,
            "$top": str(top),
            "$filter": "type eq 'Fund'",
            "$select": "code,name,companyPostingGroup,currencyCode,public,listedDate",
        }
        raw = await self._client.get("/investmentCompanies", params=params)

        response = ODataResponse[FundResponse].model_validate(raw.json())

        return response

    async def get_investors(
        self, top: int = MAX_TOP
    ) -> ODataResponse[InvestorResponse]:
        """Retrieve investors filtered by *type* (default: "Investor")."""
        params = {
            "tenant": self._odata_tenant,
            "$top": str(top),
            "$filter": "type eq 'LP'",
            "$select": "no,name,currencyCode",
        }
        raw = await self._client.get("/investors", params=params)

        response = ODataResponse[InvestorResponse].model_validate(raw.json())

        return response

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()
