import pandas as pd
from src.risk_platform.queries import fetch_transaction_risk_data
from src.risk_platform.features import build_transaction_features
from src.risk_platform.scoring import calculate_risk_score
from src.risk_platform.profiling import build_account_profiles

def main():
    print("STARTING RISK PIPELINE")
    df = fetch_transaction_risk_data()
    df = build_transaction_features(df)
    df = calculate_risk_score(df)
    account_profiles = build_account_profiles(df)
    
    print(account_profiles)
    
if __name__ == "__main__":
    main()
