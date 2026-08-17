---
title: "Create and configure an LLM proxy"
description: "Create an LLM proxy on the AI Gateway: give it a URL context, name the LLM provider it consumes, deploy it with the management API, and route a request through it."
canonical_url: https://wso2.com/api-platform/docs/ai-gateway/llm-proxy/create-and-configure-an-llm-proxy/
md_url: https://wso2.com/api-platform/docs/ai-gateway/llm-proxy/create-and-configure-an-llm-proxy.md
tags:
  - ai-gateway
  - llm-proxy
  - llm
author: WSO2 API Platform Documentation Team
last_updated: 2026-08-17
content_type: "how-to"
---

# Create and configure an LLM proxy

An LLM Proxy is a custom API endpoint that consumes an LLM provider. It gets its own URL context, such as `/assistant`, carries its own policies for the one application it serves, and inherits the access control, budgeting, and organization-wide policies the administrator set on the provider. This page takes you through deploying one and routing a request through it.

This page is for AI developers, who own LLM proxies.

## Prerequisites

- A running AI Gateway, with `ADMIN_USERNAME` and `ADMIN_PASSWORD` exported in the shell you run these commands from. See [Install the gateway](../setup-and-deployment/install-the-gateway.md).
- A deployed LLM provider on that gateway. A proxy names the provider it consumes in `provider.id`, and the gateway rejects a proxy that names one it can't find. See [Create and configure an LLM provider](../llm-provider/create-and-configure-an-llm-provider.md).

## Configure the proxy

The definition below deploys a proxy that consumes the `openai-provider` provider. Set `provider.id` to the `metadata.name` of a provider already deployed on your gateway — a value that doesn't match a deployed provider is the most common reason this request fails.

=== "Linux / macOS"

    ```bash
    curl -X POST http://localhost:9090/api/management/v1/llm-proxies \
      -H "Content-Type: application/yaml" \
      -u "$ADMIN_USERNAME:$ADMIN_PASSWORD" \
      --data-binary @- <<'EOF'
    apiVersion: gateway.api-platform.wso2.com/v1
    kind: LlmProxy
    metadata:
      name: openai-assistant
    spec:
      displayName: OpenAI Assistant
      version: v1.0
      context: /assistant
      provider:
        id: openai-provider
      policies: []
    EOF
    ```

=== "Windows (PowerShell)"

    Save the proxy definition to `openai-assistant.yaml`:

    ```powershell
    @'
    apiVersion: gateway.api-platform.wso2.com/v1
    kind: LlmProxy
    metadata:
      name: openai-assistant
    spec:
      displayName: OpenAI Assistant
      version: v1.0
      context: /assistant
      provider:
        id: openai-provider
      policies: []
    '@ | Set-Content -Path openai-assistant.yaml -Encoding utf8
    ```

    Then post it:

    ```powershell
    curl.exe -X POST http://localhost:9090/api/management/v1/llm-proxies `
      -H "Content-Type: application/yaml" `
      -u "${env:ADMIN_USERNAME}:${env:ADMIN_PASSWORD}" `
      --data-binary "@openai-assistant.yaml"
    ```

Three values shape the proxy:

- **`context`** — the URL prefix clients call, independent of the provider's own context. This proxy answers under `/assistant`.
- **`provider.id`** — the provider this proxy consumes, named by its `metadata.name`.
- **`policies`** — the policies that apply to this proxy alone. An empty list deploys the proxy with none of its own; the provider's policies still apply.

## Test the proxy

Send a chat completion request to the proxy's context on the gateway:

=== "Linux / macOS"

    ```bash
    curl -X POST "https://localhost:8443/assistant/chat/completions" \
      -H "Content-Type: application/json" \
      -d '{
        "model": "gpt-4o-mini",
        "messages": [
          {
            "role": "user",
            "content": "Hi"
          }
        ]
      }' -k
    ```

=== "Windows (PowerShell)"

    ```powershell
    curl.exe -X POST https://localhost:8443/assistant/chat/completions `
      -H "Content-Type: application/json" `
      -d '{"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Hi"}]}' -k
    ```

The `-k` flag tells `curl` to skip Transport Layer Security (TLS) certificate verification. The router presents the self-signed listener certificate that `setup.sh` or `setup.ps1` generates, and no certificate authority trusts it. Outside local testing, give the router a certificate from a trusted certificate authority and remove `-k`.

## Next steps

- Protect the proxy, which is the client-facing endpoint: [Authenticate clients](../access-control/authenticate-clients.md)
- Send requests on one proxy to more than one provider: [Route across multiple providers](multi-provider-routing.md)
- Return responses chunk by chunk: [Stream responses](streaming-responses.md)
