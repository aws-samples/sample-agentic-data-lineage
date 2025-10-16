#!/bin/bash

# Build and deploy script for public ECR
set -e

# Configuration
PUBLIC_REGISTRY="public.ecr.aws/f9c0z1d3"  # Your public ECR alias
IMAGE_NAME="marquez-mcp"
TAG=${1:-latest}
REGION="us-east-1"  # Public ECR is only available in us-east-1

echo "Checking AWS CLI configuration..."
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo "Error: AWS CLI not configured or no valid credentials found"
    echo "Please run 'aws configure' or set up your AWS credentials"
    exit 1
fi

echo "Building Docker image for x86-64 platform..."
docker build --platform linux/amd64 --provenance=false --sbom=false -t ${IMAGE_NAME}:${TAG} .

echo "Creating public ECR repository if it doesn't exist..."
if ! aws ecr-public describe-repositories --repository-names ${IMAGE_NAME} --region ${REGION} >/dev/null 2>&1; then
    echo "Repository doesn't exist, creating it..."
    aws ecr-public create-repository --repository-name ${IMAGE_NAME} --region ${REGION}
else
    echo "Repository already exists"
fi

echo "Tagging image for public ECR..."
docker tag ${IMAGE_NAME}:${TAG} ${PUBLIC_REGISTRY}/${IMAGE_NAME}:${TAG}

echo "Logging into public ECR..."
aws ecr-public get-login-password --region ${REGION} | docker login --username AWS --password-stdin public.ecr.aws

echo "Pushing image to public ECR..."
docker push ${PUBLIC_REGISTRY}/${IMAGE_NAME}:${TAG}

echo "Image pushed successfully: ${PUBLIC_REGISTRY}/${IMAGE_NAME}:${TAG}"
echo "You can now use this public image: ${PUBLIC_REGISTRY}/${IMAGE_NAME}:${TAG}"
