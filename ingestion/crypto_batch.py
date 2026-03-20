"""
Batch ingestion for CoinGecko cryptocurrency data
Fetches historical price data and market data for top cryptocurrencies
"""
import os
import json
import time
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

# Configuration
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
OUTPUT_DIR = Path("data/raw/crypto")
TOP_N_COINS = 100  # Number of top coins to fetch

# Rate limiting: CoinGecko free tier = 10-30 calls/minute
RATE_LIMIT_DELAY = 2  # seconds between requests


def get_top_coins(n: int = 100) -> list:
    """Fetch top N coins by market cap"""
    print(f"Fetching top {n} coins by market cap...")
    
    coins = []
    per_page = min(n, 250)  # Max 250 per page
    pages = (n + per_page - 1) // per_page
    
    for page in range(1, pages + 1):
        url = f"{COINGECKO_BASE_URL}/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": per_page,
            "page": page,
            "sparkline": False,
            "price_change_percentage": "1h,24h,7d,30d"
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        coins.extend(response.json())
        
        time.sleep(RATE_LIMIT_DELAY)
    
    return coins[:n]


def get_historical_prices(coin_id: str, days: int = 365) -> dict:
    """Fetch historical price data for a coin"""
    url = f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": "daily"
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def save_market_data(coins: list) -> Path:
    """Save current market data to CSV"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    df = pd.DataFrame(coins)
    
    # Select and rename relevant columns
    columns_map = {
        "id": "coin_id",
        "symbol": "symbol",
        "name": "name",
        "current_price": "price_usd",
        "market_cap": "market_cap_usd",
        "market_cap_rank": "rank",
        "total_volume": "volume_24h_usd",
        "high_24h": "high_24h",
        "low_24h": "low_24h",
        "price_change_24h": "price_change_24h",
        "price_change_percentage_24h": "price_change_pct_24h",
        "price_change_percentage_1h_in_currency": "price_change_pct_1h",
        "price_change_percentage_7d_in_currency": "price_change_pct_7d",
        "price_change_percentage_30d_in_currency": "price_change_pct_30d",
        "circulating_supply": "circulating_supply",
        "total_supply": "total_supply",
        "max_supply": "max_supply",
        "ath": "all_time_high",
        "ath_date": "ath_date",
        "atl": "all_time_low",
        "atl_date": "atl_date",
        "last_updated": "last_updated"
    }
    
    df = df[[c for c in columns_map.keys() if c in df.columns]]
    df = df.rename(columns=columns_map)
    
    # Add ingestion timestamp
    df["ingested_at"] = datetime.utcnow().isoformat()
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"market_data_{timestamp}.csv"
    df.to_csv(output_path, index=False)
    
    print(f"Saved market data for {len(df)} coins to {output_path}")
    return output_path


def save_historical_data(coin_id: str, data: dict) -> Path:
    """Save historical price data to CSV"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Convert to DataFrame
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
    
    output_path = OUTPUT_DIR / f"historical_{coin_id}.csv"
    df.to_csv(output_path, index=False)
    
    return output_path


def main():
    print("=" * 50)
    print("CoinGecko Crypto Data Batch Ingestion")
    print("=" * 50)
    
    # Step 1: Get top coins market data
    print("\n[1/2] Fetching current market data...")
    coins = get_top_coins(TOP_N_COINS)
    market_file = save_market_data(coins)
    
    # Step 2: Get historical data for top 10 coins
    print("\n[2/2] Fetching historical data for top 10 coins...")
    top_10_ids = [c["id"] for c in coins[:10]]
    
    for coin_id in top_10_ids:
        print(f"  Fetching {coin_id}...")
        try:
            historical = get_historical_prices(coin_id, days=365)
            save_historical_data(coin_id, historical)
            time.sleep(RATE_LIMIT_DELAY)
        except Exception as e:
            print(f"  Error fetching {coin_id}: {e}")
    
    print("\n" + "=" * 50)
    print("Batch ingestion complete!")
    print(f"Data saved to: {OUTPUT_DIR}")
    print("=" * 50)


if __name__ == "__main__":
    main()
