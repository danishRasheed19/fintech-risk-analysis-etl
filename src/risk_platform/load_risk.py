import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from src.load.postgres_loader import get_connection


def load_into_risk_warehouse(
    transaction_df,
    account_profiles,
    customer_profiles
):
    print("LOADING INTO WARHEOUSE")

    connection = get_connection()
    cursor = connection.cursor()

    try:

        upsert_risk_transactions(cursor, transaction_df)

        upsert_risk_accounts(cursor, account_profiles)

        upsert_risk_customers(cursor, customer_profiles)

        connection.commit()
        
        print("LOADING SUCCCESSFUL")

    except psycopg2.Error as e:

        connection.rollback()

        print(f"Risk LOAD ERROR: {e}")
        raise

    except Exception as e:

        connection.rollback()

        print(
            f"UNEXPECTED ERROR DURING LOADING into Risk: {e}"
        )
        raise

    finally:

        cursor.close()
        connection.close()
        

def upsert_risk_transactions(cursor, df):

    query = """

        INSERT INTO risk.risk_transaction (
            transaction_id,
            account_id,
            customer_id,
            merchant_risk_score,
            country_mismatch,
            is_reversed,
            is_suspended_account,
            is_closed_account,
            is_weekend,
            is_night,
            risk_score,
            risk_level,
            risk_reasons
        )

        VALUES %s

        ON CONFLICT (transaction_id)

        DO UPDATE SET
            account_id = EXCLUDED.account_id,
            customer_id = EXCLUDED.customer_id,
            merchant_risk_score = EXCLUDED.merchant_risk_score,
            country_mismatch = EXCLUDED.country_mismatch,
            is_reversed = EXCLUDED.is_reversed,
            is_suspended_account = EXCLUDED.is_suspended_account,
            is_closed_account = EXCLUDED.is_closed_account,
            is_weekend = EXCLUDED.is_weekend,
            is_night = EXCLUDED.is_night,
            risk_score = EXCLUDED.risk_score,
            risk_level = EXCLUDED.risk_level,
            risk_reasons = EXCLUDED.risk_reasons,
            updated_at = CURRENT_TIMESTAMP;

    """

    records = df[
        [
            "transaction_id",
            "account_id",
            "customer_id",
            "merchant_risk_score",
            "country_mismatch",
            "is_reversed",
            "is_suspended_account",
            "is_closed_account",
            "is_weekend",
            "is_night",
            "risk_score",
            "risk_level",
            "risk_reasons"
        ]
    ].itertuples(index=False, name=None)

    execute_values(
        cursor,
        query,
        records,
        page_size=1000
    )

def upsert_risk_accounts(cursor, df):

    query = """
        INSERT INTO risk.risk_account (
            account_id,
            transaction_count,
            total_transaction_amount,
            average_transaction_amount,
            average_risk_score,
            max_risk_score,
            high_risk_count,
            critical_risk_count,
            risk_transaction_ratio,
            account_risk_level
        )
        VALUES %s

        ON CONFLICT (account_id)
        DO UPDATE SET
            transaction_count = EXCLUDED.transaction_count,
            total_transaction_amount = EXCLUDED.total_transaction_amount,
            average_transaction_amount = EXCLUDED.average_transaction_amount,
            average_risk_score = EXCLUDED.average_risk_score,
            max_risk_score = EXCLUDED.max_risk_score,
            high_risk_count = EXCLUDED.high_risk_count,
            critical_risk_count = EXCLUDED.critical_risk_count,
            risk_transaction_ratio = EXCLUDED.risk_transaction_ratio,
            account_risk_level = EXCLUDED.account_risk_level,
            updated_at = CURRENT_TIMESTAMP;
    """

    records = df[
        [
            "account_id",
            "transaction_count",
            "total_transaction_amount",
            "average_transaction_amount",
            "average_risk_score",
            "max_risk_score",
            "high_risk_count",
            "critical_risk_count",
            "risk_transaction_ratio",
            "account_risk_level"
        ]
    ].itertuples(index=False, name=None)

    execute_values(
        cursor,
        query,
        records,
        page_size=1000
    )

def upsert_risk_customers(cursor, df):

    query = """
        INSERT INTO risk.risk_customer (
            customer_id,
            account_count,
            transaction_count,
            total_transaction_amount,
            average_account_risk,
            max_account_risk_score,
            critical_accounts,
            high_risk_accounts,
            risky_account_ratio,
            customer_risk_level
        )
        VALUES %s

        ON CONFLICT (customer_id)
        DO UPDATE SET
            account_count = EXCLUDED.account_count,
            transaction_count = EXCLUDED.transaction_count,
            total_transaction_amount = EXCLUDED.total_transaction_amount,
            average_account_risk = EXCLUDED.average_account_risk,
            max_account_risk_score = EXCLUDED.max_account_risk_score,
            critical_accounts = EXCLUDED.critical_accounts,
            high_risk_accounts = EXCLUDED.high_risk_accounts,
            risky_account_ratio = EXCLUDED.risky_account_ratio,
            customer_risk_level = EXCLUDED.customer_risk_level,
            updated_at = CURRENT_TIMESTAMP;
    """

    records = df[
        [
            "customer_id",
            "account_count",
            "transaction_count",
            "total_transaction_amount",
            "average_account_risk",
            "max_account_risk_score",
            "critical_accounts",
            "high_risk_accounts",
            "risky_account_ratio",
            "customer_risk_level"
        ]
    ].itertuples(index=False, name=None)

    execute_values(
        cursor,
        query,
        records,
        page_size=1000
    )