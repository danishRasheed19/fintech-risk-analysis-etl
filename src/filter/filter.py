def combine_validation_results(customers,accounts,merchants,transactions,validation_results, cross_validation_results):
    # getting accounts
    invalid_accounts_ids = set(cross_validation_results["account_customer"]["invalid_records"]["account_id"])
    
    cross_invalid_accounts_mask = accounts["account_id"].isin(invalid_accounts_ids)
    
    final_invalid_accounts_mask = (
       validation_results["accounts"] 
       | cross_invalid_accounts_mask
    )
    
    #getting transactions
    invalid_transaction_ids = ( set(cross_validation_results["transaction_account"]["invalid_records"]["transaction_id"])
                               | set(cross_validation_results["transaction_merchant"]["invalid_records"]["transaction_id"])
                               | set(cross_validation_results["transaction_date"]["invalid_records"]["transaction_id"])
    )
    
    cross_invalid_transactions_mask = transactions["transaction_id"].isin(invalid_transaction_ids)
    
    final_invalid_transaction_mask =(
        validation_results["transactions"]
        | cross_invalid_transactions_mask
    )
    
    return validation_results["customers"], final_invalid_accounts_mask, validation_results["merchants"], final_invalid_transaction_mask