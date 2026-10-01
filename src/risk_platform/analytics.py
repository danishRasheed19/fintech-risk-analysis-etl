import pandas as pd
import numpy as np
from src.risk_platform.queries import fetch_overview_data,fetch_risk_distributions,fetch_transaction_analysis,fetch_account_analysis,fetch_customer_analysis

def get_risk_analytics():

    overview_data = fetch_overview_data()

    risk_distribution = fetch_risk_distributions()

    transaction_analysis = fetch_transaction_analysis()

    account_analysis = fetch_account_analysis()

    customer_analysis = fetch_customer_analysis()

    return {
        "overview_data": overview_data,

        "risk_distribution": {
            key: value.to_dict(orient="records")
            for key, value in risk_distribution.items()
        },

        "transaction_analysis": {
            key: value.to_dict(orient="records")
            for key, value in transaction_analysis.items()
        },

        "account_analysis": {
            key: value.to_dict(orient="records")
            for key, value in account_analysis.items()
        },

        "customer_analysis": {
            key: value.to_dict(orient="records")
            for key, value in customer_analysis.items()
        }
    }

def get_risk_overview():
    overview_data = fetch_overview_data()
    return overview_data

def get_risk_distribution():
    return fetch_risk_distributions()

def get_transaction_analysis():
    return fetch_transaction_analysis()

def get_account_analysis():
    return fetch_account_analysis()

def get_customer_analysis():
    return fetch_customer_analysis()
def main():
    get_risk_analytics()

if __name__ == "__main__":
    main()