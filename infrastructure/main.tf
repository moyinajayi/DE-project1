# GCP Provider
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "dataset_name" {
  description = "BigQuery dataset name"
  type        = string
  default     = "final_project"
}

variable "bucket_name" {
  description = "GCS bucket name for data lake"
  type        = string
}

# GCS Bucket (Data Lake)
resource "google_storage_bucket" "data_lake" {
  name                        = var.bucket_name
  location                    = var.region
  force_destroy               = true
  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

# BigQuery Dataset (Data Warehouse)
resource "google_bigquery_dataset" "dataset" {
  dataset_id = var.dataset_name
  location   = var.region

  delete_contents_on_destroy = true
}

# Outputs
output "bucket_name" {
  value = google_storage_bucket.data_lake.name
}

output "dataset_id" {
  value = google_bigquery_dataset.dataset.dataset_id
}
