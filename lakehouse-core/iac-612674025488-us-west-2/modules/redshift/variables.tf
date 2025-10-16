# Project configuration variables (matching EKS module)
variable "project_name_alias" {
  description = "The short name of the project"
  type        = string
}

variable "workspace" {
  description = "Terraform workspace"
  type        = string
}

variable "account" {
  description = "AWS account"
  type        = string
}

variable "region" {
  description = "AWS region"
  type        = string
}

# Redshift specific variables
variable "vpc_id" {
  description = "VPC ID where Redshift cluster will be created"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for Redshift cluster (must be public subnets for external access)"
  type        = list(string)
}

variable "secret_name" {
  description = "Name of the AWS Secrets Manager secret containing the database password"
  type        = string
}

variable "default_tags" {
  description = "Default tags to apply to resources"
  type        = map(string)
}
