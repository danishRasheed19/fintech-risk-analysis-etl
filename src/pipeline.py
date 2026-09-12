import pandas as pd
from extract.extractor import extract_csv,apply_watermark,apply_pk_watermark
from validate.validator import validate_data,validate_transformed_data
from validate.cross_validation import validate_cross_dataset
from filter.filter import filter_data,filter_cross_validation_data
from transform.transformation import transform_data
from load.loading import load_data
from load.warehouse.warehouse_loader import load_into_warehouse
def main():
    data_path = "../data/raw/"

    customers = extract_csv(data_path + "customers.csv")
    accounts = extract_csv(data_path + "accounts.csv")
    merchants = extract_csv(data_path + "merchants.csv")
    transactions = extract_csv(data_path + "transactions.csv")
    
    customers = apply_watermark(customers,"customers","account_created_at")
    accounts = apply_watermark(accounts,"accounts","created_at")
    transactions = apply_watermark(transactions,"transactions","transaction_timestamp")
    merchants = apply_pk_watermark(merchants,"merchants","merchant_id")
    
    print("\nExtraction completed successfully.")

    print("\nDataset sizes:")
    

    print(f"Customers:     {len(customers):,}")
    print(f"Accounts:      {len(accounts):,}")
    print(f"Merchants:     {len(merchants):,}")
    print(f"Transactions:  {len(transactions):,}")

    validation_results = validate_data(customers,accounts,merchants,transactions, False,True)
    
    # -------------------------
    # FIRST FILTER
    # -------------------------

    filter_results = filter_data(customers,accounts,merchants,transactions,validation_results)
    customers = filter_results["customers"]["valid"]
    accounts = filter_results["accounts"]["valid"]
    merchants = filter_results["merchants"]["valid"]
    transactions = filter_results["transactions"]["valid"]
    # -------------------------
    # CROSS VALIDATION
    # -------------------------
    cross_validation_results = validate_cross_dataset(customers,accounts,merchants,transactions, True)
    
    # -------------------------
    # SECOND FILTER
    # -------------------------
    cross_filter_results = filter_cross_validation_data(customers,accounts,merchants,transactions,cross_validation_results)
    customers = cross_filter_results["customers"]["valid"]
    accounts = cross_filter_results["accounts"]["valid"]
    merchants = cross_filter_results["merchants"]["valid"]
    transactions = cross_filter_results["transactions"]["valid"]
        
    transformed_data = transform_data(customers,accounts,merchants,transactions)
       
        # -------------------------
    # COMBINE INVALID DATA
    # -------------------------

    invalid_data = {
    "customers": pd.concat([
        filter_results["customers"]["invalid"],
        cross_filter_results["customers"]["invalid"]
    ], ignore_index=True),

    "accounts": pd.concat([
        filter_results["accounts"]["invalid"],
        cross_filter_results["accounts"]["invalid"]
    ], ignore_index=True),

    "merchants": pd.concat([
        filter_results["merchants"]["invalid"],
        cross_filter_results["merchants"]["invalid"]
    ], ignore_index=True),

    "transactions": pd.concat([
        filter_results["transactions"]["invalid"],
        cross_filter_results["transactions"]["invalid"]
    ], ignore_index=True)
    }
    validate_transformed_data(transformed_data,False,True)
    
    #loading into staging
    load_data(transformed_data,invalid_data)
    
    #loading into warehouse
    load_into_warehouse()
    
    
if __name__ == "__main__":
    main()