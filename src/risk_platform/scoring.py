import pandas as pd

MERCHANT_SCORE_MAPPING = {
    0: 1, #small penalty for unkown merchant
    1: 0,
    2: 2,
    3: 4
}

def calculate_base_score(df):
    df = df.copy()
    
    df["risk_score"] = (
        (df["merchant_risk_score"].map(MERCHANT_SCORE_MAPPING))
        + df["country_mismatch"] * 3
        + df["is_reversed"] * 2
        + df["is_suspended_account"] * 5
        + df["is_closed_account"] * 5
        + df["is_weekend"] * 1
        + df["is_night"] * 2
    )
    
    return df