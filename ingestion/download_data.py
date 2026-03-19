"""
Download data from source
Modify this script based on your chosen dataset
"""
import os
import requests
from pathlib import Path

# Configuration
DATA_URL = "https://example.com/data.csv"  # Replace with your data URL
OUTPUT_DIR = Path("data/raw")
OUTPUT_FILE = OUTPUT_DIR / "data.csv"


def download_file(url: str, output_path: Path) -> None:
    """Download a file from URL to local path"""
    print(f"Downloading from {url}...")
    
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"Downloaded to {output_path}")


def main():
    download_file(DATA_URL, OUTPUT_FILE)
    print("Download complete!")


if __name__ == "__main__":
    main()
