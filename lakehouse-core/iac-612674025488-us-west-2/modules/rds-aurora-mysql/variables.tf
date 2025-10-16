# Project configuration variables (matching redshift module)
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

# Network configuration
variable "vpc_id" {
  description = "VPC ID where Aurora cluster will be created"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for Aurora cluster"
  type        = list(string)
}

# Secret Manager configuration
variable "secret_name" {
  description = "Name of the AWS Secrets Manager secret containing the database password"
  type        = string
}

# Instance configuration
variable "instance_count" {
  description = "Number of Aurora instances to create"
  type        = number
}



# Security and encryption settings
variable "storage_encrypted" {
  description = "Whether to encrypt the Aurora cluster storage"
  type        = bool
}

variable "kms_key_id" {
  description = "The ARN for the KMS encryption key for Aurora cluster storage"
  type        = string
}

variable "iam_database_authentication_enabled" {
  description = "Whether to enable IAM database authentication"
  type        = bool
}

variable "deletion_protection" {
  description = "Whether to enable deletion protection for the Aurora cluster"
  type        = bool
}

# Backup settings
variable "backup_retention_period" {
  description = "The backup retention period in days"
  type        = number
}

variable "preferred_backup_window" {
  description = "The daily time range during which automated backups are created"
  type        = string
}

variable "copy_tags_to_snapshot" {
  description = "Whether to copy all cluster tags to snapshots"
  type        = bool
}

variable "skip_final_snapshot" {
  description = "Whether to skip the final DB snapshot when the cluster is deleted"
  type        = bool
}

# Maintenance settings
variable "preferred_maintenance_window" {
  description = "The weekly time range during which system maintenance can occur"
  type        = string
}

variable "apply_immediately" {
  description = "Whether to apply changes immediately or during the next maintenance window"
  type        = bool
}

variable "auto_minor_version_upgrade" {
  description = "Whether to enable auto minor version upgrade for Aurora instances"
  type        = bool
}

# Logging settings
variable "enabled_cloudwatch_logs_exports" {
  description = "List of log types to export to CloudWatch"
  type        = list(string)
}

# Monitoring settings
variable "monitoring_interval" {
  description = "The interval for collecting enhanced monitoring metrics in seconds"
  type        = number
}

variable "monitoring_role_arn" {
  description = "The ARN for the IAM role for enhanced monitoring"
  type        = string
}

# Performance Insights settings
variable "performance_insights_enabled" {
  description = "Whether to enable Performance Insights"
  type        = bool
}


# Default tags
variable "default_tags" {
  description = "Default tags to apply to resources"
  type        = map(string)
}
