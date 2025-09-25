# GCP Deployment Guide for i18n-l10n

This directory contains all the necessary scripts and configurations to deploy the i18n-l10n NiceGUI application to Google Cloud Platform with a MySQL database.

## Prerequisites

1. **Google Cloud SDK**: Install and configure gcloud CLI
   ```bash
   # Install gcloud CLI
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   
   # Authenticate
   gcloud auth login
   gcloud config set project i18n-l10n
   ```

2. **Terraform** (optional, for infrastructure as code):
   ```bash
   # Install Terraform
   brew install terraform  # macOS
   # or download from https://www.terraform.io/downloads
   ```

## Quick Start

### Option 1: Automated Deployment (Recommended)

Run the complete deployment script:

```bash
cd deploy
chmod +x deploy-all.sh
./deploy-all.sh
```

This will:
1. Set up Cloud SQL MySQL instance
2. Deploy the app to Cloud Run
3. Configure all necessary connections

### Option 2: Manual Step-by-Step Deployment

#### Step 1: Set up Cloud SQL MySQL

```bash
cd deploy
chmod +x cloud-sql-setup.sh
./cloud-sql-setup.sh
```

This creates:
- Cloud SQL MySQL 8.0 instance
- Database: `i18n_l10n_db`
- User: `appuser`
- **Database schemas and tables**
- **Sample translation data**
- Automatic backups and maintenance

#### Step 2: Deploy to Cloud Run

```bash
chmod +x cloud-run-deploy.sh
./cloud-run-deploy.sh
```

This will:
- Build and push Docker image to Container Registry
- Deploy to Cloud Run with Cloud SQL connection
- Configure environment variables

### Option 3: Infrastructure as Code with Terraform

```bash
cd deploy/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
chmod +x deploy.sh
./deploy.sh
```

## Configuration Files

### Cloud SQL Setup (`cloud-sql-setup.sh`)
- Creates MySQL 8.0 instance
- Configures automatic backups
- Sets up database and user
- **Creates all database schemas and tables**
- **Imports sample translation data**
- Generates secure passwords

### Database Schema (`sql-schema.sql`)
- Complete SQL DDL for all tables
- Includes indexes for performance
- Sample translation tags and data
- Language enum definitions

### Database Initialization (`init-database.sh`)
- Python-based schema initialization
- Creates translation tags
- Adds sample translations
- Can be run independently

### Cloud Run Deployment (`cloud-run-deploy.sh`)
- Builds Docker image
- Pushes to Container Registry
- Deploys to Cloud Run
- Configures Cloud SQL connection

### Terraform Configuration
- `main.tf`: Complete infrastructure definition
- `variables.tf`: Configurable parameters
- `outputs.tf`: Deployment outputs
- `terraform.tfvars.example`: Example configuration

### Cloud Build (`cloudbuild.yaml`)
- Automated CI/CD pipeline
- Builds and deploys on code changes
- Integrates with Cloud Source Repositories

## Environment Variables

The application uses these environment variables:

- `PROJECT_ID`: GCP project ID
- `DB_CONNECTION_NAME`: Cloud SQL connection name
- `DB_NAME`: Database name
- `DB_USER`: Database user
- `DB_PASSWORD`: Database password (set during Cloud SQL setup)

## Database Schema

The application creates these tables:

- `users`: User information
- `greetings`: Greeting history
- `counters`: Session-based counters

## Monitoring and Logs

- **Cloud Run Logs**: View in Cloud Console > Cloud Run > Logs
- **Cloud SQL Logs**: View in Cloud Console > SQL > Logs
- **Application Logs**: Check Cloud Run service logs

## Scaling and Performance

- **Cloud Run**: Auto-scales from 0 to 10 instances
- **Cloud SQL**: Uses `db-f1-micro` tier (upgradeable)
- **Memory**: 1GB per Cloud Run instance
- **CPU**: 1 vCPU per instance

## Security

- Cloud SQL uses private IP (via VPC connector)
- No public database access
- Secure password generation
- IAM-based access control

## Cost Optimization

- Cloud Run scales to zero when not in use
- Cloud SQL can be stopped when not needed
- Use `db-f1-micro` for development
- Monitor usage in Cloud Console

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check Cloud SQL instance is running
   - Verify connection name and credentials
   - Ensure VPC connector is configured

2. **Cloud Run Deployment Failed**
   - Check Docker image builds successfully
   - Verify all environment variables are set
   - Check Cloud Run logs for errors

3. **Permission Denied**
   - Ensure proper IAM roles are assigned
   - Check service account permissions
   - Verify API enablement

### Useful Commands

```bash
# Check Cloud SQL status
gcloud sql instances list

# View Cloud Run services
gcloud run services list

# Check logs
gcloud logging read "resource.type=cloud_run_revision"

# Connect to Cloud SQL
gcloud sql connect i18n-l10n-mysql --user=root
```

## Cleanup

To remove all resources:

```bash
# Delete Cloud Run service
gcloud run services delete i18n-l10n-app --region=europe-north1

# Delete Cloud SQL instance
gcloud sql instances delete i18n-l10n-mysql

# Delete Docker images
gcloud container images delete gcr.io/i18n-l10n/i18n-l10n-app
```

Or with Terraform:
```bash
cd terraform
terraform destroy
```

## Next Steps

1. Set up custom domain (optional)
2. Configure SSL certificates
3. Set up monitoring and alerting
4. Implement CI/CD pipeline
5. Add i18n/l10n features
