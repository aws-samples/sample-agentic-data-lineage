#!/bin/bash

# Script to generate terraform.tfvars from current AWS profile
# This avoids the circular dependency issue in Terraform

echo "Generating terraform.tfvars from current AWS profile..."

# Get current AWS profile information
ACCOUNT=$(aws sts get-caller-identity --output json | jq -r .Account)
REGION=$(aws configure get region)

# Default region if not configured
if [ -z "$REGION" ]; then
    REGION="us-west-2"
    echo "Warning: No region configured in AWS profile, using default: $REGION"
fi

# Create terraform.tfvars
cat > terraform.tfvars << EOF
# Auto-generated terraform.tfvars from AWS profile
# Generated on: $(date)

account = "$ACCOUNT"
region  = "$REGION"
EOF

echo "Generated terraform.tfvars with:"
echo "  Account: $ACCOUNT"
echo "  Region: $REGION"
echo ""
echo "You can now run: terraform plan"
