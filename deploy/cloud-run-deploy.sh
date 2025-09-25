#!/bin/bash

# GCP Cloud Run Deployment Script
# This script deploys the i18n-l10n NiceGUI app to Cloud Run

set -e

# Configuration
PROJECT_ID="i18n-l10n"
SERVICE_NAME="i18n-l10n-app"
REGION="europe-north1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "Deploying i18n-l10n app to Cloud Run..."

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and push Docker image
echo "Building and pushing Docker image..."

# Check if Dockerfile exists
if [ ! -f "../Dockerfile" ]; then
    echo "❌ Dockerfile not found in project root"
    echo "Expected: $(pwd)/../Dockerfile"
    exit 1
fi

# Build from project root directory
cd ..
gcloud builds submit --tag $IMAGE_NAME .
cd deploy

# Deploy to Cloud Run (idempotent)
echo "Deploying to Cloud Run..."
if gcloud run services describe $SERVICE_NAME --region=$REGION --quiet &>/dev/null; then
    echo "✅ Cloud Run service '$SERVICE_NAME' already exists, updating..."
    gcloud run deploy $SERVICE_NAME \
        --image $IMAGE_NAME \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --port 8080 \
        --memory 1Gi \
        --cpu 1 \
        --min-instances 0 \
        --max-instances 10 \
        --timeout 300 \
        --concurrency 80 \
        --set-env-vars "PROJECT_ID=$PROJECT_ID,DB_HOST=35.228.166.220,DB_PORT=3306,DB_NAME=i18n_l10n_db,DB_USER=appuser,DB_PASSWORD=your-app-password" \
        --add-cloudsql-instances $PROJECT_ID:europe-north1:i18n-l10n-mysql
    echo "✅ Cloud Run service updated"
else
    echo "Creating new Cloud Run service..."
    gcloud run deploy $SERVICE_NAME \
        --image $IMAGE_NAME \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --port 8080 \
        --memory 1Gi \
        --cpu 1 \
        --min-instances 0 \
        --max-instances 10 \
        --timeout 300 \
        --concurrency 80 \
        --set-env-vars "PROJECT_ID=$PROJECT_ID,DB_HOST=35.228.166.220,DB_PORT=3306,DB_NAME=i18n_l10n_db,DB_USER=appuser,DB_PASSWORD=your-app-password" \
        --add-cloudsql-instances $PROJECT_ID:europe-north1:i18n-l10n-mysql
    echo "✅ Cloud Run service created"
fi

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')

echo ""
echo "=== Deployment Complete ==="
echo "Service Name: $SERVICE_NAME"
echo "Service URL: $SERVICE_URL"
echo "Region: $REGION"
echo "=========================="
