import pandas as pd
def filter_unexpected_columns(
    customers,
    accounts,
    merchants,
    transactions,
    validation_results
):

    customers = customers.drop(
        columns=validation_results["customers"]["unexpected_cols"]
    )

    accounts = accounts.drop(
        columns=validation_results["accounts"]["unexpected_cols"]
    )

    merchants = merchants.drop(
        columns=validation_results["merchants"]["unexpected_cols"]
    )

    transactions = transactions.drop(
        columns=validation_results["transactions"]["unexpected_cols"]
    )

    return customers, accounts, merchants, transactions


def combine_validation_results(
    customers,
    accounts,
    merchants,
    transactions,
    validation_results
):

    # -------------------------
    # CUSTOMERS
    # -------------------------

    customer_reasons = validation_results["customers"]["rejection_reasons"]
    customer_mask = validation_results["customers"]["invalid_rows"]

    # -------------------------
    # ACCOUNTS
    # -------------------------

    account_reasons = validation_results["accounts"]["rejection_reasons"]
    account_mask = validation_results["accounts"]["invalid_rows"]

    # -------------------------
    # MERCHANTS
    # -------------------------

    merchant_reasons = validation_results["merchants"]["rejection_reasons"]
    merchant_mask = validation_results["merchants"]["invalid_rows"]

    # -------------------------
    # TRANSACTIONS
    # -------------------------

    transaction_reasons = validation_results["transactions"]["rejection_reasons"]
    transaction_mask = validation_results["transactions"]["invalid_rows"]

    return (
        customer_mask,
        customer_reasons,
        account_mask,
        account_reasons,
        merchant_mask,
        merchant_reasons,
        transaction_mask,
        transaction_reasons
    )


def filter_validation_data(
    customers,
    accounts,
    merchants,
    transactions,
    validation_results
):

    (
        customer_mask,
        customer_reasons,
        account_mask,
        account_reasons,
        merchant_mask,
        merchant_reasons,
        transaction_mask,
        transaction_reasons
    ) = combine_validation_results(
        customers,
        accounts,
        merchants,
        transactions,
        validation_results
    )

    results = {}

    # -------------------------
    # CUSTOMERS
    # -------------------------

    invalid_customers = customers[customer_mask].copy()

    invalid_customers["rejected_reason"] = (
        customer_reasons[customer_mask]
    )

    results["customers"] = {
        "valid": customers[~customer_mask].copy(),
        "invalid": invalid_customers
    }

    # -------------------------
    # ACCOUNTS
    # -------------------------

    invalid_accounts = accounts[account_mask].copy()

    invalid_accounts["rejected_reason"] = (
        account_reasons[account_mask]
    )

    results["accounts"] = {
        "valid": accounts[~account_mask].copy(),
        "invalid": invalid_accounts
    }

    # -------------------------
    # MERCHANTS
    # -------------------------

    invalid_merchants = merchants[merchant_mask].copy()

    invalid_merchants["rejected_reason"] = (
        merchant_reasons[merchant_mask]
    )

    results["merchants"] = {
        "valid": merchants[~merchant_mask].copy(),
        "invalid": invalid_merchants
    }

    # -------------------------
    # TRANSACTIONS
    # -------------------------

    invalid_transactions = transactions[transaction_mask].copy()

    invalid_transactions["rejected_reason"] = (
        transaction_reasons[transaction_mask]
    )

    results["transactions"] = {
        "valid": transactions[~transaction_mask].copy(),
        "invalid": invalid_transactions
    }

    return results


def filter_cross_validation_data(
    customers,
    accounts,
    merchants,
    transactions,
    cross_validation_results
):

    results = {}

    # -------------------------
    # CUSTOMERS
    # -------------------------
    # Customers currently have no cross-validation rules.

    results["customers"] = {
        "valid": customers.copy(),
        "invalid": customers.iloc[0:0].copy()
    }

    # -------------------------
    # ACCOUNTS
    # -------------------------

    account_reasons = pd.Series(
        "",
        index=accounts.index,
        dtype="object"
    )

    invalid_account_ids = set(
        cross_validation_results["account_customer"]
        ["invalid_records"]["account_id"]
    )

    account_mask = accounts["account_id"].isin(
        invalid_account_ids
    )

    account_reasons.loc[account_mask] = (
        cross_validation_results["account_customer"]["reason"]
    )

    invalid_accounts = accounts[account_mask].copy()

    invalid_accounts["rejected_reason"] = (
        account_reasons[account_mask]
    )

    results["accounts"] = {
        "valid": accounts[~account_mask].copy(),
        "invalid": invalid_accounts
    }

    # -------------------------
    # MERCHANTS
    # -------------------------
    # Merchants currently have no cross-validation rules.

    results["merchants"] = {
        "valid": merchants.copy(),
        "invalid": merchants.iloc[0:0].copy()
    }

    # -------------------------
    # TRANSACTIONS
    # -------------------------

    transaction_reasons = pd.Series(
        "",
        index=transactions.index,
        dtype="object"
    )

    # Transaction → Account

    invalid_transaction_account_ids = set(
        cross_validation_results["transaction_account"]
        ["invalid_records"]["transaction_id"]
    )

    account_cross_mask = transactions["transaction_id"].isin(
        invalid_transaction_account_ids
    )

    transaction_reasons.loc[account_cross_mask] = (
        cross_validation_results["transaction_account"]["reason"]
    )

    # Transaction → Merchant

    invalid_transaction_merchant_ids = set(
        cross_validation_results["transaction_merchant"]
        ["invalid_records"]["transaction_id"]
    )

    merchant_cross_mask = transactions["transaction_id"].isin(
        invalid_transaction_merchant_ids
    )

    transaction_reasons.loc[merchant_cross_mask] = (
        transaction_reasons.loc[merchant_cross_mask]
        .apply(
            lambda x: (
                f"{x}; "
                f"{cross_validation_results['transaction_merchant']['reason']}"
            )
            if x
            else cross_validation_results["transaction_merchant"]["reason"]
        )
    )

    # Transaction → Date

    invalid_transaction_date_ids = set(
        cross_validation_results["transaction_date"]
        ["invalid_records"]["transaction_id"]
    )

    date_cross_mask = transactions["transaction_id"].isin(
        invalid_transaction_date_ids
    )

    transaction_reasons.loc[date_cross_mask] = (
        transaction_reasons.loc[date_cross_mask]
        .apply(
            lambda x: (
                f"{x}; "
                f"{cross_validation_results['transaction_date']['reason']}"
            )
            if x
            else cross_validation_results["transaction_date"]["reason"]
        )
    )

    transaction_mask = (
        account_cross_mask
        | merchant_cross_mask
        | date_cross_mask
    )

    invalid_transactions = transactions[transaction_mask].copy()

    invalid_transactions["rejected_reason"] = (
        transaction_reasons[transaction_mask]
    )

    results["transactions"] = {
        "valid": transactions[~transaction_mask].copy(),
        "invalid": invalid_transactions
    }

    return results


def filter_data(
    customers,
    accounts,
    merchants,
    transactions,
    validation_results
):

    print("FILTERING DATA")

    # ----------------------------------
    # REMOVE UNEXPECTED COLUMNS
    # ----------------------------------

    (
        customers,
        accounts,
        merchants,
        transactions
    ) = filter_unexpected_columns(
        customers,
        accounts,
        merchants,
        transactions,
        validation_results
    )

    # ----------------------------------
    # FIRST FILTER
    # Dataset-level validation
    # ----------------------------------

    first_filter_results = filter_validation_data(
        customers,
        accounts,
        merchants,
        transactions,
        validation_results
    )

    return first_filter_results