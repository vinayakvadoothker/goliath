#!/bin/bash

# Run database migration for outcome generation tables
# This creates jira_outcomes and jira_issue_history tables

set -e

echo "🔄 Running Jira Simulator database migration..."

# Get database URL from environment or use default
POSTGRES_URL="${POSTGRES_URL:-postgresql://goliath:goliath@postgres:5432/goliath}"

# Check if we're in Docker or on host
if [ -f "/.dockerenv" ] || hostname | grep -q "container"; then
    # Inside Docker, use service name
    if [[ "$POSTGRES_URL" == *"localhost"* ]]; then
        POSTGRES_URL=$(echo "$POSTGRES_URL" | sed 's/localhost/postgres/g')
    fi
else
    # On host machine, use localhost
    if [[ "$POSTGRES_URL" == *"postgres:"* ]]; then
        POSTGRES_URL=$(echo "$POSTGRES_URL" | sed 's/postgres:/localhost:/g')
    fi
fi

echo "📦 Database URL: $POSTGRES_URL"

# Run migration
if command -v psql &> /dev/null; then
    echo "✅ Running migration with psql..."
    psql "$POSTGRES_URL" -f "$(dirname "$0")/../migrations/create_outcome_tables.sql"
    echo "✅ Migration complete!"
else
    echo "⚠️  psql not found. Please run manually:"
    echo "   psql \$POSTGRES_URL -f services/jira-simulator/migrations/create_outcome_tables.sql"
    exit 1
fi

