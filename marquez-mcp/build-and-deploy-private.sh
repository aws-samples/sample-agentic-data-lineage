#!/bin/bash

# Build and deploy script for EKS
set -e

# Configuration
REGISTRY="612674025488.dkr.ecr.us-west-2.amazonaws.com"  # Replace with your ECR registry
IMAGE_NAME="marquez-mcp"
TAG=${1:-latest}
REGION="us-west-2"  # Replace with your AWS region

echo "Building Docker image for x86-64 platform..."
docker build --platform linux/amd64 --provenance=false --sbom=false -t ${IMAGE_NAME}:${TAG} .

echo "Tagging image for registry..."
docker tag ${IMAGE_NAME}:${TAG} ${REGISTRY}/${IMAGE_NAME}:${TAG}

echo "Creating ECR repository if it doesn't exist..."
aws ecr describe-repositories --repository-names ${IMAGE_NAME} --region ${REGION} >/dev/null 2>&1 || \
aws ecr create-repository --repository-name ${IMAGE_NAME} --region ${REGION} >/dev/null 2>&1

echo "Logging into ECR..."
aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${REGISTRY}

echo "Pushing image to registry..."
docker push ${REGISTRY}/${IMAGE_NAME}:${TAG}
