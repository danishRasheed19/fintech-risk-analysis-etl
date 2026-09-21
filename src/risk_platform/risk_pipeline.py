import pandas as pd
from src.risk_platform.queries import fetch_transaction_risk_data
from src.risk_platform.features import build_transaction_features

def main():
    print("STARTING RISK PIPELINE")
    df = fetch_transaction_risk_data()
    df = build_transaction_features(df)
    print(df[[
    "transaction_id",
    "risk_category",
    "merchant_risk_score",
    "currency_mismatch",
    "country_mismatch",
    "is_reversed",
    "is_suspended_account",
    "is_closed_account",
    "is_weekend",
    "transaction_hour"
    ]].head(10))
    
if __name__ == "__main__":
    main()
