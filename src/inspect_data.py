import pandas as pd

DATA_PATH = "../data/raw"

def inspect_file(filename):
    path = f"{DATA_PATH}/{filename}"

    df = pd.read_csv(path)

    print("\n" + "=" * 60)
    print(filename)
    print("=" * 60)

    print("\nShape: ")
    print(df.shape)

    print("\nColumns: ")
    print(df.columns.tolist())

    print("\nData Types: ")
    print(df.dtypes)

    print("\n Missing Values: ")
    print(df.isnull().sum())

    print("\nDuplicates: ")
    print(df.duplicated().sum())

    print("\n First 5 rows: ")
    print(df.head())


def main():
    files =[
        "customers.csv",
        "accounts.csv",
        "merchants.csv",
        "transactions.csv"
    ]

    for file in files:
        inspect_file(file)

if __name__ == "__main__":
    main()

