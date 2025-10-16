# Bedrock IAM Role for EKS Services
resource "aws_iam_role" "marquez_agent_role" {
  name = "${var.project_name_alias}-${local.workspace}-marquez-agent-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "pods.eks.amazonaws.com"
        }
        Action = [
          "sts:AssumeRole",
          "sts:TagSession"
        ]
      }
    ]
  })

  tags = local.default_tags
}

# Bedrock access policy + Glue access policy
resource "aws_iam_policy" "marquez_agent_policy" {
  name = "${var.project_name_alias}-${local.workspace}-marquez-agent-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
          "bedrock:ListFoundationModels",
          "bedrock:GetFoundationModel"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "glue:GetDatabases",
          "glue:GetDatabase",
          "glue:GetTables",
          "glue:GetTable",
          "glue:GetPartitions",
          "glue:SearchTables"
        ]
        Resource = "*"
      }
    ]
  })

  tags = local.default_tags
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "bedrock_service_policy_attachment" {
  role       = aws_iam_role.marquez_agent_role.name
  policy_arn = aws_iam_policy.marquez_agent_policy.arn
}

# Pod Identity Association for marquez-agent service
resource "aws_eks_pod_identity_association" "marquez_agent_bedrock" {
  cluster_name    = module.eks_karpenter.cluster_name
  namespace       = kubernetes_namespace.marquez.metadata[0].name
  service_account = kubernetes_service_account.marquez_agent_sa.metadata[0].name
  role_arn        = aws_iam_role.marquez_agent_role.arn

  depends_on = [
    module.eks_karpenter,
    kubernetes_service_account.marquez_agent_sa
  ]
}

# Service Account for marquez-agent
resource "kubernetes_service_account" "marquez_agent_sa" {
  metadata {
    name      = "marquez-agent-sa"
    namespace = kubernetes_namespace.marquez.metadata[0].name
  }

  depends_on = [kubernetes_namespace.marquez]
}
