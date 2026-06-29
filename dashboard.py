import streamlit as st
import plotly.express as px
import pandas as pd
import snowflake.connector
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="FinTech AML Dashboard",
    page_icon="🏦",
    layout="wide"
)

@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse="FINTECH_ANALYST_WH",
        database="FINTECH_DB",
        schema="STAGING",
        ocsp_fail_open=True,
        insecure_mode=True
    )

@st.cache_data
def load_customer_behavior():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("ALTER SESSION SET PYTHON_CONNECTOR_QUERY_RESULT_FORMAT = 'JSON'")
    cursor.execute("""
        SELECT
            CUSTOMER_ID,
            TOTAL_TRANSACTIONS,
            TOTAL_AMOUNT,
            AVG_AMOUNT,
            MAX_AMOUNT,
            MIN_AMOUNT,
            STDDEV_AMOUNT,
            UNIQUE_MERCHANTS,
            UNIQUE_COUNTRIES,
            UNIQUE_CHANNELS,
            SUSPICIOUS_HOUR_TXNS,
            HIGH_AMOUNT_TXNS,
            TO_VARCHAR(FIRST_TRANSACTION_DATE) AS FIRST_TRANSACTION_DATE,
            TO_VARCHAR(LAST_TRANSACTION_DATE) AS LAST_TRANSACTION_DATE,
            RISK_SCORE,
            RISK_LEVEL
        FROM FINTECH_DB.STAGING.MART_CUSTOMER_BEHAVIOR
    """)
    results = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    cursor.close()
    return pd.DataFrame(results, columns=columns)

@st.cache_data
def load_anomalies():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("ALTER SESSION SET PYTHON_CONNECTOR_QUERY_RESULT_FORMAT = 'JSON'")
    cursor.execute("""
        SELECT
            TRANSACTION_ID,
            CUSTOMER_ID,
            MERCHANT_NAME,
            AMOUNT_USD,
            COUNTRY,
            CHANNEL,
            STATUS,
            AMOUNT_CATEGORY,
            TRANSACTION_HOUR,
            TIME_CATEGORY,
            CUSTOMER_AVG,
            CUSTOMER_STDDEV,
            Z_SCORE,
            IS_AMOUNT_ANOMALY,
            IS_TIME_ANOMALY,
            IS_WIRE_ANOMALY,
            ANOMALY_FLAG_COUNT
        FROM FINTECH_DB.STAGING.MART_ANOMALY_TRANSACTIONS
        WHERE Z_SCORE < 50
        ORDER BY ANOMALY_FLAG_COUNT DESC, Z_SCORE DESC
        LIMIT 1000
    """)
    results = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    cursor.close()
    return pd.DataFrame(results, columns=columns)

@st.cache_data
def load_anomaly_summary():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("ALTER SESSION SET PYTHON_CONNECTOR_QUERY_RESULT_FORMAT = 'JSON'")
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN IS_AMOUNT_ANOMALY = TRUE THEN 1 ELSE 0 END) as amount_anomalies,
            SUM(CASE WHEN IS_TIME_ANOMALY = TRUE THEN 1 ELSE 0 END) as time_anomalies,
            SUM(CASE WHEN IS_WIRE_ANOMALY = TRUE THEN 1 ELSE 0 END) as wire_anomalies
        FROM FINTECH_DB.STAGING.MART_ANOMALY_TRANSACTIONS
    """)
    results = cursor.fetchall()
    cursor.close()
    return results[0]

# Header
st.title("🏦 FinTech AML Analytics Dashboard")
st.markdown("Real-time transaction monitoring and anti-money laundering detection")
st.divider()

# Load data
with st.spinner("Loading data from Snowflake..."):
    df_customers = load_customer_behavior()
    df_anomalies = load_anomalies()
    anomaly_summary = load_anomaly_summary()

# Row 1: KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Customers", f"{len(df_customers):,}")
with col2:
    high_risk = len(df_customers[df_customers['RISK_LEVEL'] == 'HIGH'])
    st.metric("High Risk Customers", f"{high_risk:,}",
              delta=f"{high_risk/len(df_customers)*100:.1f}%",
              delta_color="inverse")
with col3:
    total_txns = df_customers['TOTAL_TRANSACTIONS'].sum()
    st.metric("Total Transactions", f"{total_txns:,}")
with col4:
    total_amount = df_customers['TOTAL_AMOUNT'].sum()
    st.metric("Total Volume", f"${total_amount:,.0f}")

st.divider()

# Row 2: Charts
col1, col2 = st.columns(2)
colors = {'HIGH': '#E24B4A', 'MEDIUM': '#EF9F27', 'LOW': '#1D9E75'}

with col1:
    st.subheader("AML Risk Distribution")
    risk_counts = df_customers['RISK_LEVEL'].value_counts().reset_index()
    risk_counts.columns = ['Risk Level', 'Count']
    fig = px.pie(
        risk_counts,
        values='Count',
        names='Risk Level',
        color='Risk Level',
        color_discrete_map=colors,
        hole=0.4
    )
    fig.update_layout(margin=dict(t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Transaction Volume by Risk Level")
    risk_volume = df_customers.groupby('RISK_LEVEL')['TOTAL_AMOUNT'].sum().reset_index()
    fig = px.bar(
        risk_volume,
        x='RISK_LEVEL',
        y='TOTAL_AMOUNT',
        color='RISK_LEVEL',
        color_discrete_map=colors,
        labels={'TOTAL_AMOUNT': 'Total Amount (USD)', 'RISK_LEVEL': 'Risk Level'}
    )
    fig.update_layout(margin=dict(t=0, b=0), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Row 3: Anomalies
st.subheader("🚨 Top Anomalous Transactions")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Amount Anomalies", f"{int(anomaly_summary[1]):,}")
with col2:
    st.metric("Time Anomalies", f"{int(anomaly_summary[2]):,}")
with col3:
    st.metric("Wire Anomalies", f"{int(anomaly_summary[3]):,}")

st.subheader("Z-Score Distribution of Flagged Transactions")
fig = px.histogram(
    df_anomalies,
    x='Z_SCORE',
    nbins=50,
    color_discrete_sequence=['#E24B4A'],
    labels={'Z_SCORE': 'Z-Score', 'count': 'Count'}
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Flagged Transactions Detail")
st.dataframe(
    df_anomalies[[
        'TRANSACTION_ID', 'CUSTOMER_ID', 'AMOUNT_USD',
        'Z_SCORE', 'IS_AMOUNT_ANOMALY', 'IS_TIME_ANOMALY',
        'IS_WIRE_ANOMALY', 'ANOMALY_FLAG_COUNT'
    ]].head(50),
    use_container_width=True
)