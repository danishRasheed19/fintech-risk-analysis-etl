import pandas as pd
import psycopg2
from src.load.postgres_loader import get_connection

TRANSACTION_RISK_QUERY = """
SELECT
    t.transaction_id,
    t.account_id,
    t.customer_id,
    t.merchant_id,
    t.transaction_timestamp,
    t.transaction_type,
    t.amount,
    t.currency_code AS transaction_currency,
    t.country_code AS transaction_country,
    t.status AS transaction_status,

    a.account_type,
    a.balance,
    a.currency_code AS account_currency,
    a.status AS account_status,

    c.country_code AS customer_country,
    c.customer_status,

    m.merchant_category,
    m.country_code AS merchant_country,
    m.risk_category

FROM warehouse.fact_transaction t
JOIN warehouse.dim_account a
    ON t.account_id = a.account_id
JOIN warehouse.dim_customer c
    ON t.customer_id = c.customer_id
JOIN warehouse.dim_merchant m
    ON t.merchant_id = m.merchant_id;
"""

def fetch_transaction_risk_data():
    connection = get_connection()
    try:
        return pd.read_sql(TRANSACTION_RISK_QUERY,connection)
    except psycopg2.Error as e:
            print(f"ERROR FETCHING RISK DATA: {e}")
            raise
    finally:
        connection.close()