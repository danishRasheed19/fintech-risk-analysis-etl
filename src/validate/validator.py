import pandas as pd
def validate_schema(df,expected_cols,expected_dtypes):
    missing_cols =set(expected_cols) - set(df.columns)
    unexpected_cols = set(df.columns) - set(expected_cols)
    invalid_dtypes = validate_dtypes(df,expected_dtypes)

    return missing_cols,unexpected_cols,invalid_dtypes

def validate_dtypes(df, expected_dtypes):
    invalid_dtypes = {}

    for column, expected_type in expected_dtypes.items():

        actual_type = str(df[column].dtype)

        if expected_type == "string":
            if actual_type != "object" and actual_type != "string":
                invalid_dtypes[column] = {
                    "expected": "string",
                    "actual": actual_type
                }

        elif expected_type == "numeric":
            if not pd.api.types.is_numeric_dtype(df[column]):
                invalid_dtypes[column] = {
                    "expected": "numeric",
                    "actual": actual_type
                }

        elif expected_type == "datetime":
            converted = pd.to_datetime(
                df[column],
                errors="coerce"
            )

            invalid_count = converted.isna().sum()

            if invalid_count > 0:
                invalid_dtypes[column] = {
                    "expected": "datetime",
                    "invalid_values": invalid_count
                }

    return invalid_dtypes

def validate_structure(df,pk,required_fields):
    invalid_rows = df[required_fields].isna().sum()
    duplicate_ids = df.loc[df[pk].duplicated(),pk].tolist()

    return invalid_rows,duplicate_ids
    
def validate_customers(customers):
    expected_cols = ["customer_id", "first_name", "last_name", "email", "country", "account_type", "account_created_at", "customer_status"]
    expected_dtypes = {
    "customer_id": "string",
    "first_name": "string",
    "last_name": "string",
    "email": "string",
    "country": "string",
    "account_type": "string",
    "account_created_at": "datetime",
    "customer_status": "string"
    }
    required_fields= ["customer_id", "first_name", "last_name", "country", "account_type", "account_created_at", "customer_status"]

    #LAYER 1 Schema Validation
    missing_cols,unexpected_cols,invalid_dtypes= validate_schema(customers,expected_cols,expected_dtypes)

    #LAYER 2 Structural Validation
    validate_structure(customers,"customer_id",required_fields)
    

    return None

def validate_merchants(merchants):
    return None

def validate_accounts(accounts):
    return None

def validate_transactions(transactions):
    return None

def validate_data(customers,accounts,merchants,transactions):
    print("Validating Data")

    validate_customers(customers)
    validate_merchants(merchants)
    validate_accounts(accounts)
    validate_transactions(transactions)
