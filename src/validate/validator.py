import pandas as pd
import re
from datetime import datetime
SUPPORTED_COUNTRIES = {
    "FR", "DE", "ES", "IT", "NL",
    "BE", "GB", "US", "CA", "AU",
    "JP", "SG", "AE", "IN", "PK"
}

VALID_ACCOUNT_TYPES = {
    "CHECKING",
    "SAVINGS",
    "BUSINESS"
}

VALID_CUSTOMER_STATUSES = {
    "ACTIVE",
    "SUSPENDED",
    "CLOSED"
}
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
    invalid_rows = df[required_fields].isna()
    duplicate_ids = df.loc[df[pk].duplicated(),pk].tolist()

    return invalid_rows,duplicate_ids

def validate_customer_quality(customers):
    quality_issues = {}

    # Email format
    email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    invalid_email = (
        customers["email"].notna()
        & ~customers["email"].str.match(email_pattern, na=False)
    )

    if invalid_email.any():
        quality_issues["invalid_email"] = customers.loc[
            invalid_email, "customer_id"
        ].tolist()

    # Empty or whitespace-only text fields
    text_columns = [
        "customer_id",
        "first_name",
        "last_name",
        "email",
        "country",
        "account_type",
        "customer_status"
    ]

    for column in text_columns:
        invalid_text = customers[column].notna() & customers[column].str.strip().eq("")

        if invalid_text.any():
            quality_issues[f"empty_{column}"] = customers.loc[
                invalid_text, "customer_id"
            ].tolist()

    # Customer ID format
    invalid_id = ~customers["customer_id"].str.match(
        r"^CUST\d{6}$",
        na=False
    )

    if invalid_id.any():
        quality_issues["invalid_customer_id_format"] = customers.loc[
            invalid_id, "customer_id"
        ].tolist()

    # Name quality
    invalid_first_name = (
        customers["first_name"].notna()
        & ~customers["first_name"].str.match(
            r"^[A-Za-zÀ-ÿ' -]+$",
            na=False
        )
    )

    invalid_last_name = (
        customers["last_name"].notna()
        & ~customers["last_name"].str.match(
            r"^[A-Za-zÀ-ÿ' -]+$",
            na=False
        )
    )

    if invalid_first_name.any():
        quality_issues["invalid_first_name"] = customers.loc[
            invalid_first_name, "customer_id"
        ].tolist()

    if invalid_last_name.any():
        quality_issues["invalid_last_name"] = customers.loc[
            invalid_last_name, "customer_id"
        ].tolist()

    return quality_issues


def produce_report(validation_results):

    print("\n" + "=" * 60)
    print(f"{validation_results["meta"]["name"].upper()} DATA QUALITY REPORT")
    print("=" * 60)

    print(f"Dataset : {validation_results["meta"]["name"]}.csv")
    print(f"Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
    print(f"Total Records: {len(validation_results["meta"]["df"])}")

    print("\n" + "=" * 60)
    print("1. SCHEMA VALIDATION")
    print("=" * 60)

    if not validation_results["schema"]["missing_cols"] and not validation_results["schema"]["unexpected_cols"] and not validation_results["schema"]["invalid_dtypes"]:
        print("STATUS : PASS")
    else:
        print("STATUS: FAIL")

    print(f"\n Missing Columns: {str(validation_results["schema"]["missing_cols"])}")
    print(f"Unexpected Columns: {str(validation_results["schema"]["unexpected_cols"])}")

    print("\n")
    for column in validation_results["meta"]["expected_dtypes"]:
        if column in validation_results["schema"]["invalid_dtypes"]:
            print(f"  {column:<20} FAIL")
        else:
            print(f"  {column:<20} PASS")

    
    print("\n" + "=" * 60)
    print("2. STRUCTURAL VALIDATION")
    print("=" * 60)

    print("STATUS : FAIL")

    print("\nRequired Fields:")
    for column in validation_results["meta"]["required_fields"]:
        if validation_results["structural"]["invalid_rows"][column].any():
            print(f"  {column:<20} FAIL")
        else:
            print(f"  {column:<20} PASS")

    print("\nPrimary Key:")
    print(
        f"  Missing IDs:   "
        f"{validation_results['structural']['invalid_rows'][validation_results['meta']['pk']].sum():<10}"
    )
    print(
        f"  Duplicate IDs: "
        f"{len(validation_results['structural']['duplicate_ids']):<10}"
    )

    print(
        f"\nInvalid Records: "
        f"{validation_results['structural']['invalid_rows'].any(axis=1).sum():<10}"
    )

    print("\n" + "=" * 60)
    print("3. BUSINESS RULE VALIDATION")
    print("=" * 60)


def validate_customers(customers):
    expected_cols = ["customer_id", "first_name", "last_name", "email", "country", "account_type", "account_created_at", "customer_status"]
    expected_dtypes = {
    "customer_id": "str",
    "first_name": "str",
    "last_name": "str",
    "email": "str",
    "country": "str",
    "account_type": "str",
    "account_created_at": "datetime",
    "customer_status": "str"
    }
    required_fields= ["customer_id", "first_name", "last_name", "country", "account_type", "account_created_at", "customer_status"]

    #LAYER 1 Schema Validation
    missing_cols,unexpected_cols,invalid_dtypes= validate_schema(customers,expected_cols,expected_dtypes)


    #LAYER 2 Structural Validation
    invalid_rows,duplicate_ids = validate_structure(customers,"customer_id",required_fields)

    #Layer 3 Business Rules
    invalid_countries = ~customers["country"].isin(SUPPORTED_COUNTRIES)
    invalid_accounts = ~customers["account_type"].isin(VALID_ACCOUNT_TYPES)
    invalid_statuses = ~customers["account_type"].isin(VALID_CUSTOMER_STATUSES)

    #Check if date is in future
    dates = pd.to_datetime(
    customers["account_created_at"],
    errors="coerce"
    )
    invalid_dates = dates > pd.Timestamp.now()

    business_issues = {"Invalid Countries": invalid_countries,"Invalid Accounts": invalid_accounts,"Invalid Statuses" : invalid_statuses,"Invalid Dates" : invalid_dates}

    #Layer 4 Data Quality
    quality_issues = validate_customer_quality(customers)

    validation_results = {
    "meta":{
        "name" : "customers",
        "df" : customers,
        "expected_dtypes" : expected_dtypes,
        "required_fields" : required_fields,
        "pk" : "customer_id"
    },
    "schema": {
        "missing_cols": missing_cols,
        "unexpected_cols": unexpected_cols,
        "invalid_dtypes": invalid_dtypes
    },
    "structural": {
        "invalid_rows": invalid_rows,
        "duplicate_ids": duplicate_ids
    },
    "business": business_issues,
    "quality": quality_issues
    }


    produce_report(validation_results)

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

