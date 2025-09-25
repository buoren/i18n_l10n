#!/bin/bash

# Run database migrations locally
# Usage: ./migrate_local.sh [upgrade|downgrade|current|history]

set -e

ACTION=${1:-upgrade}

echo "Running database migration: $ACTION"

# Set up environment for local development
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=i18n_l10n_db
export DB_USER=appuser
export DB_PASSWORD=password

# Run the migration
python3 scripts/migrate.py $ACTION

echo "✅ Migration completed successfully!"
