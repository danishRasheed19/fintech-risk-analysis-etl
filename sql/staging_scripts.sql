CREATE SCHEMA IF NOT EXISTS staging;


CREATE TABLE staging.customers (
    customer_id         VARCHAR(20),
    first_name          VARCHAR(100),
    last_name           VARCHAR(100),
    email               VARCHAR(255),
    country_code        CHAR(2),
    country_name        VARCHAR(100),
    account_type        VARCHAR(50),
    account_created_at  TIMESTAMP,
    customer_status     VARCHAR(50)
);


CREATE TABLE staging.accounts (
    account_id      VARCHAR(20),
    customer_id     VARCHAR(20),
    account_type    VARCHAR(50),
    balance         NUMERIC(15, 2),
    currency_code   CHAR(3),
    currency_name   VARCHAR(50),
    created_at      TIMESTAMP,
    status          VARCHAR(50)
);


CREATE TABLE staging.merchants (
    merchant_id       VARCHAR(20),
    merchant_name     VARCHAR(255),
    merchant_category VARCHAR(100),
    country_code      CHAR(2),
    country_name      VARCHAR(100),
    risk_category     VARCHAR(50)
);


CREATE TABLE staging.transactions (
    transaction_id        VARCHAR(30),
    account_id            VARCHAR(20),
    merchant_id           VARCHAR(20),
    transaction_timestamp TIMESTAMP,
    transaction_type      VARCHAR(50),
    amount                NUMERIC(15, 2),
    currency_code         CHAR(3),
    currency_name         VARCHAR(50),
    payment_method        VARCHAR(50),
    country_code          CHAR(2),
    country_name          VARCHAR(100),
    status                VARCHAR(50),
    transaction_date      DATE,
    transaction_year      INTEGER,
    transaction_month     INTEGER,
    transaction_hour      INTEGER,
    transaction_day_of_week VARCHAR(20)
);

CREATE SCHEMA IF NOT EXISTS metadata;

CREATE TABLE metadata.watermarks (
    dataset_name VARCHAR(50) PRIMARY KEY,
    watermark TIMESTAMP NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO metadata.watermarks (dataset_name, watermark)
VALUES
    ('customers', NULL),
    ('accounts', NULL),
    ('transactions', NULL);

	
select * from metadata.watermarks

select * from staging.customers where customer_id ='CUST0089162';
select * from staging.accounts;
select * from staging.merchants;
select * from staging.transactions;

DELETE FROM staging.customers;
DELETE FROM staging.accounts;
DELETE FROM staging.merchants;
DELETE FROM staging.transactions;
update metadata.watermarks set watermark = null 

select * from staging.accounts where customer_id = 'CUST000002';


SELECT COUNT(*)
FROM staging.transactions t
LEFT JOIN staging.accounts a
    ON t.account_id = a.account_id
WHERE a.account_id IS NULL;