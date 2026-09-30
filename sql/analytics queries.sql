select * from risk.risk_customer;
select * from risk.risk_account;
select * from risk.risk_transaction;

--Risk Overview Queries------
select count(transaction_id) from risk.risk_transaction;

select sum(amount) as total_amount from risk.risk_transaction;

select transaction_id from risk.risk_transaction where risk_level='HIGH';

select transaction_id from risk.risk_transaction where risk_level='CRITICAL';

select count(account_id) from risk.risk_account;

select account_id from risk.risk_account where account_risk_level = 'HIGH';

select account_id from risk.risk_account where account_risk_level = 'CRITICAL';

select count(customer_id) from risk.risk_customer;

select customer_id from risk.risk_customer where customer_risk_level = 'HIGH';

select customer_id from risk.risk_customer where customer_risk_level = 'CRITICAL';

---Risk Distribution -----

SELECT risk_level, COUNT(*)
FROM risk.risk_transaction
GROUP BY risk_level;

SELECT account_risk_level, COUNT(*)
FROM risk.risk_account
GROUP BY account_risk_level; 

SELECT customer_risk_level, COUNT(*)
FROM risk.risk_customer
GROUP BY customer_risk_level;

----Risk BY COUNTRY -----

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

------ RISK BY MERCHANT CATEGORY ------------------
select * from warehouse.fact_transaction;
select * from warehouse.dim_merchant;

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

--------RISK BY TRANSACTION TYPE--------------
select * from warehouse.fact_transaction;
select * from risk.risk_transaction;

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


----------- RISK BY PAYMENT_METHOD -------------

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

----------- RISK BY TIME --------------

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

