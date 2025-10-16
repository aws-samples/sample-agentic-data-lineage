locals {
  project_name = "glue-openlineage"
  default_tags = {
    "DeploymentName" = local.project_name
    "ManagedBy"      = "terraform"
  }
}

data "terraform_remote_state" "rs" {
  backend = "s3"
  config = {
    bucket = "tf-state-lh-core-612674025488-us-west-2-kolya"
    key    = "env:/kolya/state"
    region = "us-west-2"
  }
}
