#!/usr/bin/env python3
"""
Database migration management script
"""

import os
import sys
import argparse
from alembic import command
from alembic.config import Config

def get_database_url():
    """Get database URL from environment variables"""
    # For Cloud SQL, we'll use the connection name
    if os.getenv('DB_CONNECTION_NAME'):
        connection_name = os.getenv('DB_CONNECTION_NAME')
        db_name = os.getenv('DB_NAME', 'i18n_l10n_db')
        db_user = os.getenv('DB_USER', 'appuser')
        db_password = os.getenv('DB_PASSWORD', '')
        return f"mysql+pymysql://{db_user}:{db_password}@/{db_name}?unix_socket=/cloudsql/{connection_name}"
    else:
        # Local development or direct connection
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '3306')
        db_name = os.getenv('DB_NAME', 'i18n_l10n_db')
        db_user = os.getenv('DB_USER', 'appuser')
        db_password = os.getenv('DB_PASSWORD', 'password')
        return f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

def run_migration(action, revision=None):
    """Run Alembic migration command"""
    try:
        # Set up Alembic config
        alembic_cfg = Config("alembic.ini")
        
        # Override the database URL
        database_url = get_database_url()
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
        if action == "upgrade":
            target = revision or "head"
            command.upgrade(alembic_cfg, target)
            print(f"✅ Database upgraded to {target}")
            
        elif action == "downgrade":
            target = revision or "-1"
            command.downgrade(alembic_cfg, target)
            print(f"✅ Database downgraded to {target}")
            
        elif action == "current":
            command.current(alembic_cfg)
            
        elif action == "history":
            command.history(alembic_cfg)
            
        elif action == "revision":
            message = revision or "Auto-generated migration"
            command.revision(alembic_cfg, autogenerate=True, message=message)
            print(f"✅ New migration created: {message}")
            
        else:
            print(f"❌ Unknown action: {action}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Database migration management")
    parser.add_argument("action", choices=["upgrade", "downgrade", "current", "history", "revision"],
                       help="Migration action to perform")
    parser.add_argument("--revision", "-r", help="Target revision (optional)")
    parser.add_argument("--message", "-m", help="Migration message (for revision)")
    
    args = parser.parse_args()
    
    # Handle revision with message
    if args.action == "revision" and args.message:
        args.revision = args.message
    
    success = run_migration(args.action, args.revision)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
