import pandas as pd
SUPPORTED_COUNTRIES = [
    "FR", "DE", "ES", "IT", "NL",
    "BE", "GB", "US", "CA", "AU",
    "JP", "SG", "AE", "IN", "PK"
]

SUPPORTED_CURRENCIES = {
    "FR": "EUR",
    "DE": "EUR",
    "ES": "EUR",
    "IT": "EUR",
    "NL": "EUR",
    "BE": "EUR",
    "GB": "GBP",
    "US": "USD",
    "CA": "CAD",
    "AU": "AUD",
    "JP": "JPY",
    "SG": "SGD",
    "AE": "AED",
    "IN": "INR",
    "PK": "PKR"
}

def validate_accounts_of_customers(accounts,customers):
    """
        Validate that every account belongs to an existing customer.
    """
    customer_ids = set(customers["customer_id"])
    
    invalid_accounts = accounts[~accounts["customer_id"].isin(customer_ids)]
    
    return { "name": "ACCOUNT_CUSTOMER_RELATIONSHIP", "invalid_records": invalid_accounts, "invalid_count": len(invalid_accounts), "status": len(invalid_accounts) == 0 }

def validate_transaction_accounts(transactions,accounts):
    """
        Validate that every transaction belongs to an existing account.
    """
    account_ids = set (accounts["account_id"])
    invalid_transactions = transactions[~transactions["account_id"].isin(account_ids)]
    return { "name": "TRANSACTION_ACCOUNT_RELATIONSHIP", "invalid_records": invalid_transactions, "invalid_count": len(invalid_transactions), "status": len(invalid_transactions) == 0 }

def validate_transaction_merchants(merchants, transactions):
    """
    Validate that every transaction references an existing merchant.
    """

    merchant_ids = set(merchants["merchant_id"])

    invalid_transactions = transactions[
        ~transactions["merchant_id"].isin(merchant_ids)
    ]

    return { "name": "TRANSACTION_MERCHANT_RELATIONSHIP", "invalid_records": invalid_transactions, "invalid_count": len(invalid_transactions), "status": len(invalid_transactions) == 0 }

def validate_date(transactions,accounts):
    transaction_dates = pd.to_datetime(
        transactions["transaction_timestamp"],
        errors="coerce"
    )

    account_dates = pd.to_datetime(
        accounts["created_at"],
        errors="coerce"
    )

    accounts_for_merge = accounts[["account_id"]].copy()
    accounts_for_merge["created_at"] = account_dates

    merged = transactions.merge(
        accounts_for_merge,
        on="account_id",
        how="left"
    )

    invalid_transactions = merged[
        transaction_dates.loc[merged.index]
        < merged["created_at"]
    ]
    return { "name": "TRANSACTION_DATE", "invalid_records": invalid_transactions, "invalid_count": len(invalid_transactions), "status": len(invalid_transactions) == 0 }

    
def validate_cross_dataset(customers, accounts, merchants, transactions):

    results = {}

    results["account_customer"] = validate_accounts_of_customers(customers,accounts)

    results["transaction_account"] = validate_transaction_accounts(accounts,transactions)

    results["transaction_merchant"] = validate_transaction_merchants(merchants,transactions)
    
    results["transaction_date"] =validate_date(transactions,accounts)

    return results

