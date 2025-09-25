#!/bin/bash

# Complete GCP Deployment Script (Idempotent)
# This script sets up the entire infrastructure and deploys the app
# Can be run multiple times safely

set -e

PROJECT_ID="i18n-l10n"
INSTANCE_NAME="i18n-l10n-mysql"
SERVICE_NAME="i18n-l10n-app"
REGION="europe-north1"

echo "Starting idempotent deployment for i18n-l10n project..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI is not installed. Please install it first."
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "Please authenticate with gcloud first:"
    echo "gcloud auth login"
    exit 1
fi

# Set the project
gcloud config set project $PROJECT_ID

# Set quota project to avoid warnings
gcloud auth application-default set-quota-project $PROJECT_ID

echo "Using project: $PROJECT_ID"

# Function to check if Cloud SQL instance exists
check_cloud_sql_instance() {
    if gcloud sql instances describe $INSTANCE_NAME --quiet &>/dev/null; then
        echo "✅ Cloud SQL instance '$INSTANCE_NAME' already exists"
        return 0
    else
        echo "❌ Cloud SQL instance '$INSTANCE_NAME' does not exist"
        return 1
    fi
}

# Function to check if Cloud Run service exists
check_cloud_run_service() {
    if gcloud run services describe $SERVICE_NAME --region=$REGION --quiet &>/dev/null; then
        echo "✅ Cloud Run service '$SERVICE_NAME' already exists"
        return 0
    else
        echo "❌ Cloud Run service '$SERVICE_NAME' does not exist"
        return 1
    fi
}

# Function to check if required APIs are enabled
check_apis() {
    echo "Checking required APIs..."
    
    local apis=("sqladmin.googleapis.com" "run.googleapis.com" "cloudbuild.googleapis.com" "containerregistry.googleapis.com" "translate.googleapis.com")
    local missing_apis=()
    
    for api in "${apis[@]}"; do
        if gcloud services list --enabled --filter="name:$api" --format="value(name)" | grep -q "$api"; then
            echo "✅ $api is enabled"
        else
            echo "❌ $api is not enabled"
            missing_apis+=("$api")
        fi
    done
    
    if [ ${#missing_apis[@]} -gt 0 ]; then
        echo "Enabling missing APIs..."
        gcloud services enable "${missing_apis[@]}"
        echo "✅ All required APIs are now enabled"
    fi
}

# Step 1: Check and enable APIs
echo ""
echo "=== Step 1: Checking and enabling required APIs ==="
check_apis

# Step 2: Set up Cloud SQL (idempotent)
echo ""
echo "=== Step 2: Setting up Cloud SQL MySQL (idempotent) ==="
if check_cloud_sql_instance; then
    echo "Cloud SQL instance already exists, skipping creation"
    
    # Check if database exists
    if gcloud sql databases describe i18n_l10n_db --instance=$INSTANCE_NAME --quiet &>/dev/null; then
        echo "✅ Database 'i18n_l10n_db' already exists"
    else
        echo "Creating database 'i18n_l10n_db'..."
        gcloud sql databases create i18n_l10n_db --instance=$INSTANCE_NAME
    fi
    
    # Check if app user exists
    if gcloud sql users describe appuser --instance=$INSTANCE_NAME --quiet &>/dev/null; then
        echo "✅ User 'appuser' already exists"
    else
        echo "Creating user 'appuser'..."
        gcloud sql users create appuser --instance=$INSTANCE_NAME --password="$(openssl rand -base64 32)"
    fi
    
    # Run migrations if needed
    echo "Running database migrations..."
    chmod +x run-migrations.sh
    ./run-migrations.sh || echo "⚠️  Migration failed, but continuing..."
    
else
    echo "Creating Cloud SQL instance..."
    chmod +x cloud-sql-setup.sh
    chmod +x init-database.sh
    ./cloud-sql-setup.sh
fi

# Step 3: Deploy to Cloud Run (idempotent)
echo ""
echo "=== Step 3: Deploying to Cloud Run (idempotent) ==="
if check_cloud_run_service; then
    echo "Cloud Run service already exists, updating..."
    chmod +x cloud-run-deploy.sh
    ./cloud-run-deploy.sh
else
    echo "Creating Cloud Run service..."
    chmod +x cloud-run-deploy.sh
    ./cloud-run-deploy.sh
fi

# Step 4: Verify deployment
echo ""
echo "=== Step 4: Verifying deployment ==="

# Check Cloud SQL status
if check_cloud_sql_instance; then
    INSTANCE_STATUS=$(gcloud sql instances describe $INSTANCE_NAME --format="value(state)")
    echo "✅ Cloud SQL instance status: $INSTANCE_STATUS"
else
    echo "❌ Cloud SQL instance not found"
fi

# Check Cloud Run status
if check_cloud_run_service; then
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')
    echo "✅ Cloud Run service URL: $SERVICE_URL"
    
    # Test the service
    echo "Testing service health..."
    if curl -f -s "$SERVICE_URL" > /dev/null; then
        echo "✅ Service is responding"
    else
        echo "⚠️  Service may not be ready yet (this is normal for new deployments)"
    fi
else
    echo "❌ Cloud Run service not found"
fi

echo ""
echo "=== Idempotent Deployment Complete! ==="
echo "Your i18n-l10n app is now running on Google Cloud Platform."
echo "The script can be run multiple times safely."
echo "=========================================="
