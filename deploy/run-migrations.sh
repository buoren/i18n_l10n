#!/bin/bash

# Run database migrations using Python (no MySQL client required)
# This script runs migrations using the application's database connection

set -e

PROJECT_ID="i18n-l10n"
INSTANCE_NAME="i18n-l10n-mysql"
DATABASE_NAME="i18n_l10n_db"

echo "Running database migrations..."

# Set the project
gcloud config set project $PROJECT_ID

# Get connection details
INSTANCE_CONNECTION_NAME=$(gcloud sql instances describe $INSTANCE_NAME --format="value(connectionName)")
INSTANCE_IP=$(gcloud sql instances describe $INSTANCE_NAME --format="value(ipAddresses[0].ipAddress)")

echo "Using connection: $INSTANCE_CONNECTION_NAME"
echo "Using IP: $INSTANCE_IP"

# Set environment variables for migration
export DB_HOST=$INSTANCE_IP
export DB_PORT=3306
export DB_NAME=$DATABASE_NAME
export DB_USER=appuser
export DB_PASSWORD="temp_password"  # This will be updated by the app

# Create a simple migration script
cat > /tmp/run_migration.py << 'EOF'
import os
import sys
from sqlalchemy import create_engine, text
from datetime import datetime

# Set up environment for direct connection
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '3306')
db_name = os.getenv('DB_NAME', 'i18n_l10n_db')
db_user = os.getenv('DB_USER', 'appuser')
db_password = os.getenv('DB_PASSWORD', 'password')

def run_migrations():
    """Run database migrations"""
    try:
        # Create database URL
        database_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        
        print(f"Connecting to database: {db_host}:{db_port}/{db_name}")
        
        # Create engine
        engine = create_engine(database_url, pool_pre_ping=True)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
        
        # Import and run Alembic migrations
        from alembic import command
        from alembic.config import Config
        
        # Set up Alembic config
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        print("✅ Database migrations completed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
EOF

# Run the migration
echo "Running migrations..."
python3 /tmp/run_migration.py

# Clean up
rm -f /tmp/run_migration.py

echo "Migration process completed!"
