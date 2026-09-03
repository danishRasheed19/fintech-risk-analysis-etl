import pandas as pd
from utils.dictionaries import country_dictionary

def transform_data(data):
    print("Transforming Data")
    return None


def transform_customers(customers):
    
    customers = customers.copy()
    
    customers["first_name"] = customers["first_name"].str.strip().str.title()
    
    customers["last_name"] = customers["last_name"].str.strip().str.title()
    
    customers["email"] = customers["email"].str.strip().str.lower()
    
    customers["country"] = customers["country"].str.strip().str.upper()
    
    customers = customers.rename(columns={"country": "country_code"})
    
    customers["country_name"] = customers["country_code"].map(country_dictionary)
    
    customers["account_type"] = customers["account_type"].str.strip().str.upper()
    
    customers["customer_status"] = customers["customer_status"].str.strip().str.upper()
    
    customers["account_created_at"] = pd.to_datetime(customers["account_created_at"])
    
    return customers