from extract.extractor import extract_csv
from validate.validator import validate_data,validate_transformed_data
from validate.cross_validation import validate_cross_dataset
from filter.filter import filter_data
from transform.transformation import transform_data
from load.loading import load_as_csv
def main():
    data_path = "../data/raw/"

    customers = extract_csv(data_path + "customers.csv")
    accounts = extract_csv(data_path + "accounts.csv")
    merchants = extract_csv(data_path + "merchants.csv")
    transactions = extract_csv(data_path + "transactions.csv")

    print("\nExtraction completed successfully.")

    print("\nDataset sizes:")
    

    print(f"Customers:     {len(customers):,}")
    print(f"Accounts:      {len(accounts):,}")
    print(f"Merchants:     {len(merchants):,}")
    print(f"Transactions:  {len(transactions):,}")

    validation_results = validate_data(customers,accounts,merchants,transactions, False,False)
    cross_validation_results = validate_cross_dataset(customers,accounts,merchants,transactions, False)
    filtered_data = filter_data(customers,accounts,merchants,transactions,validation_results,cross_validation_results)
    transformed_data = transform_data(filtered_data["customers"]["valid"],filtered_data["accounts"]["valid"],filtered_data["merchants"]["valid"],filtered_data["transactions"]["valid"])
    invalid_data = {
        "customers" : filtered_data["customers"]["invalid"],
        "accounts" : filtered_data["accounts"]["invalid"],
        "merchants" : filtered_data["merchants"]["invalid"],
        "transactions" : filtered_data["transactions"]["invalid"]
    }
    validate_transformed_data(transformed_data,False,True)
    load_as_csv(transformed_data,invalid_data)
if __name__ == "__main__":
    main()