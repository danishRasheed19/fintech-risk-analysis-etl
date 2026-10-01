from pydantic import BaseModel


class RiskByCountry(BaseModel):
    transaction_country: str
    country_name: str
    transaction_count: int
    high_risk_count: int
    critical_risk_count: int
    average_risk_score: float


class RiskByMerchantCategory(BaseModel):
    merchant_category: str
    transaction_count: int
    high_risk_count: int
    critical_risk_count: int
    average_risk_score: float


class RiskByTransactionType(BaseModel):
    transaction_type: str
    transaction_count: int
    high_risk_count: int
    critical_risk_count: int
    avg_risk_score: float


class RiskByPaymentMethod(BaseModel):
    payment_method: str
    transaction_count: int
    high_risk_count: int
    critical_risk_count: int
    avg_risk_score: float


class RiskByTime(BaseModel):
    time_period: str
    transaction_count: int
    high_risk_count: int
    critical_risk_count: int
    average_risk_score: float
    risky_transaction_ratio: float


class TransactionRiskAnalysisResponse(BaseModel):
    risk_by_country: list[RiskByCountry]
    risk_by_mercahnt_category: list[RiskByMerchantCategory]
    risk_by_transaction_type: list[RiskByTransactionType]
    risk_by_payment_method: list[RiskByPaymentMethod]
    risk_by_time: list[RiskByTime]