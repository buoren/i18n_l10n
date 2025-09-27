#!/bin/bash

# Comprehensive deployment script with Google OAuth setup
# This script handles the complete deployment process including OAuth configuration

set -e

echo "🚀 i18n-l10n Application Deployment with Google OAuth"
echo "====================================================="
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI (gcloud) is not installed."
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform is not installed."
    echo "Please install it from: https://terraform.io/downloads"
    exit 1
fi

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed."
    echo "Please install it from: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ All prerequisites are installed"
echo ""

# Get project information
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ No project is set. Please set a project:"
    echo "gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "✅ Using project: $PROJECT_ID"
echo ""

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ You are not authenticated with Google Cloud."
    echo "Please run: gcloud auth login"
    exit 1
fi

echo "✅ Authenticated with Google Cloud"
echo ""

# Step 1: Set up Google OAuth
echo "🔐 Setting up Google OAuth 2.0..."
echo "This will open the Google Cloud Console for OAuth configuration."
echo ""

read -p "Do you want to set up OAuth now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ./scripts/setup_google_oauth.sh
else
    echo "⚠️  Skipping OAuth setup. Make sure to configure it manually before deployment."
fi

echo ""

# Step 2: Build and push Docker image
echo "🐳 Building and pushing Docker image..."

# Configure Docker for Google Cloud
gcloud auth configure-docker

# Build the image
echo "Building Docker image..."
docker build -t gcr.io/$PROJECT_ID/i18n-l10n-app .

# Push the image
echo "Pushing Docker image to Google Container Registry..."
docker push gcr.io/$PROJECT_ID/i18n-l10n-app

echo "✅ Docker image built and pushed successfully"
echo ""

# Step 3: Deploy infrastructure with Terraform
echo "🏗️  Deploying infrastructure with Terraform..."

cd deploy/terraform

# Initialize Terraform
echo "Initializing Terraform..."
terraform init

# Check if terraform.tfvars exists
if [ ! -f "terraform.tfvars" ]; then
    echo "❌ terraform.tfvars not found!"
    echo "Please create it with your configuration values."
    echo "You can use terraform.tfvars.example as a template."
    exit 1
fi

# Plan the deployment
echo "Planning Terraform deployment..."
terraform plan

# Ask for confirmation
read -p "Do you want to apply the Terraform plan? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Applying Terraform plan..."
    terraform apply -auto-approve
else
    echo "❌ Deployment cancelled by user"
    exit 1
fi

echo "✅ Infrastructure deployed successfully"
echo ""

# Step 4: Get deployment information
echo "📊 Getting deployment information..."

CLOUD_RUN_URL=$(terraform output -raw cloud_run_url)
DB_CONNECTION_NAME=$(terraform output -raw database_connection_name)

echo "✅ Deployment completed!"
echo ""
echo "🌐 Application URL: $CLOUD_RUN_URL"
echo "🗄️  Database Connection: $DB_CONNECTION_NAME"
echo ""

# Step 5: Update OAuth configuration
echo "🔧 Updating OAuth configuration with production URL..."

echo "Please update your OAuth 2.0 credentials in Google Cloud Console:"
echo "1. Go to: https://console.cloud.google.com/apis/credentials"
echo "2. Click on your OAuth 2.0 client ID"
echo "3. Add these authorized JavaScript origins:"
echo "   - $CLOUD_RUN_URL"
echo "4. Add these authorized redirect URIs:"
echo "   - $CLOUD_RUN_URL/login"
echo "5. Save the changes"
echo ""

read -p "Press Enter when you've updated the OAuth configuration..."

# Step 6: Test the deployment
echo "🧪 Testing the deployment..."

echo "Testing application health..."
if curl -f -s "$CLOUD_RUN_URL" > /dev/null; then
    echo "✅ Application is responding"
else
    echo "❌ Application is not responding"
fi

echo "Testing login page..."
if curl -f -s "$CLOUD_RUN_URL/login" > /dev/null; then
    echo "✅ Login page is accessible"
else
    echo "❌ Login page is not accessible"
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Test the application at: $CLOUD_RUN_URL"
echo "2. Test the login flow at: $CLOUD_RUN_URL/login"
echo "3. Access the admin panel at: $CLOUD_RUN_URL/admin"
echo "4. Monitor the application in Google Cloud Console"
echo ""
echo "🔧 Useful commands:"
echo "- View logs: gcloud logs tail --service=i18n-l10n-app"
echo "- Update app: ./scripts/deploy_with_auth.sh"
echo "- Destroy infrastructure: cd deploy/terraform && terraform destroy"
echo ""

cd ../..
