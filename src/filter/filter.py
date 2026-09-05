def combine_validation_results(
    customers,
    accounts,
    merchants,
    transactions,
    validation_results,
    cross_validation_results
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

    invalid_account_ids = set(
        cross_validation_results["account_customer"]
        ["invalid_records"]["account_id"]
    )

    cross_invalid_accounts_mask = accounts["account_id"].isin(
        invalid_account_ids
    )

    account_reasons.loc[cross_invalid_accounts_mask] += (
        "; " +
        cross_validation_results["account_customer"]["reason"]
    )

    final_invalid_accounts_mask = (
        validation_results["accounts"]["invalid_rows"]
        | cross_invalid_accounts_mask
    )


    # -------------------------
    # MERCHANTS
    # -------------------------

    merchant_reasons = validation_results["merchants"]["rejection_reasons"]
    merchant_mask = validation_results["merchants"]["invalid_rows"]


    # -------------------------
    # TRANSACTIONS
    # -------------------------

    transaction_reasons = validation_results["transactions"]["rejection_reasons"]

    # Transaction → Account
    invalid_transaction_account_ids = set(
        cross_validation_results["transaction_account"]
        ["invalid_records"]["transaction_id"]
    )

    account_cross_mask = transactions["transaction_id"].isin(
        invalid_transaction_account_ids
    )

    transaction_reasons.loc[account_cross_mask] += (
        "; " +
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

    transaction_reasons.loc[merchant_cross_mask] += (
        "; " +
        cross_validation_results["transaction_merchant"]["reason"]
    )

    # Transaction → Date
    invalid_transaction_date_ids = set(
        cross_validation_results["transaction_date"]
        ["invalid_records"]["transaction_id"]
    )

    date_cross_mask = transactions["transaction_id"].isin(
        invalid_transaction_date_ids
    )

    transaction_reasons.loc[date_cross_mask] += (
        "; " +
        cross_validation_results["transaction_date"]["reason"]
    )

    cross_invalid_transactions_mask = (
        account_cross_mask
        | merchant_cross_mask
        | date_cross_mask
    )

    final_invalid_transaction_mask = (
        validation_results["transactions"]["invalid_rows"]
        | cross_invalid_transactions_mask
    )


    return (
        customer_mask,
        customer_reasons,

        final_invalid_accounts_mask,
        account_reasons,

        merchant_mask,
        merchant_reasons,

        final_invalid_transaction_mask,
        transaction_reasons
    )
def filter_unexpected_columns(customers,accounts,merchants,transactions,validation_results):
    customers = customers.drop(columns = validation_results["customers"]["unexpected_cols"])
    accounts = accounts.drop(columns = validation_results["accounts"]["unexpected_cols"])
    merchants = merchants.drop(columns = validation_results["merchants"]["unexpected_cols"])
    transactions = transactions.drop(columns = validation_results["transactions"]["unexpected_cols"])
    
    return customers,accounts,merchants,transactions

def filter_data(customers,accounts,merchants,transactions,validation_results,cross_validation_results):
    print ("FILTERING DATA")
    results = {}
    customers,accounts,merchants,transactions = filter_unexpected_columns(customers,accounts,merchants,transactions,validation_results)
    customers_mask,customer_reasons, accounts_mask, account_reasons,merchants_mask,merchant_reasons, transactions_mask,transaction_reasons = combine_validation_results(
        customers,accounts,merchants,transactions,validation_results,cross_validation_results
    )
    
    invalid_customers = customers[customers_mask].copy()
    invalid_customers["rejected_reason"] = customer_reasons[customers_mask]
    
    invalid_accounts = accounts[accounts_mask].copy()
    invalid_accounts["rejected_reason"] = account_reasons[accounts_mask]
    
    invalid_merchants = merchants[merchants_mask].copy()
    invalid_merchants["rejected_reason"] = merchant_reasons[merchants_mask]
    
    invalid_transactions = transactions[transactions_mask].copy()
    invalid_transactions["rejected_reason"] = transaction_reasons[transactions_mask]
    
    results["customers"] = {
        "valid" : customers[~customers_mask],
        "invalid" : invalid_customers
    }
    
    results["accounts"] = {
            "valid" : accounts[~accounts_mask],
            "invalid" : invalid_accounts
    }
    
    results["merchants"] = {
            "valid" : merchants[~merchants_mask],
            "invalid" : invalid_merchants
    }
    
    results["transactions"] = {
            "valid" : transactions[~transactions_mask],
            "invalid" : invalid_transactions
    }
    
    return results
    
