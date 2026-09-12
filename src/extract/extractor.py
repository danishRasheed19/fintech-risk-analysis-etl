import pandas as pd
from load.watermark import get_watermark
from load.postgres_loader import get_existing_ids
def extract_csv(file_path):
    
    print(f"Extracting: {file_path}")

    df = pd.read_csv(file_path)

    print(f"Reading: {len(df):,} rows")

    return df

def apply_watermark(df,dataset,incremental_column):
    print(f"Applying Watermark for {dataset}")
    watermark = get_watermark(dataset)
    print(watermark)
    if watermark is None:
        print(f"{dataset}: No watermark found. Processing all records.")
        return df

    df[incremental_column] = pd.to_datetime(df[incremental_column])
    
    watermark = pd.to_datetime(watermark)
    
    incremental_df = df[df[incremental_column] > watermark].copy()
    
    print(
        f"{dataset}: {len(incremental_df):,} new records"
    )
    
    return incremental_df
    
def apply_pk_watermark(df,dataset,pk_name):
    print(f"Applying PK based watermark for: {dataset}")
    existing_ids = get_existing_ids(dataset,pk_name)
    print(f"Existing IDs in DB: {len(existing_ids)}")
    print(f"Incoming IDs: {len(df)}")
    new_df = df[~df[pk_name].isin(existing_ids)]
    print(
            f"{dataset}: {len(new_df):,} new records"
        )
    return new_df
    