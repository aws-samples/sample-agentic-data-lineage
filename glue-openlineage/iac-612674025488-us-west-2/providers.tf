terraform {
  backend "s3" {
    region = "us-west-2"
    bucket = "glue-openlineage-tf-state-lh-core-612674025488-us-west-2-kolya"
    key    = "state"
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.10.0"
    }
  }
}
