# FinTech Transaction & Anti-Money Laundering Analytics

A production-style data engineering portfolio project demonstrating end-to-end analytics pipeline development for financial transaction monitoring and AML detection.

## Architecture
Raw Data → Snowflake RAW → dbt Staging → dbt Marts → Dashboard
↑↑
Airflow DAG GitHub Actions CI/CD

## Tech Stack

| Tool               | Purpose                       |
|--------------------|-------------------------------|
| **Snowflake**      | Cloud data warehouse          |
| **dbt Core**       | Data transformation & testing |
| **Apache Airflow** | Pipeline orchestration        |
| **Python**         | Data generation & ingestion   |
| **GitHub Actions** | CI/CD automation              |

## Project Overview

This project simulates a real-world FinTech analytics platform with:
- **50,000+ synthetic transactions** generated with realistic patterns
- **AML risk scoring** based on customer behavior analysis
- **Anomaly detection** using Z-score statistical modeling
- **Automated testing** on every code push via CI/CD

## Project Structure
fintech-analytics/
    - airflow/
        - dags/
            fintech_pipeline.py    # Daily pipeline DAG

    - fintech_dbt/
        - models/
            - staging/               # Raw data cleaning
                - stg_transactions.sql
            - marts/                 # Business logic
                - mart_customer_behavior.sql   # AML risk scoring
                - mart_anomaly_transactions.sql # Flagged transactions
        - dbt_project.yml
    - data_generator.py   # Synthetic data generation
    - upload_to_snowflake.py         # Data ingestion
    - .github/
        - workflos/
            - dbt_ci.yml # CI/CD pipeline


## dbt Models

### Staging
- **stg_transactions** — Cleans and types raw transactions, adds derived fields (amount category, time category)

### Marts
- **mart_customer_behavior** — Aggregates customer-level metrics and calculates AML risk scores (HIGH/MEDIUM/LOW)
- **mart_anomaly_transactions** — Flags suspicious transactions using Z-score analysis and behavioral rules

## AML Risk Scoring Logic

Customers are scored based on:

| Rule                                 | Score |
|--------------------------------------|-------|
| Transactions across 3+ countries     |  +30  |
| 5+ transactions between midnight–6am |  +25  |
| 3+ high-value transactions (>$5,000) |  +25  |
| High standard deviation vs average   |  +20  |

**Risk Levels:** HIGH (≥50) · MEDIUM (≥25) · LOW (<25)

## Pipeline

The Airflow DAG runs daily and executes these steps in sequence:
generate_transactions → upload_to_snowflake → dbt_run → dbt_test

## CI/CD

Every push to 'main' triggers GitHub Actions which:
1. Installs dbt
2. Connects to Snowflake
3. Runs all dbt tests automatically

## Setup

'''bash
# Clone the repo
git clone https://github.com/Shirin1388/fintech-analytics.git

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install dbt-snowflake

# Configure Snowflake connection
cp ~/.dbt/profiles.yml.example ~/.dbt/profiles.yml
# Edit profiles.yml with your Snowflake credentials
'''