import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
import pandas as pd
from load.postgres_loader import get_connection
DIM_CUSTOMER_QUERY = f"""
        INSERT INTO warehouse.dim_customer (
        customer_id,
        first_name,
        last_name,
        email,
        country_code,
        country_name,
        account_type,
        account_created_at,
        customer_status
    )
    SELECT
    customer_id,
    first_name,
    last_name,
    email,
    country_code,
    country_name,
    account_type,
    account_created_at,
    customer_status
    FROM staging.customers;
        """

DIM_ACCOUNT_QUERY= f"""
INSERT INTO warehouse.dim_account (
    account_id,
    customer_id,
    account_type,
    balance,
    currency_code,
    currency_name,
    created_at,
    status
)
SELECT
    account_id,
    customer_id,
    account_type,
    balance,
    currency_code,
    currency_name,
    created_at,
    status
FROM staging.accounts;
"""

DIM_MERCHANT_QUERY = f"""
INSERT INTO warehouse.dim_merchant (
    merchant_id,
    merchant_name,
    merchant_category,
    country_code,
    country_name,
    risk_category
)
SELECT
    merchant_id,
    merchant_name,
    merchant_category,
    country_code,
    country_name,
    risk_category
FROM staging.merchants;
"""

DIM_DATE_QUERY = f"""
INSERT INTO warehouse.dim_date (
    date_key,
    full_date,
    year,
    quarter,
    month,
    month_name,
    day,
    day_of_week,
    day_name
)
SELECT DISTINCT
    TO_CHAR(transaction_date, 'YYYYMMDD')::INTEGER AS date_key,
    transaction_date AS full_date,
    EXTRACT(YEAR FROM transaction_date)::INTEGER AS year,
    EXTRACT(QUARTER FROM transaction_date)::INTEGER AS quarter,
    EXTRACT(MONTH FROM transaction_date)::INTEGER AS month,
    TO_CHAR(transaction_date, 'Month') AS month_name,
    EXTRACT(DAY FROM transaction_date)::INTEGER AS day,
    EXTRACT(ISODOW FROM transaction_date)::INTEGER AS day_of_week,
    TO_CHAR(transaction_date, 'Day') AS day_name
FROM staging.transactions
WHERE transaction_date IS NOT NULL;
"""

FACT_TRANSATION_QUERY = f"""
INSERT INTO warehouse.fact_transaction (
    transaction_id,
    account_id,
    customer_id,
    merchant_id,
    date_key,
    transaction_timestamp,
    transaction_type,
    amount,
    currency_code,
    currency_name,
    payment_method,
    country_code,
    country_name,
    status
)
SELECT
    t.transaction_id,
    t.account_id,
    a.customer_id,
    t.merchant_id,
    TO_CHAR(t.transaction_date, 'YYYYMMDD')::INTEGER AS date_key,
    t.transaction_timestamp,
    t.transaction_type,
    t.amount,
    t.currency_code,
    t.currency_name,
    t.payment_method,
    t.country_code,
    t.country_name,
    t.status
FROM staging.transactions t
JOIN staging.accounts a
    ON t.account_id = a.account_id;
"""
def load_into_warehouse():
    print("LOADING INTO WAREHOUSE")
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(DIM_CUSTOMER_QUERY)
        cursor.execute(DIM_ACCOUNT_QUERY)
        cursor.execute(DIM_MERCHANT_QUERY)
        cursor.execute(DIM_DATE_QUERY)
        cursor.execute(FACT_TRANSATION_QUERY)
        connection.commit()
        print("Warehouse loading successful")
    except psycopg2.Error as e:
        connection.rollback()
        print(f"Warehouse LOADING ERROR: {e}")
        raise
    finally:
        cursor.close()
        connection.close()