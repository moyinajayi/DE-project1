"""
Airflow DAG for the Crypto Analytics Pipeline.

Pipeline steps:
  1. Fetch data from CoinGecko API (crypto_batch.py)
  2. Upload raw CSVs to GCS (upload_to_gcs.py)
  3. Load from GCS into BigQuery (crypto_load_to_bq.py)
  4. Run dbt transformations (dbt run)
"""

from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT_DIR = Path(__file__).resolve().parents[2]  # de-final-project/
INGESTION_DIR = PROJECT_DIR / "ingestion"
DBT_DIR = PROJECT_DIR / "dbt" / "crypto_dbt"

default_args = {
    "owner": "moyin",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="crypto_analytics_pipeline",
    default_args=default_args,
    description="End-to-end crypto data pipeline: API → GCS → BigQuery → dbt",
    schedule_interval="@daily",
    start_date=datetime(2026, 3, 24),
    catchup=False,
    tags=["crypto", "data-engineering"],
) as dag:

    fetch_data = BashOperator(
        task_id="fetch_crypto_data",
        bash_command=f"cd {PROJECT_DIR} && python3 {INGESTION_DIR}/crypto_batch.py",
    )

    upload_to_gcs = BashOperator(
        task_id="upload_to_gcs",
        bash_command=f"cd {PROJECT_DIR} && python3 {INGESTION_DIR}/upload_to_gcs.py",
    )

    load_to_bq = BashOperator(
        task_id="load_to_bigquery",
        bash_command=f"cd {PROJECT_DIR} && python3 {INGESTION_DIR}/crypto_load_to_bq.py",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_DIR} && dbt run",
    )

    fetch_data >> upload_to_gcs >> load_to_bq >> dbt_run
