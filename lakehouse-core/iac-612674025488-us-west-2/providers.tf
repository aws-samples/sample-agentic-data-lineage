terraform {
  //TODO: Parameterize it in CICD pipeline
  //Specify with your own state bucket
  backend "s3" {
    region = "us-west-2"
    bucket = "tf-state-lh-core-612674025488-us-west-2-kolya"
    key    = "state"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.15.0"
    }
    kubectl = {
      source  = "gavinbunney/kubectl"
      version = "~> 1.19.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "3.0.2"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.38.0"
    }
  }
}

provider "aws" {
  //TODO: Parameterize it in CICD pipeline
  region = var.region
  assume_role {
    # Use variables directly to avoid circular dependency with data sources
    role_arn = "arn:${var.partition}:iam::${var.account}:role/${var.project_name_alias}-${var.account}-${var.region}-${terraform.workspace}-deploy-role"
  }
}

provider "helm" {
  kubernetes = {
    host                   = data.aws_eks_cluster.cluster.endpoint
    cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority[0].data)
    token                  = data.aws_eks_cluster_auth.cluster.token
  }
}

provider "kubernetes" {
  host                   = data.aws_eks_cluster.cluster.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.cluster.token
}

provider "kubectl" {
  apply_retry_count      = 5
  host                   = data.aws_eks_cluster.cluster.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.cluster.token
  load_config_file       = false
}
