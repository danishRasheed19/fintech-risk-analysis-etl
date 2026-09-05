import pandas as pd
from datetime import datetime
from pathlib import Path

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
        
