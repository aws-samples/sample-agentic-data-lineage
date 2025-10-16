# marquez
resource "kubernetes_namespace" "marquez" {
  metadata {
    name = "marquez"
  }

  depends_on = [
    module.eks_addons
  ]
}

resource "helm_release" "marquez" {
  name       = "marquez"
  namespace  = kubernetes_namespace.marquez.metadata[0].name
  repository = local.helm_repo
  chart      = "marquez"
  version    = "0.51.1"

  values = [
    jsonencode({
      marquez = {
        db = {
          host     = module.rds_aurora_postgresql.cluster_endpoint
          user     = module.rds_aurora_postgresql.master_username
          password = module.rds_aurora_postgresql.master_password
        }
      }
      # nodeSelector = {
      #   "karpenter.sh/nodepool" = "common-nodepool"
      # }
    })
  ]

  depends_on = [
    kubernetes_namespace.marquez,
    module.rds_aurora_postgresql
  ]
}


resource "kubectl_manifest" "marquez_web_ing" {
  yaml_body = templatefile("${path.module}/marquez-manifest/ingress-marquez-web.yaml", {
    inbound_cidrs = var.ingress_inbound_cidrs
  })
  depends_on = [
    helm_release.marquez
  ]
}

resource "kubectl_manifest" "marquez_ing" {
  yaml_body = templatefile("${path.module}/marquez-manifest/ingress-marquez.yaml", {})
  depends_on = [
    helm_release.marquez
  ]
}

resource "kubectl_manifest" "marquez_mcp" {
  yaml_body = templatefile("${path.module}/marquez-manifest/marquez-mcp.yaml", {
    ecr_repository_url = "${local.account}.dkr.ecr.${local.region}.amazonaws.com"
  })
  depends_on = [
    helm_release.marquez,
  ]
}

resource "kubectl_manifest" "marquez_mcp_svc" {
  yaml_body = templatefile("${path.module}/marquez-manifest/svc-marquez-mcp.yaml", {})
  depends_on = [
    helm_release.marquez
  ]
}

resource "kubectl_manifest" "marquez_mcp_ing" {
  yaml_body = templatefile("${path.module}/marquez-manifest/ingress-marquez-mcp.yaml", {
    inbound_cidrs = var.ingress_inbound_cidrs
  })
  depends_on = [
    helm_release.marquez
  ]
}


resource "kubectl_manifest" "marquez_agent_config" {
  yaml_body = templatefile("${path.module}/marquez-manifest/cfm-marquez-agent.yaml", {
    redshift_host    = module.redshift.cluster_host
    bedrock_model_id = var.bedrock_model_id
    bedrock_region   = local.region
  })
  depends_on = [
    helm_release.marquez,
    module.redshift
  ]
}

resource "kubectl_manifest" "marquez_agent" {
  yaml_body = templatefile("${path.module}/marquez-manifest/marquez-agent.yaml", {
    ecr_repository_url = "${local.account}.dkr.ecr.${local.region}.amazonaws.com"
  })
  depends_on = [
    helm_release.marquez,
    kubernetes_service_account.marquez_agent_sa,
    kubectl_manifest.marquez_agent_config
  ]
}

resource "kubectl_manifest" "marquez_agent_svc" {
  yaml_body = templatefile("${path.module}/marquez-manifest/svc-marquez-agent.yaml", {})
  depends_on = [
    helm_release.marquez
  ]
}

resource "kubectl_manifest" "marquez_agent_ing" {
  yaml_body = templatefile("${path.module}/marquez-manifest/ingress-marquez-agent.yaml", {
    inbound_cidrs = var.ingress_inbound_cidrs
  })
  depends_on = [
    helm_release.marquez
  ]
}
