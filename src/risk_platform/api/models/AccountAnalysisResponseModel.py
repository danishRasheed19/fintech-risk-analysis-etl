from pydantic import BaseModel


class RiskiestAccount(BaseModel):
    account_id: str
    account_risk_level: str
    average_risk_score: float
    max_risk_score: int
    risk_transaction_ratio: float
    high_risk_count: int
    critical_risk_count: int
    transaction_count: int
    total_transaction_amount: float


class RiskiestAccountByAmount(BaseModel):
    account_id: str
    transaction_count: int
    total_transaction_amount: float
    average_risk_score: float
    risk_transaction_ratio: float
    account_risk_level: str
    critical_risk_count: int
    high_risk_count: int


class AccountRiskResponse(BaseModel):
    riskiest_accounts: list[RiskiestAccount]
    riskiest_accounts_by_amount: list[RiskiestAccountByAmount]