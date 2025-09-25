# Troubleshooting Guide

This guide helps you resolve common deployment issues.

## 🚨 Common Errors and Solutions

### 1. MySQL Client Not Found

**Error:**
```
ERROR: (gcloud.sql.connect) Mysql client not found. Please install a mysql client and make sure it is in PATH to be able to connect to the database instance.
```

**Solution:**
The deployment scripts now handle this automatically. If you still see this error:

```bash
# Option 1: Install MySQL client (macOS)
brew install mysql-client

# Option 2: Install MySQL client (Ubuntu/Debian)
sudo apt-get install mysql-client

# Option 3: Skip migration (will run on app startup)
# The app will run migrations automatically when it starts
```

### 2. Dockerfile Not Found

**Error:**
```
ERROR: (gcloud.builds.submit) Invalid value for [source]: Dockerfile required when specifying --tag
```

**Solution:**
Make sure you're running from the correct directory:

```bash
# Run from the deploy directory
cd deploy
./deploy-all.sh

# Or check if Dockerfile exists
ls -la ../Dockerfile
```

### 3. Quota Project Warning

**Error:**
```
WARNING: Your active project does not match the quota project in your local Application Default Credentials file.
```

**Solution:**
This is now fixed automatically, but you can also run:

```bash
gcloud auth application-default set-quota-project i18n-l10n
```

### 4. Cloud Run Service Not Found

**Error:**
```
❌ Cloud Run service 'i18n-l10n-app' does not exist
```

**Solution:**
This is normal for first-time deployment. The script will create it automatically.

### 5. Migration Failed

**Error:**
```
⚠️ Migration failed, but continuing...
```

**Solution:**
Migrations will run automatically when the app starts. This is not a critical error.

## 🔧 Manual Fixes

### Reset Everything

If you want to start fresh:

```bash
# Delete all resources
gcloud sql instances delete i18n-l10n-mysql
gcloud run services delete i18n-l10n-app --region=europe-north1
gcloud container images delete gcr.io/i18n-l10n/i18n-l10n-app

# Re-run deployment
./deploy-all.sh
```

### Check Status

```bash
# Check what's deployed
./check-status.sh

# Check individual resources
gcloud sql instances list
gcloud run services list
gcloud container images list
```

### Manual Migration

If migrations fail, run them manually:

```bash
# Set environment variables
export DB_HOST=your-instance-ip
export DB_PORT=3306
export DB_NAME=i18n_l10n_db
export DB_USER=appuser
export DB_PASSWORD=your-password

# Run migrations
./run-migrations.sh
```

## 🐛 Debug Mode

Enable debug mode for more detailed output:

```bash
# Set debug environment
export DEBUG=1

# Run deployment with verbose output
./deploy-all.sh
```

## 📞 Getting Help

### Check Logs

```bash
# Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision" --limit=50

# Cloud SQL logs
gcloud logging read "resource.type=sql_database" --limit=20

# Build logs
gcloud logging read "resource.type=cloud_build" --limit=20
```

### Common Issues Checklist

- [ ] Project has billing enabled
- [ ] Required APIs are enabled
- [ ] User has proper permissions
- [ ] Dockerfile exists in project root
- [ ] Cloud SQL instance is running
- [ ] Database and user exist
- [ ] Cloud Run service is deployed

### Quick Fixes

```bash
# Fix quota project
gcloud auth application-default set-quota-project i18n-l10n

# Enable missing APIs
gcloud services enable sqladmin.googleapis.com run.googleapis.com cloudbuild.googleapis.com containerregistry.googleapis.com

# Check project
gcloud config get-value project

# Re-authenticate
gcloud auth login
gcloud auth application-default login
```

## 🎯 Success Indicators

You know everything is working when:

- ✅ `./check-status.sh` shows all green checkmarks
- ✅ Cloud Run service URL is accessible
- ✅ Database migrations completed
- ✅ No error messages in logs

## 📝 Still Having Issues?

1. **Check the logs** using the commands above
2. **Run `./check-status.sh`** to see what's missing
3. **Try the manual fixes** listed above
4. **Reset and start fresh** if needed

The deployment is designed to be resilient and self-healing, so most issues resolve themselves on subsequent runs.
