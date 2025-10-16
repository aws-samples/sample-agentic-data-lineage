# karpenter
resource "helm_release" "karpenter" {
  namespace  = "kube-system"
  name       = "karpenter"
  repository = "oci://public.ecr.aws/karpenter/"
  chart      = "karpenter"
  version    = var.karpenter_version
  timeout    = 600

  values = [
    <<-EOT
    serviceAccount:
      name: ${var.karpenter_service_account}
    settings:
      clusterName: ${var.cluster_name}
      clusterEndpoint: ${var.cluster_endpoint}
      interruptionQueue: ${var.karpenter_queue_name}
    EOT
  ]


}

resource "kubectl_manifest" "karpenter_common_node_class" {
  yaml_body = templatefile("${path.root}/karpenter-node/common/common-ec2nodeclass.yaml", {
    subnetSelectorTermsValue = var.cluster_name
    node_iam_role_name       = var.karpenter_node_iam_role_name
  })

  depends_on = [helm_release.karpenter]
}

resource "kubectl_manifest" "karpenter_common_node_pool" {
  yaml_body = templatefile("${path.root}/karpenter-node/common/common-nodepool.yaml", {})

  depends_on = [kubectl_manifest.karpenter_common_node_class]
}
