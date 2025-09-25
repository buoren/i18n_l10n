#!/bin/bash

# Database Schema Initialization Script
# This script creates the database schemas and initial data

set -e

# Configuration
PROJECT_ID="i18n-l10n"
INSTANCE_NAME="i18n-l10n-mysql"
DATABASE_NAME="i18n_l10n_db"
REGION="europe-north1"

echo "Initializing database schemas for i18n-l10n project..."

# Set the project
gcloud config set project $PROJECT_ID

# Get connection details
INSTANCE_CONNECTION_NAME=$(gcloud sql instances describe $INSTANCE_NAME --format="value(connectionName)")
echo "Using connection: $INSTANCE_CONNECTION_NAME"

# Create a temporary Python script to initialize the database
cat > /tmp/init_db.py << 'EOF'
import os
import sys
from sqlalchemy import create_engine, text
from datetime import datetime

# Set up environment for Cloud SQL connection
os.environ['DB_CONNECTION_NAME'] = sys.argv[1]
os.environ['DB_NAME'] = sys.argv[2]
os.environ['DB_USER'] = 'appuser'
os.environ['DB_PASSWORD'] = sys.argv[3]

# Import our database models
sys.path.append('/workspace')
from i18n_l10n.database import Base, db_manager, LanguageCode

def init_database():
    """Initialize the database with schemas and initial data"""
    print("Creating database schemas...")
    
    # Create all tables
    Base.metadata.create_all(bind=db_manager.engine)
    print("✓ Database schemas created successfully")
    
    # Create initial translation tags
    print("Creating initial translation tags...")
    
    # Common translation tags for the app
    initial_tags = [
        ("i18n-l10n-app", "Hello World"),
        ("i18n-l10n-app", "Welcome to the i18n/l10n Testing App"),
        ("i18n-l10n-app", "Your Name"),
        ("i18n-l10n-app", "Enter your name here..."),
        ("i18n-l10n-app", "Say Hello"),
        ("i18n-l10n-app", "Click Counter"),
        ("i18n-l10n-app", "Reset"),
        ("i18n-l10n-app", "Recent Greetings"),
        ("i18n-l10n-app", "Language Selection"),
        ("i18n-l10n-app", "Coming Soon"),
        ("i18n-l10n-app", "Database connected and storing data"),
        ("i18n-l10n-app", "Built with ❤️ using NiceGUI + MySQL"),
        ("i18n-l10n-app", "Refresh Greetings"),
        ("i18n-l10n-app", "No greetings yet"),
    ]
    
    tag_ids = {}
    for app, tag in initial_tags:
        tag_id = db_manager.create_translation_tag(app, tag)
        if tag_id:
            tag_ids[f"{app}:{tag}"] = tag_id
            print(f"✓ Created tag: {tag}")
        else:
            print(f"✗ Failed to create tag: {tag}")
    
    # Add some sample translations
    print("Adding sample translations...")
    
    # Sample translations for "Hello World"
    hello_world_tag_id = tag_ids.get("i18n-l10n-app:Hello World")
    if hello_world_tag_id:
        sample_translations = [
            (LanguageCode.EN_US, "Hello World"),
            (LanguageCode.ES_ES, "Hola Mundo"),
            (LanguageCode.FR_FR, "Bonjour le Monde"),
            (LanguageCode.DE_DE, "Hallo Welt"),
            (LanguageCode.IT_IT, "Ciao Mondo"),
            (LanguageCode.PT_BR, "Olá Mundo"),
            (LanguageCode.RU_RU, "Привет, мир"),
            (LanguageCode.JA_JP, "こんにちは世界"),
            (LanguageCode.KO_KR, "안녕하세요 세계"),
            (LanguageCode.ZH_CN, "你好世界"),
        ]
        
        for language, text in sample_translations:
            success = db_manager.save_translation(
                translation_tag_id=hello_world_tag_id,
                language=language,
                text=text,
                context="Main greeting message"
            )
            if success:
                print(f"✓ Added {language.value}: {text}")
            else:
                print(f"✗ Failed to add {language.value}")
    
    print("\n=== Database Initialization Complete ===")
    print("✓ All schemas created")
    print("✓ Initial translation tags created")
    print("✓ Sample translations added")
    print("=========================================")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python init_db.py <connection_name> <database_name> <password>")
        sys.exit(1)
    
    init_database()
EOF

# Get the app user password (you'll need to provide this)
echo "Please enter the app user password for the database:"
read -s APP_PASSWORD

# Run the initialization script using Cloud SQL Proxy or direct connection
echo "Running database initialization..."

# Check if we can connect directly
if command -v mysql &> /dev/null; then
    echo "Using direct MySQL connection..."
    # Get connection details
    INSTANCE_IP=$(gcloud sql instances describe $INSTANCE_NAME --format="value(ipAddresses[0].ipAddress)")
    
    # Run migration using Python script
    export DB_HOST=$INSTANCE_IP
    export DB_PORT=3306
    export DB_NAME=$DATABASE_NAME
    export DB_USER=appuser
    export DB_PASSWORD=$APP_PASSWORD
    
    python3 /tmp/init_db.py $INSTANCE_CONNECTION_NAME $DATABASE_NAME $APP_PASSWORD
else
    echo "MySQL client not found. Skipping migration - will be handled by application startup."
    echo "⚠️  Database migrations will run when the application starts."
fi

# Clean up
rm -f /tmp/init_db.py

echo ""
echo "Database initialization completed!"
echo "You can now deploy your application."
