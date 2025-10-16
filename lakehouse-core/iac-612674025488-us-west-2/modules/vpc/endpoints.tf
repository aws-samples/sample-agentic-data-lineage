# S3 VPC Endpoint (Gateway)
resource "aws_vpc_endpoint" "s3" {
  count = var.enable_s3_endpoint ? 1 : 0

  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.private.id]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = concat([
      {
        Effect    = "Allow"
        Principal = "*"
        Action = [
          "s3:GetObject"
        ]
        Resource = [
          "arn:aws:s3:::prod-${var.region}-starport-layer-bucket/*"
        ]
      }
      ], length(var.s3_bucket_arns) > 0 ? [
      {
        Effect    = "Allow"
        Principal = "*"
        Action = [
          "s3:*"
        ]
        Resource = flatten([
          var.s3_bucket_arns,
          [for arn in var.s3_bucket_arns : "${arn}/*"]
        ])
      }
    ] : [])
  })

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-s3-endpoint"
  })
}

# ECR API VPC Endpoint (Interface)
resource "aws_vpc_endpoint" "ecr_api" {
  count = var.enable_ecr_endpoint ? 1 : 0

  vpc_id             = aws_vpc.main.id
  service_name       = "com.amazonaws.${var.region}.ecr.api"
  vpc_endpoint_type  = "Interface"
  subnet_ids         = aws_subnet.private[*].id
  security_group_ids = [aws_security_group.vpc_endpoints[0].id]

  private_dns_enabled = true

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-ecr-api-endpoint"
  })
}

# ECR DKR VPC Endpoint (Interface)
resource "aws_vpc_endpoint" "ecr_dkr" {
  count = var.enable_ecr_endpoint ? 1 : 0

  vpc_id             = aws_vpc.main.id
  service_name       = "com.amazonaws.${var.region}.ecr.dkr"
  vpc_endpoint_type  = "Interface"
  subnet_ids         = aws_subnet.private[*].id
  security_group_ids = [aws_security_group.vpc_endpoints[0].id]

  private_dns_enabled = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect    = "Allow"
        Principal = "*"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = "*"
      }
    ]
  })

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-ecr-dkr-endpoint"
  })
}

# EC2 VPC Endpoint (Interface) - Required for EBS CSI Driver
# resource "aws_vpc_endpoint" "ec2" {
#   count = var.enable_ecr_endpoint ? 1 : 0

#   vpc_id             = aws_vpc.main.id
#   service_name       = "com.amazonaws.${var.region}.ec2"
#   vpc_endpoint_type  = "Interface"
#   subnet_ids         = aws_subnet.private[*].id
#   security_group_ids = [aws_security_group.vpc_endpoints[0].id]

#   private_dns_enabled = true

#   tags = merge(var.tags, {
#     Name = "${var.name_prefix}-ec2-endpoint"
#   })
# }

# Security Group for VPC Endpoints
resource "aws_security_group" "vpc_endpoints" {
  count = var.enable_ecr_endpoint ? 1 : 0

  name_prefix = "${var.name_prefix}-vpc-endpoints-"
  vpc_id      = aws_vpc.main.id
  description = "Security group for VPC endpoints"

  ingress {
    description = "HTTPS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block]
  }

  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.tags, {
    Name = "${var.name_prefix}-vpc-endpoints-sg"
  })
}
