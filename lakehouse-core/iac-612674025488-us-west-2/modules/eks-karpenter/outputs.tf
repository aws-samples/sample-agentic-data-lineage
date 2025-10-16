# EKS Outputs
output "cluster_name" {
  description = "Name of the EKS cluster"
  value       = module.eks.cluster_name
}

output "cluster_arn" {
  description = "ARN of the EKS cluster"
  value       = module.eks.cluster_arn
}

output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "cluster_security_group_id" {
  description = "Security group ids attached to the cluster control plane"
  value       = module.eks.cluster_security_group_id
}

output "cluster_iam_role_name" {
  description = "IAM role name associated with EKS cluster"
  value       = module.eks.cluster_iam_role_name
}

output "cluster_iam_role_arn" {
  description = "IAM role ARN associated with EKS cluster"
  value       = module.eks.cluster_iam_role_arn
}

output "cluster_certificate_authority_data" {
  description = "Base64 encoded certificate data required to communicate with the cluster"
  value       = module.eks.cluster_certificate_authority_data
}

output "cluster_version" {
  description = "The Kubernetes version for the EKS cluster"
  value       = module.eks.cluster_version
}

output "oidc_provider_arn" {
  description = "The ARN of the OIDC Provider if enabled"
  value       = module.eks.oidc_provider_arn
}

output "eks_managed_node_groups" {
  description = "Map of attribute maps for all EKS managed node groups created"
  value       = module.eks.eks_managed_node_groups
}

output "node_iam_role_arn" {
  description = "ARN of the EKS node group IAM role"
  value       = module.eks.node_iam_role_arn
}

# Karpenter Outputs
output "karpenter_service_account" {
  description = "Karpenter service account name"
  value       = module.karpenter.service_account
}

output "karpenter_queue_name" {
  description = "Karpenter SQS queue name"
  value       = module.karpenter.queue_name
}

output "karpenter_node_iam_role_name" {
  description = "Karpenter node IAM role name"
  value       = module.karpenter.node_iam_role_name
}

output "karpenter_node_iam_role_arn" {
  description = "Karpenter node IAM role ARN"
  value       = module.karpenter.node_iam_role_arn
}

output "karpenter_iam_role_name" {
  description = "Karpenter controller IAM role name"
  value       = module.karpenter.iam_role_name
}
