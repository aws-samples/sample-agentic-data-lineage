# Data source to get password from AWS Secrets Manager
data "aws_secretsmanager_secret" "aurora_password" {
  name = var.secret_name
}

data "aws_secretsmanager_secret_version" "aurora_password" {
  secret_id = data.aws_secretsmanager_secret.aurora_password.id
}

# Data source to get VPC information
data "aws_vpc" "selected" {
  id = var.vpc_id
}

# Local variables for consistent naming (matching redshift module pattern)
locals {
  cluster_identifier = "${var.project_name_alias}-aurora-${var.workspace}"
  resource_prefix    = "${var.project_name_alias}-${var.account}-${var.region}-${var.workspace}"

  # Default configurations (hard-coded)
  default_database_name   = "testdb"
  default_master_username = "admin"
  default_engine          = "aurora-mysql"
  default_engine_version  = "8.0.mysql_aurora.3.07.0"
  default_instance_class  = "db.r6g.large"
}

# Security Group for Aurora
resource "aws_security_group" "aurora_security_group" {
  name        = "${local.resource_prefix}-aurora-sg"
  vpc_id      = var.vpc_id
  description = "Security group for Aurora cluster ${local.cluster_identifier}"

  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.selected.cidr_block]
    description = "Aurora MySQL VPC access only"
  }

  tags = merge(var.default_tags, {
    Name = "${local.resource_prefix}-aurora-sg"
  })
}

# Aurora Subnet Group
resource "aws_db_subnet_group" "aurora_subnet_group" {
  name       = "${local.resource_prefix}-aurora-subnet-group"
  subnet_ids = var.subnet_ids

  tags = merge(var.default_tags, {
    Name = "${local.resource_prefix}-aurora-subnet-group"
  })
}

# Aurora Cluster
resource "aws_rds_cluster" "aurora_cluster" {
  cluster_identifier = local.cluster_identifier

  # Engine configuration
  engine         = local.default_engine
  engine_version = local.default_engine_version

  # Database configuration
  database_name   = local.default_database_name
  master_username = local.default_master_username
  master_password = jsondecode(data.aws_secretsmanager_secret_version.aurora_password.secret_string)["password"]

  # Network configuration
  db_subnet_group_name   = aws_db_subnet_group.aurora_subnet_group.name
  vpc_security_group_ids = [aws_security_group.aurora_security_group.id]
  port                   = 3306

  # Security and encryption settings (exposed as variables)
  storage_encrypted                   = var.storage_encrypted
  kms_key_id                          = var.kms_key_id
  iam_database_authentication_enabled = var.iam_database_authentication_enabled

  # Backup settings (exposed as variables)
  backup_retention_period   = var.backup_retention_period
  preferred_backup_window   = var.preferred_backup_window
  copy_tags_to_snapshot     = var.copy_tags_to_snapshot
  skip_final_snapshot       = var.skip_final_snapshot
  final_snapshot_identifier = var.skip_final_snapshot ? null : "${local.cluster_identifier}-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  # Maintenance settings
  preferred_maintenance_window = var.preferred_maintenance_window
  apply_immediately            = var.apply_immediately

  # Logging settings (exposed as variables)
  enabled_cloudwatch_logs_exports = var.enabled_cloudwatch_logs_exports

  # Monitoring settings (exposed as variables)
  monitoring_interval = var.monitoring_interval
  monitoring_role_arn = var.monitoring_role_arn

  # Performance Insights settings (exposed as variables)
  performance_insights_enabled = var.performance_insights_enabled

  # Deletion protection (exposed as variable)
  deletion_protection = var.deletion_protection

  tags = merge(var.default_tags, {
    Name = local.cluster_identifier
  })
}

# Aurora Cluster Instances
resource "aws_rds_cluster_instance" "aurora_cluster_instances" {
  count              = var.instance_count
  identifier         = "${local.cluster_identifier}-${count.index}"
  cluster_identifier = aws_rds_cluster.aurora_cluster.id
  instance_class     = local.default_instance_class
  engine             = aws_rds_cluster.aurora_cluster.engine
  engine_version     = aws_rds_cluster.aurora_cluster.engine_version


  # Monitoring settings (exposed as variables)
  monitoring_interval = var.monitoring_interval
  monitoring_role_arn = var.monitoring_role_arn

  # Auto minor version upgrade (exposed as variable)
  auto_minor_version_upgrade = var.auto_minor_version_upgrade

  # Network configuration - explicitly disable public access
  publicly_accessible = false

  tags = merge(var.default_tags, {
    Name = "${local.cluster_identifier}-${count.index}"
  })
}
