# Data Engineering Final Project

## 🎯 Objective
Build an end-to-end data pipeline with a dashboard containing at least 2 tiles.

---

## 📋 Project Checklist

### 1. Dataset Selection
- [ ] Choose a dataset (see suggestions below)
- [ ] Ensure dataset is large enough (100K+ rows recommended)
- [ ] Verify data has interesting dimensions for visualization

**Dataset Ideas:**
| Dataset | Source | Good For |
|---------|--------|----------|
| Spotify Charts | [Kaggle](https://www.kaggle.com/datasets) | Music trends, artist analytics |
| Stack Overflow Survey | [SO Annual Survey](https://insights.stackoverflow.com/survey) | Developer trends |
| GitHub Archive | [GH Archive](https://www.gharchive.org/) | Open source activity |
| Weather Data | [NOAA](https://www.ncdc.noaa.gov/cdo-web/) | Climate analysis |
| Flight Data | [OpenSky](https://opensky-network.org/) | Aviation analytics |
| Crypto Prices | [CoinGecko API](https://www.coingecko.com/en/api) | Financial trends |
| Reddit Posts | [Pushshift](https://pushshift.io/) | Social media analysis |
| E-commerce | [Brazilian E-commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) | Sales analytics |

---

### 2. Infrastructure Setup
- [ ] Create GCP project (or AWS/Azure)
- [ ] Set up service account with appropriate permissions
- [ ] Create Cloud Storage bucket (data lake)
- [ ] Create BigQuery dataset (data warehouse)

---

### 3. Data Ingestion Pipeline
Choose **Batch** or **Stream**:

#### Option A: Batch Pipeline
- [ ] Write Python script to download/fetch data
- [ ] Upload raw data to GCS (data lake)
- [ ] Load from GCS to BigQuery (raw tables)

#### Option B: Stream Pipeline  
- [ ] Set up Kafka/Redpanda
- [ ] Create producer to ingest data
- [ ] Create consumer/Flink job to process
- [ ] Write to data warehouse

---

### 4. Data Transformation (dbt)
- [ ] Create dbt project
- [ ] Build staging models (clean raw data)
- [ ] Build intermediate models (business logic)
- [ ] Build mart models (dashboard-ready)

---

### 5. Workflow Orchestration (Optional but recommended)
- [ ] Set up Prefect/Airflow
- [ ] Create DAG for pipeline
- [ ] Schedule daily/hourly runs

---

### 6. Dashboard (Required - 2 tiles minimum)
- [ ] Connect to BigQuery mart tables
- [ ] Create Tile 1: _________________
- [ ] Create Tile 2: _________________

**Dashboard Tools:**
- Google Looker Studio (free, native BigQuery integration)
- Metabase (open source)
- Streamlit (Python-based)
- Apache Superset

---

## 🏗️ Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Source     │────▶│  Data Lake   │────▶│  Warehouse   │
│   (API/File) │     │    (GCS)     │     │  (BigQuery)  │
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
                                          │  Dashboard   │
                                          │  (2 tiles)   │
                                          └──────────────┘
```

---

## 📁 Project Structure

```
de-final-project/
├── README.md                 # This file
├── infrastructure/           # Terraform files
│   └── main.tf
├── ingestion/               # Data ingestion scripts
│   ├── download_data.py
│   └── upload_to_gcs.py
├── dbt/                     # dbt project
│   ├── dbt_project.yml
│   └── models/
├── orchestration/           # Airflow/Prefect
│   └── flows/
├── dashboard/               # Dashboard screenshots
│   └── screenshots/
└── docker-compose.yml       # Local development
```

---

## ✅ Evaluation Criteria

| Criteria | Points | Notes |
|----------|--------|-------|
| Problem description | 2 | Clear README explaining the project |
| Cloud infrastructure | 4 | IaC preferred (Terraform) |
| Data ingestion | 4 | Batch or stream pipeline |
| Data warehouse | 4 | Tables created, partitioned/clustered |
| Transformations | 4 | dbt or Spark |
| Dashboard | 4 | 2+ tiles with meaningful insights |
| Reproducibility | 4 | Instructions to run the project |

**Total: 26 points**

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- GCP account with billing enabled
- Terraform (optional)

### Setup

1. **Clone and enter project:**
   ```bash
   cd de-final-project
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Set up GCP credentials:**
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
   ```

4. **Run infrastructure (if using Terraform):**
   ```bash
   cd infrastructure
   terraform init
   terraform apply
   ```

5. **Run ingestion pipeline:**
   ```bash
   python ingestion/download_data.py
   python ingestion/upload_to_gcs.py
   ```

6. **Run dbt transformations:**
   ```bash
   cd dbt
   dbt run
   ```

---

## 📊 Dashboard

### Tile 1: [Description]
_Screenshot here_

### Tile 2: [Description]
_Screenshot here_

---

## 📝 Notes

- Dataset chosen: _________________
- Data lake location: `gs://bucket-name/`
- BigQuery dataset: `project.dataset`

---

## 👤 Author
- Name: Moyin
- Course: Data Engineering Zoomcamp 2026
