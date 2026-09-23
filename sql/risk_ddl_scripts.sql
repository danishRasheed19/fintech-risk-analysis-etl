CREATE SCHEMA IF NOT EXISTS risk;


CREATE TABLE IF NOT EXISTS risk.risk_transaction (
    transaction_id VARCHAR(50) PRIMARY KEY,
    account_id VARCHAR(50) NOT NULL,
    customer_id VARCHAR(50) NOT NULL,

    risk_score INTEGER NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    risk_reasons TEXT,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS risk.risk_account (
    account_id VARCHAR(50) PRIMARY KEY,

    transaction_count INTEGER NOT NULL,
    total_transaction_amount NUMERIC(18, 2) NOT NULL,
    average_transaction_amount NUMERIC(18, 2) NOT NULL,

    average_risk_score NUMERIC(10, 2) NOT NULL,
    max_risk_score INTEGER NOT NULL,

    high_risk_count INTEGER NOT NULL,
    critical_risk_count INTEGER NOT NULL,

    risk_transaction_ratio NUMERIC(10, 4) NOT NULL,
    account_risk_level VARCHAR(20) NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS risk.risk_customer (
    customer_id VARCHAR(50) PRIMARY KEY,

    account_count INTEGER NOT NULL,
    transaction_count INTEGER NOT NULL,
    total_transaction_amount NUMERIC(18, 2) NOT NULL,

    average_account_risk NUMERIC(10, 2) NOT NULL,
    max_account_risk_score NUMERIC(10, 2) NOT NULL,

    critical_accounts INTEGER NOT NULL,
    high_risk_accounts INTEGER NOT NULL,

    risky_account_ratio NUMERIC(10, 4) NOT NULL,
    customer_risk_level VARCHAR(20) NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

select * from risk.risk_customer;