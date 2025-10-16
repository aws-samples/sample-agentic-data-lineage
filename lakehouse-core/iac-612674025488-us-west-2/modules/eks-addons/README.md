<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | >= 5.0.0 |
| <a name="requirement_helm"></a> [helm](#requirement\_helm) | >= 2.0.0 |
| <a name="requirement_kubectl"></a> [kubectl](#requirement\_kubectl) | >= 1.19.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | >= 5.0.0 |
| <a name="provider_helm"></a> [helm](#provider\_helm) | >= 2.0.0 |
| <a name="provider_kubectl"></a> [kubectl](#provider\_kubectl) | >= 1.19.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_eks_pod_identity_association.aws_lbc](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/eks_pod_identity_association) | resource |
| [aws_iam_policy.aws_lbc](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy) | resource |
| [aws_iam_role.aws_lbc](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role_policy_attachment.aws_lbc](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [helm_release.aws_lbc](https://registry.terraform.io/providers/hashicorp/helm/latest/docs/resources/release) | resource |
| [helm_release.karpenter](https://registry.terraform.io/providers/hashicorp/helm/latest/docs/resources/release) | resource |
| [kubectl_manifest.karpenter_common_node_class](https://registry.terraform.io/providers/gavinbunney/kubectl/latest/docs/resources/manifest) | resource |
| [kubectl_manifest.karpenter_common_node_pool](https://registry.terraform.io/providers/gavinbunney/kubectl/latest/docs/resources/manifest) | resource |
| [aws_iam_policy_document.aws_lbc](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_account"></a> [account](#input\_account) | AWS account ID | `string` | n/a | yes |
| <a name="input_aws_lbc_version"></a> [aws\_lbc\_version](#input\_aws\_lbc\_version) | Version of AWS Load Balancer Controller to install | `string` | `"1.13.4"` | no |
| <a name="input_cluster_endpoint"></a> [cluster\_endpoint](#input\_cluster\_endpoint) | EKS cluster endpoint | `string` | n/a | yes |
| <a name="input_cluster_name"></a> [cluster\_name](#input\_cluster\_name) | Name of the EKS cluster | `string` | n/a | yes |
| <a name="input_default_tags"></a> [default\_tags](#input\_default\_tags) | Default tags to apply to all resources | `map(string)` | `{}` | no |
| <a name="input_helm_repo"></a> [helm\_repo](#input\_helm\_repo) | Helm repository URL | `string` | n/a | yes |
| <a name="input_iam_policy_path"></a> [iam\_policy\_path](#input\_iam\_policy\_path) | Path to the IAM policy file for AWS Load Balancer Controller | `string` | `""` | no |
| <a name="input_karpenter_node_iam_role_name"></a> [karpenter\_node\_iam\_role\_name](#input\_karpenter\_node\_iam\_role\_name) | IAM role name for Karpenter nodes | `string` | n/a | yes |
| <a name="input_karpenter_queue_name"></a> [karpenter\_queue\_name](#input\_karpenter\_queue\_name) | Karpenter SQS queue name for interruption handling | `string` | n/a | yes |
| <a name="input_karpenter_service_account"></a> [karpenter\_service\_account](#input\_karpenter\_service\_account) | Karpenter service account name | `string` | n/a | yes |
| <a name="input_karpenter_version"></a> [karpenter\_version](#input\_karpenter\_version) | Version of Karpenter to install | `string` | `"1.6.2"` | no |
| <a name="input_partition"></a> [partition](#input\_partition) | AWS partition (aws, aws-cn, aws-us-gov) | `string` | `"aws"` | no |
| <a name="input_project_name_alias"></a> [project\_name\_alias](#input\_project\_name\_alias) | Project name alias for resource naming | `string` | n/a | yes |
| <a name="input_region"></a> [region](#input\_region) | AWS region | `string` | n/a | yes |
| <a name="input_vpc_id"></a> [vpc\_id](#input\_vpc\_id) | VPC ID where the cluster is deployed | `string` | n/a | yes |
| <a name="input_workspace"></a> [workspace](#input\_workspace) | Terraform workspace name | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_aws_lbc_helm_release_name"></a> [aws\_lbc\_helm\_release\_name](#output\_aws\_lbc\_helm\_release\_name) | Name of the AWS Load Balancer Controller Helm release |
| <a name="output_aws_lbc_helm_release_namespace"></a> [aws\_lbc\_helm\_release\_namespace](#output\_aws\_lbc\_helm\_release\_namespace) | Namespace of the AWS Load Balancer Controller Helm release |
| <a name="output_aws_lbc_iam_role_arn"></a> [aws\_lbc\_iam\_role\_arn](#output\_aws\_lbc\_iam\_role\_arn) | ARN of the IAM role for AWS Load Balancer Controller |
| <a name="output_aws_lbc_iam_role_name"></a> [aws\_lbc\_iam\_role\_name](#output\_aws\_lbc\_iam\_role\_name) | Name of the IAM role for AWS Load Balancer Controller |
| <a name="output_aws_lbc_policy_arn"></a> [aws\_lbc\_policy\_arn](#output\_aws\_lbc\_policy\_arn) | ARN of the IAM policy for AWS Load Balancer Controller |
<!-- END_TF_DOCS -->
