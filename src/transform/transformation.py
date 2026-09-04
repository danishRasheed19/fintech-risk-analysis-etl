import pandas as pd
from utils.dictionaries.country_dictionary import COUNTRIES
from utils.dictionaries.currency_dictionary import CURRENCY_NAMES

def transform_data(customers,accounts,merchants,transactions):
    print("Transforming Data")
    results = {}
    transformed_customers = transform_customers(customers)
    transformed_accounts = transform_accounts(accounts)
    transformed_merchants = transform_merchants(merchants)
    transformed_transactions = transform_transactions(transactions)
    results ={
        "customers" : transformed_customers,
        "accounts" : transformed_accounts,
        "merchants" : transformed_merchants,
        "transactions" : transformed_transactions
    }
    return results


def transform_customers(customers):
    
    customers = customers.copy()
    
    customers["first_name"] = customers["first_name"].str.strip().str.title()
    
    customers["last_name"] = customers["last_name"].str.strip().str.title()
    
    customers["email"] = customers["email"].str.strip().str.lower()
    
    customers["country"] = customers["country"].str.strip().str.upper()
    
    customers = customers.rename(columns={"country": "country_code"})
    
    customers["country_name"] = customers["country_code"].map(COUNTRIES)
    
    customers["account_type"] = customers["account_type"].str.strip().str.upper()
    
    customers["customer_status"] = customers["customer_status"].str.strip().str.upper()
    
    customers["account_created_at"] = pd.to_datetime(customers["account_created_at"])
    
    return customers

def transform_accounts(accounts):
    accounts = accounts.copy()
    accounts["account_type"] = accounts["account_type"].str.strip().str.upper()
    
    accounts["currency"] = accounts["currency"].str.strip().str.upper()
    
    accounts = accounts.rename(columns={"currency":"currency_code"})
    
    accounts["currency_name"] = accounts["currency_code"].map(CURRENCY_NAMES)
    
    accounts["created_at"] = pd.to_datetime(accounts["created_at"])
    
    accounts["status"] = accounts["status"].str.strip().str.upper()
    
    accounts["balance"] = pd.to_numeric(accounts["balance"]).round(2)

    return accounts

def transform_merchants(merchants):
    merchants = merchants.copy()
    
    merchants["merchant_name"] = merchants["merchant_name"].str.strip().str.title()
    
    merchants["merchant_category"] = merchants["merchant_category"].str.strip().str.upper()
    
    merchants["country"] = merchants["country"].str.strip().str.upper()
    
    merchants = merchants.rename(columns = {"country" : "country_code"})
    
    merchants["country_name"] = merchants["country_code"].map(COUNTRIES)
    
    merchants["risk_category"] = merchants["risk_category"].str.strip().str.upper()
    
    return merchants
    
def transform_transactions(transactions):
    transactions = transactions.copy()
    
    transactions["transaction_type"] = transactions["transaction_type"].str.strip().str.upper()
    
    transactions["payment_method"] = transactions["payment_method"].str.strip().str.upper()
    
    transactions["amount"] = pd.to_numeric(transactions["amount"]).round(2)
    
    transactions["currency"] = transactions["currency"].str.strip().str.upper()
    
    transactions["country"] =transactions["country"].str.strip().str.upper()
    
    transactions = transactions.rename(columns = {"currency":"currency_code","country":"country_code"})
    
    transactions["currency_name"] = transactions["currency_code"].map(CURRENCY_NAMES)
    
    transactions["country_name"] = transactions["country_code"].map(COUNTRIES)

    transactions["status"] = transactions["status"].str.strip().str.upper()
    
    transactions["transaction_timestamp"] = pd.to_datetime(
    transactions["transaction_timestamp"]
)

    transactions["transaction_date"] = (
    transactions["transaction_timestamp"].dt.date
    )

    transactions["transaction_year"] = (
    transactions["transaction_timestamp"].dt.year
    )

    transactions["transaction_month"] = (
    transactions["transaction_timestamp"].dt.month
    )

    transactions["transaction_hour"] = (
    transactions["transaction_timestamp"].dt.hour
    )
    
    return transactions

    
    