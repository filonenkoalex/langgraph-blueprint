"""Domain entity models (funds, investors, securities, etc.)."""

from pydantic import BaseModel, ConfigDict, Field


class FundResponse(BaseModel):
    """Fund entity from the Fund Accounting API."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., alias="code", description="Unique fund identifier")
    type: str = Field(..., description="Fund type")
    name: str = Field(..., description="Fund name")
    currency_code: str = Field(..., alias="currencyCode", description="Currency code")
    company_posting_group: str = Field(..., alias="companyPostingGroup")
    group_code: str = Field(..., alias="groupCode")
    investor_no: str = Field(..., alias="investorNo")
    client_code: str = Field(..., alias="clientCode")
    jurisdiction_code: str = Field(..., alias="jurisdictionCode")
    legacy_code: str = Field(..., alias="legacyCode")
    active: bool = Field(..., description="Whether the fund is active")
    acy_code: str = Field(..., alias="acyCode")
    application_method: str = Field(..., alias="applicationMethod")
    exchange_rate_source_code: str = Field(..., alias="exchangeRateSourceCode")
    preferred_bank_account: str = Field(..., alias="preferredBankAccount")
    inv_allocation_rule_group: str = Field(..., alias="invAllocationRuleGroup")
    use_commitment_ledger: bool = Field(..., alias="useCommitmentLedger")
    use_investment_account_on_docs: bool = Field(
        ..., alias="useInvestmentAccountOnDocs"
    )
    external_id: str = Field(..., alias="externalId")


class InvestorResponse(BaseModel):
    """Investor entity from the Fund Accounting API."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., alias="no", description="Unique investor identifier")
    name: str = Field(..., description="Investor name")
    type: str = Field(..., description="Investor type")
    group: str = Field(..., description="Investor group")
    currency_code: str = Field(..., alias="currencyCode", description="Currency code")
    posting_group: str = Field(..., alias="postingGroup")


class GLAccountResponse(BaseModel):
    """G/L Account entity from the Fund Accounting API."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., alias="no", description="Unique G/L account identifier")
    name: str = Field(..., description="Account name")
    account_type: str = Field(..., alias="accountType", description="Account type")


class SecurityResponse(BaseModel):
    """Security entity from the Fund Accounting API."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., alias="no", description="Unique security identifier")
    name: str = Field(..., alias="description", description="Security name")
    issuer_code: str = Field(..., alias="issuerCode")
    issuer_company_name: str = Field(..., alias="secIssuerCompanyName")
    security_type: str = Field(..., alias="securityType")
    currency_code: str = Field(..., alias="currencyCode")
    external_id: str = Field(..., alias="externalId")
