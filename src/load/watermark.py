import json
from pathlib import Path
from datetime import datetime

WATERMARK_PATH = Path("../../data/metadata/watermarks.json")
DEFAULT_WATERMARKS = {
    "customers": None,
    "accounts": None,
    "transactions": None
}

def load_watermarks():
    try:
        WATERMARK_PATH.parent.mkdir(parents=True,exist_ok=True)
        if not WATERMARK_PATH.exists():
            save_watermarks(DEFAULT_WATERMARKS)
            return DEFAULT_WATERMARKS.copy()
        with open(WATERMARK_PATH,"r") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR LOADING WATERMARKS: {e}")
        raise

def save_watermarks(watermarks):
    try:
        WATERMARK_PATH.parent.mkdir(parents=True,exist_ok=True)
        with open (WATERMARK_PATH,"w") as file:
            json.dump(watermarks,file,indent=4)
    except OSError as e:
        print(f"ERROR SAVING WATERMARKS: {e}")
        raise

def get_watermark(dataset):
    watermarks = load_watermarks()
    return watermarks.get(dataset)

def set_watermarks(dataset,timestamp):
    watermarks = load_watermarks()
    if dataset not in watermarks:
        raise ValueError(
            f"Unsupported dataset for watermarking: {dataset}"
        )
    
    if isinstance(timestamp,datetime):
        timestamp = timestamp.isoformat()
    
    watermarks[dataset] = timestamp
    save_watermarks(watermarks)
