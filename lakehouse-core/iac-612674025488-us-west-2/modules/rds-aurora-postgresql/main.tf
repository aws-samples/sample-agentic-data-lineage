# Data source to get password from AWS Secrets Manager
data "aws_secretsmanager_secret" "aurora_postgresql_password" {
  name = var.secret_name
}

data "aws_secretsmanager_secret_version" "aurora_postgresql_password" {
  secret_id = data.aws_secretsmanager_secret.aurora_postgresql_password.id
}

# Data source to get VPC information
data "aws_vpc" "selected" {
  id = var.vpc_id
}

# Local variables for consistent naming (matching redshift module pattern)
locals {
  cluster_identifier = "${var.project_name_alias}-aurora-postgres-${var.workspace}"
  resource_prefix    = "${var.project_name_alias}-${var.account}-${var.region}-${var.workspace}"

  # Default configurations (hard-coded)
  default_database_name   = "marquez"
  default_master_username = "postgres"
  default_engine          = "aurora-postgresql"
  default_engine_version  = "16.6"
  default_instance_class  = "db.t4g.medium"
}

# Security Group for Aurora PostgreSQL
resource "aws_security_group" "aurora_security_group" {
  name        = "${local.resource_prefix}-aurora-postgres-sg"
  vpc_id      = var.vpc_id
  description = "Security group for Aurora PostgreSQL cluster ${local.cluster_identifier}"

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.selected.cidr_block]
    description = "Aurora PostgreSQL VPC access only"
  }

  # Allow access from specified external CIDR blocks
  ingress {
    from_port = 5432
    to_port   = 5432
    protocol  = "tcp"
    cidr_blocks = [
      "104.153.113.16/28",
      "15.248.80.128/25",
      "205.251.233.104/29",
      "205.251.233.176/29",
      "205.251.233.232/29",
      "205.251.233.48/29",
      "52.46.249.224/29",
      "52.46.249.248/29"
    ]
    description = "Aurora PostgreSQL access from external networks"
  }

  tags = merge(var.default_tags, {
    Name = "${local.resource_prefix}-aurora-postgres-sg"
  })
}

# Aurora Subnet Group - using public subnets for external access
resource "aws_db_subnet_group" "aurora_subnet_group" {
  name       = "${local.resource_prefix}-aurora-postgres-subnet-group-public"
  subnet_ids = var.subnet_ids # Must be public subnet IDs for external connectivity

  lifecycle {
    create_before_destroy = true
  }

  tags = merge(var.default_tags, {
    Name = "${local.resource_prefix}-aurora-postgres-subnet-group-public"
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
  master_password = jsondecode(data.aws_secretsmanager_secret_version.aurora_postgresql_password.secret_string)["password"]

  # Network configuration
  db_subnet_group_name   = aws_db_subnet_group.aurora_subnet_group.name
  vpc_security_group_ids = [aws_security_group.aurora_security_group.id]
  port                   = 5432

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

  # Logging settings (exposed as variables) - PostgreSQL specific logs
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

  # Network configuration - enable public access for external connectivity
  publicly_accessible = true

  tags = merge(var.default_tags, {
    Name = "${local.cluster_identifier}-${count.index}"
  })
}
