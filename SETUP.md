# Quick Setup Guide - i18n-l10n App

This is a step-by-step guide to get your i18n-l10n NiceGUI application running on Google Cloud Platform.

## 🚀 One-Command Setup (Recommended)

If you want to get everything running quickly:

```bash
# 1. Clone and navigate to the project
cd /Users/buoren/repos/i18n_l10n

# 2. Install Google Cloud SDK (if not already installed)
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# 3. Authenticate with Google Cloud
gcloud auth login
gcloud config set project i18n-l10n

# 4. Deploy everything (idempotent - safe to run multiple times)
cd deploy
./deploy-all.sh
```

That's it! Your app will be available at the URL shown at the end.

**✨ The script is idempotent** - you can run it multiple times safely without errors!

## 📋 Prerequisites Checklist

Before running the setup, make sure you have:

- [ ] **Google Cloud Account** with billing enabled
- [ ] **Google Cloud SDK** installed and authenticated
- [ ] **Project ID**: `i18n-l10n` (or update scripts with your project ID)
- [ ] **Billing enabled** on your GCP project

## 🔧 Manual Setup (Step by Step)

If you prefer to run each step manually:

### Step 1: Set up Cloud SQL Database
```bash
cd deploy
chmod +x cloud-sql-setup.sh
./cloud-sql-setup.sh
```
This creates:
- MySQL 8.0 instance
- Database with all tables
- Sample translation data
- Secure passwords

### Step 2: Deploy to Cloud Run
```bash
chmod +x cloud-run-deploy.sh
./cloud-run-deploy.sh
```
This:
- Builds Docker image
- Deploys to Cloud Run
- Connects to database

## 🏠 Local Development Setup

To run the app locally for development:

```bash
# 1. Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# 2. Install dependencies
poetry install

# 3. Run locally (uses SQLite fallback)
poetry run python -m i18n_l10n.main
```

The app will be available at `http://localhost:8080`

## 🌐 What You Get

After setup, you'll have:

- **Web App**: NiceGUI application with interactive UI
- **Database**: MySQL with translation tables
- **Features**:
  - Hello World greeting system
  - Click counter (persistent)
  - Recent greetings display
  - Language selection (ready for i18n)
  - Database status indicator

## 🔍 Troubleshooting

### Check Deployment Status:
```bash
# Quick status check
cd deploy
./check-status.sh

# Or check individual resources
gcloud sql instances list
gcloud run services list
gcloud container images list
```

### Common Issues:

1. **"Project not found"**
   ```bash
   gcloud projects create i18n-l10n
   gcloud config set project i18n-l10n
   ```

2. **"Billing not enabled"**
   - Go to Google Cloud Console
   - Enable billing for your project

3. **"Permission denied"**
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

4. **"Cloud SQL instance not found"**
   - Run `./deploy-all.sh` again (it's idempotent!)
   - Or run `./cloud-sql-setup.sh` specifically

5. **"Service not responding"**
   - Check status with `./check-status.sh`
   - Wait a few minutes for Cloud Run to start
   - Check logs: `gcloud logging read "resource.type=cloud_run_revision"`

### Re-run Deployment:
```bash
# Safe to run multiple times
./deploy-all.sh

# Or check what's missing first
./check-status.sh
```

## 📊 Cost Estimation

- **Cloud SQL**: ~$7-15/month (db-f1-micro)
- **Cloud Run**: ~$0-5/month (scales to zero)
- **Container Registry**: ~$0.10/GB/month
- **Total**: ~$7-20/month for development

## 🧹 Cleanup

To remove everything and avoid charges:

```bash
# Delete Cloud Run service
gcloud run services delete i18n-l10n-app --region=europe-north1

# Delete Cloud SQL instance
gcloud sql instances delete i18n-l10n-mysql

# Delete Docker images
gcloud container images delete gcr.io/i18n-l10n/i18n-l10n-app
```

## 📚 More Information

- **Full Documentation**: `deploy/README.md`
- **Database Schema**: `deploy/sql-schema.sql`
- **Terraform Setup**: `deploy/terraform/`
- **Local Development**: `README.md`

## 🆘 Need Help?

If you run into issues:

1. Check the logs: `gcloud logging read "resource.type=cloud_run_revision"`
2. Verify your GCP project has billing enabled
3. Make sure all APIs are enabled
4. Check the detailed documentation in `deploy/README.md`

---

**Ready to start?** Run `cd deploy && ./deploy-all.sh` and you'll be up and running in about 5-10 minutes! 🚀
