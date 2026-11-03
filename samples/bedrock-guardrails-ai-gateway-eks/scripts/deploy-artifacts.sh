#!/usr/bin/env bash
# Deploys the provider and proxies through the management API, and issues one key per application.
# Run `kubectl -n ai-gateway port-forward svc/ai-gateway-controller 9090:9090` first.
set -euo pipefail
# shellcheck source=scripts/common.sh
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

API="http://localhost:9090/api/management/v1"
NETRC_FILE="$(mktemp)"
trap 'rm -f "${NETRC_FILE}"' EXIT
chmod 600 "${NETRC_FILE}"
aws secretsmanager get-secret-value --secret-id "${SECRET_PREFIX}/admin-password" \
  --query SecretString --output text \
  | { read -r pw; printf 'machine localhost login admin password %s\n' "${pw}"; } > "${NETRC_FILE}"

api() {
  curl --fail-with-body -sS --netrc-file "${NETRC_FILE}" "$@"
}

# Creates the artifact, or replaces it if it already exists.
apply_artifact() {
  local kind="$1" name="$2" file="$3"
  local method="POST" url="${API}/${kind}"
  if api -o /dev/null "${API}/${kind}/${name}" 2>/dev/null; then
    method="PUT"
    url="${API}/${kind}/${name}"
  fi
  envsubst "${SUBST_VARS}" < "${file}" \
    | api -o /dev/null -X "${method}" "${url}" -H "Content-Type: application/yaml" --data-binary @-
  echo "Deployed ${kind}/${name}"
}

apply_artifact llm-providers bedrock-provider gateway/bedrock-provider.yaml

for app in ${APPS}; do
  # Provider key that the proxy sends on the internal route, stored as an encrypted gateway secret.
  if ! api -o /dev/null "${API}/secrets/${app}-loopback" 2>/dev/null; then
    loopback_key="$(api -X POST "${API}/llm-providers/bedrock-provider/api-keys" \
      -H "Content-Type: application/json" -d "{\"name\":\"${app}-loopback\"}" | jq -r '.apiKey.apiKey')"
    api -o /dev/null -X POST "${API}/secrets" -H "Content-Type: application/yaml" --data-binary @- <<SECRET
apiVersion: gateway.api-platform.wso2.com/v1
kind: Secret
metadata:
  name: ${app}-loopback
spec:
  displayName: ${app} provider key
  value: "${loopback_key}"
SECRET
    unset loopback_key
  fi

  apply_artifact llm-proxies "${app}" "gateway/${app}-proxy.yaml"

  # Application key, piped straight into Secrets Manager so it never appears in the terminal.
  if ! secret_exists "${SECRET_PREFIX}/apps/${app}"; then
    api -X POST "${API}/llm-proxies/${app}/api-keys" \
      -H "Content-Type: application/json" -d "{\"name\":\"${app}-app\"}" \
      | jq -r '.apiKey.apiKey' \
      | aws secretsmanager create-secret --name "${SECRET_PREFIX}/apps/${app}" \
          --description "Gateway API key for ${app}" \
          --secret-string file:///dev/stdin >/dev/null
    echo "Stored the ${app} key in Secrets Manager as ${SECRET_PREFIX}/apps/${app}"
  fi
done
