data "aws_availability_zones" "available" {
  # checkov:skip=CKV_AWS_394:The slice below always takes the first two zones, so a new zone doesn't change the result.
  state = "available"
}

locals {
  azs = slice(data.aws_availability_zones.available.names, 0, 2)
}

# VPC with private subnets for the cluster and a single NAT gateway for image pulls.
module "vpc" {
  # terraform-aws-modules/vpc/aws v6.7.3, pinned to the release commit.
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-vpc.git?ref=b3abd6df2ecf052451a361ed55b8f06f8742a795"

  name = var.cluster_name
  cidr = var.vpc_cidr
  azs  = local.azs

  private_subnets = [for i, _ in local.azs : cidrsubnet(var.vpc_cidr, 4, i)]
  public_subnets  = [for i, _ in local.azs : cidrsubnet(var.vpc_cidr, 8, 48 + i)]

  enable_nat_gateway   = true
  single_nat_gateway   = true
  enable_dns_hostnames = true

  private_subnet_tags = { "kubernetes.io/role/internal-elb" = 1 }
  public_subnet_tags  = { "kubernetes.io/role/elb" = 1 }
}

# Amazon EKS Auto Mode cluster. Auto Mode includes the EKS Pod Identity Agent.
# The module creates an AWS KMS key that encrypts Kubernetes secrets.
module "eks" {
  # terraform-aws-modules/eks/aws v21.29.0, pinned to the release commit.
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-eks.git?ref=91f11ea01656c26b8e6b8eb1b74f19863f60056c"

  name               = var.cluster_name
  kubernetes_version = var.kubernetes_version

  endpoint_public_access       = true
  endpoint_public_access_cidrs = [var.admin_cidr]

  enable_cluster_creator_admin_permissions = true

  compute_config = {
    enabled    = true
    node_pools = ["general-purpose", "system"]
  }

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets
}

# Interface VPC endpoint (AWS PrivateLink) for Amazon Bedrock Runtime.
# Converse and ApplyGuardrail both use this endpoint.
resource "aws_security_group" "bedrock_endpoint" {
  name        = "${var.cluster_name}-bedrock-runtime-endpoint"
  description = "HTTPS from the VPC to the Amazon Bedrock Runtime endpoint"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "HTTPS from inside the VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }
}

resource "aws_vpc_endpoint" "bedrock_runtime" {
  vpc_id              = module.vpc.vpc_id
  service_name        = "com.amazonaws.${var.region}.bedrock-runtime"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = module.vpc.private_subnets
  security_group_ids  = [aws_security_group.bedrock_endpoint.id]
  private_dns_enabled = true
}
