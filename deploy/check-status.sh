#!/bin/bash

# Status check script for i18n-l10n deployment
# This script checks the status of all deployed resources

set -e

PROJECT_ID="i18n-l10n"
INSTANCE_NAME="i18n-l10n-mysql"
SERVICE_NAME="i18n-l10n-app"
REGION="europe-north1"

echo "Checking deployment status for i18n-l10n project..."
echo "Project: $PROJECT_ID"
echo "=========================================="

# Set the project
gcloud config set project $PROJECT_ID

# Check Cloud SQL instance
echo ""
echo "=== Cloud SQL Status ==="
if gcloud sql instances describe $INSTANCE_NAME --quiet &>/dev/null; then
    INSTANCE_STATUS=$(gcloud sql instances describe $INSTANCE_NAME --format="value(state)")
    INSTANCE_TIER=$(gcloud sql instances describe $INSTANCE_NAME --format="value(settings.tier)")
    INSTANCE_REGION=$(gcloud sql instances describe $INSTANCE_NAME --format="value(region)")
    
    echo "✅ Instance: $INSTANCE_NAME"
    echo "   Status: $INSTANCE_STATUS"
    echo "   Tier: $INSTANCE_TIER"
    echo "   Region: $INSTANCE_REGION"
    
    # Check database
    if gcloud sql databases describe i18n_l10n_db --instance=$INSTANCE_NAME --quiet &>/dev/null; then
        echo "✅ Database: i18n_l10n_db"
    else
        echo "❌ Database: i18n_l10n_db (not found)"
    fi
    
    # Check user
    if gcloud sql users describe appuser --instance=$INSTANCE_NAME --quiet &>/dev/null; then
        echo "✅ User: appuser"
    else
        echo "❌ User: appuser (not found)"
    fi
    
    # Get connection info
    CONNECTION_NAME=$(gcloud sql instances describe $INSTANCE_NAME --format="value(connectionName)")
    PUBLIC_IP=$(gcloud sql instances describe $INSTANCE_NAME --format="value(ipAddresses[0].ipAddress)")
    echo "   Connection: $CONNECTION_NAME"
    echo "   Public IP: $PUBLIC_IP"
    
else
    echo "❌ Cloud SQL instance '$INSTANCE_NAME' not found"
fi

# Check Cloud Run service
echo ""
echo "=== Cloud Run Status ==="
if gcloud run services describe $SERVICE_NAME --region=$REGION --quiet &>/dev/null; then
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')
    SERVICE_STATUS=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.conditions[0].status)')
    SERVICE_READY=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.conditions[0].type)')
    
    echo "✅ Service: $SERVICE_NAME"
    echo "   URL: $SERVICE_URL"
    echo "   Status: $SERVICE_STATUS"
    echo "   Ready: $SERVICE_READY"
    
    # Test service health
    echo "   Testing service..."
    if curl -f -s "$SERVICE_URL" > /dev/null; then
        echo "   ✅ Service is responding"
    else
        echo "   ⚠️  Service not responding (may be starting up)"
    fi
    
else
    echo "❌ Cloud Run service '$SERVICE_NAME' not found"
fi

# Check required APIs
echo ""
echo "=== API Status ==="
local apis=("sqladmin.googleapis.com" "run.googleapis.com" "cloudbuild.googleapis.com" "containerregistry.googleapis.com")

for api in "${apis[@]}"; do
    if gcloud services list --enabled --filter="name:$api" --format="value(name)" | grep -q "$api"; then
        echo "✅ $api"
    else
        echo "❌ $api (not enabled)"
    fi
done

# Check Docker images
echo ""
echo "=== Container Images ==="
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"
if gcloud container images describe $IMAGE_NAME --quiet &>/dev/null; then
    echo "✅ Image: $IMAGE_NAME"
    
    # Get image details
    CREATED=$(gcloud container images describe $IMAGE_NAME --format="value(creationTimestamp)")
    echo "   Created: $CREATED"
else
    echo "❌ Image: $IMAGE_NAME (not found)"
fi

# Summary
echo ""
echo "=== Summary ==="
TOTAL_CHECKS=0
PASSED_CHECKS=0

# Count checks
if gcloud sql instances describe $INSTANCE_NAME --quiet &>/dev/null; then
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
fi

if gcloud run services describe $SERVICE_NAME --region=$REGION --quiet &>/dev/null; then
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
fi

if gcloud container images describe $IMAGE_NAME --quiet &>/dev/null; then
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
fi

echo "Passed: $PASSED_CHECKS/$TOTAL_CHECKS checks"

if [ $PASSED_CHECKS -eq $TOTAL_CHECKS ]; then
    echo "🎉 All systems operational!"
else
    echo "⚠️  Some issues detected. Run './deploy-all.sh' to fix them."
fi

echo "=========================================="
