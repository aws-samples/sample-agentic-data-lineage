resource "aws_security_group" "glue_sg" {
  name        = "glue-sg"
  description = "Security group for AWS Glue job"
  vpc_id      = data.terraform_remote_state.rs.outputs.vpc_id

  # Self-referencing rule required by AWS Glue
  ingress {
    from_port = 0
    to_port   = 65535
    protocol  = "tcp"
    self      = true
  }

  egress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Glue Connection for VPC access
resource "aws_glue_connection" "vpc_connection" {
  name            = "${local.project_name}-vpc-connection"
  connection_type = "NETWORK"

  # AWS Glue uses VPC endpoints to access Amazon S3 through private IP addresses, without needing to specify S3 URLs in connection properties.

  physical_connection_requirements {
    availability_zone      = "us-west-2a"
    security_group_id_list = [aws_security_group.glue_sg.id]
    subnet_id              = data.terraform_remote_state.rs.outputs.private_subnet_ids[0]
  }

  tags = local.default_tags
}
