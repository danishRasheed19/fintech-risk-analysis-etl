from extract.extractor import extract_csv
from validate.validator import validate_data
from validate.cross_validation import validate_cross_dataset
from filter.filter import combine_validation_results
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
    combine_validation_results(customers,accounts,merchants,transactions,validation_results,cross_validation_results)


if __name__ == "__main__":
    main()