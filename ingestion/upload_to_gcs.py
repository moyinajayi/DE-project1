"""
Upload data to Google Cloud Storage (Data Lake)
"""
import os
from pathlib import Path
from google.cloud import storage

# Configuration
BUCKET_NAME = os.getenv("GCS_BUCKET", "your-bucket-name")
SOURCE_DIR = Path("data/raw")
DESTINATION_PREFIX = "raw/"


def upload_to_gcs(bucket_name: str, source_path: Path, destination_blob: str) -> None:
    """Upload a file to GCS"""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob)
    
    blob.upload_from_filename(source_path)
    print(f"Uploaded {source_path} to gs://{bucket_name}/{destination_blob}")


def main():
    # Upload all files in source directory
    for file_path in SOURCE_DIR.glob("*"):
        if file_path.is_file():
            destination = f"{DESTINATION_PREFIX}{file_path.name}"
            upload_to_gcs(BUCKET_NAME, file_path, destination)
    
    print("Upload complete!")


if __name__ == "__main__":
    main()
