# Aurora cluster outputs
output "cluster_identifier" {
  description = "The Aurora cluster identifier"
  value       = aws_rds_cluster.aurora_cluster.cluster_identifier
}

output "cluster_endpoint" {
  description = "The cluster endpoint (writer)"
  value       = aws_rds_cluster.aurora_cluster.endpoint
}

output "cluster_reader_endpoint" {
  description = "The cluster reader endpoint"
  value       = aws_rds_cluster.aurora_cluster.reader_endpoint
}

output "cluster_port" {
  description = "The port the cluster accepts connections on"
  value       = aws_rds_cluster.aurora_cluster.port
}

output "cluster_arn" {
  description = "The ARN of the Aurora cluster"
  value       = aws_rds_cluster.aurora_cluster.arn
}

output "cluster_resource_id" {
  description = "The resource ID of the Aurora cluster"
  value       = aws_rds_cluster.aurora_cluster.cluster_resource_id
}

output "database_name" {
  description = "The name of the default database"
  value       = aws_rds_cluster.aurora_cluster.database_name
}

output "master_username" {
  description = "The master username"
  value       = aws_rds_cluster.aurora_cluster.master_username
}

output "master_password" {
  description = "The master password (from Secrets Manager)"
  value       = jsondecode(data.aws_secretsmanager_secret_version.aurora_password.secret_string)["password"]
  sensitive   = true
}

output "engine" {
  description = "The database engine"
  value       = aws_rds_cluster.aurora_cluster.engine
}

output "engine_version" {
  description = "The database engine version"
  value       = aws_rds_cluster.aurora_cluster.engine_version
}

output "hosted_zone_id" {
  description = "The hosted zone ID of the Aurora cluster"
  value       = aws_rds_cluster.aurora_cluster.hosted_zone_id
}

# Instance outputs
output "cluster_instances" {
  description = "List of Aurora cluster instance identifiers"
  value       = aws_rds_cluster_instance.aurora_cluster_instances[*].identifier
}

output "cluster_instance_endpoints" {
  description = "List of Aurora cluster instance endpoints"
  value       = aws_rds_cluster_instance.aurora_cluster_instances[*].endpoint
}

# Security group outputs
output "security_group_id" {
  description = "The ID of the Aurora security group"
  value       = aws_security_group.aurora_security_group.id
}

output "security_group_arn" {
  description = "The ARN of the Aurora security group"
  value       = aws_security_group.aurora_security_group.arn
}

# Subnet group outputs
output "subnet_group_name" {
  description = "The name of the Aurora subnet group"
  value       = aws_db_subnet_group.aurora_subnet_group.name
}

output "subnet_group_arn" {
  description = "The ARN of the Aurora subnet group"
  value       = aws_db_subnet_group.aurora_subnet_group.arn
}

# Connection information
output "mysql_connection_string" {
  description = "MySQL connection string for the Aurora cluster"
  value       = "mysql://${aws_rds_cluster.aurora_cluster.master_username}@${aws_rds_cluster.aurora_cluster.endpoint}:${aws_rds_cluster.aurora_cluster.port}/${aws_rds_cluster.aurora_cluster.database_name}"
}

output "mysql_connection_command" {
  description = "MySQL command to connect to the Aurora cluster (use terraform output to get the password)"
  value       = "mysql -h ${aws_rds_cluster.aurora_cluster.endpoint} -P ${aws_rds_cluster.aurora_cluster.port} -u ${aws_rds_cluster.aurora_cluster.master_username} -p -D ${aws_rds_cluster.aurora_cluster.database_name}"
}
