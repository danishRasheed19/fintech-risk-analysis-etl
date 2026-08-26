from extract.extractor import extract_csv
from validate.validator import validate_customers
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

    validate_customers(customers)


if __name__ == "__main__":
    main()