import pandas as pd

from reporting.html_report import produce_cross_validation_report

from load.postgres_loader import get_existing_ids, get_existing_accounts


def validate_accounts_of_customers(accounts, customers):

    """
    Validate that every account belongs to an existing customer.
    """

    if accounts.empty:
        return {
            "name": "ACCOUNT_CUSTOMER_RELATIONSHIP",
            "invalid_records": accounts.iloc[0:0],
            "invalid_count": 0,
            "status": True,
            "reason": "Account does not have a customer"
        }

    existing_customer_ids = get_existing_ids(
        "customers",
        "customer_id"
    )

    customer_ids = set(customers["customer_id"])

    all_customer_ids = customer_ids | existing_customer_ids

    invalid_accounts = accounts[
        ~accounts["customer_id"].isin(all_customer_ids)
    ]

    return {
        "name": "ACCOUNT_CUSTOMER_RELATIONSHIP",
        "invalid_records": invalid_accounts,
        "invalid_count": len(invalid_accounts),
        "status": len(invalid_accounts) == 0,
        "reason": "Account does not have a customer"
    }


def validate_transaction_accounts(transactions, accounts):

    """
    Validate that every transaction belongs to an existing account.
    """

    if transactions.empty:
        return {
            "name": "TRANSACTION_ACCOUNT_RELATIONSHIP",
            "invalid_records": transactions.iloc[0:0],
            "invalid_count": 0,
            "status": True,
            "reason": "Transaction does not have account"
        }

    existing_account_ids = get_existing_ids(
        "accounts",
        "account_id"
    )

    account_ids = set(accounts["account_id"])

    all_account_ids = account_ids | existing_account_ids

    invalid_transactions = transactions[
        ~transactions["account_id"].isin(all_account_ids)
    ]

    return {
        "name": "TRANSACTION_ACCOUNT_RELATIONSHIP",
        "invalid_records": invalid_transactions,
        "invalid_count": len(invalid_transactions),
        "status": len(invalid_transactions) == 0,
        "reason": "Transaction does not have account"
    }


def validate_transaction_merchants(merchants, transactions):

    """
    Validate that every transaction references an existing merchant.
    """

    if transactions.empty:
        return {
            "name": "TRANSACTION_MERCHANT_RELATIONSHIP",
            "invalid_records": transactions.iloc[0:0],
            "invalid_count": 0,
            "status": True,
            "reason": "Transaction does not have a merchant"
        }

    existing_merchant_ids = get_existing_ids(
        "merchants",
        "merchant_id"
    )

    merchant_ids = set(merchants["merchant_id"])

    all_merchant_ids = merchant_ids | existing_merchant_ids

    invalid_transactions = transactions[
        ~transactions["merchant_id"].isin(all_merchant_ids)
    ]

    return {
        "name": "TRANSACTION_MERCHANT_RELATIONSHIP",
        "invalid_records": invalid_transactions,
        "invalid_count": len(invalid_transactions),
        "status": len(invalid_transactions) == 0,
        "reason": "Transaction does not have a merchant"
    }


def validate_date(transactions, accounts):

    """
    Validate that a transaction does not occur before
    its account was created.
    """

    if transactions.empty:
        return {
            "name": "TRANSACTION_DATE",
            "invalid_records": transactions.iloc[0:0],
            "invalid_count": 0,
            "status": True,
            "reason": "Invalid Date"
        }

    transactions_for_merge = transactions.copy()

    transactions_for_merge["transaction_timestamp"] = pd.to_datetime(
        transactions_for_merge["transaction_timestamp"],
        errors="coerce"
    )

    accounts_for_merge = accounts[
        ["account_id", "created_at"]
    ].copy()

    accounts_for_merge["created_at"] = pd.to_datetime(
        accounts_for_merge["created_at"],
        errors="coerce"
    )

    # Fetch existing accounts from PostgreSQL
    existing_accounts = get_existing_accounts()

    existing_accounts["created_at"] = pd.to_datetime(
        existing_accounts["created_at"],
        errors="coerce"
    )

    # Combine existing accounts with current batch.
    # Current batch takes precedence.
    accounts_for_merge = pd.concat(
        [
            existing_accounts,
            accounts_for_merge
        ],
        ignore_index=True
    ).drop_duplicates(
        subset="account_id",
        keep="last"
    )

    merged = transactions_for_merge.merge(
        accounts_for_merge,
        on="account_id",
        how="left"
    )

    invalid_transactions = merged[
        merged["transaction_timestamp"] < merged["created_at"]
    ]

    return {
        "name": "TRANSACTION_DATE",
        "invalid_records": invalid_transactions,
        "invalid_count": len(invalid_transactions),
        "status": len(invalid_transactions) == 0,
        "reason": "Invalid Date"
    }


def validate_cross_dataset(
    customers,
    accounts,
    merchants,
    transactions,
    html_report=False
):

    print("VALIDATING CROSS DATASET")

    results = {}

    results["account_customer"] = validate_accounts_of_customers(
        accounts,
        customers
    )

    results["transaction_account"] = validate_transaction_accounts(
        transactions,
        accounts
    )

    results["transaction_merchant"] = validate_transaction_merchants(
        merchants,
        transactions
    )

    results["transaction_date"] = validate_date(
        transactions,
        accounts
    )

    if html_report:
        produce_cross_validation_report(results)

    return results