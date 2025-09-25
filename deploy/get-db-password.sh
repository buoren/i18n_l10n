#!/bin/bash

# Get database password for Cloud Run deployment
# This script retrieves the app user password from Cloud SQL

set -e

PROJECT_ID="i18n-l10n"
INSTANCE_NAME="i18n-l10n-mysql"

echo "Getting database password for Cloud Run deployment..."

# Get the app user password
# Note: This is a simplified approach. In production, you'd want to use Secret Manager
APP_PASSWORD=$(gcloud sql users describe appuser --instance=$INSTANCE_NAME --format="value(password)" 2>/dev/null || echo "password")

if [ "$APP_PASSWORD" = "password" ]; then
    echo "⚠️  Could not retrieve password, using default. You may need to set the password manually."
    echo "To set the password manually:"
    echo "gcloud sql users set-password appuser --instance=$INSTANCE_NAME --password='your-secure-password'"
else
    echo "✅ Retrieved app user password"
fi

echo "App user password: $APP_PASSWORD"
echo ""
echo "To update Cloud Run with the correct password, run:"
echo "gcloud run services update i18n-l10n-app --region=europe-north1 --set-env-vars=\"DB_PASSWORD=$APP_PASSWORD\""
