#!/bin/bash

# Script to help set up Google OAuth 2.0 for the i18n-l10n application
# This script provides instructions and helps configure the necessary settings

set -e

echo "🔐 Google OAuth 2.0 Setup for i18n-l10n Application"
echo "=================================================="
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI (gcloud) is not installed."
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ You are not authenticated with Google Cloud."
    echo "Please run: gcloud auth login"
    exit 1
fi

# Get current project
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ No project is set. Please set a project:"
    echo "gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "✅ Using project: $PROJECT_ID"
echo ""

# Enable required APIs
echo "🔧 Enabling required Google Cloud APIs..."
gcloud services enable identitytoolkit.googleapis.com
gcloud services enable oauth2.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com

echo "✅ APIs enabled successfully"
echo ""

# Create OAuth consent screen
echo "📋 Setting up OAuth consent screen..."
echo "Please follow these steps in the Google Cloud Console:"
echo ""
echo "1. Go to: https://console.cloud.google.com/apis/credentials/consent"
echo "2. Select your project: $PROJECT_ID"
echo "3. Choose 'External' user type and click 'Create'"
echo "4. Fill out the required fields:"
echo "   - App name: i18n-l10n Translation App"
echo "   - User support email: your-email@example.com"
echo "   - Developer contact information: your-email@example.com"
echo "5. Click 'Save and Continue'"
echo "6. In the Scopes section, click 'Add or Remove Scopes'"
echo "7. Add these scopes:"
echo "   - ../auth/userinfo.email"
echo "   - ../auth/userinfo.profile"
echo "   - openid"
echo "8. Click 'Save and Continue'"
echo "9. Add test users if needed (for testing)"
echo "10. Click 'Save and Continue'"
echo ""

read -p "Press Enter when you've completed the OAuth consent screen setup..."

# Create OAuth 2.0 credentials
echo "🔑 Creating OAuth 2.0 credentials..."
echo "Please follow these steps in the Google Cloud Console:"
echo ""
echo "1. Go to: https://console.cloud.google.com/apis/credentials"
echo "2. Click 'Create Credentials' > 'OAuth client ID'"
echo "3. Choose 'Web application'"
echo "4. Set the name: i18n-l10n-web-client"
echo "5. Add authorized JavaScript origins:"
echo "   - http://localhost:8080 (for local development)"
echo "   - https://your-cloud-run-url.run.app (for production)"
echo "6. Add authorized redirect URIs:"
echo "   - http://localhost:8080/login (for local development)"
echo "   - https://your-cloud-run-url.run.app/login (for production)"
echo "7. Click 'Create'"
echo "8. Copy the Client ID and Client Secret"
echo ""

read -p "Press Enter when you've created the OAuth credentials..."

# Get credentials from user
echo "📝 Please enter your OAuth credentials:"
read -p "Google Client ID: " GOOGLE_CLIENT_ID
read -s -p "Google Client Secret: " GOOGLE_CLIENT_SECRET
echo ""

# Generate JWT secret
JWT_SECRET=$(openssl rand -base64 32)

echo "🔐 Generated JWT secret: $JWT_SECRET"
echo ""

# Create terraform.tfvars file
echo "📄 Creating terraform.tfvars file..."
cat > ../deploy/terraform/terraform.tfvars << EOF
# Terraform variables for i18n-l10n GCP infrastructure
project_id = "$PROJECT_ID"
region = "europe-north1"
database_tier = "db-f1-micro"
environment = "dev"

# OAuth Configuration
google_client_id = "$GOOGLE_CLIENT_ID"
google_client_secret = "$GOOGLE_CLIENT_SECRET"
jwt_secret = "$JWT_SECRET"

# Database password (you'll need to set this)
db_password = "CHANGE_ME_SECURE_PASSWORD"
EOF

echo "✅ Created terraform.tfvars file"
echo ""

# Create .env file for local development
echo "📄 Creating .env file for local development..."
cat > ../.env << EOF
# Local development environment variables
GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET=$GOOGLE_CLIENT_SECRET
JWT_SECRET=$JWT_SECRET
PROJECT_ID=$PROJECT_ID
DB_CONNECTION_NAME=localhost:3306
DB_NAME=i18n_l10n_db
DB_USER=root
DB_PASSWORD=your_local_password
EOF

echo "✅ Created .env file for local development"
echo ""

echo "🎉 Google OAuth setup completed!"
echo ""
echo "Next steps:"
echo "1. Update the database password in terraform.tfvars"
echo "2. Update the Cloud Run URL in the OAuth credentials (after deployment)"
echo "3. Deploy the application:"
echo "   cd ../deploy/terraform"
echo "   terraform init"
echo "   terraform plan"
echo "   terraform apply"
echo ""
echo "4. For local development:"
echo "   source .env"
echo "   python -m i18n_l10n.main"
echo ""
echo "5. Test the authentication flow at: http://localhost:8080/login"
echo ""
