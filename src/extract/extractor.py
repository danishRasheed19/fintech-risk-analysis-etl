import pandas as pd

def extract_csv(file_path):
    print(f"Extracting: {file_path}")

    df = pd.read_csv(file_path)

    print(f"Reading: {len(df):,} rows")

    return df