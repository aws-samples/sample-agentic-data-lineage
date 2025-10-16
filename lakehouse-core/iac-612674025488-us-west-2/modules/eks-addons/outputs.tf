# AWS Load Balancer Controller outputs
output "aws_lbc_iam_role_arn" {
  description = "ARN of the IAM role for AWS Load Balancer Controller"
  value       = aws_iam_role.aws_lbc.arn
}

output "aws_lbc_iam_role_name" {
  description = "Name of the IAM role for AWS Load Balancer Controller"
  value       = aws_iam_role.aws_lbc.name
}

output "aws_lbc_policy_arn" {
  description = "ARN of the IAM policy for AWS Load Balancer Controller"
  value       = aws_iam_policy.aws_lbc.arn
}

output "aws_lbc_helm_release_name" {
  description = "Name of the AWS Load Balancer Controller Helm release"
  value       = helm_release.aws_lbc.name
}

output "aws_lbc_helm_release_namespace" {
  description = "Namespace of the AWS Load Balancer Controller Helm release"
  value       = helm_release.aws_lbc.namespace
}

# Karpenter outputs
# output "karpenter_helm_release_name" {
#   description = "Name of the Karpenter Helm release"
#   value       = helm_release.karpenter.name
# }

# output "karpenter_helm_release_namespace" {
#   description = "Namespace of the Karpenter Helm release"
#   value       = helm_release.karpenter.namespace
# }

# output "karpenter_node_class_name" {
#   description = "Name of the Karpenter EC2NodeClass"
#   value       = "common-ec2nodeclass"
# }

# output "karpenter_node_pool_name" {
#   description = "Name of the Karpenter NodePool"
#   value       = "common-nodepool"
# }
