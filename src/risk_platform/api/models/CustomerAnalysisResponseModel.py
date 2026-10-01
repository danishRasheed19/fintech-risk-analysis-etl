from pydantic import BaseModel


class RiskiestCustomer(BaseModel):
    customer_id: str
    account_count: int
    customer_risk_level: str
    critical_accounts: int
    high_risk_accounts: int
    risky_account_ratio: float
    average_account_risk: float
    max_account_risk_score: int
    total_transaction_amount: float


class RiskyCustomerByAmount(BaseModel):
    customer_id: str
    customer_risk_level: str
    account_count: int
    transaction_count: int
    total_transaction_amount: float
    average_account_risk: float
    critical_accounts: int
    high_risk_accounts: int


class RiskyCustomerByCriticalCount(BaseModel):
    customer_id: str
    customer_risk_level: str
    account_count: int
    transaction_count: int
    total_transaction_amount: float
    average_account_risk: float
    max_account_risk_score: int
    critical_accounts: int
    high_risk_accounts: int
    risky_account_ratio: float


class CustomerRiskResponse(BaseModel):
    riskiest_customers: list[RiskiestCustomer]
    risky_customer_by_amount: list[RiskyCustomerByAmount]
    risky_customer_by_critical_count: list[RiskyCustomerByCriticalCount]