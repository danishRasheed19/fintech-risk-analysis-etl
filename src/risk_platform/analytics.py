import pandas as pd
import numpy as np
from src.risk_platform.queries import fetch_overview_data,fetch_risk_distributions

def perform_analytics():
    overview_data = get_risk_overview()
    risk_distribution = get_risk_distribution()
    print(risk_distribution["customer_distribution"]["count"])

def get_risk_overview():
    overview_data = fetch_overview_data()
    return overview_data

def get_risk_distribution():
    return fetch_risk_distributions()

def main():
    perform_analytics()

if __name__ == "__main__":
    main()