# Project configuration variables
variable "project_name_alias" {
  description = "Project name alias for resource naming"
  type        = string
}

variable "account" {
  description = "AWS account ID"
  type        = string
}

variable "region" {
  description = "AWS region"
  type        = string
}

variable "workspace" {
  description = "Terraform workspace name"
  type        = string
}

variable "partition" {
  description = "AWS partition (aws, aws-cn, aws-us-gov)"
  type        = string
  default     = "aws"
}

# EKS cluster information
variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
}

variable "cluster_endpoint" {
  description = "EKS cluster endpoint"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where the cluster is deployed"
  type        = string
}

# Karpenter configuration
variable "karpenter_version" {
  description = "Version of Karpenter to install"
  type        = string
  default     = "1.6.2"
}

variable "karpenter_service_account" {
  description = "Karpenter service account name"
  type        = string
}

variable "karpenter_queue_name" {
  description = "Karpenter SQS queue name for interruption handling"
  type        = string
}

variable "karpenter_node_iam_role_name" {
  description = "IAM role name for Karpenter nodes"
  type        = string
}

# Helm configuration
variable "helm_repo" {
  description = "Helm repository URL"
  type        = string
}

# AWS Load Balancer Controller configuration
variable "aws_lbc_version" {
  description = "Version of AWS Load Balancer Controller to install"
  type        = string
  default     = "1.13.4"
}

# Tags
variable "default_tags" {
  description = "Default tags to apply to all resources"
  type        = map(string)
  default     = {}
}

# IAM policy path
variable "iam_policy_path" {
  description = "Path to the IAM policy file for AWS Load Balancer Controller"
  type        = string
  default     = ""
}
