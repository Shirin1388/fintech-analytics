from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'shirin',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

DBT_VENV = "/home/shirin/fintech-analytics/venv/bin/activate"
SNOWFLAKE_VENV = "/home/shirin/fintech-analytics/snowflake_venv/bin/activate"
DBT_DIR = "/home/shirin/fintech-analytics/fintech_dbt"
DATA_DIR = "/home/shirin/fintech-analytics"

with DAG(
    dag_id='fintech_pipeline',
    default_args=default_args,
    description='FinTech AML Analytics Pipeline',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['fintech', 'aml', 'dbt'],
) as dag:

    generate_data = BashOperator(
        task_id='generate_transactions',
        bash_command=f'source {SNOWFLAKE_VENV} && python3 {DATA_DIR}/data_generator.py',
    )

    upload_to_snowflake = BashOperator(
        task_id='upload_to_snowflake',
        bash_command=f'source {SNOWFLAKE_VENV} && python3 {DATA_DIR}/upload_to_snowflake.py',
    )

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command=f'source {DBT_VENV} && cd {DBT_DIR} && dbt run --no-partial-parse',
    )

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command=f'source {DBT_VENV} && cd {DBT_DIR} && dbt test',
    )

    generate_data >> upload_to_snowflake >> dbt_run >> dbt_test