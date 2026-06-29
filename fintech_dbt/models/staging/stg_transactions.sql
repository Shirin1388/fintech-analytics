WITH source AS (
    SELECT * FROM {{ source('raw', 'RAW_TRANSACTIONS') }}
),

renamed AS (
    SELECT
        TRANSACTION_ID                          AS transaction_id,
        CUSTOMER_ID                             AS customer_id,
        MERCHANT_NAME                           AS merchant_name,
        AMOUNT_USD                              AS amount_usd,
        TRANSACTION_TS                          AS transaction_ts,
        DATE(TRANSACTION_TS)                    AS transaction_date,
        COUNTRY                                 AS country,
        CHANNEL                                 AS channel,
        STATUS                                  AS status,

        -- calculation fields
        CASE
            WHEN AMOUNT_USD > 5000 THEN 'high'
            WHEN AMOUNT_USD > 1000 THEN 'medium'
            ELSE 'low'
        END                                     AS amount_category,

        HOUR(TRANSACTION_TS)                    AS transaction_hour,

        CASE
            WHEN HOUR(TRANSACTION_TS) BETWEEN 0 AND 5 THEN 'suspicious_hours'
            ELSE 'normal_hours'
        END                                     AS time_category

    FROM source
    WHERE TRANSACTION_ID IS NOT NULL
      AND AMOUNT_USD > 0
)

SELECT * FROM renamed