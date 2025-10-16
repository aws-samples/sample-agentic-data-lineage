# resource "aws_security_group" "ssh_sg" {
#   name        = "${local.deployment_name}-bastion-sg"
#   description = "Allow SSH inbound traffic for bastion host"
#   vpc_id      = module.vpc.vpc_id

#   # SSH from allowed external IP ranges
#   ingress {
#     description = "SSH from allowed IP ranges"
#     from_port   = 22
#     to_port     = 22
#     protocol    = "tcp"
#     cidr_blocks = [
#       "104.153.113.16/28",
#       "15.248.80.128/25",
#       "205.251.233.104/29",
#       "205.251.233.176/29",
#       "205.251.233.232/29",
#       "205.251.233.48/29",
#       "52.46.249.224/29",
#       "52.46.249.248/29"
#     ]
#   }

#   # Allow SSH from EKS nodes (private subnets)
#   ingress {
#     description = "SSH from EKS nodes"
#     from_port   = 22
#     to_port     = 22
#     protocol    = "tcp"
#     cidr_blocks = [
#       "10.0.10.0/24", # Private subnet 1
#       "10.0.11.0/24"  # Private subnet 2
#     ]
#   }

#   # Allow ICMP from VPC for connectivity testing
#   ingress {
#     description = "ICMP from VPC"
#     from_port   = -1
#     to_port     = -1
#     protocol    = "icmp"
#     cidr_blocks = ["10.0.0.0/16"]
#   }

#   # Allow common ports from EKS nodes for services
#   ingress {
#     description = "HTTP from EKS nodes"
#     from_port   = 80
#     to_port     = 80
#     protocol    = "tcp"
#     cidr_blocks = [
#       "10.0.10.0/24",
#       "10.0.11.0/24"
#     ]
#   }

#   ingress {
#     description = "HTTPS from EKS nodes"
#     from_port   = 443
#     to_port     = 443
#     protocol    = "tcp"
#     cidr_blocks = [
#       "10.0.10.0/24",
#       "10.0.11.0/24"
#     ]
#   }

#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }

#   tags = merge(local.default_tags, {
#     Name = "${local.deployment_name}-bastion-sg"
#   })
# }

# resource "aws_instance" "bastion" {
#   ami                    = "ami-01102c5e8ab69fb75"
#   instance_type          = "t3.small"
#   key_name               = "bastion"
#   subnet_id              = module.vpc.public_subnet_ids[0]
#   vpc_security_group_ids = [aws_security_group.ssh_sg.id]

#   tags = merge(local.default_tags, {
#     Name = "${local.deployment_name}-bastion"
#   })
# }
