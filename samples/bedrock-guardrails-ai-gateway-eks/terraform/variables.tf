variable "region" {
  description = "AWS Region for every resource. Amazon Bedrock, Amazon Bedrock Guardrails, and Amazon EKS Auto Mode must be available in it."
  type        = string
}

variable "model_id" {
  description = "Amazon Bedrock foundation model ID that the gateway may invoke, for example amazon.nova-lite-v1:0."
  type        = string
}

variable "admin_cidr" {
  description = "CIDR block allowed to reach the public Amazon EKS API endpoint, for example your workstation's IP address with /32."
  type        = string
}

variable "cluster_name" {
  description = "Name of the Amazon EKS cluster and prefix for related resources."
  type        = string
  default     = "ai-gateway-guardrails"
}

variable "kubernetes_version" {
  description = "Kubernetes version for the Amazon EKS cluster."
  type        = string
  default     = "1.35"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}
