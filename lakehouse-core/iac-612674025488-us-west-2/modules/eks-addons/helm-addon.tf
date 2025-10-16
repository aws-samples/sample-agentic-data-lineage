locals {
  resource_prefix = "${var.project_name_alias}-${var.account}-${var.region}-${var.workspace}"
}

# pod identity
data "aws_iam_policy_document" "aws_lbc" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["pods.eks.amazonaws.com"]
    }

    actions = [
      "sts:AssumeRole",
      "sts:TagSession"
    ]
  }
}

resource "aws_iam_role" "aws_lbc" {
  name               = "${local.resource_prefix}-albc"
  assume_role_policy = data.aws_iam_policy_document.aws_lbc.json

  tags = var.default_tags
}

resource "aws_iam_policy" "aws_lbc" {
  policy = var.iam_policy_path != "" ? templatefile(var.iam_policy_path, {
    partition = var.partition
    }) : templatefile("${path.root}/iam/AWSLoadBalancerController.json", {
    partition = var.partition
  })
  name = "${local.resource_prefix}-albc"

  tags = var.default_tags
}

resource "aws_iam_role_policy_attachment" "aws_lbc" {
  policy_arn = aws_iam_policy.aws_lbc.arn
  role       = aws_iam_role.aws_lbc.name
}

resource "aws_eks_pod_identity_association" "aws_lbc" {
  cluster_name    = var.cluster_name
  namespace       = "kube-system"
  service_account = "aws-load-balancer-controller"
  role_arn        = aws_iam_role.aws_lbc.arn
}

# helm install addon
resource "helm_release" "aws_lbc" {
  name       = "aws-load-balancer-controller"
  namespace  = "kube-system"
  repository = var.helm_repo
  chart      = "aws-load-balancer-controller"
  version    = var.aws_lbc_version
  timeout    = 600

  values = [
    <<EOT
    clusterName: ${var.cluster_name}
    region: ${var.region}
    vpcId: ${var.vpc_id}
    serviceAccount:
      name: aws-load-balancer-controller
    EOT
  ]

  depends_on = [aws_eks_pod_identity_association.aws_lbc]
}
