<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
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
| [aws_redshift_cluster.redshift_cluster](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/redshift_cluster) | resource |
| [aws_redshift_subnet_group.redshift_subnet_group](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/redshift_subnet_group) | resource |
| [aws_security_group.redshift_security_group](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group) | resource |
| [aws_secretsmanager_secret.redshift_password](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/secretsmanager_secret) | data source |
| [aws_secretsmanager_secret_version.redshift_password](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/secretsmanager_secret_version) | data source |
| [aws_vpc.selected](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/vpc) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_account"></a> [account](#input\_account) | AWS account | `string` | n/a | yes |
| <a name="input_default_tags"></a> [default\_tags](#input\_default\_tags) | Default tags to apply to resources | `map(string)` | n/a | yes |
| <a name="input_project_name_alias"></a> [project\_name\_alias](#input\_project\_name\_alias) | The short name of the project | `string` | n/a | yes |
| <a name="input_region"></a> [region](#input\_region) | AWS region | `string` | n/a | yes |
| <a name="input_secret_name"></a> [secret\_name](#input\_secret\_name) | Name of the AWS Secrets Manager secret containing the database password | `string` | n/a | yes |
| <a name="input_subnet_ids"></a> [subnet\_ids](#input\_subnet\_ids) | List of subnet IDs for Redshift cluster (must be public subnets for external access) | `list(string)` | n/a | yes |
| <a name="input_vpc_id"></a> [vpc\_id](#input\_vpc\_id) | VPC ID where Redshift cluster will be created | `string` | n/a | yes |
| <a name="input_workspace"></a> [workspace](#input\_workspace) | Terraform workspace | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_cluster_endpoint"></a> [cluster\_endpoint](#output\_cluster\_endpoint) | The connection endpoint |
| <a name="output_cluster_host"></a> [cluster\_host](#output\_cluster\_host) | The connection hostname (without port) |
| <a name="output_cluster_identifier"></a> [cluster\_identifier](#output\_cluster\_identifier) | The Redshift cluster identifier |
| <a name="output_cluster_port"></a> [cluster\_port](#output\_cluster\_port) | The port the cluster accepts connections on |
| <a name="output_connection_string"></a> [connection\_string](#output\_connection\_string) | JDBC connection string for the Redshift cluster |
| <a name="output_database_name"></a> [database\_name](#output\_database\_name) | The name of the default database |
| <a name="output_master_password"></a> [master\_password](#output\_master\_password) | The master password (from Secrets Manager) |
| <a name="output_master_username"></a> [master\_username](#output\_master\_username) | The master username |
| <a name="output_psql_connection_command"></a> [psql\_connection\_command](#output\_psql\_connection\_command) | psql command to connect to the Redshift cluster (use terraform output to get the password) |
<!-- END_TF_DOCS -->
