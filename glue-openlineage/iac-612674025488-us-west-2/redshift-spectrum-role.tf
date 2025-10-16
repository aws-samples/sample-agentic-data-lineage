# IAM Role for Redshift Spectrum
resource "aws_iam_role" "redshift_spectrum_role" {
  name = "${local.project_name}-redshift-spectrum-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "redshift.amazonaws.com"
        }
      }
    ]
  })

  tags = local.default_tags
}

# IAM Policy for Redshift Spectrum (Glue and S3 permissions)
resource "aws_iam_role_policy" "redshift_spectrum_policy" {
  name = "${local.project_name}-redshift-spectrum-policy"
  role = aws_iam_role.redshift_spectrum_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "glue:CreateDatabase",
          "glue:DeleteDatabase",
          "glue:GetDatabase",
          "glue:GetDatabases",
          "glue:UpdateDatabase",
          "glue:CreateTable",
          "glue:DeleteTable",
          "glue:BatchDeleteTable",
          "glue:UpdateTable",
          "glue:GetTable",
          "glue:GetTables",
          "glue:BatchCreatePartition",
          "glue:CreatePartition",
          "glue:DeletePartition",
          "glue:BatchDeletePartition",
          "glue:UpdatePartition",
          "glue:GetPartition",
          "glue:GetPartitions",
          "glue:BatchGetPartition"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket",
        ]
        Resource = [
          "${data.terraform_remote_state.rs.outputs.landign_zone_s3_bucket_arn}/*",
          "${data.terraform_remote_state.rs.outputs.landign_zone_s3_bucket_arn}"
        ]
      }
    ]
  })
}

# Associate IAM role to Redshift cluster
resource "aws_redshift_cluster_iam_roles" "redshift_spectrum_role_attachment" {
  cluster_identifier = data.terraform_remote_state.rs.outputs.redshift_cluster_identifier
  iam_role_arns = [
    aws_iam_role.redshift_spectrum_role.arn
  ]
}
