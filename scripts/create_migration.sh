#!/bin/bash

# Create a new database migration
# Usage: ./create_migration.sh "Migration message"

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 \"Migration message\""
    echo "Example: $0 \"Add user preferences table\""
    exit 1
fi

MESSAGE="$1"

echo "Creating new migration: $MESSAGE"

# Set up environment for local development
export DB_HOST=localhost
export DB_PORT=3306
export DB_NAME=i18n_l10n_db
export DB_USER=appuser
export DB_PASSWORD=password

# Create the migration
python3 scripts/migrate.py revision --message "$MESSAGE"

echo "✅ Migration created successfully!"
echo "📝 Review the generated migration file in alembic/versions/"
echo "🚀 Run 'python3 scripts/migrate.py upgrade' to apply the migration"
