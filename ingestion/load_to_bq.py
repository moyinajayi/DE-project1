"""
Load data from GCS to BigQuery
"""
import os
from google.cloud import bigquery

# Configuration
PROJECT_ID = os.getenv("GCP_PROJECT", "your-project-id")
DATASET_ID = "final_project"
TABLE_ID = "raw_data"
GCS_URI = "gs://your-bucket-name/raw/*.csv"


def load_gcs_to_bq(gcs_uri: str, table_ref: str) -> None:
    """Load data from GCS to BigQuery"""
    client = bigquery.Client(project=PROJECT_ID)
    
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    
    load_job = client.load_table_from_uri(
        gcs_uri,
        table_ref,
        job_config=job_config,
    )
    
    load_job.result()  # Wait for job to complete
    
    table = client.get_table(table_ref)
    print(f"Loaded {table.num_rows} rows to {table_ref}")


def main():
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    load_gcs_to_bq(GCS_URI, table_ref)
    print("Load complete!")


if __name__ == "__main__":
    main()
