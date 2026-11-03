output "region" {
  value = var.region
}

output "model_id" {
  value = var.model_id
}

output "cluster_name" {
  value = module.eks.cluster_name
}

output "baseline_guardrail_id" {
  value = aws_bedrock_guardrail.baseline.guardrail_id
}

output "baseline_guardrail_version" {
  value = aws_bedrock_guardrail_version.baseline.version
}

output "support_guardrail_id" {
  value = aws_bedrock_guardrail.support_assistant.guardrail_id
}

output "support_guardrail_version" {
  value = aws_bedrock_guardrail_version.support_assistant.version
}
