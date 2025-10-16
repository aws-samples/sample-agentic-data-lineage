# Redshift cluster outputs
output "cluster_identifier" {
  description = "The Redshift cluster identifier"
  value       = aws_redshift_cluster.redshift_cluster.cluster_identifier
}

output "cluster_endpoint" {
  description = "The connection endpoint"
  value       = aws_redshift_cluster.redshift_cluster.endpoint
}

output "cluster_host" {
  description = "The connection hostname (without port)"
  value       = split(":", aws_redshift_cluster.redshift_cluster.endpoint)[0]
}

output "cluster_port" {
  description = "The port the cluster accepts connections on"
  value       = aws_redshift_cluster.redshift_cluster.port
}

output "database_name" {
  description = "The name of the default database"
  value       = aws_redshift_cluster.redshift_cluster.database_name
}

output "master_username" {
  description = "The master username"
  value       = aws_redshift_cluster.redshift_cluster.master_username
}

output "master_password" {
  description = "The master password (from Secrets Manager)"
  value       = jsondecode(data.aws_secretsmanager_secret_version.redshift_password.secret_string)["password"]
  sensitive   = true
}

output "connection_string" {
  description = "JDBC connection string for the Redshift cluster"
  value       = "jdbc:redshift://${aws_redshift_cluster.redshift_cluster.endpoint}:${aws_redshift_cluster.redshift_cluster.port}/${aws_redshift_cluster.redshift_cluster.database_name}"
}

output "psql_connection_command" {
  description = "psql command to connect to the Redshift cluster (use terraform output to get the password)"
  value       = "psql -h ${aws_redshift_cluster.redshift_cluster.endpoint} -p ${aws_redshift_cluster.redshift_cluster.port} -U ${aws_redshift_cluster.redshift_cluster.master_username} -d ${aws_redshift_cluster.redshift_cluster.database_name}"
}
