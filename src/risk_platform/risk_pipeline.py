import pandas as pd
from src.risk_platform.queries import fetch_transaction_risk_data
from src.risk_platform.features import build_transaction_features
from src.risk_platform.scoring import calculate_risk_score

def main():
    print("STARTING RISK PIPELINE")
    df = fetch_transaction_risk_data()
    df = build_transaction_features(df)
    df = calculate_risk_score(df)
    
if __name__ == "__main__":
    main()
