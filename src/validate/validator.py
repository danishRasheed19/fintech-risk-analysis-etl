import pandas as pd
import re
from datetime import datetime
from validate.validation_exceptions import ValidationError
from reporting.html_report import produce_html_report
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
VALID_MERCHANT_CATEGORIES = {
    "GROCERY",
    "RESTAURANT",
    "E_COMMERCE",
    "TRAVEL",
    "ENTERTAINMENT",
    "ELECTRONICS",
    "FASHION",
    "HEALTHCARE",
    "TRANSPORT",
    "UTILITIES",
    "GAMING",
    "FINANCIAL_SERVICES"
}
VALID_RISK_CATEGORIES = {
    "LOW",
    "MEDIUM",
    "HIGH"
}

VALID_CURRENCIES ={
    "EUR",
    "GBP",
    "USD",
    "CAD",
    "AUD",
    "JPY",
    "SGD",
    "AED",
    "INR",
    "PKR"
}
VALID_ACCOUNT_STATUSES = {
    "ACTIVE",
    "CLOSED",
    "SUSPENDED"
}

VALID_TRANSACTION_TYPES = {
    "PURCHASE",
    "TRANSFER",
    "WITHDRAWAL",
    "PAYMENT",
    "REFUND"
}

VALID_PAYMENT_METHODS = {
    "CARD",
    "BANK_TRANSFER",
    "DIRECT_DEBIT",
    "CASH",
    "DIGITAL_WALLET"
}

VALID_TRANSACTION_STATUSES = [
    "COMPLETED",
    "FAILED",
    "PENDING",
    "REVERSED"
]

def validate_input(df,name):
    if df is None:
        raise ValidationError(f"{name} data is None")

    if not isinstance(df, pd.DataFrame):
        raise ValidationError(
            f"{name} must be a pandas DataFrame"
        )
    if df.empty:
        raise ValidationError(
            f"{name} DataFrame is empty"
        )
def validate_schema(df,expected_cols,expected_dtypes):
    missing_cols =set(expected_cols) - set(df.columns)
    unexpected_cols = set(df.columns) - set(expected_cols)
    invalid_dtypes = validate_dtypes(df,expected_dtypes)

    return missing_cols,unexpected_cols,invalid_dtypes

def validate_dtypes(df, expected_dtypes):
    invalid_dtypes = {}

    for column, expected_type in expected_dtypes.items():
        if column not in df.columns:
            continue
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
        quality_issues["invalid email"] = customers.loc[
            invalid_email, "customer_id"
        ].tolist()

    # Missing emails
    missing_email = customers["email"].isna()

    if missing_email.any():
        quality_issues["missing email"] = customers.loc[
            missing_email, "customer_id"
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
        quality_issues["invalid customer id format"] = customers.loc[
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
        quality_issues["invalid first name"] = customers.loc[
            invalid_first_name, "customer_id"
        ].tolist()

    if invalid_last_name.any():
        quality_issues["invalid last name"] = customers.loc[
            invalid_last_name, "customer_id"
        ].tolist()

    return quality_issues

def validate_merchant_quality(merchants):

    quality_issues = {}

    # Merchant ID format
    invalid_id = ~merchants["merchant_id"].str.match(
        r"^MER\d{5}$",
        na=False
    )

    if invalid_id.any():
        quality_issues["invalid merchant id format"] = merchants.loc[
            invalid_id, "merchant_id"
        ].tolist()

    # Empty or whitespace-only text fields
    text_columns = [
        "merchant_id",
        "merchant_name",
        "merchant_category",
        "country",
        "risk_category"
    ]

    for column in text_columns:

        invalid_text = (
            merchants[column].notna()
            & merchants[column].ne(merchants[column].str.strip())
        )

        if invalid_text.any():
            quality_issues[f"whitespace {column}"] = merchants.loc[
                invalid_text, "merchant_id"
            ].tolist()

    return quality_issues

def validate_account_quality(accounts):

    quality_issues = {}

    # Account ID format
    invalid_account_id = ~accounts["account_id"].str.match(
        r"^ACC\d{7}$",
        na=False
    )

    if invalid_account_id.any():
        quality_issues["invalid account id format"] = accounts.loc[
            invalid_account_id, "account_id"
        ].tolist()

    # Customer ID format
    invalid_customer_id = ~accounts["customer_id"].str.match(
        r"^CUST\d{6}$",
        na=False
    )

    if invalid_customer_id.any():
        quality_issues["invalid customer id format"] = accounts.loc[
            invalid_customer_id, "account_id"
        ].tolist()

    # Empty or whitespace-only text fields
    text_columns = [
        "account_id",
        "customer_id",
        "account_type",
        "currency",
        "status"
    ]

    for column in text_columns:

        invalid_text = (
            accounts[column].notna()
            & accounts[column].ne(accounts[column].str.strip())
        )

        if invalid_text.any():
            quality_issues[f"whitespace {column}"] = accounts.loc[
                invalid_text, "account_id"
            ].tolist()

    return quality_issues

def produce_report(validation_results):

    report_status = True

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
        report_status = False
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

    if (validation_results["structural"]["invalid_rows"].any(axis=1).sum() == 0) and (len(validation_results['structural']['duplicate_ids']) == 0):
        print("STATUS : PASS")
    else:
        report_status = False
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

    business_issues = validation_results["business"]["issues"]
    if not business_issues:
        print("STATUS : PASS")
    else:
        report_status = False
        print("STATUS : FAIL")

    print("\n")

    for key,value in business_issues.items():
        print(f"{key.upper()}: {value.sum()} \n")

    print("\n" + "=" * 60)
    print("4. DATA QUALITY VALIDATION")
    print("=" * 60)

    quality_issues = validation_results["quality"]["issues"]

    if not quality_issues:
        print("STATUS : PASS")
    else:
        report_status = False
        print("STATUS : FAIL")

    print("\n")

    for key,value in quality_issues.items():
        print(f"{key.upper()} : {len(value):<20} \n")

    print("\n" + "=" * 60)
    print("OVERALL RESULT")
    print("=" * 60)

    if report_status:
        print ("STATUS : PASS")
    else:
        print ("STATUS : FAIL")

    print (f"Total Records: {len(validation_results["meta"]["df"]):<20}")
    print (f"Valid Records: {(~validation_results["overall_invalid"]).sum():<20}")
    print (f"Invalid Records: {validation_results["overall_invalid"].sum():<20}")

    print("\n" + "=" * 60)
    print(f"END OF {validation_results["meta"]["name"].upper()} REPORT")
    print("=" * 60)

def validate_customers(customers, console = False, html_report = False):
    validate_input(customers,"Customers")
    expected_cols = [
        "customer_id",
        "first_name",
        "last_name",
        "email",
        "country",
        "account_type",
        "account_created_at",
        "customer_status"
    ]

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

    required_fields = [
        "customer_id",
        "first_name",
        "last_name",
        "country",
        "account_type",
        "account_created_at",
        "customer_status"
    ]

    # Layer 1: Schema Validation
    missing_cols, unexpected_cols, invalid_dtypes = validate_schema(
        customers,
        expected_cols,
        expected_dtypes
    )

    # Schema-level mask
    # Schema issues aren't naturally row-level, so start with all False
    schema_invalid = pd.Series(False, index=customers.index)

    # Layer 2: Structural Validation
    invalid_rows, duplicate_ids = validate_structure(
        customers,
        "customer_id",
        required_fields
    )

    # Convert column-level missing-value DataFrame
    # into a row-level mask
    structural_invalid = invalid_rows.any(axis=1)

    # Add duplicate IDs to structural mask
    structural_invalid = (
        structural_invalid
        | customers["customer_id"].duplicated()
    )

    # Layer 3: Business Rules
    invalid_countries = ~customers["country"].isin(SUPPORTED_COUNTRIES)

    invalid_accounts = ~customers["account_type"].isin(
        VALID_ACCOUNT_TYPES
    )

    invalid_statuses = ~customers["customer_status"].isin(
        VALID_CUSTOMER_STATUSES
    )

    # Check if date is in future
    dates = pd.to_datetime(
        customers["account_created_at"],
        errors="coerce"
    )

    invalid_dates = dates > pd.Timestamp.now()

    # Combine all business rules into one row-level mask
    business_invalid = (
        invalid_countries
        | invalid_accounts
        | invalid_statuses
        | invalid_dates
    )

    if invalid_countries.any() or invalid_accounts.any() or invalid_statuses.any() or invalid_dates.any():
        business_issues = {
            "Invalid Countries": invalid_countries,
            "Invalid Accounts": invalid_accounts,
            "Invalid Statuses": invalid_statuses,
            "Invalid Dates": invalid_dates
        }

    # Layer 4: Data Quality
    quality_issues = validate_customer_quality(customers)

    # Overall quality mask
    quality_invalid = pd.Series(False, index=customers.index)

    # We need to convert the customer IDs stored in quality_issues
    # back into a row-level mask
    for issue_ids in quality_issues.values():
        quality_invalid = (
            quality_invalid
            | customers["customer_id"].isin(issue_ids)
        )

    # Overall invalid mask
    overall_invalid = (
        structural_invalid
        | business_invalid
        | quality_invalid
    )

    validation_results = {

        "meta": {
            "name": "customers",
            "df": customers,
            "expected_dtypes": expected_dtypes,
            "required_fields": required_fields,
            "pk": "customer_id"
        },

        "schema": {
            "missing_cols": missing_cols,
            "unexpected_cols": unexpected_cols,
            "invalid_dtypes": invalid_dtypes,
            "invalid": schema_invalid
        },

        "structural": {
            "invalid_rows": invalid_rows,
            "duplicate_ids": duplicate_ids,
            "invalid": structural_invalid
        },

        "business": {
            "issues": business_issues,
            "invalid": business_invalid
        },

        "quality": {
            "issues": quality_issues,
            "invalid": quality_invalid
        },

        "overall_invalid": overall_invalid
    }
    if console:
        produce_report(validation_results)
    if html_report:
        produce_html_report(validation_results)
    return overall_invalid

def validate_merchants(merchants, console = False, html_report = False):
    validate_input(merchants,"merchants")
    expected_cols = [
    "merchant_id",
    "merchant_name",
    "merchant_category",
    "country",
    "risk_category"
    ]

    expected_dtypes = {
    "merchant_id": "str",
    "merchant_name": "str",
    "merchant_category": "str",
    "country": "str",
    "risk_category": "str"
    }

    required_fields = [
    "merchant_id",
    "merchant_name",
    "merchant_category",
    "country",
    "risk_category"
    ]

    # Layer 1: Schema Validation
    missing_cols, unexpected_cols, invalid_dtypes = validate_schema(
            merchants,
            expected_cols,
            expected_dtypes
        )
    
    # Schema-level mask
    # Schema issues aren't naturally row-level, so start with all False
    schema_invalid = pd.Series(False, index=merchants.index)

    # Layer 2: Structural Validation
    invalid_rows, duplicate_ids = validate_structure(
        merchants,
        "merchant_id",
        required_fields
    )
    
    # Convert column-level missing-value DataFrame
    # into a row-level mask
    structural_invalid = invalid_rows.any(axis=1)
    
    # Add duplicate IDs to structural mask
    structural_invalid = (
        structural_invalid
        | merchants["merchant_id"].duplicated()
    )

    # Layer 3: Business Rules
    invalid_countries = ~merchants["country"].isin(SUPPORTED_COUNTRIES)

    invalid_merchant_categories = ~merchants["merchant_category"].isin(
        VALID_MERCHANT_CATEGORIES
    )

    invalid_risk_categories = ~merchants["risk_category"].isin(
        VALID_RISK_CATEGORIES
    )

    # Combine all business rules into one row-level mask
    business_invalid = (
        invalid_countries
        | invalid_merchant_categories
        | invalid_risk_categories
    )

    if invalid_countries.any() or invalid_merchant_categories.any() or invalid_risk_categories.any():
        business_issues = {
            "Invalid Countries": invalid_countries,
            "Invalid Merchant Categories": invalid_merchant_categories,
            "Invalid Risk Categories": invalid_risk_categories,
        }
    else:
        business_issues = {}

    # Layer 4: Data Quality
    quality_issues = validate_merchant_quality(merchants)

    # Overall quality mask
    quality_invalid = pd.Series(False, index=merchants.index)

    # We need to convert the customer IDs stored in quality_issues
    # back into a row-level mask
    for issue_ids in quality_issues.values():
        quality_invalid = (
            quality_invalid
            | merchants["merchant_id"].isin(issue_ids)
        )

    # Overall invalid mask
    overall_invalid = (
        structural_invalid
        | business_invalid
        | quality_invalid
    )

    validation_results = {
    
            "meta": {
                "name": "merchants",
                "df": merchants,
                "expected_dtypes": expected_dtypes,
                "required_fields": required_fields,
                "pk": "merchant_id"
            },
    
            "schema": {
                "missing_cols": missing_cols,
                "unexpected_cols": unexpected_cols,
                "invalid_dtypes": invalid_dtypes,
                "invalid": schema_invalid
            },
    
            "structural": {
                "invalid_rows": invalid_rows,
                "duplicate_ids": duplicate_ids,
                "invalid": structural_invalid
            },
    
            "business": {
                "issues": business_issues,
                "invalid": business_invalid
            },
    
            "quality": {
                "issues": quality_issues,
                "invalid": quality_invalid
            },
    
            "overall_invalid": overall_invalid
    }
    if console:
        produce_report(validation_results)
    if html_report:
        produce_html_report(validation_results)
    return overall_invalid


def validate_accounts(accounts, console = False, html_report = False):
    validate_input(accounts,"accounts")
    expected_cols = [
    "account_id",
    "customer_id",
    "account_type",
    "currency",
    "balance",
    "created_at",
    "status"
    ]

    expected_dtypes = {
    "account_id": "str",
    "customer_id": "str",
    "account_type": "str",
    "currency": "str",
    "balance": "float64",
    "created_at": "datetime",
    "status": "str"
    }

    required_fields = [
    "account_id",
    "customer_id",
    "account_type",
    "currency",
    "balance",
    "created_at",
    "status"
    ]
    
    # Layer 1: Schema Validation
    missing_cols, unexpected_cols, invalid_dtypes = validate_schema(
        accounts,
        expected_cols,
        expected_dtypes
    )
        
    # Schema-level mask
    # Schema issues aren't naturally row-level, so start with all False
    schema_invalid = pd.Series(False, index=accounts.index)
    
    # Layer 2: Structural Validation
    invalid_rows, duplicate_ids = validate_structure(
        accounts,
        "account_id",
        required_fields
    )
        
    # Convert column-level missing-value DataFrame
    # into a row-level mask
    structural_invalid = invalid_rows.any(axis=1)
        
    # Add duplicate IDs to structural mask
    structural_invalid = (
        structural_invalid
        | accounts["account_id"].duplicated()
    )
    
    # Layer 3: Business Rules
    invalid_account_types = ~accounts["account_type"].isin(VALID_ACCOUNT_TYPES)
    
    invalid_accounts_statuses = ~accounts["status"].isin(VALID_ACCOUNT_STATUSES)
    
    invalid_currencies = ~accounts["currency"].isin(VALID_CURRENCIES)
    
    invalid_balances = accounts["balance"] < 0
    
    # Check if date is in future
    dates = pd.to_datetime(
        accounts["created_at"],
        errors="coerce"
    )
    
    invalid_dates = dates > pd.Timestamp.now()
    
    # Combine all business rules into one row-level mask
    business_invalid = (
        invalid_account_types
        | invalid_accounts_statuses
        | invalid_currencies
        | invalid_balances
        | invalid_dates
    )
    
    if invalid_account_types.any() or invalid_accounts_statuses.any() or invalid_balances.any() or invalid_currencies.any() or invalid_dates.any():
            business_issues = {
                "Invalid Account Types": invalid_account_types,
                "Invalid Account Statuses": invalid_accounts_statuses,
                "Invalid Balances": invalid_balances,
                "Invalid Currencies": invalid_currencies,
                "Invalid Dates": invalid_dates
            }
    else:
        business_issues = {}
    
    # Layer 4: Data Quality
    quality_issues = validate_account_quality(accounts)
    
    # Overall quality mask
    quality_invalid = pd.Series(False, index=accounts.index)
    
    # We need to convert the customer IDs stored in quality_issues
    # back into a row-level mask
    for issue_ids in quality_issues.values():
        quality_invalid = (
            quality_invalid
            | accounts["account_id"].isin(issue_ids)
        )
    
    # Overall invalid mask
    overall_invalid = (
        structural_invalid
        | business_invalid
        | quality_invalid
    )
    
    validation_results = {
        
                "meta": {
                    "name": "accounts",
                    "df": accounts,
                    "expected_dtypes": expected_dtypes,
                    "required_fields": required_fields,
                    "pk": "account_id"
                },
        
                "schema": {
                    "missing_cols": missing_cols,
                    "unexpected_cols": unexpected_cols,
                    "invalid_dtypes": invalid_dtypes,
                    "invalid": schema_invalid
                },
        
                "structural": {
                    "invalid_rows": invalid_rows,
                    "duplicate_ids": duplicate_ids,
                    "invalid": structural_invalid
                },
        
                "business": {
                    "issues": business_issues,
                    "invalid": business_invalid
                },
        
                "quality": {
                    "issues": quality_issues,
                    "invalid": quality_invalid
                },
        
                "overall_invalid": overall_invalid
    }
    if console:
        produce_report(validation_results)
    if html_report:
        produce_html_report(validation_results)
    return overall_invalid


def validate_transaction_quality(transactions):

    quality_issues = {}

    # Transaction ID format
    invalid_transaction_id = transactions["transaction_id"].notna() & ~transactions["transaction_id"].str.match(
        r"^TX\d{9}$",
        na=False
    )

    if invalid_transaction_id.any():
        quality_issues["invalid transaction id format"] = transactions.loc[
            invalid_transaction_id, "transaction_id"
        ].tolist()

    # Account ID format
    invalid_account_id = transactions["account_id"].notna() & ~transactions["account_id"].str.match(
        r"^ACC\d{7}$",
        na=False
    )

    if invalid_account_id.any():
        quality_issues["invalid account id format"] = transactions.loc[
            invalid_account_id, "transaction_id"
        ].tolist()

    # Merchant ID format
    invalid_merchant_id = (
    transactions["merchant_id"].notna()
    & ~transactions["merchant_id"].str.match(
        r"^MER\d{5}$",
        na=False
    )
)

    if invalid_merchant_id.any():
        quality_issues["invalid merchant id format"] = transactions.loc[
            invalid_merchant_id, "transaction_id"
        ].tolist()

    # Empty or whitespace-only text fields
    text_columns = [
        "transaction_id",
        "account_id",
        "merchant_id",
        "transaction_type",
        "currency",
        "payment_method",
        "country",
        "status"
    ]

    for column in text_columns:

        invalid_text = (
            transactions[column].notna()
            & transactions[column].ne(
                transactions[column].str.strip()
            )
        )

        if invalid_text.any():
            quality_issues[f"whitespace {column}"] = transactions.loc[
                invalid_text, "transaction_id"
            ].tolist()

    return quality_issues

def validate_transactions(transactions ,console = False, html_report = False):
    validate_input(transactions,"transactions")
    expected_cols = [
    "transaction_id",
    "account_id",
    "merchant_id",
    "transaction_timestamp",
    "transaction_type",
    "amount",
    "currency",
    "payment_method",
    "country",
    "status"
    ]

    expected_dtypes = {
    "transaction_id": "str",
    "account_id": "str",
    "merchant_id": "str",
    "transaction_timestamp": "datetime",
    "transaction_type": "str",
    "amount": "float64",
    "currency": "str",
    "payment_method": "str",
    "country": "str",
    "status": "str"
    }

    required_fields = [
    "transaction_id",
    "account_id",
    "merchant_id",
    "transaction_timestamp",
    "transaction_type",
    "amount",
    "currency",
    "payment_method",
    "country",
    "status"
    ]
    
    # Layer 1: Schema Validation
    missing_cols, unexpected_cols, invalid_dtypes = validate_schema(
        transactions,
        expected_cols,
        expected_dtypes
    )
        
    # Schema-level mask
    # Schema issues aren't naturally row-level, so start with all False
    schema_invalid = pd.Series(False, index=transactions.index)
    
    # Layer 2: Structural Validation
    invalid_rows, duplicate_ids = validate_structure(
        transactions,
        "transaction_id",
        required_fields
    )
        
    # Convert column-level missing-value DataFrame
    # into a row-level mask
    structural_invalid = invalid_rows.any(axis=1)
        
    # Add duplicate IDs to structural mask
    structural_invalid = (
        structural_invalid
        | transactions["transaction_id"].duplicated()
    )
    
    # Layer 3: Business Rules
    invalid_transaction_types = ~transactions["transaction_type"].isin(VALID_TRANSACTION_TYPES)
    
    invalid_payment_methods = ~transactions["payment_method"].isin(VALID_PAYMENT_METHODS)
    
    invalid_currencies = ~transactions["currency"].isin(VALID_CURRENCIES)
    
    invalid_countries = ~transactions["country"].isin(SUPPORTED_COUNTRIES)
    
    invalid_transaction_statuses = ~transactions["status"].isin(VALID_TRANSACTION_STATUSES)
    
    invalid_amounts = transactions["amount"] < 0
    
    # Check if date is in future
    dates = pd.to_datetime(
        transactions["transaction_timestamp"],
        errors="coerce"
    )
    
    invalid_dates = dates > pd.Timestamp.now()
    
    # Combine all business rules into one row-level mask
    business_invalid = (
        invalid_transaction_types
        | invalid_payment_methods
        | invalid_currencies
        | invalid_amounts
        | invalid_dates
        | invalid_countries
        | invalid_transaction_statuses
    )
    
    if invalid_transaction_types.any() or invalid_payment_methods.any() or invalid_amounts.any() or invalid_currencies.any() or invalid_dates.any() or invalid_countries.any() or invalid_transaction_statuses.any():
            business_issues = {
                "Invalid Transaction Types": invalid_transaction_types,
                "Invalid Payment Methods": invalid_payment_methods,
                "Invalid Amounts": invalid_amounts,
                "Invalid Currencies": invalid_currencies,
                "Invalid Dates": invalid_dates,
                "Invalid Countries" : invalid_countries,
                "Invalid Transaction Statuses": invalid_transaction_statuses
            }
    else:
        business_issues = {}
    
    # Layer 4: Data Quality
    quality_issues = validate_transaction_quality(transactions)
    
    # Overall quality mask
    quality_invalid = pd.Series(False, index=transactions.index)
    
    # We need to convert the customer IDs stored in quality_issues
    # back into a row-level mask
    for issue_ids in quality_issues.values():
        quality_invalid = (
            quality_invalid
            | transactions["transaction_id"].isin(issue_ids)
        )
    
    # Overall invalid mask
    overall_invalid = (
        structural_invalid
        | business_invalid
        | quality_invalid
    )
    
    validation_results = {
        
                "meta": {
                    "name": "transactions",
                    "df": transactions,
                    "expected_dtypes": expected_dtypes,
                    "required_fields": required_fields,
                    "pk": "transaction_id"
                },
        
                "schema": {
                    "missing_cols": missing_cols,
                    "unexpected_cols": unexpected_cols,
                    "invalid_dtypes": invalid_dtypes,
                    "invalid": schema_invalid
                },
        
                "structural": {
                    "invalid_rows": invalid_rows,
                    "duplicate_ids": duplicate_ids,
                    "invalid": structural_invalid
                },
        
                "business": {
                    "issues": business_issues,
                    "invalid": business_invalid
                },
        
                "quality": {
                    "issues": quality_issues,
                    "invalid": quality_invalid
                },
        
                "overall_invalid": overall_invalid
    }
    if console:
        produce_report(validation_results)
    if html_report:
        produce_html_report(validation_results)
    return overall_invalid

def validate_data(customers,accounts,merchants,transactions, console = False, html_report = False):
    validation_results = {}
    print("Validating Data")

    datasets = [
        (customers,validate_customers,"Customers"),
        (accounts,validate_accounts,"Accounts"),
        (merchants,validate_merchants,"Merchants"),
        (transactions,validate_transactions,"Transactions")
    ]
    for df, validator,name in datasets:
        try:
            validation_results [name.lower()] = validator(df, console,html_report)
            
        except ValidationError as e:
            print(f"\n{name.upper()} VALIDATION ERROR: {e}")
            validation_results[name.lower()] = {
            "status": "ERROR",
            "error_type": "VALIDATION_ERROR",
            "error": str(e)
            }
        except Exception as e:
            print(f"\n{name.upper()} UNEXPECTED ERROR: {e}")
            validation_results[name.lower()] = {
                        "status": "ERROR",
                        "error_type": "UNEXPECTED_ERROR",
                        "error": str(e)
                }
    return validation_results
