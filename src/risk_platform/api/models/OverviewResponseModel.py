from pydantic import BaseModel


class OverviewResponse(BaseModel):
    total_transaction_count: int
    total_transaction_amount: float
    total_customer_count: int
    total_account_count: int
    high_risk_transactions: int
    high_risk_customers: int
    high_risk_accounts: int
    critical_risk_transactions: int
    critical_risk_customers: int
    critical_risk_accounts: int