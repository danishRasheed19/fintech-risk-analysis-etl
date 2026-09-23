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

