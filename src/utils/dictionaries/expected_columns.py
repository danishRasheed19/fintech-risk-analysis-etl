expected_columns = {
        "customers": [
            "customer_id",
            "first_name",
            "last_name",
            "email",
            "country_code",
            "country_name",
            "account_type",
            "account_created_at",
            "customer_status"
        ],

        "accounts": [
            "account_id",
            "customer_id",
            "account_type",
            "currency_code",
            "currency_name",
            "balance",
            "created_at",
            "status"
        ],

        "merchants": [
            "merchant_id",
            "merchant_name",
            "merchant_category",
            "country_code",
            "country_name",
            "risk_category"
        ],

        "transactions": [
            "transaction_id",
            "account_id",
            "merchant_id",
            "transaction_timestamp",
            "transaction_date",
            "transaction_year",
            "transaction_month",
            "transaction_hour",
            "transaction_type",
            "amount",
            "currency_code",
            "currency_name",
            "payment_method",
            "country_code",
            "country_name",
            "status"
        ]
}