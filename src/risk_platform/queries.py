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

GET_TRANSACTION_RISK_DISTRIBUTION = """SELECT risk_level, COUNT(*) FROM risk.risk_transaction GROUP BY risk_level;"""

GET_ACCOUNT_RISK_DISTRIBUTION = """SELECT account_risk_level, COUNT(*) FROM risk.risk_account GROUP BY account_risk_level; """

GET_CUSTOMER_RISK_DISTRIBUTION = """SELECT customer_risk_level, COUNT(*) FROM risk.risk_customer GROUP BY customer_risk_level;"""

GET_RISK_BY_COUNTRY = """
SELECT
    t.country_code AS transaction_country,
	t.country_name AS country_name,
    COUNT(*) AS transaction_count,
    COUNT(*) FILTER (
        WHERE r.risk_level = 'HIGH'
    ) AS high_risk_count,
    COUNT(*) FILTER (
        WHERE r.risk_level = 'CRITICAL'
    ) AS critical_risk_count,
    ROUND(AVG(r.risk_score), 2) AS average_risk_score
FROM risk.risk_transaction r
JOIN warehouse.fact_transaction t
    ON r.transaction_id = t.transaction_id
GROUP BY t.country_code, t.country_name
ORDER BY average_risk_score DESC;   
"""

GET_RISK_BY_MERCHANT_CATEGORY = """
select m.merchant_category AS merchant_category,
COUNT(*) AS transaction_count,
COUNT(*) FILTER(
WHERE r.risk_level = 'HIGH'
) AS high_risk_count,
COUNT(*) FILTER( 
where r.risk_level = 'CRITICAL'
) AS critical_risk_count,
ROUND(AVG(r.risk_score),2) AS average_risk_score
FROM risk.risk_transaction r
JOIN warehouse.fact_transaction t
	ON r.transaction_id = t.transaction_id
JOIN warehouse.dim_merchant m
	ON t.merchant_id = m.merchant_id
GROUP BY m.merchant_category
ORDER BY average_risk_score DESC;
"""

GET_RISK_BY_TRANSACTION_TYPE = """
select t.transaction_type AS transaction_type,
COUNT(*) AS transaction_count,
COUNT(*) FILTER(
WHERE r.risk_level = 'HIGH'
) AS high_risk_count,
COUNT(*) FILTER(
WHERE r.risk_level = 'CRITICAL'
) AS critical_risk_count,
ROUND(AVG(r.risk_score),2) AS avg_risk_score
FROM risk.risk_transaction r
JOIN warehouse.fact_transaction t
	ON r.transaction_id = t.transaction_id
GROUP BY t.transaction_type
ORDER BY avg_risk_score DESC;
"""

GET_RISK_BY_PAYMENT_METHOD = """
select t.payment_method AS payment_method,
COUNT(*) AS transaction_count,
COUNT(*) FILTER(
WHERE r.risk_level = 'HIGH'
) AS high_risk_count,
COUNT(*) FILTER(
WHERE r.risk_level = 'CRITICAL'
) AS critical_risk_count,
ROUND(AVG(r.risk_score),2) AS avg_risk_score
FROM risk.risk_transaction r
JOIN warehouse.fact_transaction t
	ON r.transaction_id = t.transaction_id
GROUP BY t.payment_method
ORDER BY avg_risk_score DESC;
"""

GET_RISK_BY_TIME = """
WITH transaction_periods AS (
    SELECT
        r.risk_score,
        r.risk_level,
        CASE
            WHEN EXTRACT(HOUR FROM t.transaction_timestamp) BETWEEN 0 AND 5
                THEN 'Night'
            WHEN EXTRACT(HOUR FROM t.transaction_timestamp) BETWEEN 6 AND 11
                THEN 'Morning'
            WHEN EXTRACT(HOUR FROM t.transaction_timestamp) BETWEEN 12 AND 17
                THEN 'Afternoon'
            ELSE 'Evening'
        END AS time_period
    FROM risk.risk_transaction r
    JOIN warehouse.fact_transaction t
        ON r.transaction_id = t.transaction_id
)
SELECT
    time_period,
    COUNT(*) AS transaction_count,
    COUNT(*) FILTER (WHERE risk_level = 'HIGH') AS high_risk_count,
    COUNT(*) FILTER (WHERE risk_level = 'CRITICAL') AS critical_risk_count,
    ROUND(AVG(risk_score), 2) AS average_risk_score,
    ROUND(
        COUNT(*) FILTER (
            WHERE risk_level IN ('HIGH', 'CRITICAL')
        )::NUMERIC / COUNT(*),
        4
    ) AS risky_transaction_ratio
FROM transaction_periods
GROUP BY time_period
ORDER BY
    CASE time_period
        WHEN 'Night' THEN 1
        WHEN 'Morning' THEN 2
        WHEN 'Afternoon' THEN 3
        WHEN 'Evening' THEN 4
    END;
"""

GET_RISKIEST_ACCOUNTS = """
SELECT
    account_id,
    account_risk_level,
    average_risk_score,
    max_risk_score,
    risk_transaction_ratio,
    high_risk_count,
    critical_risk_count,
    transaction_count,
    total_transaction_amount
FROM risk.risk_account
ORDER BY
    CASE account_risk_level
        WHEN 'CRITICAL' THEN 1
        WHEN 'HIGH' THEN 2
        WHEN 'MEDIUM' THEN 3
        WHEN 'LOW' THEN 4
    END,
    critical_risk_count DESC,
    average_risk_score DESC,
    risk_transaction_ratio DESC
LIMIT 10;
"""

GET_RISKY_ACCOUNTS_ACCORDING_TO_TRANSACTION_VOLUME = """
SELECT
    account_id,
    transaction_count,
    total_transaction_amount,
    average_risk_score,
    risk_transaction_ratio,
    account_risk_level,
	critical_risk_count,
	high_risk_count
FROM risk.risk_account
WHERE account_risk_level IN ('HIGH', 'CRITICAL')
ORDER BY total_transaction_amount DESC
LIMIT 10;
"""

GET_RISKIEST_CUSTOMERS = """
SELECT
    customer_id,
    account_count,
    customer_risk_level,
    critical_accounts,
    high_risk_accounts,
    risky_account_ratio,
    average_account_risk,
    max_account_risk_score,
    total_transaction_amount
FROM risk.risk_customer
WHERE account_count > 1
  AND customer_risk_level IN ('HIGH', 'CRITICAL')
ORDER BY
    CASE customer_risk_level
        WHEN 'CRITICAL' THEN 1
        WHEN 'HIGH' THEN 2
    END,
    critical_accounts DESC,
    risky_account_ratio DESC
LIMIT 10;
"""

GET_RISKY_CUSTOMER_BY_AMOUNT = """
SELECT
    customer_id,
    customer_risk_level,
    account_count,
    transaction_count,
    total_transaction_amount,
    average_account_risk,
    critical_accounts,
    high_risk_accounts
FROM risk.risk_customer
WHERE customer_risk_level IN ('HIGH', 'CRITICAL')
ORDER BY total_transaction_amount DESC
LIMIT 10;
"""
GET_RISKY_CUSTOMER_BY_CRITICAL_COUNT = """
SELECT
    customer_id,
    customer_risk_level,
    account_count,
    transaction_count,
    total_transaction_amount,
    average_account_risk,
    max_account_risk_score,
    critical_accounts,
    high_risk_accounts,
    risky_account_ratio
FROM risk.risk_customer
ORDER BY
    CASE customer_risk_level
        WHEN 'CRITICAL' THEN 1
        WHEN 'HIGH' THEN 2
        WHEN 'MEDIUM' THEN 3
        WHEN 'LOW' THEN 4
    END,
    critical_accounts DESC,
    average_account_risk DESC,
    risky_account_ratio DESC
LIMIT 10;
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

def fetch_risk_distributions():
    connection = get_connection()
    try:
        transaction_distribution = pd.read_sql(GET_TRANSACTION_RISK_DISTRIBUTION,connection)
        account_distribution = pd.read_sql(GET_ACCOUNT_RISK_DISTRIBUTION,connection)
        customer_distribution = pd.read_sql(GET_CUSTOMER_RISK_DISTRIBUTION,connection)
        return {
            "transaction_distribution" : transaction_distribution,
            "account_distribution" : account_distribution,
            "customer_distribution" : customer_distribution
        }
    except psycopg2.Error as e:
        print(f"Error while fetching risk distributions: {e}")
    finally:
        connection.close()

def fetch_transaction_analysis():
    connection = get_connection()
    try:
        risk_by_country = pd.read_sql(GET_RISK_BY_COUNTRY,connection)
        risk_by_mercahnt_category = pd.read_sql(GET_RISK_BY_MERCHANT_CATEGORY,connection)
        risk_by_transaction_type = pd.read_sql(GET_RISK_BY_TRANSACTION_TYPE,connection)
        risk_by_payment_method = pd.read_sql(GET_RISK_BY_PAYMENT_METHOD,connection)
        risk_by_time = pd.read_sql(GET_RISK_BY_TIME,connection)
        return{
            "risk_by_country" : risk_by_country,
            "risk_by_mercahnt_category" : risk_by_mercahnt_category,
            "risk_by_transaction_type" : risk_by_transaction_type,
            "risk_by_payment_method" : risk_by_payment_method,
            "risk_by_time" : risk_by_time
        }
    except psycopg2.Error as e:
        print(f"Error while fetching transaction analysis: {e}")
    finally:
        connection.close()
    
def fetch_account_analysis():
    connection = get_connection()
    try:
        return {
            "riskiest_accounts" : pd.read_sql(GET_RISKIEST_ACCOUNTS,connection),
            "riskiest_accounts_by_amount" : pd.read_sql(GET_RISKY_ACCOUNTS_ACCORDING_TO_TRANSACTION_VOLUME,connection)
        }
    except psycopg2.Error as e:
        print(f"Error while fetching account analysis: {e}")
    finally:
        connection.close()
        
def fetch_customer_analysis():
    connection = get_connection()
    try:
        return {
            "riskiest_customers" : pd.read_sql(GET_RISKIEST_CUSTOMERS,connection),
            "risky_customer_by_amount" : pd.read_sql(GET_RISKY_CUSTOMER_BY_AMOUNT,connection),
            "risky_customer_by_critical_count" : pd.read_sql(GET_RISKY_CUSTOMER_BY_CRITICAL_COUNT,connection)
        }
    except psycopg2.Error as e:
        print(f"Error while fetching customer analysis:{e}")
    finally:
        connection.close()