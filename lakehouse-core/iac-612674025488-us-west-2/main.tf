locals {
  # Use variables directly - no fallback to data sources to avoid circular dependency
  account     = var.account
  region      = var.region
  s3_endpoint = var.s3_endpoint != "" ? var.s3_endpoint : "s3.${local.region}.amazonaws.com"

  workspace           = terraform.workspace
  deployment_name     = "${var.project_name}-${local.workspace}"
  deployment_role_arn = "arn:${var.partition}:iam::${local.account}:role/${var.project_name_alias}-${local.account}-${local.region}-${local.workspace}-deploy-role"
  az                  = data.aws_availability_zones.available.names[0]
  eks_version         = var.eks-version
  cluster_name        = "${var.project_name_alias}-eks-${local.workspace}"
  default_tags = {
    "DeploymentName" = local.deployment_name
    "Workspace"      = local.workspace
    "ManagedBy"      = "terraform"
    "Repository"     = "git@gitlab.com:kolya-amazon/lakehouse-core.git"
  }
  internet_domains = [
  ]
  internal_domains = [
  ]
  domains = [
    "marquez-web",
    "marquez"
  ]
  helm_repo = "oci://${local.account}.dkr.ecr.${local.region}.amazonaws.com"
}

data "aws_region" "current" {}

data "aws_caller_identity" "current" {}

data "aws_availability_zones" "available" {}

# S3 Bucket for lakehouse landing zone
resource "aws_s3_bucket" "lakehouse_landing_zone_bucket" {
  bucket = "${var.project_name_alias}-${local.workspace}-landing-zone"
  tags   = local.default_tags
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"

  name_prefix         = local.deployment_name
  vpc_cidr            = "10.0.0.0/16"
  tags                = local.default_tags
  cluster_name        = local.cluster_name
  region              = data.aws_region.current.id
  enable_s3_endpoint  = true
  enable_ecr_endpoint = true
  s3_bucket_arns      = [aws_s3_bucket.lakehouse_landing_zone_bucket.arn]
}

# RDS Aurora PostgreSQL Module
module "rds_aurora_postgresql" {
  source = "./modules/rds-aurora-postgresql"

  # Project configuration (matching other modules)
  project_name_alias = var.project_name_alias
  workspace          = local.workspace
  account            = local.account
  region             = local.region

  # Network configuration - using public subnets for external access
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.public_subnet_ids # Changed to public subnets for external connectivity

  # Secret Manager configuration
  secret_name = "aurora-postgresql-pwd" # pragma: allowlist secret

  # Instance configuration
  instance_count = 1

  # Security settings (all configurable, defaults for testing)
  storage_encrypted                   = false
  kms_key_id                          = ""
  iam_database_authentication_enabled = false
  deletion_protection                 = false

  # Backup settings (minimal for testing)
  backup_retention_period = 1
  preferred_backup_window = "03:00-04:00"
  copy_tags_to_snapshot   = false
  skip_final_snapshot     = true

  # Maintenance settings
  preferred_maintenance_window = "sun:04:00-sun:05:00"
  apply_immediately            = true
  auto_minor_version_upgrade   = false

  # Logging settings (disabled for testing)
  enabled_cloudwatch_logs_exports = []

  # Monitoring settings (disabled for testing)
  monitoring_interval = 0
  monitoring_role_arn = ""

  # Performance Insights settings (disabled for testing)
  performance_insights_enabled = false

  # Tags
  default_tags = local.default_tags
}

# Redshift Module
module "redshift" {
  source = "./modules/redshift"

  # Project configuration (matching EKS module)
  project_name_alias = var.project_name_alias
  workspace          = local.workspace
  account            = local.account
  region             = local.region

  # Network configuration - using public subnets for external access
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.public_subnet_ids # Changed to public subnets for external connectivity

  # Secret Manager configuration
  secret_name = "redshift-pwd" # pragma: allowlist secret

  # Tags
  default_tags = local.default_tags
}

# RDS Aurora MySQL Module
# module "rds_aurora_mysql" {
#   source = "./modules/rds-aurora-mysql"

#   # Project configuration (matching other modules)
#   project_name_alias = var.project_name_alias
#   workspace          = local.workspace
#   account            = local.account
#   region             = local.region

#   # Network configuration (using existing VPC and subnets)
#   vpc_id     = module.vpc.vpc_id
#   subnet_ids = module.vpc.private_subnet_ids

#   # Secret Manager configuration
#   secret_name = "aurora-mysql-pwd" # pragma: allowlist secret

#   # Instance configuration
#   instance_count = 1

#   # Security settings (all configurable, defaults for testing)
#   storage_encrypted                   = false
#   kms_key_id                          = ""
#   iam_database_authentication_enabled = false
#   deletion_protection                 = false

#   # Backup settings (minimal for testing)
#   backup_retention_period = 1
#   preferred_backup_window = "03:00-04:00"
#   copy_tags_to_snapshot   = false
#   skip_final_snapshot     = true

#   # Maintenance settings
#   preferred_maintenance_window = "sun:04:00-sun:05:00"
#   apply_immediately            = true
#   auto_minor_version_upgrade   = false

#   # Logging settings (disabled for testing)
#   enabled_cloudwatch_logs_exports = []

#   # Monitoring settings (disabled for testing)
#   monitoring_interval = 0
#   monitoring_role_arn = ""

#   # Performance Insights settings (disabled for testing)
#   performance_insights_enabled = false

#   # Tags
#   default_tags = local.default_tags
# }

# EKS and Karpenter Module
module "eks_karpenter" {
  source = "./modules/eks-karpenter"

  # Project configuration
  project_name_alias = var.project_name_alias
  workspace          = local.workspace
  account            = local.account
  region             = local.region
  partition          = var.partition

  # EKS configuration
  cluster_name       = local.cluster_name
  kubernetes_version = local.eks_version
  vpc_id             = module.vpc.vpc_id
  subnet_ids         = module.vpc.private_subnet_ids

  # Tags
  default_tags = local.default_tags

  depends_on = [module.vpc]
}

# EKS Add-ons Module
module "eks_addons" {
  source = "./modules/eks-addons"

  # Project configuration
  project_name_alias = var.project_name_alias
  account            = local.account
  region             = local.region
  workspace          = local.workspace
  partition          = var.partition

  # EKS cluster information
  cluster_name     = module.eks_karpenter.cluster_name
  cluster_endpoint = module.eks_karpenter.cluster_endpoint
  vpc_id           = module.vpc.vpc_id

  # Karpenter configuration
  karpenter_version            = var.karpenter_version
  karpenter_service_account    = module.eks_karpenter.karpenter_service_account
  karpenter_queue_name         = module.eks_karpenter.karpenter_queue_name
  karpenter_node_iam_role_name = module.eks_karpenter.karpenter_node_iam_role_name

  # Helm configuration
  helm_repo = local.helm_repo

  # AWS Load Balancer Controller configuration
  aws_lbc_version = var.aws_lbc_version

  # Tags
  default_tags = local.default_tags

  depends_on = [module.eks_karpenter, module.vpc]
}

# Data sources for EKS cluster information (used by providers)
data "aws_eks_cluster" "cluster" {
  name = module.eks_karpenter.cluster_name

  depends_on = [module.eks_karpenter]
}

data "aws_eks_cluster_auth" "cluster" {
  name = module.eks_karpenter.cluster_name

  depends_on = [module.eks_karpenter]
}
