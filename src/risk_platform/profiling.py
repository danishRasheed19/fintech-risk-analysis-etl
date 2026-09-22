import pandas as pd

def build_account_profiles(df):
    account_profiles = (
        df.groupby("account_id")
        .agg(
            transaction_count = ("transaction_id","count"),
            total_transaction_amount = ("amount","sum"),
            average_transaction_amount = ("amount","mean"),
            average_risk_score = ("risk_score","mean"),
            max_risk_score = ("risk_score","max"),
            high_risk_count = (
                "risk_level",
                lambda x : (x == "HIGH").sum()
            ),
            critical_risk_count = (
                "risk_level",
                lambda x : (x == "CRITICAL").sum()
            )
        ).reset_index()
    )
    
    account_profiles["risk_transaction_ratio"] = (
        (account_profiles["high_risk_count"] + account_profiles["critical_risk_count"]) / (account_profiles["transaction_count"])
    )
    
    return account_profiles

