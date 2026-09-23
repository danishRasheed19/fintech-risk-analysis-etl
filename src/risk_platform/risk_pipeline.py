import pandas as pd
from src.risk_platform.queries import fetch_transaction_risk_data
from src.risk_platform.features import build_transaction_features
from src.risk_platform.scoring import calculate_risk_score
from src.risk_platform.profiling import build_account_profiles,build_customer_profiles

def main():
    print("STARTING RISK PIPELINE")
    transaction_df = fetch_transaction_risk_data()
    transaction_df = build_transaction_features(transaction_df)
    transaction_df = calculate_risk_score(transaction_df)
    account_profiles = build_account_profiles(transaction_df)
    customer_profiles = build_customer_profiles(account_profiles,transaction_df)
    print(customer_profiles[customer_profiles["customer_risk_level"] == "CRITICAL"].head())

if __name__ == "__main__":
    main()
