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

GET_TOTAL_TRANSACTION_COUNT = """
    SELECT COUNT(*)
    FROM risk.risk_transaction;
"""

GET_TOTAL_TRANSACTION_AMOUNT = """
    SELECT COALESCE(SUM(amount), 0)
    FROM risk.risk_transaction;
"""

GET_HIGH_RISK_TRANSACTIONS = """
    SELECT COUNT(*)
    FROM risk.risk_transaction
    WHERE risk_level = 'HIGH';
"""

GET_CRITICAL_RISK_TRANSACTIONS = """
    SELECT COUNT(*)
    FROM risk.risk_transaction
    WHERE risk_level = 'CRITICAL';
"""

GET_TOTAL_ACCOUNT_COUNT = """
    SELECT COUNT(*)
    FROM risk.risk_account;
"""

GET_HIGH_RISK_ACCOUNTS = """
    SELECT COUNT(*)
    FROM risk.risk_account
    WHERE account_risk_level = 'HIGH';
"""

GET_CRITICAL_RISK_ACCOUNTS = """
    SELECT COUNT(*)
    FROM risk.risk_account
    WHERE account_risk_level = 'CRITICAL';
"""

GET_TOTAL_CUSTOMER_COUNT = """
    SELECT COUNT(*)
    FROM risk.risk_customer;
"""

GET_HIGH_RISK_CUSTOMERS = """
    SELECT COUNT(*)
    FROM risk.risk_customer
    WHERE customer_risk_level = 'HIGH';
"""

GET_CRITICAL_RISK_CUSTOMERS = """
    SELECT COUNT(*)
    FROM risk.risk_customer
    WHERE customer_risk_level = 'CRITICAL';
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

def fetch_overview_data():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(GET_TOTAL_TRANSACTION_COUNT)
        total_transaction_count = cursor.fetchone()[0]
        
        cursor.execute(GET_TOTAL_TRANSACTION_AMOUNT)
        total_transaction_amount = cursor.fetchone()[0]
        
        cursor.execute(GET_TOTAL_CUSTOMER_COUNT)
        total_customer_count = cursor.fetchone()[0]
        
        cursor.execute(GET_TOTAL_ACCOUNT_COUNT)
        total_account_count = cursor.fetchone()[0]
        
        cursor.execute(GET_HIGH_RISK_TRANSACTIONS)
        high_risk_transactions = cursor.fetchone()[0]
        
        cursor.execute(GET_HIGH_RISK_CUSTOMERS)
        high_risk_customers = cursor.fetchone()[0]
        
        cursor.execute(GET_HIGH_RISK_ACCOUNTS)
        high_risk_accounts = cursor.fetchone()[0]
        
        cursor.execute(GET_CRITICAL_RISK_TRANSACTIONS)
        critical_risk_transactions = cursor.fetchone()[0]
        
        cursor.execute(GET_CRITICAL_RISK_CUSTOMERS)
        critical_risk_customers =cursor.fetchone()[0]
        
        cursor.execute(GET_CRITICAL_RISK_ACCOUNTS)
        critical_risk_accounts = cursor.fetchone()[0]
        
        return {
          "total_transaction_count" : total_transaction_count,
          "total_transaction_amount" : total_transaction_amount,
          "total_customer_count" : total_customer_count,
          "total_account_count" : total_account_count,
          "high_risk_transactions" : high_risk_transactions,
          "high_risk_customers" : high_risk_customers,
          "high_risk_accounts" : high_risk_accounts,
          "critical_risk_transactions" : critical_risk_transactions,
          "critical_risk_customers" : critical_risk_customers,
          "critical_risk_accounts" : critical_risk_accounts
        }
    except psycopg2.Error as e:
        print(f"ERROR FETCHING OVERVIEW DATA : {e}")
        raise
    finally:
        cursor.close()
        connection.close()
