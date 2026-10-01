from pydantic import BaseModel


class TransactionDistribution(BaseModel):
    risk_level: str
    count: int


class AccountDistribution(BaseModel):
    account_risk_level: str
    count: int


class CustomerDistribution(BaseModel):
    customer_risk_level: str
    count: int


class RiskDistributionResponse(BaseModel):
    transaction_distribution: list[TransactionDistribution]
    account_distribution: list[AccountDistribution]
    customer_distribution: list[CustomerDistribution]