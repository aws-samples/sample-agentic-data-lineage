variable "name_prefix" {
  description = "Name prefix for all resources"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "tags" {
  description = "A map of tags to assign to the resource"
  type        = map(string)
  default     = {}
}

variable "cluster_name" {
  description = "Cluster name"
  type        = string
}

variable "enable_s3_endpoint" {
  description = "Enable S3 VPC endpoint"
  type        = bool
  default     = true
}

variable "enable_ecr_endpoint" {
  description = "Enable ECR DKR VPC endpoint"
  type        = bool
  default     = true
}

variable "s3_bucket_arns" {
  description = "List of S3 bucket ARNs to allow access through VPC endpoint"
  type        = list(string)
  default     = []
}

variable "region" {
  description = "AWS region"
  type        = string
}
