import pandas as pd
import numpy as np
from src.risk_platform.queries import fetch_overview_data,fetch_risk_distributions,fetch_transaction_analysis,fetch_account_analysis,fetch_customer_analysis

def perform_analytics():
    overview_data = get_risk_overview()
    risk_distribution = get_risk_distribution()
    transation_analysis = get_transaction_analysis()
    account_analysis = get_account_analysis()
    customer_analysis = get_customer_analysis()
    print(customer_analysis)

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
    perform_analytics()

if __name__ == "__main__":
    main()