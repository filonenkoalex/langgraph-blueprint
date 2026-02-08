"""Business Central API models."""

from .common import ODataResponse
from .models import FundResponse, InvestorResponse

__all__ = [
    "FundResponse",
    "InvestorResponse",
    "ODataResponse",
]
