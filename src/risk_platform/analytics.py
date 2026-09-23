import pandas as pd
import numpy as np
from src.risk_platform.queries import fetch_overview_data

def perform_analytics():
    overview_data = get_risk_overview()
    print(overview_data)

def get_risk_overview():
    overview_data = fetch_overview_data()
    return overview_data

def main():
    perform_analytics()

if __name__ == "__main__":
    main()