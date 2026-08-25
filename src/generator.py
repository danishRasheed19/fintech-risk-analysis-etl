import os
import random
import numpy as np
import pandas as pd
from faker import Faker

# ============================================================
# CONFIGURATION
# ============================================================

SEED = 42

N_CUSTOMERS = 10_000
N_ACCOUNTS = 12_000
N_MERCHANTS = 1_000
N_TRANSACTIONS = 100_000

OUTPUT_DIR = "data/raw"

random.seed(SEED)
np.random.seed(SEED)

fake = Faker()
Faker.seed(SEED)


# ============================================================
# SETUP
# ============================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# CONSTANTS
# ============================================================

COUNTRIES = [
    "FR", "DE", "ES", "IT", "NL",
    "BE", "GB", "US", "CA", "AU",
    "JP", "SG", "AE", "IN", "PK"
]

CURRENCIES = {
    "FR": "EUR",
    "DE": "EUR",
    "ES": "EUR",
    "IT": "EUR",
    "NL": "EUR",
    "BE": "EUR",
    "GB": "GBP",
    "US": "USD",
    "CA": "CAD",
    "AU": "AUD",
    "JP": "JPY",
    "SG": "SGD",
    "AE": "AED",
    "IN": "INR",
    "PK": "PKR"
}

ACCOUNT_TYPES = [
    "CHECKING",
    "SAVINGS",
    "BUSINESS"
]

ACCOUNT_STATUSES = [
    "ACTIVE",
    "ACTIVE",
    "ACTIVE",
    "ACTIVE",
    "SUSPENDED",
    "CLOSED"
]

CUSTOMER_STATUSES = [
    "ACTIVE",
    "ACTIVE",
    "ACTIVE",
    "SUSPENDED",
    "CLOSED"
]

MERCHANT_CATEGORIES = [
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
]

RISK_CATEGORIES = [
    "LOW",
    "LOW",
    "LOW",
    "MEDIUM",
    "MEDIUM",
    "HIGH"
]

TRANSACTION_TYPES = [
    "PURCHASE",
    "PURCHASE",
    "PURCHASE",
    "TRANSFER",
    "WITHDRAWAL",
    "PAYMENT",
    "REFUND"
]

PAYMENT_METHODS = [
    "CARD",
    "CARD",
    "CARD",
    "BANK_TRANSFER",
    "DIRECT_DEBIT",
    "CASH",
    "DIGITAL_WALLET"
]

TRANSACTION_STATUSES = [
    "COMPLETED",
    "COMPLETED",
    "COMPLETED",
    "COMPLETED",
    "FAILED",
    "PENDING",
    "REVERSED"
]


# ============================================================
# 1. GENERATE CUSTOMERS
# ============================================================

def generate_customers():

    print("Generating customers...")

    customers = []

    for i in range(1, N_CUSTOMERS + 1):

        country = random.choice(COUNTRIES)

        customers.append({
            "customer_id": f"CUST{i:06d}",
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email().lower(),
            "country": country,
            "account_type": random.choice(ACCOUNT_TYPES),
            "account_created_at": fake.date_time_between(
                start_date="-5y",
                end_date="now"
            ),
            "customer_status": random.choice(CUSTOMER_STATUSES)
        })

    df = pd.DataFrame(customers)

    return df


# ============================================================
# 2. GENERATE ACCOUNTS
# ============================================================

def generate_accounts(customers):

    print("Generating accounts...")

    accounts = []

    customer_ids = customers["customer_id"].tolist()

    for i in range(1, N_ACCOUNTS + 1):

        customer_id = random.choice(customer_ids)

        customer_country = customers.loc[
            customers["customer_id"] == customer_id,
            "country"
        ].iloc[0]

        currency = CURRENCIES[customer_country]

        accounts.append({
            "account_id": f"ACC{i:07d}",
            "customer_id": customer_id,
            "account_type": random.choice(ACCOUNT_TYPES),
            "currency": currency,
            "balance": round(
                np.random.lognormal(mean=7, sigma=1.2),
                2
            ),
            "created_at": fake.date_time_between(
                start_date="-5y",
                end_date="now"
            ),
            "status": random.choice(ACCOUNT_STATUSES)
        })

    return pd.DataFrame(accounts)


# ============================================================
# 3. GENERATE MERCHANTS
# ============================================================

def generate_merchants():

    print("Generating merchants...")

    merchants = []

    for i in range(1, N_MERCHANTS + 1):

        country = random.choice(COUNTRIES)

        merchants.append({
            "merchant_id": f"MER{i:05d}",
            "merchant_name": fake.company(),
            "merchant_category": random.choice(MERCHANT_CATEGORIES),
            "country": country,
            "risk_category": random.choice(RISK_CATEGORIES)
        })

    return pd.DataFrame(merchants)


# ============================================================
# 4. GENERATE TRANSACTIONS
# ============================================================

def generate_transactions(accounts, merchants):

    print(f"Generating {N_TRANSACTIONS:,} transactions...")

    # Create fast lookup dictionaries
    account_lookup = accounts.set_index("account_id").to_dict("index")

    account_ids = list(account_lookup.keys())
    merchant_ids = merchants["merchant_id"].tolist()

    transactions = []

    start_date = pd.Timestamp("2025-08-01")
    end_date = pd.Timestamp("2026-08-25")

    time_range_seconds = int(
        (end_date - start_date).total_seconds()
    )

    for i in range(1, N_TRANSACTIONS + 1):

        account_id = random.choice(account_ids)
        merchant_id = random.choice(merchant_ids)

        account = account_lookup[account_id]

        currency = account["currency"]

        transaction_type = random.choice(
            TRANSACTION_TYPES
        )

        amount = round(
            np.random.lognormal(
                mean=3.5,
                sigma=1.1
            ),
            2
        )

        # 0.5% large transactions
        if random.random() < 0.005:
            amount = round(
                np.random.uniform(1000, 10000),
                2
            )

        random_seconds = random.randint(
            0,
            time_range_seconds
        )

        timestamp = (
            start_date +
            pd.Timedelta(seconds=random_seconds)
        )

        transactions.append({
            "transaction_id": f"TX{i:09d}",
            "account_id": account_id,
            "merchant_id": merchant_id,
            "transaction_timestamp": timestamp,
            "transaction_type": transaction_type,
            "amount": amount,
            "currency": currency,
            "payment_method": random.choice(
                PAYMENT_METHODS
            ),
            "country": customers_country_from_account(
                accounts,
                account_id
            ),
            "status": random.choice(
                TRANSACTION_STATUSES
            )
        })

    return pd.DataFrame(transactions)



# ============================================================
# HELPER
# ============================================================

def customers_country_from_account(accounts, account_id):

    account = accounts[
        accounts["account_id"] == account_id
    ].iloc[0]

    currency_to_country = {
        "EUR": "FR",
        "GBP": "GB",
        "USD": "US",
        "CAD": "CA",
        "AUD": "AU",
        "JPY": "JP",
        "SGD": "SG",
        "AED": "AE",
        "INR": "IN",
        "PKR": "PK"
    }

    return currency_to_country.get(
        account["currency"],
        "FR"
    )


# ============================================================
# 5. INTRODUCE DATA QUALITY ISSUES
# ============================================================

def introduce_data_quality_issues(
    customers,
    accounts,
    merchants,
    transactions
):

    print("Introducing data quality issues...")

    # --------------------------------------------------------
    # Missing customer emails
    # --------------------------------------------------------

    missing_email_indices = np.random.choice(
        customers.index,
        size=30,
        replace=False
    )

    customers.loc[
        missing_email_indices,
        "email"
    ] = None

    # --------------------------------------------------------
    # Duplicate customers
    # --------------------------------------------------------

    duplicate_customers = customers.sample(
        10,
        random_state=SEED
    )

    customers = pd.concat(
        [customers, duplicate_customers],
        ignore_index=True
    )

    # --------------------------------------------------------
    # Negative transaction amounts
    # --------------------------------------------------------

    negative_indices = np.random.choice(
        transactions.index,
        size=50,
        replace=False
    )

    transactions.loc[
        negative_indices,
        "amount"
    ] *= -1

    # --------------------------------------------------------
    # Missing merchant IDs
    # --------------------------------------------------------

    missing_merchant_indices = np.random.choice(
        transactions.index,
        size=50,
        replace=False
    )

    transactions.loc[
        missing_merchant_indices,
        "merchant_id"
    ] = None

    # --------------------------------------------------------
    # Invalid currencies
    # --------------------------------------------------------

    invalid_currency_indices = np.random.choice(
        transactions.index,
        size=20,
        replace=False
    )

    transactions.loc[
        invalid_currency_indices,
        "currency"
    ] = "XXX"

    # --------------------------------------------------------
    # Invalid account IDs
    # --------------------------------------------------------

    invalid_account_indices = np.random.choice(
        transactions.index,
        size=20,
        replace=False
    )

    transactions.loc[
        invalid_account_indices,
        "account_id"
    ] = "INVALID_ACCOUNT"

    return (
        customers,
        accounts,
        merchants,
        transactions
    )


# ============================================================
# 6. SAVE DATA
# ============================================================

def save_data(
    customers,
    accounts,
    merchants,
    transactions
):

    print("Saving datasets...")

    customers.to_csv(
        f"{OUTPUT_DIR}/customers.csv",
        index=False
    )

    accounts.to_csv(
        f"{OUTPUT_DIR}/accounts.csv",
        index=False
    )

    merchants.to_csv(
        f"{OUTPUT_DIR}/merchants.csv",
        index=False
    )

    transactions.to_csv(
        f"{OUTPUT_DIR}/transactions.csv",
        index=False
    )

    print("\nFiles created:")
    print(f"  customers.csv     → {len(customers):,} rows")
    print(f"  accounts.csv      → {len(accounts):,} rows")
    print(f"  merchants.csv     → {len(merchants):,} rows")
    print(f"  transactions.csv  → {len(transactions):,} rows")


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("FINTECH ETL - DATA GENERATOR")
    print("=" * 60)

    customers = generate_customers()

    accounts = generate_accounts(
        customers
    )

    merchants = generate_merchants()

    transactions = generate_transactions(
        accounts,
        merchants
    )

    (
        customers,
        accounts,
        merchants,
        transactions
    ) = introduce_data_quality_issues(
        customers,
        accounts,
        merchants,
        transactions
    )

    save_data(
        customers,
        accounts,
        merchants,
        transactions
    )

    print("\nData generation complete!")


if __name__ == "__main__":
    main()