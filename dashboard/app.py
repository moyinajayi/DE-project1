"""
Streamlit Dashboard for Cryptocurrency Analytics
Data Engineering Final Project
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from google.cloud import bigquery
from google.oauth2 import service_account
import os

# Page configuration
st.set_page_config(
    page_title="Crypto Analytics Dashboard",
    page_icon="🪙",
    layout="wide"
)

try:
    HAS_STREAMLIT_SECRETS = "gcp_service_account" in st.secrets and "project" in st.secrets
except Exception:
    HAS_STREAMLIT_SECRETS = False


def get_bigquery_client():
    """Create BigQuery client with proper authentication"""
    # Check if running on Streamlit Cloud (secrets available)
    if HAS_STREAMLIT_SECRETS:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
        project_id = st.secrets["project"]["gcp_project_id"]
        return bigquery.Client(credentials=credentials, project=project_id)
    else:
        # Local development - uses default credentials (gcloud auth)
        project_id = os.getenv("GCP_PROJECT", "your-project-id")
        return bigquery.Client(project=project_id)


# Configuration
if HAS_STREAMLIT_SECRETS:
    PROJECT_ID = st.secrets["project"]["gcp_project_id"]
    DATASET_ID = st.secrets["project"]["dataset_id"]
else:
    PROJECT_ID = os.getenv("GCP_PROJECT", "your-project-id")
    DATASET_ID = "final_project"


@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data_from_bq(query: str) -> pd.DataFrame:
    """Load data from BigQuery"""
    client = get_bigquery_client()
    return client.query(query).to_dataframe()


@st.cache_data(ttl=60)  # Cache for 1 minute (for live data)
def get_market_data() -> pd.DataFrame:
    """Fetch current market data"""
    query = f"""
    SELECT *
    FROM `{PROJECT_ID}.{DATASET_ID}.crypto_market_data`
    ORDER BY rank
    LIMIT 100
    """
    return load_data_from_bq(query)


@st.cache_data(ttl=300)
def get_historical_prices(coin_ids: list) -> pd.DataFrame:
    """Fetch historical price data"""
    coin_list = "', '".join(coin_ids)
    query = f"""
    SELECT timestamp, coin_id, price_usd, volume_usd, market_cap_usd
    FROM `{PROJECT_ID}.{DATASET_ID}.crypto_historical_prices`
    WHERE coin_id IN ('{coin_list}')
    ORDER BY coin_id, timestamp
    """
    return load_data_from_bq(query)


@st.cache_data(ttl=60)
def get_streaming_data() -> pd.DataFrame:
    """Fetch recent streaming data"""
    query = f"""
    SELECT *
    FROM `{PROJECT_ID}.{DATASET_ID}.crypto_prices_stream`
    WHERE fetched_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
    ORDER BY fetched_at DESC
    """
    return load_data_from_bq(query)


def format_large_number(num):
    """Format large numbers with B/M/K suffix"""
    if num is None:
        return "N/A"
    if num >= 1e12:
        return f"${num/1e12:.2f}T"
    if num >= 1e9:
        return f"${num/1e9:.2f}B"
    if num >= 1e6:
        return f"${num/1e6:.2f}M"
    if num >= 1e3:
        return f"${num/1e3:.2f}K"
    return f"${num:.2f}"


def main():
    # Header
    st.title("🪙 Crypto Analytics Dashboard")
    st.markdown("Real-time cryptocurrency market data and analytics")
    st.markdown("---")
    
    # Check for demo mode
    demo_mode = st.sidebar.checkbox("Demo Mode (sample data)", value=True)
    
    if demo_mode:
        # Use sample data for demo
        df_market = pd.DataFrame({
            "rank": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "coin_id": ["bitcoin", "ethereum", "tether", "binancecoin", "solana",
                        "ripple", "usd-coin", "cardano", "avalanche-2", "dogecoin"],
            "name": ["Bitcoin", "Ethereum", "Tether", "BNB", "Solana", 
                     "XRP", "USDC", "Cardano", "Avalanche", "Dogecoin"],
            "symbol": ["btc", "eth", "usdt", "bnb", "sol", 
                       "xrp", "usdc", "ada", "avax", "doge"],
            "price_usd": [67234.12, 3456.78, 1.00, 567.89, 145.23,
                          0.52, 1.00, 0.45, 35.67, 0.12],
            "market_cap_usd": [1.32e12, 4.15e11, 1.12e11, 8.5e10, 6.3e10,
                               2.8e10, 2.7e10, 1.6e10, 1.4e10, 1.7e10],
            "volume_24h_usd": [3.2e10, 1.8e10, 5.5e10, 1.2e9, 2.3e9,
                               1.1e9, 5.2e9, 3.5e8, 4.2e8, 8.9e8],
            "price_change_pct_24h": [2.34, -1.23, 0.01, 3.45, 5.67,
                                     -0.89, 0.00, 1.23, -2.34, 8.90],
            "price_change_pct_7d": [5.67, 3.21, 0.00, -2.34, 12.45,
                                    1.23, 0.01, -4.56, -8.90, 15.67],
        })
        
        # Generate sample historical data
        import numpy as np
        dates = pd.date_range(end=pd.Timestamp.now(), periods=365, freq='D')
        df_historical = pd.DataFrame()
        
        for coin, base_price in [("bitcoin", 45000), ("ethereum", 2500), ("tether", 1.0), ("binancecoin", 550), ("solana", 145), ("ripple", 2.4), ("usd-coin", 1.0), ("cardano", 0.45), ("avalanche-2", 35), ("dogecoin", 0.12)]:
            prices = base_price * (1 + np.cumsum(np.random.randn(365) * 0.02))
            temp_df = pd.DataFrame({
                "timestamp": dates,
                "coin_id": coin,
                "price_usd": prices,
                "volume_usd": np.random.uniform(1e9, 5e10, 365)
            })
            df_historical = pd.concat([df_historical, temp_df])
    else:
        # Load real data from BigQuery
        try:
            df_market = get_market_data()
            df_historical = get_historical_prices(["bitcoin", "ethereum", "binancecoin", "ripple", "tether"])
        except Exception as e:
            st.error(f"Error loading data: {e}")
            st.info("Enable Demo Mode to see sample data")
            return
    
    # Sidebar filters
    st.sidebar.header("🔧 Filters")
    
    top_n = st.sidebar.slider("Show top N coins", 5, 50, 10)
    df_display = df_market.head(top_n)
    
    available_coins = df_market["name"].tolist()[:20]
    selected_coins = st.sidebar.multiselect(
        "Select coins for chart",
        options=available_coins,
        default=available_coins[:10]
    )
    
    # KPI Row
    col1, col2, col3, col4 = st.columns(4)
    
    total_market_cap = df_market["market_cap_usd"].sum()
    btc_dominance = (df_market[df_market["symbol"] == "btc"]["market_cap_usd"].iloc[0] / total_market_cap * 100) if len(df_market) > 0 else 0
    total_volume = df_market["volume_24h_usd"].sum()
    avg_change = df_market["price_change_pct_24h"].mean()
    
    with col1:
        st.metric(
            label="Total Market Cap",
            value=format_large_number(total_market_cap),
        )
    
    with col2:
        st.metric(
            label="BTC Dominance",
            value=f"{btc_dominance:.1f}%",
        )
    
    with col3:
        st.metric(
            label="24h Volume",
            value=format_large_number(total_volume),
        )
    
    with col4:
        st.metric(
            label="Avg 24h Change",
            value=f"{avg_change:+.2f}%",
            delta=f"{avg_change:.2f}%"
        )
    
    st.markdown("---")
    
    # Charts Row
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("📊 Market Cap Distribution")
        fig_pie = px.pie(
            df_display,
            values="market_cap_usd",
            names="name",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with chart_col2:
        st.subheader("📈 24h Price Change (%)")
        df_sorted = df_display.sort_values("price_change_pct_24h", ascending=True)
        colors = ['#ef4444' if x < 0 else '#22c55e' for x in df_sorted["price_change_pct_24h"]]
        
        fig_bar = go.Figure(go.Bar(
            x=df_sorted["price_change_pct_24h"],
            y=df_sorted["name"],
            orientation='h',
            marker_color=colors
        ))
        fig_bar.update_layout(
            xaxis_title="Change (%)",
            yaxis_title="",
            height=400
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("---")
    
    # Historical Price Chart
    st.subheader("📉 Historical Price Trends")
    
    if not df_historical.empty and selected_coins:
        # Map display names to coin_ids used in historical data
        if "coin_id" in df_market.columns:
            name_to_id = dict(zip(df_market["name"], df_market["coin_id"] if "coin_id" in df_market.columns else df_market["name"].str.lower()))
        else:
            name_to_id = {name: name.lower() for name in df_market["name"]}
        selected_ids = [name_to_id.get(name, name.lower()) for name in selected_coins]
        df_hist_filtered = df_historical[df_historical["coin_id"].isin(selected_ids)]
        
        if not df_hist_filtered.empty:
            fig_line = px.line(
                df_hist_filtered,
                x="timestamp",
                y="price_usd",
                color="coin_id",
                title="Price History (USD)",
                labels={"price_usd": "Price (USD)", "timestamp": "Date", "coin_id": "Coin"}
            )
            fig_line.update_layout(height=400)
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("Select coins from the sidebar to view historical data")
    else:
        st.info("No historical data available for selected coins")
    
    st.markdown("---")
    
    # Data Table
    st.subheader("📋 Market Data")
    
    # Format the display dataframe
    display_df = df_display[["rank", "name", "symbol", "price_usd", "market_cap_usd", 
                              "volume_24h_usd", "price_change_pct_24h", "price_change_pct_7d"]].copy()
    display_df.columns = ["Rank", "Name", "Symbol", "Price (USD)", "Market Cap", 
                          "24h Volume", "24h Change %", "7d Change %"]
    
    st.dataframe(
        display_df.style.format({
            "Price (USD)": "${:,.2f}",
            "Market Cap": "${:,.0f}",
            "24h Volume": "${:,.0f}",
            "24h Change %": "{:+.2f}%",
            "7d Change %": "{:+.2f}%"
        }).map(
            lambda x: 'color: #22c55e' if isinstance(x, str) and x.startswith('+') else 
                      ('color: #ef4444' if isinstance(x, str) and x.startswith('-') else ''),
            subset=["24h Change %", "7d Change %"]
        ),
        use_container_width=True,
        hide_index=True
    )
    
    # Footer
    st.markdown("---")
    st.caption("Data Engineering Final Project | Crypto Analytics Dashboard | Data from CoinGecko")
    
    if demo_mode:
        st.caption("⚠️ Demo mode: displaying sample data. Disable to load from BigQuery.")


if __name__ == "__main__":
    main()
