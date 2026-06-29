WITH transactions AS (
    SELECT * FROM {{ ref('stg_transactions') }}
),

customer_baselines AS (
    SELECT
        customer_id,
        AVG(amount_usd)         AS avg_amount,
        STDDEV(amount_usd)      AS stddev_amount
    FROM transactions
    WHERE status = 'completed'
    GROUP BY customer_id
),

anomalies AS (
    SELECT
        t.*,
        b.avg_amount            AS customer_avg,
        b.stddev_amount         AS customer_stddev,

        -- Z-score: چقدر این تراکنش از میانگین مشتری فاصله داره
        CASE
            WHEN b.stddev_amount = 0 THEN 0
            ELSE (t.amount_usd - b.avg_amount) / b.stddev_amount
        END                     AS z_score,

        -- فلگ‌های anomaly
        CASE WHEN t.amount_usd > b.avg_amount + (3 * b.stddev_amount)
            THEN TRUE ELSE FALSE END    AS is_amount_anomaly,

        CASE WHEN t.time_category = 'suspicious_hours'
            THEN TRUE ELSE FALSE END    AS is_time_anomaly,

        CASE WHEN t.amount_category = 'high' AND t.channel = 'wire'
            THEN TRUE ELSE FALSE END    AS is_wire_anomaly

    FROM transactions t
    LEFT JOIN customer_baselines b ON t.customer_id = b.customer_id
),

flagged AS (
    SELECT
        *,
        (
            CASE WHEN is_amount_anomaly THEN 1 ELSE 0 END +
            CASE WHEN is_time_anomaly THEN 1 ELSE 0 END +
            CASE WHEN is_wire_anomaly THEN 1 ELSE 0 END
        )                       AS anomaly_flag_count

    FROM anomalies
)

SELECT * FROM flagged
WHERE anomaly_flag_count > 0