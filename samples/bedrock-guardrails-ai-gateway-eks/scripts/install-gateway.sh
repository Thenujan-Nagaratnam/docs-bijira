#!/usr/bin/env bash
# Installs WSO2 AI Gateway 2026.09.24 on the Amazon EKS cluster created by Terraform.
set -euo pipefail
# shellcheck source=scripts/common.sh
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT
umask 077

echo "Updating kubeconfig for ${CLUSTER_NAME}"
aws eks update-kubeconfig --region "${AWS_REGION}" --name "${CLUSTER_NAME}"

kubectl apply -f k8s/storageclass.yaml
kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

# 1. 256-bit AES key that encrypts gateway secrets at rest. Generated once, kept in Secrets Manager.
KEY_SECRET="${SECRET_PREFIX}/encryption-key"
if ! secret_exists "${KEY_SECRET}"; then
  openssl rand 32 | aws secretsmanager create-secret --name "${KEY_SECRET}" \
    --description "AES-256 key for WSO2 AI Gateway secrets" \
    --secret-binary fileb:///dev/stdin >/dev/null
fi
aws secretsmanager get-secret-value --secret-id "${KEY_SECRET}" --query SecretBinary --output text \
  | base64 -d \
  | kubectl -n "${NAMESPACE}" create secret generic gateway-encryption-keys \
      --from-file=default-aesgcm256-v1.bin=/dev/stdin --dry-run=client -o yaml \
  | kubectl apply -f -

# 2. Admin password for the management API. Only its bcrypt hash reaches Helm.
ADMIN_SECRET="${SECRET_PREFIX}/admin-password"
if ! secret_exists "${ADMIN_SECRET}"; then
  openssl rand -base64 24 | tr -d '\n' | aws secretsmanager create-secret --name "${ADMIN_SECRET}" \
    --description "WSO2 AI Gateway management API admin password" \
    --secret-string file:///dev/stdin >/dev/null
fi
ADMIN_HASH="$(aws secretsmanager get-secret-value --secret-id "${ADMIN_SECRET}" --query SecretString --output text \
  | htpasswd -niBC 10 admin | cut -d: -f2 | tr -d '\n')"
cat > "${TMP_DIR}/admin-values.yaml" <<VALUES
gateway:
  config:
    controller:
      auth:
        basic:
          enabled: true
          users:
            - username: "admin"
              password: "${ADMIN_HASH}"
              password_hashed: true
              roles: ["admin"]
VALUES

# 3. TLS certificate for the gateway listener, issued by a private CA for this walkthrough.
mkdir -p certs
if [ ! -f certs/gateway-ca.crt ]; then
  openssl req -x509 -newkey rsa:3072 -sha256 -days 30 -nodes \
    -keyout "${TMP_DIR}/ca.key" -out certs/gateway-ca.crt -subj "/CN=ai-gateway-walkthrough-ca" 2>/dev/null
  openssl req -newkey rsa:3072 -sha256 -nodes -keyout "${TMP_DIR}/tls.key" -out "${TMP_DIR}/tls.csr" \
    -subj "/CN=localhost" 2>/dev/null
  printf 'subjectAltName=DNS:localhost,DNS:%s-gateway-runtime.%s.svc,DNS:%s-gateway-runtime.%s.svc.cluster.local\n' \
    "${RELEASE}" "${NAMESPACE}" "${RELEASE}" "${NAMESPACE}" > "${TMP_DIR}/san.ext"
  openssl x509 -req -in "${TMP_DIR}/tls.csr" -CA certs/gateway-ca.crt -CAkey "${TMP_DIR}/ca.key" \
    -CAcreateserial -days 30 -sha256 -extfile "${TMP_DIR}/san.ext" -out "${TMP_DIR}/tls.crt" 2>/dev/null
  kubectl -n "${NAMESPACE}" create secret tls gateway-tls \
    --cert="${TMP_DIR}/tls.crt" --key="${TMP_DIR}/tls.key" --dry-run=client -o yaml | kubectl apply -f -
fi

# 4. Install the public Helm chart.
envsubst "${SUBST_VARS}" < helm/values.yaml > "${TMP_DIR}/values.yaml"
helm upgrade --install "${RELEASE}" "${CHART}" --version "${CHART_VERSION}" \
  --namespace "${NAMESPACE}" \
  --values "${TMP_DIR}/values.yaml" \
  --values "${TMP_DIR}/admin-values.yaml" \
  --wait --timeout 15m

kubectl get pods -n "${NAMESPACE}"
