<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 5.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 5.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_db_subnet_group.aurora_subnet_group](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/db_subnet_group) | resource |
| [aws_rds_cluster.aurora_cluster](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/rds_cluster) | resource |
| [aws_rds_cluster_instance.aurora_cluster_instances](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/rds_cluster_instance) | resource |
| [aws_security_group.aurora_security_group](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group) | resource |
| [aws_secretsmanager_secret.aurora_postgresql_password](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/secretsmanager_secret) | data source |
| [aws_secretsmanager_secret_version.aurora_postgresql_password](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/secretsmanager_secret_version) | data source |
| [aws_vpc.selected](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/vpc) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_account"></a> [account](#input\_account) | AWS account | `string` | n/a | yes |
| <a name="input_apply_immediately"></a> [apply\_immediately](#input\_apply\_immediately) | Whether to apply changes immediately or during the next maintenance window | `bool` | n/a | yes |
| <a name="input_auto_minor_version_upgrade"></a> [auto\_minor\_version\_upgrade](#input\_auto\_minor\_version\_upgrade) | Whether to enable auto minor version upgrade for Aurora PostgreSQL instances | `bool` | n/a | yes |
| <a name="input_backup_retention_period"></a> [backup\_retention\_period](#input\_backup\_retention\_period) | The backup retention period in days | `number` | n/a | yes |
| <a name="input_copy_tags_to_snapshot"></a> [copy\_tags\_to\_snapshot](#input\_copy\_tags\_to\_snapshot) | Whether to copy all cluster tags to snapshots | `bool` | n/a | yes |
| <a name="input_default_tags"></a> [default\_tags](#input\_default\_tags) | Default tags to apply to resources | `map(string)` | n/a | yes |
| <a name="input_deletion_protection"></a> [deletion\_protection](#input\_deletion\_protection) | Whether to enable deletion protection for the Aurora PostgreSQL cluster | `bool` | n/a | yes |
| <a name="input_enabled_cloudwatch_logs_exports"></a> [enabled\_cloudwatch\_logs\_exports](#input\_enabled\_cloudwatch\_logs\_exports) | List of log types to export to CloudWatch (postgresql supports: postgresql) | `list(string)` | n/a | yes |
| <a name="input_iam_database_authentication_enabled"></a> [iam\_database\_authentication\_enabled](#input\_iam\_database\_authentication\_enabled) | Whether to enable IAM database authentication | `bool` | n/a | yes |
| <a name="input_instance_count"></a> [instance\_count](#input\_instance\_count) | Number of Aurora PostgreSQL instances to create | `number` | n/a | yes |
| <a name="input_kms_key_id"></a> [kms\_key\_id](#input\_kms\_key\_id) | The ARN for the KMS encryption key for Aurora PostgreSQL cluster storage | `string` | n/a | yes |
| <a name="input_monitoring_interval"></a> [monitoring\_interval](#input\_monitoring\_interval) | The interval for collecting enhanced monitoring metrics in seconds | `number` | n/a | yes |
| <a name="input_monitoring_role_arn"></a> [monitoring\_role\_arn](#input\_monitoring\_role\_arn) | The ARN for the IAM role for enhanced monitoring | `string` | n/a | yes |
| <a name="input_performance_insights_enabled"></a> [performance\_insights\_enabled](#input\_performance\_insights\_enabled) | Whether to enable Performance Insights | `bool` | n/a | yes |
| <a name="input_preferred_backup_window"></a> [preferred\_backup\_window](#input\_preferred\_backup\_window) | The daily time range during which automated backups are created | `string` | n/a | yes |
| <a name="input_preferred_maintenance_window"></a> [preferred\_maintenance\_window](#input\_preferred\_maintenance\_window) | The weekly time range during which system maintenance can occur | `string` | n/a | yes |
| <a name="input_project_name_alias"></a> [project\_name\_alias](#input\_project\_name\_alias) | The short name of the project | `string` | n/a | yes |
| <a name="input_region"></a> [region](#input\_region) | AWS region | `string` | n/a | yes |
| <a name="input_secret_name"></a> [secret\_name](#input\_secret\_name) | Name of the AWS Secrets Manager secret containing the database password | `string` | n/a | yes |
| <a name="input_skip_final_snapshot"></a> [skip\_final\_snapshot](#input\_skip\_final\_snapshot) | Whether to skip the final DB snapshot when the cluster is deleted | `bool` | n/a | yes |
| <a name="input_storage_encrypted"></a> [storage\_encrypted](#input\_storage\_encrypted) | Whether to encrypt the Aurora PostgreSQL cluster storage | `bool` | n/a | yes |
| <a name="input_subnet_ids"></a> [subnet\_ids](#input\_subnet\_ids) | List of subnet IDs for Aurora PostgreSQL cluster (must be public subnets for external access) | `list(string)` | n/a | yes |
| <a name="input_vpc_id"></a> [vpc\_id](#input\_vpc\_id) | VPC ID where Aurora PostgreSQL cluster will be created | `string` | n/a | yes |
| <a name="input_workspace"></a> [workspace](#input\_workspace) | Terraform workspace | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_cluster_arn"></a> [cluster\_arn](#output\_cluster\_arn) | The ARN of the Aurora PostgreSQL cluster |
| <a name="output_cluster_endpoint"></a> [cluster\_endpoint](#output\_cluster\_endpoint) | The cluster endpoint (writer) |
| <a name="output_cluster_identifier"></a> [cluster\_identifier](#output\_cluster\_identifier) | The Aurora PostgreSQL cluster identifier |
| <a name="output_cluster_instance_endpoints"></a> [cluster\_instance\_endpoints](#output\_cluster\_instance\_endpoints) | List of Aurora PostgreSQL cluster instance endpoints |
| <a name="output_cluster_instances"></a> [cluster\_instances](#output\_cluster\_instances) | List of Aurora PostgreSQL cluster instance identifiers |
| <a name="output_cluster_port"></a> [cluster\_port](#output\_cluster\_port) | The port the cluster accepts connections on |
| <a name="output_cluster_reader_endpoint"></a> [cluster\_reader\_endpoint](#output\_cluster\_reader\_endpoint) | The cluster reader endpoint |
| <a name="output_cluster_resource_id"></a> [cluster\_resource\_id](#output\_cluster\_resource\_id) | The resource ID of the Aurora PostgreSQL cluster |
| <a name="output_database_name"></a> [database\_name](#output\_database\_name) | The name of the default database |
| <a name="output_engine"></a> [engine](#output\_engine) | The database engine |
| <a name="output_engine_version"></a> [engine\_version](#output\_engine\_version) | The database engine version |
| <a name="output_hosted_zone_id"></a> [hosted\_zone\_id](#output\_hosted\_zone\_id) | The hosted zone ID of the Aurora PostgreSQL cluster |
| <a name="output_master_password"></a> [master\_password](#output\_master\_password) | The master password (from Secrets Manager) |
| <a name="output_master_username"></a> [master\_username](#output\_master\_username) | The master username |
| <a name="output_postgresql_connection_string"></a> [postgresql\_connection\_string](#output\_postgresql\_connection\_string) | PostgreSQL connection string for the Aurora cluster |
| <a name="output_psql_connection_command"></a> [psql\_connection\_command](#output\_psql\_connection\_command) | psql command to connect to the Aurora PostgreSQL cluster (use terraform output to get the password) |
| <a name="output_security_group_arn"></a> [security\_group\_arn](#output\_security\_group\_arn) | The ARN of the Aurora PostgreSQL security group |
| <a name="output_security_group_id"></a> [security\_group\_id](#output\_security\_group\_id) | The ID of the Aurora PostgreSQL security group |
| <a name="output_subnet_group_arn"></a> [subnet\_group\_arn](#output\_subnet\_group\_arn) | The ARN of the Aurora PostgreSQL subnet group |
| <a name="output_subnet_group_name"></a> [subnet\_group\_name](#output\_subnet\_group\_name) | The name of the Aurora PostgreSQL subnet group |
<!-- END_TF_DOCS -->
