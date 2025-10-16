variable "project_name" {
  description = "The name of the project"
  type        = string
  default     = "lakehouse-core"
}

variable "project_name_alias" {
  description = "The short name of the project"
  type        = string
  default     = "lh-core"
}

variable "partition" {
  description = "AWS partition"
  type        = string
  default     = "aws"
}

variable "region" {
  description = "AWS region"
  type        = string
  # No default - will be provided via terraform.tfvars, environment variable, or AWS profile
}

variable "s3_endpoint" {
  description = "S3 endpoint (will be dynamically constructed based on region)"
  type        = string
  default     = ""
}

variable "account" {
  description = "AWS account"
  type        = string
  # No default - will be provided via terraform.tfvars, environment variable, or detected from AWS profile
}

variable "eks-version" {
  type    = string
  default = "1.33"
}

variable "karpenter_version" {
  description = "Version of Karpenter to install"
  type        = string
  default     = "1.6.2"
}

variable "aws_lbc_version" {
  description = "Version of AWS Load Balancer Controller to install"
  type        = string
  default     = "1.13.4"
}

variable "bedrock_model_id" {
  description = "Bedrock model ID for Marquez agent"
  type        = string
  default     = "us.anthropic.claude-sonnet-4-20250514-v1:0"
}

variable "ingress_inbound_cidrs" {
  description = "Comma-separated list of CIDR blocks allowed to access the ingress"
  type        = string
  default     = "104.153.113.16/28,15.248.80.128/25,205.251.233.104/29,205.251.233.176/29,205.251.233.232/29,205.251.233.48/29,52.46.249.224/29,52.46.249.248/29"
}
