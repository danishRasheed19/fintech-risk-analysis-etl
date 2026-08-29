import pandas as pd

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

def validate_cross_dataset(customers, accounts, merchants, transactions):

    results = {}

    results["account_customer"] = validate_accounts_of_customers(
        customers,
        accounts
    )

    results["transaction_account"] = validate_transaction_accounts(
        accounts,
        transactions
    )

    results["transaction_merchant"] = validate_transaction_merchants(
        merchants,
        transactions
    )

    return results

