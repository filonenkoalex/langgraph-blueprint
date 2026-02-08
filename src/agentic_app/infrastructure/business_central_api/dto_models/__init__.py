"""Business Central API contracts."""

from .bc_fund_response import FundResponse
from .bc_investor_response import InvestorResponse
from .bc_odata_response import ODataResponse

__all__ = [
    "FundResponse",
    "InvestorResponse",
    "ODataResponse",
]
