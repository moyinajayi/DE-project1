"""
Streaming ingestion for CoinGecko cryptocurrency data
Continuously fetches live price updates and streams to GCS/BigQuery

Can be run as:
1. Direct to BigQuery streaming inserts
2. To GCS as small batch files
3. To Kafka/Pub-Sub (if configured)
"""
import os
import json
import time
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
from google.cloud import bigquery
from google.cloud import storage

# Configuration
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
POLL_INTERVAL = 60  # seconds between API calls (respect rate limits)
COINS_TO_TRACK = ["bitcoin", "ethereum", "solana", "cardano", "dogecoin", 
                  "ripple", "polkadot", "avalanche-2", "chainlink", "polygon"]

# GCP Configuration
PROJECT_ID = os.getenv("GCP_PROJECT", "your-project-id")
DATASET_ID = "final_project"
TABLE_ID = "crypto_prices_stream"
BUCKET_NAME = os.getenv("GCS_BUCKET", "your-bucket-name")

# Output mode: "bigquery", "gcs", or "local"
OUTPUT_MODE = os.getenv("STREAM_OUTPUT_MODE", "local")


def fetch_simple_prices(coin_ids: list) -> dict:
    """Fetch current prices for multiple coins"""
    url = f"{COINGECKO_BASE_URL}/simple/price"
    params = {
        "ids": ",".join(coin_ids),
        "vs_currencies": "usd",
        "include_24hr_vol": "true",
        "include_24hr_change": "true",
        "include_market_cap": "true",
        "include_last_updated_at": "true"
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def transform_price_data(raw_data: dict) -> list:
    """Transform API response to flat records"""
    records = []
    fetch_time = datetime.utcnow()
    
    for coin_id, data in raw_data.items():
        record = {
            "coin_id": coin_id,
            "price_usd": data.get("usd"),
            "volume_24h_usd": data.get("usd_24h_vol"),
            "change_24h_pct": data.get("usd_24h_change"),
            "market_cap_usd": data.get("usd_market_cap"),
            "last_updated_at": datetime.fromtimestamp(
                data.get("last_updated_at", fetch_time.timestamp())
            ).isoformat(),
            "fetched_at": fetch_time.isoformat()
        }
        records.append(record)
    
    return records


def write_to_bigquery(records: list):
    """Stream records to BigQuery using streaming inserts"""
    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    
    errors = client.insert_rows_json(table_ref, records)
    
    if errors:
        print(f"BigQuery streaming errors: {errors}")
    else:
        print(f"Inserted {len(records)} records to BigQuery")


def write_to_gcs(records: list):
    """Write records to GCS as JSON file"""
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    blob_name = f"streaming/crypto_prices_{timestamp}.json"
    blob = bucket.blob(blob_name)
    
    blob.upload_from_string(
        json.dumps(records, indent=2),
        content_type="application/json"
    )
    print(f"Wrote {len(records)} records to gs://{BUCKET_NAME}/{blob_name}")


def write_to_local(records: list):
    """Write records to local file for testing"""
    output_dir = Path("data/streaming/crypto")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"prices_{timestamp}.json"
    
    with open(output_path, "w") as f:
        json.dump(records, f, indent=2)
    
    print(f"Wrote {len(records)} records to {output_path}")


def create_bigquery_table():
    """Create the streaming table if it doesn't exist"""
    client = bigquery.Client(project=PROJECT_ID)
    
    schema = [
        bigquery.SchemaField("coin_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("price_usd", "FLOAT64"),
        bigquery.SchemaField("volume_24h_usd", "FLOAT64"),
        bigquery.SchemaField("change_24h_pct", "FLOAT64"),
        bigquery.SchemaField("market_cap_usd", "FLOAT64"),
        bigquery.SchemaField("last_updated_at", "TIMESTAMP"),
        bigquery.SchemaField("fetched_at", "TIMESTAMP"),
    ]
    
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    table = bigquery.Table(table_ref, schema=schema)
    
    # Partition by day for efficient querying
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="fetched_at"
    )
    
    try:
        client.create_table(table)
        print(f"Created table {table_ref}")
    except Exception as e:
        if "Already Exists" in str(e):
            print(f"Table {table_ref} already exists")
        else:
            raise


def main():
    print("=" * 50)
    print("CoinGecko Crypto Streaming Ingestion")
    print(f"Output mode: {OUTPUT_MODE}")
    print(f"Tracking: {', '.join(COINS_TO_TRACK)}")
    print(f"Poll interval: {POLL_INTERVAL}s")
    print("=" * 50)
    print("Press Ctrl+C to stop\n")
    
    # Create BigQuery table if needed
    if OUTPUT_MODE == "bigquery":
        create_bigquery_table()
    
    iteration = 0
    while True:
        try:
            iteration += 1
            print(f"\n[{datetime.utcnow().isoformat()}] Iteration {iteration}")
            
            # Fetch prices
            raw_data = fetch_simple_prices(COINS_TO_TRACK)
            records = transform_price_data(raw_data)
            
            # Log sample
            if records:
                btc = next((r for r in records if r["coin_id"] == "bitcoin"), None)
                if btc:
                    print(f"  BTC: ${btc['price_usd']:,.2f} ({btc['change_24h_pct']:+.2f}%)")
            
            # Write based on mode
            if OUTPUT_MODE == "bigquery":
                write_to_bigquery(records)
            elif OUTPUT_MODE == "gcs":
                write_to_gcs(records)
            else:
                write_to_local(records)
            
            # Wait for next poll
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\nStopping stream...")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
