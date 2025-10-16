resource "aws_s3_bucket" "datalake_libs_bucket" {
  bucket = "${local.project_name}-dependent-libs"
  tags   = local.default_tags
}
