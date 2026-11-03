#!/usr/bin/env bash
# Shared settings for the scripts. Reads the Terraform outputs into environment variables.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

tf_output() {
  terraform -chdir="${ROOT_DIR}/terraform" output -raw "$1"
}

AWS_REGION="$(tf_output region)"
CLUSTER_NAME="$(tf_output cluster_name)"
BEDROCK_MODEL_ID="$(tf_output model_id)"
BASELINE_GUARDRAIL_ID="$(tf_output baseline_guardrail_id)"
BASELINE_GUARDRAIL_VERSION="$(tf_output baseline_guardrail_version)"
SUPPORT_GUARDRAIL_ID="$(tf_output support_guardrail_id)"
SUPPORT_GUARDRAIL_VERSION="$(tf_output support_guardrail_version)"
export AWS_REGION CLUSTER_NAME BEDROCK_MODEL_ID \
  BASELINE_GUARDRAIL_ID BASELINE_GUARDRAIL_VERSION \
  SUPPORT_GUARDRAIL_ID SUPPORT_GUARDRAIL_VERSION
export AWS_DEFAULT_REGION="${AWS_REGION}"

# Names used across the scripts.
export NAMESPACE="ai-gateway"
export RELEASE="ai-gateway"
export CHART="oci://ghcr.io/wso2/api-platform/helm-charts/gateway"
export CHART_VERSION="2026.09.24"
export SECRET_PREFIX="wso2-ai-gateway"
export APPS="support-assistant employee-assistant"

# Only these variables are substituted, so JSONPath expressions such as $.messages stay intact.
# shellcheck disable=SC2016 # Single quotes are intentional: envsubst expands these names.
export SUBST_VARS='${AWS_REGION} ${BASELINE_GUARDRAIL_ID} ${BASELINE_GUARDRAIL_VERSION} ${SUPPORT_GUARDRAIL_ID} ${SUPPORT_GUARDRAIL_VERSION}'

secret_exists() {
  aws secretsmanager describe-secret --secret-id "$1" >/dev/null 2>&1
}
