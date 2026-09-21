-- ============================================================
-- WAREHOUSE SCHEMA
-- ============================================================

CREATE SCHEMA IF NOT EXISTS warehouse;


-- ============================================================
-- DIMENSION: CUSTOMER
-- ============================================================

CREATE TABLE warehouse.dim_customer (
    customer_id         VARCHAR(20) PRIMARY KEY,
    first_name          VARCHAR(100) NOT NULL,
    last_name           VARCHAR(100) NOT NULL,
    email               VARCHAR(255),
    country_code        CHAR(2),
    country_name        VARCHAR(100),
    account_type        VARCHAR(50),
    account_created_at  TIMESTAMP,
    customer_status     VARCHAR(50)
);


-- ============================================================
-- DIMENSION: ACCOUNT
-- ============================================================

CREATE TABLE warehouse.dim_account (
    account_id      VARCHAR(20) PRIMARY KEY,
    customer_id     VARCHAR(20) NOT NULL,
    account_type    VARCHAR(50),
    balance         NUMERIC(15, 2),
    currency_code   CHAR(3),
    currency_name   VARCHAR(50),
    created_at      TIMESTAMP,
    status          VARCHAR(50),

    CONSTRAINT fk_account_customer
        FOREIGN KEY (customer_id)
        REFERENCES warehouse.dim_customer(customer_id)
);


-- ============================================================
-- DIMENSION: MERCHANT
-- ============================================================

CREATE TABLE warehouse.dim_merchant (
    merchant_id        VARCHAR(20) PRIMARY KEY,
    merchant_name      VARCHAR(255) NOT NULL,
    merchant_category  VARCHAR(100),
    country_code       CHAR(2),
    country_name       VARCHAR(100),
    risk_category      VARCHAR(50)
);


-- ============================================================
-- DIMENSION: DATE
-- ============================================================

CREATE TABLE warehouse.dim_date (
    date_key       INTEGER PRIMARY KEY,
    full_date      DATE NOT NULL UNIQUE,
    year           INTEGER NOT NULL,
    quarter        INTEGER NOT NULL,
    month          INTEGER NOT NULL,
    month_name     VARCHAR(20) NOT NULL,
    day            INTEGER NOT NULL,
    day_of_week    INTEGER NOT NULL,
    day_name       VARCHAR(20) NOT NULL
);


-- ============================================================
-- FACT: TRANSACTION
-- ============================================================

CREATE TABLE warehouse.fact_transaction (
    transaction_id          VARCHAR(30) PRIMARY KEY,
    account_id              VARCHAR(20) NOT NULL,
    customer_id             VARCHAR(20) NOT NULL,
    merchant_id             VARCHAR(20) NOT NULL,
    date_key                INTEGER NOT NULL,
    transaction_timestamp   TIMESTAMP NOT NULL,
    transaction_type        VARCHAR(50),
    amount                  NUMERIC(15, 2),
    currency_code           CHAR(3),
    currency_name           VARCHAR(50),
    payment_method          VARCHAR(50),
    country_code            CHAR(2),
    country_name            VARCHAR(100),
    status                  VARCHAR(50),

    CONSTRAINT fk_transaction_account
        FOREIGN KEY (account_id)
        REFERENCES warehouse.dim_account(account_id),

    CONSTRAINT fk_transaction_customer
        FOREIGN KEY (customer_id)
        REFERENCES warehouse.dim_customer(customer_id),

    CONSTRAINT fk_transaction_merchant
        FOREIGN KEY (merchant_id)
        REFERENCES warehouse.dim_merchant(merchant_id),

    CONSTRAINT fk_transaction_date
        FOREIGN KEY (date_key)
        REFERENCES warehouse.dim_date(date_key)
);

select * from warehouse.dim_customer;
select * from warehouse.dim_account;
select * from warehouse.dim_merchant;
select * from warehouse.dim_date;
select * from warehouse.fact_transaction

Delete from warehouse.dim_customer;
Delete from warehouse.dim_account;
Delete from warehouse.dim_merchant;
Delete from warehouse.dim_date;
Delete from warehouse.fact_transaction;


