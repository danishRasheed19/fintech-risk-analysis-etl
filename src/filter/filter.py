def combine_validation_results(customers,accounts,merchants,transactions,validation_results, cross_validation_results):
    # getting accounts
    invalid_accounts_ids = set(cross_validation_results["account_customer"]["invalid_records"]["account_id"])
    
    cross_invalid_accounts_mask = accounts["account_id"].isin(invalid_accounts_ids)
    
    final_invalid_accounts_mask = (
       validation_results["accounts"]["invalid_rows"]
       | cross_invalid_accounts_mask
    )
    
    #getting transactions
    invalid_transaction_ids = ( set(cross_validation_results["transaction_account"]["invalid_records"]["transaction_id"])
                               | set(cross_validation_results["transaction_merchant"]["invalid_records"]["transaction_id"])
                               | set(cross_validation_results["transaction_date"]["invalid_records"]["transaction_id"])
    )
    
    cross_invalid_transactions_mask = transactions["transaction_id"].isin(invalid_transaction_ids)
    
    final_invalid_transaction_mask =(
        validation_results["transactions"]["invalid_rows"]
        | cross_invalid_transactions_mask
    )
    
    return validation_results["customers"]["invalid_rows"], final_invalid_accounts_mask, validation_results["merchants"]["invalid_rows"], final_invalid_transaction_mask

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
    customers_mask, accounts_mask, merchants_mask, transactions_mask = combine_validation_results(
        customers,accounts,merchants,transactions,validation_results,cross_validation_results
    )
    
    results["customers"] = {
        "valid" : customers[~customers_mask],
        "invalid" : customers[customers_mask]
    }
    
    results["accounts"] = {
            "valid" : accounts[~accounts_mask],
            "invalid" : accounts[accounts_mask]
    }
    
    results["merchants"] = {
            "valid" : merchants[~merchants_mask],
            "invalid" : merchants[merchants_mask]
    }
    
    results["transactions"] = {
            "valid" : transactions[~transactions_mask],
            "invalid" : transactions[transactions_mask]
    }
    
    return results
    
