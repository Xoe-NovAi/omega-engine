#!/bin/bash
set -e

DB_PATH="data/workbench/workbench.db"
BACKUP_PATH="data/workbench/workbench.db.bak"
SQL_FILE="scripts/migrate_workbench_domain.sql"

echo "🛡️ Backing up database..."
cp "$DB_PATH" "$BACKUP_PATH"

echo "🚀 Executing migration..."
sqlite3 "$DB_PATH" < "$SQL_FILE"

echo "🧪 Validating migration..."
# Check if column exists
COL_CHECK=$(sqlite3 "$DB_PATH" "PRAGMA table_info(projects);" | grep "domain")

if [ -z "$COL_CHECK" ]; then
    echo "❌ Migration failed: 'domain' column not found."
    echo "🔄 Rolling back..."
    mv "$BACKUP_PATH" "$DB_PATH"
    exit 1
fi

echo "✅ Migration successful."

# Seed test data
echo "🌱 Seeding test domains..."
sqlite3 "$DB_PATH" "UPDATE projects SET domain = 'foundation_community' WHERE id = 'prj_community_tool';"
sqlite3 "$DB_PATH" "UPDATE projects SET domain = 'custom_stack' WHERE id = 'prj_arcana_nova';"

echo "📊 Validation Report:"
sqlite3 "$DB_PATH" "SELECT id, name, domain FROM projects;"
