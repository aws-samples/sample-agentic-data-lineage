#!/bin/bash

# 严格错误处理：任何命令失败都立即退出
set -euo pipefail

# 错误处理函数
error_exit() {
    echo "❌ Error on line $1: Command failed with exit code $2"
    echo "🛑 Script execution terminated"
    exit $2
}

# 捕获错误并调用错误处理函数
trap 'error_exit $LINENO $?' ERR

echo "🔧 Starting dbt run with strict error handling..."

# Load environment variables from .env file
if [[ -f .env ]]; then
    echo "📋 Loading environment variables from .env file..."
    set -a  # automatically export all variables
    source .env
    set +a  # turn off automatic export
    echo "✅ Environment variables loaded"
else
    echo "❌ Error: .env file not found"
    exit 1
fi

# Run dbt and sync lineage data to Marquez after completion
echo "🚀 Starting dbt run..."

# Switch to dbt project directory
echo "📁 Switching to dbt project directory..."
cd dbt_redshift_openlineage

# Run dbt (会自动因为 set -e 而在失败时退出)
echo "🏃 Running dbt..."
dbt run --profiles-dir .
echo "✅ dbt run completed successfully"

# Generate dbt docs to create catalog.json
echo "📚 Generating dbt documentation..."
dbt docs generate --profiles-dir .
echo "✅ dbt documentation generated successfully"

# Generate super manifest
echo "📋 Generating super manifest with colibri..."
colibri generate
echo "✅ Super manifest generated successfully"

# Switch to marquez_lineage directory to execute sync script
echo "📁 Switching to marquez_lineage directory..."
cd ../marquez_lineage

echo "🔄 Starting lineage sync to Marquez..."
python3 marquez_lineage_sync.py
echo "✅ Lineage sync completed successfully"

echo "🎉 All tasks completed!"
