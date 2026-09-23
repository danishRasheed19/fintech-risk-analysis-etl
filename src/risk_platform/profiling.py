import pandas as pd
import numpy as np

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
    
    account_profiles = assign_account_risk_profile(account_profiles)
    return account_profiles

def assign_account_risk_profile(df):
    df = df.copy()
    
    conditions = [
    (
        (df["critical_risk_count"] >= 2) |
        (
            (df["risk_transaction_ratio"] >= 0.75) &
            (df["transaction_count"] >= 8)
        ) |
        (
            (df["average_risk_score"] >= 15) &
            (df["transaction_count"] >= 8)
        )
    ),

    (
        (df["critical_risk_count"] >= 1) |
        (
            (df["risk_transaction_ratio"] >= 0.50) &
            (df["transaction_count"] >= 5)
        ) |
        (
            (df["average_risk_score"] >= 10) &
            (df["transaction_count"] >= 5)
        )
    ),

    (
        (
            (df["risk_transaction_ratio"] >= 0.25) &
            (df["transaction_count"] >= 4)
        ) |
        (
            (df["average_risk_score"] >= 6) &
            (df["transaction_count"] >= 4)
        )
    )
    ]
    
    choices = [
            "CRITICAL",
            "HIGH",
            "MEDIUM"
    ]
    
    df["account_risk_level"] = np.select(conditions,choices,default="LOW")
    return df

def build_customer_profiles(account_profiles,df):
    account_customers = (df [["customer_id","account_id"]].drop_duplicates())
    
    customer_profiles = (
        account_profiles.merge(account_customers,on = "account_id",how="left")
        .groupby("customer_id")
        .agg(
            account_count = ("account_id","count"),
            transaction_count = ("transaction_count","sum"),
            total_transaction_amount = ("total_transaction_amount","sum"),
            average_account_risk = ("average_risk_score","mean"),
            max_account_risk_score=("max_risk_score", "max"),
            critical_accounts = (
                "account_risk_level",
                lambda x : (x=="CRITICAL").sum()
                ),
            high_risk_accounts = (
                "account_risk_level",
                lambda x : (x == "HIGH").sum()
            )
        ).reset_index()
    )
    customer_profiles ["risky_account_ratio"] = (customer_profiles["critical_accounts"] + customer_profiles["high_risk_accounts"]) / customer_profiles["account_count"]
    customer_profiles = assign_customer_risk_profile(customer_profiles)
    return customer_profiles

def assign_customer_risk_profile(df):

    df = df.copy()

    conditions = [
        (
            (df["critical_accounts"] >= 2) |
            (
                (df["risky_account_ratio"] >= 0.75) &
                (df["account_count"] >= 2)
            ) |
            (
                (df["average_account_risk"] >= 15) &
                (df["account_count"] >= 2)
            )
        ),

        (
            (df["critical_accounts"] >= 1) |
            (
                (df["risky_account_ratio"] >= 0.50) &
                (df["account_count"] >= 2)
            ) |
            (
                (df["average_account_risk"] >= 10) &
                (df["account_count"] >= 2)
            )
        ),

        (
            (df["high_risk_accounts"] >= 1) |
            (
                (df["risky_account_ratio"] >= 0.25) &
                (df["account_count"] >= 2)
            ) |
            (
                (df["average_account_risk"] >= 6) &
                (df["account_count"] >= 2)
            )
        )
    ]

    choices = [
        "CRITICAL",
        "HIGH",
        "MEDIUM"
    ]

    df["customer_risk_level"] = np.select(
        conditions,
        choices,
        default="LOW"
    )

    return df