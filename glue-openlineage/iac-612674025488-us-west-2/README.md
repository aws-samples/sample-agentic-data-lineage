# iac-612674025488-us-west-2

<!-- BEGIN_TF_DOCS -->


## Requirements

## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 6.10.0 |

## Providers

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | 6.10.0 |
| <a name="provider_terraform"></a> [terraform](#provider\_terraform) | n/a |

## Modules

## Modules

No modules.

## Resources

## Resources

| Name | Type |
|------|------|
| [aws_glue_catalog_database.iceberg_database](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/glue_catalog_database) | resource |
| [aws_glue_connection.vpc_connection](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/glue_connection) | resource |
| [aws_glue_job.glue_spark_customers_job](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/glue_job) | resource |
| [aws_glue_job.glue_spark_orders_job](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/glue_job) | resource |
| [aws_glue_job.glue_spark_payments_job](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/glue_job) | resource |
| [aws_iam_role.glue_job_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role.redshift_spectrum_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role_policy.glue_job_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy.redshift_spectrum_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy_attachment.glue_service_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_redshift_cluster_iam_roles.redshift_spectrum_role_attachment](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/redshift_cluster_iam_roles) | resource |
| [aws_s3_bucket.datalake_libs_bucket](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket) | resource |
| [aws_s3_object.pyspark_customers_script](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_object) | resource |
| [aws_s3_object.pyspark_orders_script](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_object) | resource |
| [aws_s3_object.pyspark_payments_script](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_object) | resource |
| [aws_security_group.glue_sg](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group) | resource |
| [terraform_remote_state.rs](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/data-sources/remote_state) | data source |

## Inputs

## Inputs

No inputs.

## Outputs

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_glue_vpc_connection_name"></a> [glue\_vpc\_connection\_name](#output\_glue\_vpc\_connection\_name) | Name of the Glue VPC connection |
<!-- END_TF_DOCS -->
