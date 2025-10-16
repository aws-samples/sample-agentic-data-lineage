#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    echo "📋 Loading environment variables from .env file..."
    set -a  # automatically export all variables
    source .env
    set +a  # turn off automatic export
    echo "✅ Environment variables loaded"
else
    echo "⚠️  Warning: .env file not found"
fi

# Run dbt and sync lineage data to Marquez after completion
echo "🚀 Starting dbt run..."

# Switch to dbt project directory
cd dbt_redshift_openlineage

# Run dbt
echo "🏃 Running dbt..."
dbt run --profiles-dir .

# Generate dbt docs to create catalog.json
echo "📚 Generating dbt documentation..."
dbt docs generate --profiles-dir .

# generate super manifest
colibri generate

# Check if dbt run was successful
if [ $? -eq 0 ]; then
    echo "✅ dbt run completed successfully"
    echo "🔄 Starting lineage sync to Marquez..."

    # Switch to marquez_lineage directory to execute sync script
    cd ../marquez_lineage
    python3 marquez_lineage_sync.py

    if [ $? -eq 0 ]; then
        echo "✅ Lineage sync completed successfully"
    else
        echo "❌ Lineage sync failed"
        exit 1
    fi
else
    echo "❌ dbt run failed"
    exit 1
fi

echo "🎉 All tasks completed!"
