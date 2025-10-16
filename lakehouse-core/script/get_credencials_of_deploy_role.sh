#!/bin/bash

# Clean up old kubectl config backup files, keep only config file
cleanup_old_backups() {
    local kube_dir="$HOME/.kube"
    if [ -d "$kube_dir" ]; then
        echo "Cleaning up old kubectl config backup files..."
        # Delete all backup files, keep only config file
        rm -f "$kube_dir"/config.backup.* 2>/dev/null
        echo "Deleted all backup files, kept only config file"

        # Show remaining files
        echo "Remaining files in ~/.kube directory:"
        ls -la "$kube_dir" 2>/dev/null || echo "Directory is empty or does not exist"
    fi
}

# Clean up old backups at script start
cleanup_old_backups

# Get current AWS profile information
CURRENT_PROFILE=$(aws configure list-profiles 2>/dev/null | head -1)
if [ -n "$AWS_PROFILE" ]; then
    CURRENT_PROFILE="$AWS_PROFILE"
fi

echo "Using AWS profile: ${CURRENT_PROFILE:-default}"

# Get account and region from current AWS configuration
ACCOUNT=$(aws sts get-caller-identity --output json | jq -r .Account)
REGION=$(aws configure get region)

# Default region if not configured
if [ -z "$REGION" ]; then
    REGION="us-west-2"
    echo "Warning: No region configured, using default: $REGION"
fi

# Determine workspace with better logic
# 1. Check if we're in terraform directory and get current workspace
if [ -f "terraform.tfstate" ] || [ -d ".terraform" ]; then
    TERRAFORM_WS=$(terraform workspace show 2>/dev/null)
    if [ "$TERRAFORM_WS" != "default" ]; then
        CURRENT_WS="$TERRAFORM_WS"
    else
        # If terraform workspace is default, try to extract from directory name or use kolya as fallback
        CURRENT_WS="kolya"
    fi
else
    # Not in terraform directory, use kolya as default for this project
    CURRENT_WS="kolya"
fi

# Allow override via environment variable
if [ -n "$WORKSPACE" ]; then
    CURRENT_WS="$WORKSPACE"
fi

EKS_CLUSTER_NAME="lh-core-eks-${CURRENT_WS}"

echo "Configuration:"
echo "  Account: $ACCOUNT"
echo "  Region: $REGION"
echo "  Workspace: $CURRENT_WS"
echo "  EKS Cluster: $EKS_CLUSTER_NAME"

# Verify the role exists before trying to assume it
ROLE_ARN="arn:aws:iam::${ACCOUNT}:role/lh-core-${ACCOUNT}-${REGION}-${CURRENT_WS}-deploy-role"
echo "Checking role: $ROLE_ARN"

# Check if role exists
if ! aws iam get-role --role-name "lh-core-${ACCOUNT}-${REGION}-${CURRENT_WS}-deploy-role" >/dev/null 2>&1; then
    echo "Error: Role does not exist: lh-core-${ACCOUNT}-${REGION}-${CURRENT_WS}-deploy-role"
    echo "Available roles with 'lh-core' prefix:"
    aws iam list-roles --query 'Roles[?starts_with(RoleName, `lh-core`)].RoleName' --output table 2>/dev/null || echo "  Unable to list roles"
    exit 1
fi

# Check if EKS cluster exists
if ! aws eks describe-cluster --name "$EKS_CLUSTER_NAME" --region "$REGION" >/dev/null 2>&1; then
    echo "Error: EKS cluster does not exist: $EKS_CLUSTER_NAME"
    echo "Available EKS clusters:"
    aws eks list-clusters --region "$REGION" --query 'clusters' --output table 2>/dev/null || echo "  Unable to list clusters"
    exit 1
fi

SESSION_NAME="temp-session-name"

echo "Assuming role: $ROLE_ARN"
CREDS=$(aws sts assume-role --role-arn "$ROLE_ARN" --role-session-name "$SESSION_NAME" --duration-seconds 3600 --output json)

if [ $? -ne 0 ]; then
    echo "Error: Failed to assume role. Check your permissions."
    exit 1
fi

AWS_ACCESS_KEY_ID=$(echo $CREDS | jq -r '.Credentials.AccessKeyId')
AWS_SECRET_ACCESS_KEY=$(echo $CREDS | jq -r '.Credentials.SecretAccessKey')
AWS_SESSION_TOKEN=$(echo $CREDS | jq -r '.Credentials.SessionToken')

# Verify credentials were extracted successfully
if [ "$AWS_ACCESS_KEY_ID" = "null" ] || [ -z "$AWS_ACCESS_KEY_ID" ]; then
    echo "Error: Failed to extract credentials from assume-role response"
    exit 1
fi

echo export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
echo export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
echo export AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN

aws eks update-kubeconfig --region ${REGION} --name ${EKS_CLUSTER_NAME}

# Update ~/.kube/config with the new credentials (after aws eks update-kubeconfig)
KUBE_CONFIG="$HOME/.kube/config"
if [ -f "$KUBE_CONFIG" ]; then
    # Create a backup
    cp "$KUBE_CONFIG" "$KUBE_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"

    # Get the EKS cluster user name dynamically
    EKS_USER_NAME="arn:aws:eks:${REGION}:${ACCOUNT}:cluster/${EKS_CLUSTER_NAME}"
    echo "Updating kubeconfig for user: $EKS_USER_NAME"

    # Remove existing AWS credential env vars if they exist (using simpler approach)
    yq eval 'del(.users[0].user.exec.env[] | select(.name == "AWS_ACCESS_KEY_ID" or .name == "AWS_SECRET_ACCESS_KEY" or .name == "AWS_SESSION_TOKEN"))' -i "$KUBE_CONFIG"

    # Add the new AWS credentials to the env section
    yq eval "(.users[0].user.exec.env) += [
        {\"name\": \"AWS_ACCESS_KEY_ID\", \"value\": \"$AWS_ACCESS_KEY_ID\"},
        {\"name\": \"AWS_SECRET_ACCESS_KEY\", \"value\": \"$AWS_SECRET_ACCESS_KEY\"},
        {\"name\": \"AWS_SESSION_TOKEN\", \"value\": \"$AWS_SESSION_TOKEN\"}
    ]" -i "$KUBE_CONFIG"

    echo "Updated ~/.kube/config with new AWS credentials"
    echo "Current env vars in kubeconfig:"
    yq eval '.users[0].user.exec.env' "$KUBE_CONFIG"
else
    echo "Warning: ~/.kube/config not found"
fi
