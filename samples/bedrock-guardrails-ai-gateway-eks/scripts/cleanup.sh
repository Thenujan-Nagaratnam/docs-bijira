#!/usr/bin/env bash
# Removes the gateway, its Amazon EBS volume, and the walkthrough's secrets.
# Run this before `terraform destroy`.
set -euo pipefail
# shellcheck source=scripts/common.sh
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

aws eks update-kubeconfig --region "${AWS_REGION}" --name "${CLUSTER_NAME}" >/dev/null

helm uninstall "${RELEASE}" --namespace "${NAMESPACE}" --wait 2>/dev/null || true
kubectl delete namespace "${NAMESPACE}" --ignore-not-found --wait=true

# Wait until EKS Auto Mode has deleted the controller's EBS volume.
for _ in $(seq 1 30); do
  remaining="$(kubectl get pv -o jsonpath='{.items[?(@.spec.storageClassName=="auto-ebs-sc")].metadata.name}')"
  [ -z "${remaining}" ] && break
  sleep 10
done
kubectl delete -f k8s/storageclass.yaml --ignore-not-found

for secret in $(aws secretsmanager list-secrets --filters Key=name,Values="${SECRET_PREFIX}" \
    --query 'SecretList[].Name' --output text); do
  aws secretsmanager delete-secret --secret-id "${secret}" --force-delete-without-recovery >/dev/null
  echo "Deleted secret ${secret}"
done

rm -rf certs
echo "Done. Now run terraform destroy."
