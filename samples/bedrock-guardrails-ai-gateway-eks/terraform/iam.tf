# IAM role for the gateway pods. EKS Pod Identity issues temporary credentials
# for it to the ai-gateway service account in the ai-gateway namespace only.
resource "aws_iam_role" "gateway" {
  name = "${var.cluster_name}-gateway-bedrock"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "pods.eks.amazonaws.com" }
      Action    = ["sts:AssumeRole", "sts:TagSession"]
    }]
  })
}

resource "aws_iam_role_policy" "gateway_bedrock" {
  name = "bedrock-converse-and-guardrails"
  role = aws_iam_role.gateway.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ConverseOneModel"
        Effect   = "Allow"
        Action   = "bedrock:InvokeModel"
        Resource = "arn:aws:bedrock:${var.region}::foundation-model/${var.model_id}"
      },
      {
        Sid    = "ApplyApprovedGuardrails"
        Effect = "Allow"
        Action = "bedrock:ApplyGuardrail"
        Resource = [
          aws_bedrock_guardrail.baseline.guardrail_arn,
          aws_bedrock_guardrail.support_assistant.guardrail_arn,
        ]
      }
    ]
  })
}

resource "aws_eks_pod_identity_association" "gateway" {
  cluster_name    = module.eks.cluster_name
  namespace       = "ai-gateway"
  service_account = "ai-gateway"
  role_arn        = aws_iam_role.gateway.arn
}
