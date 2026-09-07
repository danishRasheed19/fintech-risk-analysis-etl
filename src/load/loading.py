import pandas as pd
from datetime import datetime
from pathlib import Path
from load.watermark import set_watermarks
def load_as_csv(transformed_data,rejected_data):
    #loading rejected data
    try:
        print("LOADING REJECTED CSV")
        for name, value in rejected_data.items():
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_dir = Path(f"../data/rejected/{name}")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{name}_{timestamp}.csv"
            value.to_csv(output_path,index=False)
        print("REJECTED CSV LOADING COMPLETE")
    #loading transfromed data
        print("LOADING TRANSFORMED DATA")
        for name,value in transformed_data.items():
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_dir = Path(f"../data/processed/{name}")
            output_dir.mkdir(parents=True,exist_ok=True)
            output_path = output_dir / f"{name}_{timestamp}.csv"
            value.to_csv(output_path,index=False)
        print("PROCESSED CSV LOADING COMPLETE")
    
    except OSError as e:
        print(f"FILE SYSTEM ERROR DURING LOADING: {e}")
        raise
    
    except Exception as e:
        print(f"UNEXPECTED ERROR DURING LOADING: {e}")
        raise
        
def load_data(transformed_data,rejected_data):
    customer_watermark = transformed_data["customers"]["account_created_at"].max()
    account_watermark = transformed_data["accounts"]["created_at"].max()
    transaction_watermark = transformed_data["transactions"]["transaction_timestamp"].max()   
    
    print(customer_watermark)
    load_as_csv(transformed_data,rejected_data)
    
    # Only update watermarks after successful loading
    if pd.notna(customer_watermark):
        set_watermarks("customers", customer_watermark)

    if pd.notna(account_watermark):
        set_watermarks("accounts", account_watermark)

    if pd.notna(transaction_watermark):
        set_watermarks("transactions", transaction_watermark)
    
    print("Watermarks updated")
