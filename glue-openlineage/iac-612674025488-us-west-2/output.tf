output "glue_vpc_connection_name" {
  description = "Name of the Glue VPC connection"
  value       = aws_glue_connection.vpc_connection.name
}
