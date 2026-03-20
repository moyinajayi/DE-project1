"""
Load crypto data from GCS to BigQuery
Handles both market data and historical price data
"""
import os
from google.cloud import bigquery

# Configuration
PROJECT_ID = os.getenv("GCP_PROJECT", "your-project-id")
DATASET_ID = "final_project"
BUCKET_NAME = os.getenv("GCS_BUCKET", "your-bucket-name")


def create_dataset_if_not_exists(client: bigquery.Client, dataset_id: str):
    """Create BigQuery dataset if it doesn't exist"""
    dataset_ref = f"{PROJECT_ID}.{dataset_id}"
    
    try:
        client.get_dataset(dataset_ref)
        print(f"Dataset {dataset_ref} already exists")
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        client.create_dataset(dataset)
        print(f"Created dataset {dataset_ref}")


def load_market_data(client: bigquery.Client):
    """Load current market data CSV to BigQuery"""
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.crypto_market_data"
    gcs_uri = f"gs://{BUCKET_NAME}/raw/crypto/market_data_*.csv"
    
    schema = [
        bigquery.SchemaField("coin_id", "STRING"),
        bigquery.SchemaField("symbol", "STRING"),
        bigquery.SchemaField("name", "STRING"),
        bigquery.SchemaField("price_usd", "FLOAT64"),
        bigquery.SchemaField("market_cap_usd", "FLOAT64"),
        bigquery.SchemaField("rank", "INT64"),
        bigquery.SchemaField("volume_24h_usd", "FLOAT64"),
        bigquery.SchemaField("high_24h", "FLOAT64"),
        bigquery.SchemaField("low_24h", "FLOAT64"),
        bigquery.SchemaField("price_change_24h", "FLOAT64"),
        bigquery.SchemaField("price_change_pct_24h", "FLOAT64"),
        bigquery.SchemaField("price_change_pct_1h", "FLOAT64"),
        bigquery.SchemaField("price_change_pct_7d", "FLOAT64"),
        bigquery.SchemaField("price_change_pct_30d", "FLOAT64"),
        bigquery.SchemaField("circulating_supply", "FLOAT64"),
        bigquery.SchemaField("total_supply", "FLOAT64"),
        bigquery.SchemaField("max_supply", "FLOAT64"),
        bigquery.SchemaField("all_time_high", "FLOAT64"),
        bigquery.SchemaField("ath_date", "TIMESTAMP"),
        bigquery.SchemaField("all_time_low", "FLOAT64"),
        bigquery.SchemaField("atl_date", "TIMESTAMP"),
        bigquery.SchemaField("last_updated", "TIMESTAMP"),
        bigquery.SchemaField("ingested_at", "TIMESTAMP"),
    ]
    
    job_config = bigquery.LoadJobConfig(
        schema=schema,
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    
    load_job = client.load_table_from_uri(gcs_uri, table_ref, job_config=job_config)
    load_job.result()
    
    table = client.get_table(table_ref)
    print(f"Loaded {table.num_rows} rows to {table_ref}")


def load_historical_data(client: bigquery.Client):
    """Load historical price data CSVs to BigQuery"""
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.crypto_historical_prices"
    gcs_uri = f"gs://{BUCKET_NAME}/raw/crypto/historical_*.csv"
    
    schema = [
        bigquery.SchemaField("timestamp", "TIMESTAMP"),
        bigquery.SchemaField("price_usd", "FLOAT64"),
        bigquery.SchemaField("volume_usd", "FLOAT64"),
        bigquery.SchemaField("market_cap_usd", "FLOAT64"),
        bigquery.SchemaField("coin_id", "STRING"),
        bigquery.SchemaField("ingested_at", "TIMESTAMP"),
    ]
    
    job_config = bigquery.LoadJobConfig(
        schema=schema,
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="timestamp"
        ),
    )
    
    load_job = client.load_table_from_uri(gcs_uri, table_ref, job_config=job_config)
    load_job.result()
    
    table = client.get_table(table_ref)
    print(f"Loaded {table.num_rows} rows to {table_ref}")


def main():
    print("=" * 50)
    print("Loading Crypto Data to BigQuery")
    print("=" * 50)
    
    client = bigquery.Client(project=PROJECT_ID)
    
    # Create dataset if needed
    create_dataset_if_not_exists(client, DATASET_ID)
    
    # Load tables
    print("\n[1/2] Loading market data...")
    try:
        load_market_data(client)
    except Exception as e:
        print(f"Error loading market data: {e}")
    
    print("\n[2/2] Loading historical price data...")
    try:
        load_historical_data(client)
    except Exception as e:
        print(f"Error loading historical data: {e}")
    
    print("\n" + "=" * 50)
    print("Load complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
