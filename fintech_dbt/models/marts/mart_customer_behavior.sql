WITH transactions AS (
    SELECT * FROM {{ ref('stg_transactions') }}
),

customer_stats AS (
    SELECT
        customer_id,
        COUNT(*)                                    AS total_transactions,
        SUM(amount_usd)                             AS total_amount,
        AVG(amount_usd)                             AS avg_amount,
        MAX(amount_usd)                             AS max_amount,
        MIN(amount_usd)                             AS min_amount,
        STDDEV(amount_usd)                          AS stddev_amount,
        COUNT(DISTINCT merchant_name)               AS unique_merchants,
        COUNT(DISTINCT country)                     AS unique_countries,
        COUNT(DISTINCT channel)                     AS unique_channels,
        SUM(CASE WHEN time_category = 'suspicious_hours' 
            THEN 1 ELSE 0 END)                      AS suspicious_hour_txns,
        SUM(CASE WHEN amount_category = 'high' 
            THEN 1 ELSE 0 END)                      AS high_amount_txns,
        MIN(transaction_date)                       AS first_transaction_date,
        MAX(transaction_date)                       AS last_transaction_date
    FROM transactions
    WHERE status = 'completed'
    GROUP BY customer_id
),

risk_scored AS (
    SELECT
        *,
        -- AML Risk Score
        (
            CASE WHEN unique_countries > 15 THEN 30 ELSE 0 END +
            CASE WHEN suspicious_hour_txns > 30 THEN 25 ELSE 0 END +
            CASE WHEN high_amount_txns > 3 THEN 25 ELSE 0 END +
            CASE WHEN stddev_amount > avg_amount * 2 THEN 20 ELSE 0 END
        )                                           AS risk_score,

        CASE
            WHEN (
                CASE WHEN unique_countries > 15 THEN 30 ELSE 0 END +
                CASE WHEN suspicious_hour_txns > 30 THEN 25 ELSE 0 END +
                CASE WHEN high_amount_txns > 3 THEN 25 ELSE 0 END +
                CASE WHEN stddev_amount > avg_amount * 2 THEN 20 ELSE 0 END
            ) >= 50 THEN 'HIGH'
            WHEN (
                CASE WHEN unique_countries > 15 THEN 30 ELSE 0 END +
                CASE WHEN suspicious_hour_txns > 30 THEN 25 ELSE 0 END +
                CASE WHEN high_amount_txns > 3 THEN 25 ELSE 0 END +
                CASE WHEN stddev_amount > avg_amount * 2 THEN 20 ELSE 0 END
            ) >= 25 THEN 'MEDIUM'
            ELSE 'LOW'
        END                                         AS risk_level

    FROM customer_stats
)

SELECT * FROM risk_scored