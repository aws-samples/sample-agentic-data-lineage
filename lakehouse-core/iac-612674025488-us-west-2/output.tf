# # output "aws_caller_identity" {
# #   description = "Current assumed role to conduct the deployment"
# #   value       = data.aws_caller_identity.current.arn
# # }

# # output "region" {
# #   description = "Aws region"
# #   value       = data.aws_region.current.id
# # }

###################################
# VPC Outputs
###################################
output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = module.vpc.vpc_cidr_block
}

output "public_subnet_ids" {
  description = "List of IDs of the public subnets"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "List of IDs of the private subnets"
  value       = module.vpc.private_subnet_ids
}

output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = module.vpc.internet_gateway_id
}

output "nat_gateway_id" {
  description = "ID of the NAT Gateway"
  value       = module.vpc.nat_gateway_id
}

# ###################################
# # EKS Cluster Control Plane
# ###################################
# output "eks_cluster_arn" {
#   description = "The ARN of the EKS cluster"
#   value       = module.eks_karpenter.cluster_arn
# }

# output "eks_cluster_name" {
#   description = "The Name of the EKS cluster"
#   value       = module.eks_karpenter.cluster_name
# }

# output "eks_endpoint" {
#   description = "Endpoint for your Kubernetes API server"
#   value       = data.aws_eks_cluster.cluster.endpoint
# }

# output "cluster_version" {
#   description = "The Kubernetes version for the cluster"
#   value       = module.eks_karpenter.cluster_version
# }

# output "cluster_iam_role_name" {
#   description = "iam role name of EKS cluster control plane"
#   value       = module.eks_karpenter.cluster_iam_role_name
# }

# # output "eks_ca" {
# #   description = "Base64 encoded certificate data required to communicate with the cluster"
# #   value = data.aws_eks_cluster.eks.certificate_authority[0].data
# # }

# # output "eks_token" {
# #   value     = data.aws_eks_cluster_auth.eks.token
# #   sensitive = true # Avoid sensitive information leakage
# # }

# ###################################
# # EKS Managed Node Group
# ###################################
# output "core_node_group_role_name" {
#   description = "EKS managed node group of core_node_group IAM role name"
#   value       = module.eks_karpenter.eks_managed_node_groups["core_node_group"]["iam_role_name"]
# }

# output "core_node_group_role_arn" {
#   description = "EKS managed node group of core_node_group IAM role arn"
#   value       = module.eks_karpenter.eks_managed_node_groups["core_node_group"]["iam_role_arn"]
# }

# output "cluster_node_iam_role_arn" {
#   description = "EKS Auto node IAM role name"
#   value       = module.eks_karpenter.node_iam_role_arn
# }


# ###################################
# # Karpenter
# ###################################
output "node_iam_role_name_karpenter" {
  description = "Node iam role of karpenter"
  value       = module.eks_karpenter.karpenter_node_iam_role_name
}

output "node_iam_role_arn_karpenter" {
  description = "Node iam role arn of karpenter"
  value       = module.eks_karpenter.karpenter_node_iam_role_arn
}

output "iam_role_arn_karpenter" {
  description = "Iam role arn of karpenter"
  value       = module.eks_karpenter.karpenter_iam_role_name
}

###################################
# Redshift Cluster
###################################
output "redshift_cluster_identifier" {
  description = "Redshift cluster identifier"
  value       = module.redshift.cluster_identifier
}

output "redshift_cluster_endpoint" {
  description = "Redshift cluster endpoint"
  value       = module.redshift.cluster_endpoint
}

output "redshift_cluster_host" {
  description = "Redshift cluster hostname (without port)"
  value       = module.redshift.cluster_host
}

output "redshift_cluster_port" {
  description = "Redshift cluster port"
  value       = module.redshift.cluster_port
}

output "redshift_database_name" {
  description = "Redshift database name"
  value       = module.redshift.database_name
}

output "redshift_master_username" {
  description = "Redshift master username"
  value       = module.redshift.master_username
}

output "redshift_connection_string" {
  description = "JDBC connection string for Redshift cluster"
  value       = module.redshift.connection_string
}

output "redshift_psql_connection_command" {
  description = "psql connection command (password needs to be retrieved from AWS managed Secrets Manager secret)"
  value       = module.redshift.psql_connection_command
}

###################################
# RDS Aurora Mysql Cluster
###################################
# output "aurora_cluster_identifier" {
#   description = "Aurora cluster identifier"
#   value       = module.rds_aurora_mysql.cluster_identifier
# }

# output "aurora_cluster_writer_endpoint" {
#   description = "Aurora cluster writer endpoint"
#   value       = module.rds_aurora_mysql.cluster_endpoint
# }

# output "aurora_cluster_reader_endpoint" {
#   description = "Aurora cluster reader endpoint"
#   value       = module.rds_aurora_mysql.cluster_reader_endpoint
# }

# output "aurora_mysql_connection_command" {
#   description = "MySQL connection command (password needs to be retrieved from AWS Secrets Manager)"
#   value       = module.rds_aurora_mysql.mysql_connection_command
# }
###################################
# RDS Aurora PostgreSQL Cluster
###################################
output "aurora_postgresql_cluster_identifier" {
  description = "Aurora PostgreSQL cluster identifier"
  value       = module.rds_aurora_postgresql.cluster_identifier
}

output "aurora_postgresql_cluster_writer_endpoint" {
  description = "Aurora PostgreSQL cluster writer endpoint"
  value       = module.rds_aurora_postgresql.cluster_endpoint
}

output "aurora_postgresql_cluster_reader_endpoint" {
  description = "Aurora PostgreSQL cluster reader endpoint"
  value       = module.rds_aurora_postgresql.cluster_reader_endpoint
}

output "aurora_postgresql_cluster_port" {
  description = "Aurora PostgreSQL cluster port"
  value       = module.rds_aurora_postgresql.cluster_port
}

output "aurora_postgresql_database_name" {
  description = "Aurora PostgreSQL database name"
  value       = module.rds_aurora_postgresql.database_name
}

output "aurora_postgresql_master_username" {
  description = "Aurora PostgreSQL master username"
  value       = module.rds_aurora_postgresql.master_username
}

output "aurora_postgresql_connection_command" {
  description = "psql connection command (password needs to be retrieved from AWS Secrets Manager)"
  value       = module.rds_aurora_postgresql.psql_connection_command
}

###################################
# Landing zone
###################################
output "landign_zone_s3_bucket_arn" {
  value = aws_s3_bucket.lakehouse_landing_zone_bucket.arn
}


# ###################################
# # Ec2 bastion
# ###################################
# output "ssh_command" {
#   value = "ssh -i ~/path/to/bastion.pem ec2-user@${aws_instance.bastion.public_ip}"
# }


##################################
# EKS Add-ons Outputs
##################################
# output "aws_lbc_iam_role_arn" {
#   description = "ARN of the IAM role for AWS Load Balancer Controller"
#   value       = module.eks_addons.aws_lbc_iam_role_arn
# }

# output "aws_lbc_iam_role_name" {
#   description = "Name of the IAM role for AWS Load Balancer Controller"
#   value       = module.eks_addons.aws_lbc_iam_role_name
# }

# output "karpenter_helm_release_name" {
#   description = "Name of the Karpenter Helm release"
#   value       = module.eks_addons.karpenter_helm_release_name
# }

# output "karpenter_helm_release_namespace" {
#   description = "Namespace of the Karpenter Helm release"
#   value       = module.eks_addons.karpenter_helm_release_namespace
# }
