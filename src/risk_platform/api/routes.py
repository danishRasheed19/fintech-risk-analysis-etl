from fastapi import APIRouter

from src.risk_platform.analytics import get_risk_overview,get_risk_distribution,get_account_analysis,get_transaction_analysis,get_customer_analysis
from src.risk_platform.api.models.OverviewResponseModel import OverviewResponse
from src.risk_platform.api.models.RiskDistributionResponseModel import RiskDistributionResponse
from src.risk_platform.api.models.TransactionAnalysisResponseModel import TransactionRiskAnalysisResponse
from src.risk_platform.api.models.AccountAnalysisResponseModel import AccountRiskResponse
from src.risk_platform.api.models.CustomerAnalysisResponseModel import CustomerRiskResponse

router = APIRouter(
    prefix="/api/risk",
    tags=["Risk Analytics"]
)

@router.get("/get_overview",response_model=OverviewResponse)
def risk_analytics():
    return get_risk_overview()

@router.get("/get_risk_distributions",response_model=RiskDistributionResponse)
def risk_analytics():
    return get_risk_distribution()

@router.get("/get_transaction_analysis",response_model= TransactionRiskAnalysisResponse)
def risk_analytics():
    return get_transaction_analysis()

@router.get("/get_account_analysis",response_model = AccountRiskResponse)
def risk_analytics():
    return get_account_analysis()

@router.get("/get_customer_analysis",response_model=CustomerRiskResponse)
def risk_analytics():
    return get_customer_analysis()