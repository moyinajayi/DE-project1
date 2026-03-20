"""Fetch historical data only for coins we're missing"""
import time
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
OUTPUT_DIR = Path("data/raw/crypto")

MISSING_COINS = ["solana", "dogecoin", "cardano", "tron", "usd-coin"]


def fetch_and_save(coin_id: str, max_retries: int = 5):
    url = f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": 365, "interval": "daily"}

    for attempt in range(max_retries):
        response = requests.get(url, params=params)
        if response.status_code == 429:
            wait = 60 * (attempt + 1)
            print(f"  Rate limited. Waiting {wait}s ({attempt+1}/{max_retries})...")
            time.sleep(wait)
            continue
        response.raise_for_status()
        data = response.json()

        prices = data.get("prices", [])
        volumes = data.get("total_volumes", [])
        market_caps = data.get("market_caps", [])

        df = pd.DataFrame(prices, columns=["timestamp", "price_usd"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

        if volumes:
            vol_df = pd.DataFrame(volumes, columns=["timestamp", "volume_usd"])
            vol_df["timestamp"] = pd.to_datetime(vol_df["timestamp"], unit="ms")
            df = df.merge(vol_df, on="timestamp", how="left")
        if market_caps:
            cap_df = pd.DataFrame(market_caps, columns=["timestamp", "market_cap_usd"])
            cap_df["timestamp"] = pd.to_datetime(cap_df["timestamp"], unit="ms")
            df = df.merge(cap_df, on="timestamp", how="left")

        df["coin_id"] = coin_id
        df["ingested_at"] = datetime.utcnow().isoformat()

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        path = OUTPUT_DIR / f"historical_{coin_id}.csv"
        df.to_csv(path, index=False)
        print(f"  Saved {coin_id} ({len(df)} rows)")
        return

    print(f"  Failed to fetch {coin_id} after {max_retries} retries")


if __name__ == "__main__":
    for coin in MISSING_COINS:
        existing = OUTPUT_DIR / f"historical_{coin}.csv"
        if existing.exists():
            print(f"Skipping {coin} (already exists)")
            continue
        print(f"Fetching {coin}...")
        fetch_and_save(coin)
        time.sleep(15)
