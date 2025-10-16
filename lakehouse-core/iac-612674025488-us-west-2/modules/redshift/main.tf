# Data source to get password from AWS Secrets Manager
data "aws_secretsmanager_secret" "redshift_password" {
  name = var.secret_name
}

data "aws_secretsmanager_secret_version" "redshift_password" {
  secret_id = data.aws_secretsmanager_secret.redshift_password.id
}



# Data source to get VPC information
data "aws_vpc" "selected" {
  id = var.vpc_id
}

# Local variables for consistent naming (matching EKS module pattern)
locals {
  cluster_identifier = "${var.project_name_alias}-redshift-${var.workspace}"
  resource_prefix    = "${var.project_name_alias}-${var.account}-${var.region}-${var.workspace}"

  # Default configurations (hard-coded)
  default_database_name   = "testdb"
  default_master_username = "admin"
  default_node_type       = "ra3.xlplus" # Small instance for testing
  default_number_of_nodes = 1            # Single node for testing
}



# Security Group for Redshift
resource "aws_security_group" "redshift_security_group" {
  name        = "${local.resource_prefix}-redshift-sg"
  vpc_id      = var.vpc_id
  description = "Security group for Redshift cluster ${local.cluster_identifier}"

  ingress {
    from_port   = 5439
    to_port     = 5439
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.selected.cidr_block]
    description = "Redshift VPC access only"
  }

  # Allow access from specified external CIDR blocks
  ingress {
    from_port = 5439
    to_port   = 5439
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
    description = "Redshift access from external networks"
  }

  tags = merge(var.default_tags, {
    Name = "${local.resource_prefix}-redshift-sg"
  })
}

# Redshift Subnet Group - using public subnets for external access
resource "aws_redshift_subnet_group" "redshift_subnet_group" {
  name       = "${local.resource_prefix}-redshift-subnet-group-public"
  subnet_ids = var.subnet_ids # Must be public subnet IDs for external connectivity

  lifecycle {
    create_before_destroy = true
  }

  tags = merge(var.default_tags, {
    Name = "${local.resource_prefix}-redshift-subnet-group-public"
  })
}

# Redshift Cluster - Simplified for testing
resource "aws_redshift_cluster" "redshift_cluster" {
  cluster_identifier = local.cluster_identifier

  # Database configuration
  database_name   = local.default_database_name
  master_username = local.default_master_username
  master_password = jsondecode(data.aws_secretsmanager_secret_version.redshift_password.secret_string)["password"]

  # Cluster configuration
  node_type       = local.default_node_type
  number_of_nodes = local.default_number_of_nodes

  # Network configuration
  cluster_subnet_group_name = aws_redshift_subnet_group.redshift_subnet_group.name
  vpc_security_group_ids    = [aws_security_group.redshift_security_group.id]
  publicly_accessible       = true # Enable public access for external connectivity
  port                      = 5439

  # Minimal settings for testing
  encrypted                           = false # No encryption for testing
  automated_snapshot_retention_period = 1     # Minimum required for ra3 nodes
  skip_final_snapshot                 = true  # Skip final snapshot

  tags = merge(var.default_tags, {
    Name = local.cluster_identifier
  })
}
