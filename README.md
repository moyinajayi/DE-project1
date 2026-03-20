# Crypto Analytics — Data Engineering Final Project

## 🎯 Problem Description

This project builds an **end-to-end data pipeline** for cryptocurrency market analytics. It ingests real-time and historical price data from the [CoinGecko API](https://www.coingecko.com/en/api), stores it in a cloud data lake and warehouse, transforms it with dbt, and surfaces insights through an interactive Streamlit dashboard.

**Key questions answered:**
- What is the current market cap distribution across top cryptocurrencies?
- Which coins had the biggest 24-hour price swings?
- How have prices trended over the past year for major coins?

---

## 📋 Project Checklist

### 1. Dataset Selection
- [x] Choose a dataset — **CoinGecko Cryptocurrency API**
- [x] Dataset is large enough (100+ coins, 365 days of daily history)
- [x] Data has interesting dimensions (price, market cap, volume, % changes)

### 2. Infrastructure Setup
- [x] Create GCP project
- [x] Set up service account with appropriate permissions
- [x] Create Cloud Storage bucket (data lake) via Terraform
- [x] Create BigQuery dataset (data warehouse) via Terraform

### 3. Data Ingestion Pipeline (Batch)
- [x] Python script to fetch data from CoinGecko API (`crypto_batch.py`)
- [x] Upload raw CSVs to GCS data lake (`upload_to_gcs.py`)
- [x] Load from GCS to BigQuery raw tables (`crypto_load_to_bq.py`)
- [x] (Optional) Live streaming prices (`crypto_stream.py`)

### 4. Data Transformation (dbt)
- [x] Create dbt project (`dbt/crypto_dbt`)
- [x] dbt models configured and running (PASS=2)

### 5. Workflow Orchestration
- [ ] Not yet implemented (Prefect listed as dependency)

### 6. Dashboard (Streamlit — 4 tiles + data table)
- [x] Tile 1: Market Cap Distribution (donut chart)
- [x] Tile 2: 24h Price Change (horizontal bar chart)
- [x] Tile 3: Historical Price Trends (line chart)
- [x] Tile 4: KPI Cards (Total Market Cap, BTC Dominance, 24h Volume, Avg Change)
- [x] Interactive data table with formatted prices and color-coded changes

---

## 🏗️ Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  CoinGecko   │────▶│  GCS Bucket  │────▶│  BigQuery    │
│    API       │     │  (Data Lake) │     │  (Warehouse) │
└──────────────┘     └──────────────┘     └──────────────┘
                                                 │
                                                 ▼
                                          ┌──────────────┐
                                          │     dbt      │
                                          │ (Transform)  │
                                          └──────────────┘
                                                 │
                                                 ▼
                                          ┌──────────────┐
                                          │  Streamlit   │
                                          │  Dashboard   │
                                          └──────────────┘
```

**Technologies used:**
- **Cloud:** Google Cloud Platform (GCS, BigQuery)
- **IaC:** Terraform
- **Ingestion:** Python (requests, google-cloud-storage, google-cloud-bigquery)
- **Transformation:** dbt (dbt-bigquery)
- **Dashboard:** Streamlit + Plotly
- **Language:** Python 3.9+

---

## 📁 Project Structure

```
de-final-project/
├── README.md                       # This file
├── requirements.txt                # Python dependencies
├── .gitignore
├── .streamlit/
│   ├── config.toml                 # Streamlit theme & server config
│   └── secrets.toml.example        # Template for GCP secrets
├── infrastructure/                 # Terraform IaC
│   ├── main.tf                     # GCS bucket + BigQuery dataset
│   └── terraform.tfvars.example    # Template for Terraform variables
├── ingestion/                      # Data ingestion scripts
│   ├── crypto_batch.py             # Fetch top 100 coins + 1yr history
│   ├── upload_to_gcs.py            # Upload raw CSVs to GCS
│   ├── crypto_load_to_bq.py        # Load from GCS into BigQuery
│   └── crypto_stream.py            # (Optional) Live price streaming
├── dbt/
│   └── crypto_dbt/                 # dbt project
│       ├── dbt_project.yml
│       └── models/
├── orchestration/                  # (Placeholder for Prefect/Airflow)
└── dashboard/
    ├── app.py                      # Streamlit dashboard application
    ├── requirements.txt            # Dashboard-specific dependencies
    └── screenshots/                # Dashboard screenshots
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- GCP account with billing enabled
- Terraform
- gcloud CLI (for authentication)

### 1. Clone and set up environment

```bash
cd de-final-project
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Authenticate with GCP

```bash
# Option A: Service account key
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"

# Option B: Application Default Credentials
gcloud auth application-default login
```

### 3. Configure and deploy infrastructure

```bash
cd infrastructure
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your GCP project ID and bucket name
terraform init
terraform apply
```

### 4. Run the ingestion pipeline

```bash
cd ..
export GCP_PROJECT="your-gcp-project-id"
export GCS_BUCKET="your-bucket-name"

# Fetch historical crypto data from CoinGecko (top 100 coins + 1yr history for top 5)
python3 ingestion/crypto_batch.py

# Upload raw CSVs to GCS
python3 ingestion/upload_to_gcs.py

# Load from GCS into BigQuery (creates partitioned tables)
python3 ingestion/crypto_load_to_bq.py
```

### 5. Run dbt transformations

```bash
cd dbt/crypto_dbt
dbt run
```

### 6. Launch the dashboard

```bash
cd ../../dashboard
export GCP_PROJECT="your-gcp-project-id"
streamlit run app.py
```

The dashboard opens at `http://localhost:8501`. Toggle **Demo Mode** off in the sidebar to load live BigQuery data.

---

## 📊 Dashboard

### Tile 1: Market Cap Distribution
Donut chart showing market cap distribution of top cryptocurrencies.

### Tile 2: 24h Price Change
Horizontal bar chart showing price changes — green for gains, red for losses.

### Tile 3: Historical Price Trends
Line chart showing price history over 365 days for selected coins.

### Tile 4: KPI Cards
- Total Market Cap
- BTC Dominance %
- 24h Trading Volume
- Average 24h Price Change

### Data Table
Formatted table with prices, market caps, volumes, and color-coded % changes.

---

## 📝 Dataset & Tables

- **Source:** [CoinGecko API](https://www.coingecko.com/en/api) (free tier)
- **Data lake:** `gs://<bucket-name>/raw/crypto/`
- **BigQuery dataset:** `<project>.final_project`

| Table | Description | Partitioning |
|-------|-------------|--------------|
| `crypto_market_data` | Current market snapshot (100 coins) | — |
| `crypto_historical_prices` | Daily prices for top 5 coins (365 days) | Partitioned by `timestamp` (DAY) |
| `crypto_prices_stream` | Live streaming prices (optional) | — |

---

## ✅ Evaluation Criteria

| Criteria | Points | Status |
|----------|--------|--------|
| Problem description | 2 | Clear README with problem statement |
| Cloud infrastructure | 4 | Terraform (GCS + BigQuery) |
| Data ingestion | 4 | Batch pipeline (API → GCS → BigQuery) |
| Data warehouse | 4 | Partitioned tables in BigQuery |
| Transformations | 4 | dbt project with models |
| Dashboard | 4 | Streamlit with 4 tiles + data table |
| Reproducibility | 4 | Step-by-step instructions above |

**Total: 26 points**

---

## 👤 Author
- **Name:** Moyin
- **Course:** Data Engineering Zoomcamp 2026
