import pandas as pd
from src.risk_platform.queries import fetch_transaction_risk_data

def main():
    print("STARTING RISK PIPELINE")
    risk_df = fetch_transaction_risk_data()
    print(risk_df)
    
if __name__ == "__main__":
    main()
