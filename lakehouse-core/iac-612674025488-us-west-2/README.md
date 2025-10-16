<!-- BEGIN_TF_DOCS -->


## Requirements

## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 6.15.0 |
| <a name="requirement_helm"></a> [helm](#requirement\_helm) | 3.0.2 |
| <a name="requirement_kubectl"></a> [kubectl](#requirement\_kubectl) | ~> 1.19.0 |
| <a name="requirement_kubernetes"></a> [kubernetes](#requirement\_kubernetes) | 2.38.0 |

## Providers

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | 6.15.0 |
| <a name="provider_helm"></a> [helm](#provider\_helm) | 3.0.2 |
| <a name="provider_kubectl"></a> [kubectl](#provider\_kubectl) | 1.19.0 |
| <a name="provider_kubernetes"></a> [kubernetes](#provider\_kubernetes) | 2.38.0 |

## Modules

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_eks_addons"></a> [eks\_addons](#module\_eks\_addons) | ./modules/eks-addons | n/a |
| <a name="module_eks_karpenter"></a> [eks\_karpenter](#module\_eks\_karpenter) | ./modules/eks-karpenter | n/a |
| <a name="module_rds_aurora_postgresql"></a> [rds\_aurora\_postgresql](#module\_rds\_aurora\_postgresql) | ./modules/rds-aurora-postgresql | n/a |
| <a name="module_redshift"></a> [redshift](#module\_redshift) | ./modules/redshift | n/a |
| <a name="module_vpc"></a> [vpc](#module\_vpc) | ./modules/vpc | n/a |

## Resources

## Resources

| Name | Type |
|------|------|
| [aws_eks_pod_identity_association.marquez_agent_bedrock](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/eks_pod_identity_association) | resource |
| [aws_iam_policy.marquez_agent_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_role.marquez_agent_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role_policy_attachment.bedrock_service_policy_attachment](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_s3_bucket.lakehouse_landing_zone_bucket](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket) | resource |
| [helm_release.marquez](https://registry.terraform.io/providers/hashicorp/helm/3.0.2/docs/resources/release) | resource |
| [kubectl_manifest.marquez_agent](https://registry.terraform.io/providers/gavinbunney/kubectl/latest/docs/resources/manifest) | resource |
| [kubectl_manifest.marquez_agent_config](https://registry.terraform.io/providers/gavinbunney/kubectl/latest/docs/resources/manifest) | resource |
| [kubectl_manifest.marquez_agent_ing](https://registry.terraform.io/providers/gavinbunney/kubectl/latest/docs/resources/manifest) | resource |
| [kubectl_manifest.marquez_agent_svc](https://registry.terraform.io/providers/gavinbunney/kubectl/latest/docs/resources/manifest) | resource |
| [kubectl_manifest.marquez_ing](https://registry.terraform.io/providers/gavinbunney/kubectl/latest/docs/resources/manifest) | resource |
| [kubectl_manifest.marquez_mcp](https://registry.terraform.io/providers/gavinbunney/kubectl/latest/docs/resources/manifest) | resource |
| [kubectl_manifest.marquez_mcp_ing](https://registry.terraform.io/providers/gavinbunney/kubectl/latest/docs/resources/manifest) | resource |
| [kubectl_manifest.marquez_mcp_svc](https://registry.terraform.io/providers/gavinbunney/kubectl/latest/docs/resources/manifest) | resource |
| [kubectl_manifest.marquez_web_ing](https://registry.terraform.io/providers/gavinbunney/kubectl/latest/docs/resources/manifest) | resource |
| [kubernetes_namespace.marquez](https://registry.terraform.io/providers/hashicorp/kubernetes/2.38.0/docs/resources/namespace) | resource |
| [kubernetes_service_account.marquez_agent_sa](https://registry.terraform.io/providers/hashicorp/kubernetes/2.38.0/docs/resources/service_account) | resource |
| [aws_availability_zones.available](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/availability_zones) | data source |
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |
| [aws_eks_cluster.cluster](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/eks_cluster) | data source |
| [aws_eks_cluster_auth.cluster](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/eks_cluster_auth) | data source |
| [aws_region.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/region) | data source |

## Inputs

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_account"></a> [account](#input\_account) | AWS account | `string` | n/a | yes |
| <a name="input_aws_lbc_version"></a> [aws\_lbc\_version](#input\_aws\_lbc\_version) | Version of AWS Load Balancer Controller to install | `string` | `"1.13.4"` | no |
| <a name="input_bedrock_model_id"></a> [bedrock\_model\_id](#input\_bedrock\_model\_id) | Bedrock model ID for Marquez agent | `string` | `"us.anthropic.claude-sonnet-4-20250514-v1:0"` | no |
| <a name="input_eks-version"></a> [eks-version](#input\_eks-version) | n/a | `string` | `"1.33"` | no |
| <a name="input_ingress_inbound_cidrs"></a> [ingress\_inbound\_cidrs](#input\_ingress\_inbound\_cidrs) | Comma-separated list of CIDR blocks allowed to access the ingress | `string` | `"104.153.113.16/28,15.248.80.128/25,205.251.233.104/29,205.251.233.176/29,205.251.233.232/29,205.251.233.48/29,52.46.249.224/29,52.46.249.248/29"` | no |
| <a name="input_karpenter_version"></a> [karpenter\_version](#input\_karpenter\_version) | Version of Karpenter to install | `string` | `"1.6.2"` | no |
| <a name="input_partition"></a> [partition](#input\_partition) | AWS partition | `string` | `"aws"` | no |
| <a name="input_project_name"></a> [project\_name](#input\_project\_name) | The name of the project | `string` | `"lakehouse-core"` | no |
| <a name="input_project_name_alias"></a> [project\_name\_alias](#input\_project\_name\_alias) | The short name of the project | `string` | `"lh-core"` | no |
| <a name="input_region"></a> [region](#input\_region) | AWS region | `string` | n/a | yes |
| <a name="input_s3_endpoint"></a> [s3\_endpoint](#input\_s3\_endpoint) | S3 endpoint (will be dynamically constructed based on region) | `string` | `""` | no |

## Outputs

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_aurora_postgresql_cluster_identifier"></a> [aurora\_postgresql\_cluster\_identifier](#output\_aurora\_postgresql\_cluster\_identifier) | Aurora PostgreSQL cluster identifier |
| <a name="output_aurora_postgresql_cluster_port"></a> [aurora\_postgresql\_cluster\_port](#output\_aurora\_postgresql\_cluster\_port) | Aurora PostgreSQL cluster port |
| <a name="output_aurora_postgresql_cluster_reader_endpoint"></a> [aurora\_postgresql\_cluster\_reader\_endpoint](#output\_aurora\_postgresql\_cluster\_reader\_endpoint) | Aurora PostgreSQL cluster reader endpoint |
| <a name="output_aurora_postgresql_cluster_writer_endpoint"></a> [aurora\_postgresql\_cluster\_writer\_endpoint](#output\_aurora\_postgresql\_cluster\_writer\_endpoint) | Aurora PostgreSQL cluster writer endpoint |
| <a name="output_aurora_postgresql_connection_command"></a> [aurora\_postgresql\_connection\_command](#output\_aurora\_postgresql\_connection\_command) | psql connection command (password needs to be retrieved from AWS Secrets Manager) |
| <a name="output_aurora_postgresql_database_name"></a> [aurora\_postgresql\_database\_name](#output\_aurora\_postgresql\_database\_name) | Aurora PostgreSQL database name |
| <a name="output_aurora_postgresql_master_username"></a> [aurora\_postgresql\_master\_username](#output\_aurora\_postgresql\_master\_username) | Aurora PostgreSQL master username |
| <a name="output_iam_role_arn_karpenter"></a> [iam\_role\_arn\_karpenter](#output\_iam\_role\_arn\_karpenter) | Iam role arn of karpenter |
| <a name="output_internet_gateway_id"></a> [internet\_gateway\_id](#output\_internet\_gateway\_id) | ID of the Internet Gateway |
| <a name="output_landign_zone_s3_bucket_arn"></a> [landign\_zone\_s3\_bucket\_arn](#output\_landign\_zone\_s3\_bucket\_arn) | ################################## Landing zone ################################## |
| <a name="output_nat_gateway_id"></a> [nat\_gateway\_id](#output\_nat\_gateway\_id) | ID of the NAT Gateway |
| <a name="output_node_iam_role_arn_karpenter"></a> [node\_iam\_role\_arn\_karpenter](#output\_node\_iam\_role\_arn\_karpenter) | Node iam role arn of karpenter |
| <a name="output_node_iam_role_name_karpenter"></a> [node\_iam\_role\_name\_karpenter](#output\_node\_iam\_role\_name\_karpenter) | Node iam role of karpenter |
| <a name="output_private_subnet_ids"></a> [private\_subnet\_ids](#output\_private\_subnet\_ids) | List of IDs of the private subnets |
| <a name="output_public_subnet_ids"></a> [public\_subnet\_ids](#output\_public\_subnet\_ids) | List of IDs of the public subnets |
| <a name="output_redshift_cluster_endpoint"></a> [redshift\_cluster\_endpoint](#output\_redshift\_cluster\_endpoint) | Redshift cluster endpoint |
| <a name="output_redshift_cluster_host"></a> [redshift\_cluster\_host](#output\_redshift\_cluster\_host) | Redshift cluster hostname (without port) |
| <a name="output_redshift_cluster_identifier"></a> [redshift\_cluster\_identifier](#output\_redshift\_cluster\_identifier) | Redshift cluster identifier |
| <a name="output_redshift_cluster_port"></a> [redshift\_cluster\_port](#output\_redshift\_cluster\_port) | Redshift cluster port |
| <a name="output_redshift_connection_string"></a> [redshift\_connection\_string](#output\_redshift\_connection\_string) | JDBC connection string for Redshift cluster |
| <a name="output_redshift_database_name"></a> [redshift\_database\_name](#output\_redshift\_database\_name) | Redshift database name |
| <a name="output_redshift_master_username"></a> [redshift\_master\_username](#output\_redshift\_master\_username) | Redshift master username |
| <a name="output_redshift_psql_connection_command"></a> [redshift\_psql\_connection\_command](#output\_redshift\_psql\_connection\_command) | psql connection command (password needs to be retrieved from AWS managed Secrets Manager secret) |
| <a name="output_vpc_cidr_block"></a> [vpc\_cidr\_block](#output\_vpc\_cidr\_block) | CIDR block of the VPC |
| <a name="output_vpc_id"></a> [vpc\_id](#output\_vpc\_id) | ID of the VPC |
<!-- END_TF_DOCS -->
