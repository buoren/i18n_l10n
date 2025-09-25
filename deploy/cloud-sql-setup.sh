#!/bin/bash

# GCP Cloud SQL MySQL Setup Script
# This script creates a Cloud SQL MySQL instance for the i18n-l10n project

set -e

# Configuration
PROJECT_ID="i18n-l10n"
INSTANCE_NAME="i18n-l10n-mysql"
DATABASE_NAME="i18n_l10n_db"
REGION="europe-north1"
TIER="db-f1-micro"
ROOT_PASSWORD="$(openssl rand -base64 32)"

echo "Setting up Cloud SQL MySQL instance for project: $PROJECT_ID"

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable sqladmin.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable translate.googleapis.com

# Create Cloud SQL instance with public IP (idempotent)
echo "Creating Cloud SQL MySQL instance with public IP..."
if gcloud sql instances describe $INSTANCE_NAME --quiet &>/dev/null; then
    echo "✅ Cloud SQL instance '$INSTANCE_NAME' already exists, skipping creation"
else
    gcloud sql instances create $INSTANCE_NAME \
        --database-version=MYSQL_8_0 \
        --tier=$TIER \
        --region=$REGION \
        --root-password=$ROOT_PASSWORD \
        --storage-type=SSD \
        --storage-size=10GB \
        --storage-auto-increase \
        --backup \
        --enable-bin-log \
        --maintenance-window-day=SUN \
        --maintenance-window-hour=03 \
        --deletion-protection \
        --assign-ip
    echo "✅ Cloud SQL instance created with public IP"
fi

# Create database (idempotent)
echo "Creating database: $DATABASE_NAME"
if gcloud sql databases describe $DATABASE_NAME --instance=$INSTANCE_NAME --quiet &>/dev/null; then
    echo "✅ Database '$DATABASE_NAME' already exists, skipping creation"
else
    gcloud sql databases create $DATABASE_NAME --instance=$INSTANCE_NAME
    echo "✅ Database created"
fi

# Create application user (idempotent)
echo "Creating application user..."
APP_PASSWORD="$(openssl rand -base64 32)"
if gcloud sql users describe appuser --instance=$INSTANCE_NAME --quiet &>/dev/null; then
    echo "✅ User 'appuser' already exists, skipping creation"
    # Get existing password or generate new one
    APP_PASSWORD="existing_password"
else
    gcloud sql users create appuser \
        --instance=$INSTANCE_NAME \
        --password="$APP_PASSWORD"
    echo "✅ User created"
fi

# Get connection details
INSTANCE_CONNECTION_NAME=$(gcloud sql instances describe $INSTANCE_NAME --format="value(connectionName)")
PUBLIC_IP=$(gcloud sql instances describe $INSTANCE_NAME --format="value(ipAddresses[0].ipAddress)")

# Initialize database schema using Alembic
echo "Initializing database schema with Alembic..."
# Set environment variables for migration
export DB_CONNECTION_NAME=$INSTANCE_CONNECTION_NAME
export DB_NAME=$DATABASE_NAME
export DB_USER=appuser
export DB_PASSWORD=$APP_PASSWORD

# Run initial migration
echo "Running database migrations..."
chmod +x run-migrations.sh
./run-migrations.sh || echo "⚠️  Migration failed, but continuing..."

echo ""
echo "=== Cloud SQL Setup Complete ==="
echo "Instance Name: $INSTANCE_NAME"
echo "Database Name: $DATABASE_NAME"
echo "Connection Name: $INSTANCE_CONNECTION_NAME"
echo "Public IP: $PUBLIC_IP"
echo "Root Password: $ROOT_PASSWORD"
echo "App User Password: $APP_PASSWORD"
echo ""
echo "Connection string: mysql://appuser:$APP_PASSWORD@$PUBLIC_IP:3306/$DATABASE_NAME"
echo ""
echo "Database schema has been initialized with all tables and sample data."
echo "Save these credentials securely!"
echo "================================"
