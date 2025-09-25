#!/bin/bash

# Terraform deployment script for i18n-l10n GCP infrastructure

set -e

echo "Deploying i18n-l10n infrastructure with Terraform..."

# Check if terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "Error: Terraform is not installed. Please install it first."
    echo "Visit: https://www.terraform.io/downloads"
    exit 1
fi

# Check if gcloud is installed and authenticated
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI is not installed. Please install it first."
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if terraform.tfvars exists
if [ ! -f "terraform.tfvars" ]; then
    echo "Error: terraform.tfvars file not found."
    echo "Please copy terraform.tfvars.example to terraform.tfvars and update the values."
    exit 1
fi

# Initialize Terraform
echo "Initializing Terraform..."
terraform init

# Plan the deployment
echo "Planning Terraform deployment..."
terraform plan

# Ask for confirmation
read -p "Do you want to apply these changes? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 1
fi

# Apply the configuration
echo "Applying Terraform configuration..."
terraform apply -auto-approve

# Get outputs
echo ""
echo "=== Deployment Complete! ==="
echo "Cloud Run URL: $(terraform output -raw cloud_run_url)"
echo "Database Connection Name: $(terraform output -raw database_connection_name)"
echo "Database Public IP: $(terraform output -raw database_public_ip)"
echo "============================="
