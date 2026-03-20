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
    # Upload all files recursively and keep raw/<subdir>/<file> paths.
    for file_path in SOURCE_DIR.rglob("*"):
        if file_path.is_file():
            relative_path = file_path.relative_to(SOURCE_DIR)
            destination = f"{DESTINATION_PREFIX}{relative_path.as_posix()}"
            upload_to_gcs(BUCKET_NAME, file_path, destination)
    
    print("Upload complete!")


if __name__ == "__main__":
    main()
