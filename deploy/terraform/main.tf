# Terraform configuration for i18n-l10n GCP infrastructure
terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

# Configure the Google Cloud Provider
provider "google" {
  project = var.project_id
  region  = var.region
}

# Variables are defined in variables.tf

# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "sqladmin.googleapis.com",
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "containerregistry.googleapis.com",
    "identitytoolkit.googleapis.com",
    "vpcaccess.googleapis.com"
  ])

  service = each.value
  disable_on_destroy = false
}

# Cloud SQL instance
resource "google_sql_database_instance" "mysql" {
  name             = "i18n-l10n-mysql"
  database_version = "MYSQL_8_0"
  region           = var.region

  depends_on = [google_project_service.apis]

  settings {
    tier = var.database_tier
    
    disk_size = 10
    disk_type = "PD_SSD"
    disk_autoresize = true
    
    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      location                       = var.region
      binary_log_enabled             = true
    }
    
    maintenance_window {
      day          = 7
      hour         = 3
      update_track = "stable"
    }
    
    ip_configuration {
      ipv4_enabled = true
      require_ssl  = false
    }
  }

  deletion_protection = true
}

# Database
resource "google_sql_database" "database" {
  name     = "i18n_l10n_db"
  instance = google_sql_database_instance.mysql.name
}

# Database user
resource "google_sql_user" "appuser" {
  name     = "appuser"
  instance = google_sql_database_instance.mysql.name
  password = var.db_password
}

# Cloud Run service
resource "google_cloud_run_v2_service" "app" {
  name     = "i18n-l10n-app"
  location = var.region

  depends_on = [google_project_service.apis]

  template {
    containers {
      image = "gcr.io/${var.project_id}/i18n-l10n-app"
      
      ports {
        container_port = 8080
      }
      
      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
      
      env {
        name  = "DB_CONNECTION_NAME"
        value = google_sql_database_instance.mysql.connection_name
      }
      
      env {
        name  = "DB_NAME"
        value = google_sql_database.database.name
      }
      
      env {
        name  = "DB_USER"
        value = google_sql_user.appuser.name
      }
      
      env {
        name  = "GOOGLE_CLIENT_ID"
        value = var.google_client_id
      }
      
      env {
        name  = "GOOGLE_CLIENT_SECRET"
        value = var.google_client_secret
      }
      
      env {
        name  = "JWT_SECRET"
        value = var.jwt_secret
      }
      
      env {
        name  = "DEPLOYMENT_VERSION"
        value = "v2-no-alembic"
      }
      
      
      env {
        name = "DB_PASSWORD"
        value_source {
          secret_key_ref {
            secret = "db_password"
            version = "latest"
          }
        }
      }
      
      resources {
        limits = {
          cpu    = "1"
          memory = "1Gi"
        }
      }
    }
    
    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
    
    vpc_access {
      connector = google_vpc_access_connector.connector.id
      egress    = "PRIVATE_RANGES_ONLY"
    }
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}

# VPC Access Connector for Cloud SQL private IP
resource "google_vpc_access_connector" "connector" {
  name          = "i18n-l10n-connector"
  ip_cidr_range = "10.8.0.0/28"
  network       = "default"
  region        = var.region
}

# IAM policy for Cloud Run
resource "google_cloud_run_service_iam_policy" "policy" {
  location = google_cloud_run_v2_service.app.location
  service  = google_cloud_run_v2_service.app.name

  policy_data = data.google_iam_policy.policy.policy_data
}

data "google_iam_policy" "policy" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
}

# Outputs are defined in outputs.tf
