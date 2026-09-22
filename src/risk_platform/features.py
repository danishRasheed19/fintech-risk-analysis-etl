import pandas as pd

def merchant_risk(df):
    df = df.copy()
    merchant_risk_mapping = {
            "LOW": 1,
            "MEDIUM": 2,
            "HIGH": 3
    }
    df["merchant_risk_score"] = df["risk_category"].map(merchant_risk_mapping).fillna(0).astype(int)
    return df

def currency_mismatch(df):
    df= df.copy()
    df["currency_mismatch"] = (df["transaction_currency"] != df["account_currency"]).astype(int)
    return df

def country_mismatch(df):
    df = df.copy()
    df["country_mismatch"] = (df["transaction_country"] != df["customer_country"]).astype(int)
    return df

def is_reversed(df):
    df=df.copy()
    df["is_reversed"] = (df["transaction_status"] == "REVERSED").astype(int)
    return df

def is_suspended_account(df):
    df=df.copy()
    df["is_suspended_account"] = (df["account_status"] == "SUSPENDED").astype(int)
    return df

def is_closed_account(df):
    df=df.copy()
    df["is_closed_account"] = (df["account_status"] == "CLOSED").astype(int)
    return df

def add_time_features(df):
    df = df.copy()
    df["transaction_hour"] = df["transaction_timestamp"].dt.hour
    
    df["is_night"] = (
    (df["transaction_hour"] < 6) |
    (df["transaction_hour"] >= 22)
    ).astype(int)

    df["is_weekend"] = (
        df["transaction_timestamp"].dt.dayofweek >= 5
    ).astype(int)
    return df

def build_transaction_features(df):
    df = df.copy()
    df = merchant_risk(df)
    df = country_mismatch(df)
    df = is_reversed(df)
    df = is_suspended_account(df)
    df = is_closed_account(df)
    df = add_time_features(df)
    return df


def describe_features(df):
    print("Describing the features: ")
    print(df[[
    "merchant_risk_score",
    "country_mismatch",
    "is_reversed",
    "is_suspended_account",
    "is_closed_account",
    "transaction_hour",
    "is_night",
    "is_weekend"
    ]].describe())
    
    print(f"Country Mismatch: {df["country_mismatch"].value_counts()}")
    print(f"Is Reversed: {df["is_reversed"].value_counts()}")
    print(f"Is suspended: {df["is_suspended_account"].value_counts()}")
    print(f"Is closed account: {df["is_closed_account"].value_counts()}")
    print(f"Is night: {df["is_night"].value_counts()}")
    print(f"Is weekend: {df["is_weekend"].value_counts()}")