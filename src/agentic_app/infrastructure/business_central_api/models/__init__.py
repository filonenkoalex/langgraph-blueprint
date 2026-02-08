"""Business Central API models."""

from .common import ODataResponse
from .entities import FundResponse, InvestorResponse

__all__ = [
    "FundResponse",
    "InvestorResponse",
    "ODataResponse",
]
