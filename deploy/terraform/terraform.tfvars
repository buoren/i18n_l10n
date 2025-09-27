# Terraform variables for i18n-l10n GCP infrastructure
project_id     = "i18n-l10n"
region         = "europe-north1"
database_tier  = "db-f1-micro"
db_password    = "SecurePassword123"
environment    = "dev"

# OAuth Configuration - USE SECRETS MANAGER IN PRODUCTION
google_client_id     = "your_google_client_id_here"
google_client_secret = "your_google_client_secret_here"
jwt_secret          = "your_jwt_secret_here"
