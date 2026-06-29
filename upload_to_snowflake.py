import snowflake.connector
import pandas as pd
from snowflake.connector.pandas_tools import write_pandas

# connect to Snowflake
conn = snowflake.connector.connect(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    warehouse="FINTECH_ANALYST_WH",
    database="FINTECH_DB",
    schema="RAW",
    ocsp_fail_open=True,
    insecure_mode=True
)

# create table if not exists
conn.cursor().execute("""
    CREATE TABLE IF NOT EXISTS RAW_TRANSACTIONS (
        TRANSACTION_ID VARCHAR,
        CUSTOMER_ID VARCHAR,
        MERCHANT_NAME VARCHAR,
        AMOUNT_USD FLOAT,
        TRANSACTION_TS TIMESTAMP,
        COUNTRY VARCHAR,
        CHANNEL VARCHAR,
        STATUS VARCHAR
    )
""")

# upload data from CSV to Snowflake
df = pd.read_csv("/home/shirin/fintech-analytics/raw_transactions.csv")
df.columns = df.columns.str.upper()
df['TRANSACTION_TS'] = pd.to_datetime(df['TRANSACTION_TS'], format='ISO8601')

success, nchunks, nrows, _ = write_pandas(conn, df, "RAW_TRANSACTIONS")
print(f"Uploaded {nrows} rows successfully")

conn.close()