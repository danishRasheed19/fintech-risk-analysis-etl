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

def calculate_interaction_score(df):
    df = df.copy()
    
    df["interaction_score"] = 0
    
    #suspended account and country mismatch
    df.loc[
        (df["country_mismatch"] == 1) & (df["is_suspended_account"] == 1), "interaction_score"
    ] += 4
    
    #closed account and country mismatch
    df.loc[
        (df["country_mismatch"] == 1) & (df["is_closed_account"] == 1), "interaction_score"
    ] +=4
    
    #high risk merchant and country mismatch
    df.loc[
        (df["country_mismatch"] == 1) & (df["merchant_risk_score"] == 3) , "interaction_score"
    ] += 3
    
    #High risk merchant and reversed transaction
    df.loc[
        (df["merchant_risk_score"] == 3) & (df["is_reversed"] == 1), "interaction_score"
    ] += 2
    
    # Suspended/closed account and reversed transaction
    df.loc[
        (
            (df["is_suspended_account"] == 1) |
            (df["is_closed_account"] == 1)
        ) &
        (df["is_reversed"] == 1),
        "interaction_score"
    ] += 3

    # Country mismatch and night transaction
    df.loc[
        (df["country_mismatch"] == 1) &
        (df["is_night"] == 1),
        "interaction_score"
    ] += 2

    # Add interaction points to base score
    df["risk_score"] += df["interaction_score"]

    return df

def calculate_risk_score(df):
    df = df.copy()
    
    df = calculate_base_score(df)
    df = calculate_interaction_score(df)
    return df