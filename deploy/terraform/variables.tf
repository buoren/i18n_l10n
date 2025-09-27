# Terraform variables for i18n-l10n GCP infrastructure

variable "project_id" {
  description = "The GCP project ID"
  type        = string
  default     = "i18n-l10n"
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "europe-north1"
}

variable "database_tier" {
  description = "The Cloud SQL instance tier"
  type        = string
  default     = "db-f1-micro"
}

variable "db_password" {
  description = "Password for the database user"
  type        = string
  sensitive   = true
  default     = ""
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "google_client_id" {
  description = "Google OAuth 2.0 Client ID"
  type        = string
  sensitive   = true
  default     = ""
}

variable "google_client_secret" {
  description = "Google OAuth 2.0 Client Secret"
  type        = string
  sensitive   = true
  default     = ""
}

variable "jwt_secret" {
  description = "JWT secret key for token signing"
  type        = string
  sensitive   = true
  default     = ""
}
