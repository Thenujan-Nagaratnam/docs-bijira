---
title: "AI Gateway Quick Start Guide"
description: "Run API Platform AI Gateway with Docker Compose, deploy an LLM provider and an LLM proxy, route your first LLM request, and govern the gateway from AI Workspace."
canonical_url: https://wso2.com/api-platform/docs/ai-gateway/quick-start-guide/
md_url: https://wso2.com/api-platform/docs/ai-gateway/quick-start-guide.md
tags:
  - ai-gateway
  - llm
  - mcp
  - quickstart
  - docker
author: WSO2 API Platform Documentation Team
last_updated: 2026-08-10
content_type: "quickstart"
---

# Quick Start Guide

This guide takes you from a downloaded distribution to a large language model (LLM) request routed through the API Platform AI Gateway. It then shows you how to govern that gateway from [AI Workspace](../../ai-workspace/next/overview.md), the control plane for AI traffic.

## Prerequisites

A Docker-compatible container runtime such as:

- [Docker Desktop](https://docs.docker.com/desktop/) (Windows / macOS)
- [Podman Desktop](https://podman-desktop.io/) or [Podman](https://podman.io/docs/installation) (Windows / macOS / Linux)
- [Rancher Desktop](https://rancherdesktop.io/) (Windows / macOS)
- [Colima](https://github.com/abiosoft/colima) (macOS)
- [Docker Engine](https://docs.docker.com/engine/install/) + [Compose plugin](https://docs.docker.com/compose/install/linux/) (Linux)

These examples use `docker compose`. If you use another Compose-compatible runtime, use the equivalent commands.

Verify the commands for your runtime are available. For Docker:

```bash
docker --version
docker compose version
```

To call an LLM through the gateway, you also need an OpenAI API key.

The **Windows (PowerShell)** examples on this page require PowerShell 7.3 or later.

## Start the gateway

The commands below use version `1.2.0`. Substitute the API Platform AI Gateway release version you want to run in the download URL, the archive name, and the directory name.

=== "Linux / macOS"

    ```bash
    # Download distribution.
    wget https://github.com/wso2/api-platform/releases/download/ai-gateway/v1.2.0-rc/wso2apip-ai-gateway-1.2.0-rc.zip

    # Unzip the downloaded distribution.
    unzip wso2apip-ai-gateway-1.2.0-rc.zip

    cd wso2apip-ai-gateway-1.2.0-rc/

    # Run the one-time setup. This provisions the AES-256 at-rest encryption key, the router HTTPS
    # listener certificate, api-platform.env, and the gateway-controller admin credentials. It prints
    # the admin password once — copy it.
    ./scripts/setup.sh

    # Export the admin credentials so the management-API calls below can authenticate.
    # The username defaults to "admin"; use the password setup.sh just printed.
    export ADMIN_USERNAME=admin
    export ADMIN_PASSWORD='<the password scripts/setup.sh printed>'

    # Start the complete stack
    docker compose up

    # Verify gateway controller admin endpoint is running
    curl http://localhost:9094/api/admin/v1/health
    ```

=== "Windows (PowerShell)"

    ```powershell
    # Download distribution.
    Invoke-WebRequest -Uri https://github.com/wso2/api-platform/releases/download/ai-gateway/v1.2.0-rc/wso2apip-ai-gateway-1.2.0-rc.zip -OutFile wso2apip-ai-gateway-1.2.0-rc.zip

    # Unzip the downloaded distribution.
    Expand-Archive -Path wso2apip-ai-gateway-1.2.0-rc.zip -DestinationPath .

    Set-Location wso2apip-ai-gateway-1.2.0-rc

    # Run the one-time setup. This provisions the AES-256 at-rest encryption key, the router HTTPS
    # listener certificate, api-platform.env, and the gateway-controller admin credentials. It prints
    # the admin password once — copy it.
    powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1

    # Set the admin credentials so the management-API calls below can authenticate.
    # The username defaults to "admin"; use the password setup.ps1 just printed.
    $env:ADMIN_USERNAME='admin'
    $env:ADMIN_PASSWORD='<the password setup.ps1 printed>'

    # Start the complete stack
    docker compose up

    # Verify gateway controller admin endpoint is running
    curl.exe http://localhost:9094/api/admin/v1/health
    ```

    Note the `.exe`, since `curl` is an alias for `Invoke-WebRequest` in Windows PowerShell. PowerShell 7 removes that alias, and `curl.exe` works in both versions.

    The remaining `curl` commands on this page pipe their YAML payload in through a shell heredoc (`--data-binary @- <<'EOF'`), which PowerShell does not support. Either run them from Git Bash or WSL, or use the **Windows (PowerShell)** tab on each command below, which saves the YAML to a file and posts that file explicitly.

!!! tip "Port 8080, 8443, 9090, or 9094 already taken?"
    If the start command fails with a port binding error, identify what is already listening on the default ports:

    On macOS or Linux, run:

    ```bash
    lsof -nP -iTCP:8080 -sTCP:LISTEN
    lsof -nP -iTCP:8443 -sTCP:LISTEN
    lsof -nP -iTCP:9090 -sTCP:LISTEN
    lsof -nP -iTCP:9094 -sTCP:LISTEN
    ```

    On Windows PowerShell, run:

    ```powershell
    Get-NetTCPConnection -State Listen -LocalPort 8080,8443,9090,9094 | Select-Object LocalAddress, LocalPort, OwningProcess
    ```

    Stop the conflicting service if you don't need it. If you need to keep it running, change the host-side value of the relevant `ports:` mapping in `docker-compose.yaml`. Then use the remapped host port in the verification and test commands on this page.

!!! tip "Customizing configuration"
    The setup script (`setup.sh`, or `setup.ps1` on Windows) writes `api-platform.env`, which is loaded into the containers via Docker Compose `env_file`. To change the storage backend, connect to a control plane, or tune other settings, edit that file (or the `config.toml` interpolation tokens directly). See [Gateway Configuration and Environment Interpolation](./setup/configuration.md).

## Deploy an OpenAI LLM provider configuration

The API Platform Gateway includes first-class support for the OpenAI LLM provider. As a platform administrator, replace `<openai-apikey>` with your OpenAI API key and run the following command to deploy a sample OpenAI LLM provider.

=== "Linux / macOS"

    ```bash
    curl -X POST http://localhost:9090/api/management/v1/llm-providers \
      -H "Content-Type: application/yaml" \
      -u "$ADMIN_USERNAME:$ADMIN_PASSWORD" \
      --data-binary @- <<'EOF'
    apiVersion: gateway.api-platform.wso2.com/v1
    kind: LlmProvider
    metadata:
      name: openai-provider
    spec:
      displayName: OpenAI Provider
      version: v1.0
      template: openai
      context: /openai/latest
      upstream:
        url: https://api.openai.com/v1
        auth:
          type: api-key
          header: Authorization
          value: <openai-apikey>
      accessControl:
        mode: deny_all
        exceptions:
          - path: /chat/completions
            methods: [POST]
          - path: /models
            methods: [GET]
          - path: /models/{modelId}
            methods: [GET]
    EOF
    ```

=== "Windows (PowerShell)"

    Save the provider definition to `openai-provider.yaml`:

    ```powershell
    @'
    apiVersion: gateway.api-platform.wso2.com/v1
    kind: LlmProvider
    metadata:
      name: openai-provider
    spec:
      displayName: OpenAI Provider
      version: v1.0
      template: openai
      context: /openai/latest
      upstream:
        url: https://api.openai.com/v1
        auth:
          type: api-key
          header: Authorization
          value: <openai-apikey>
      accessControl:
        mode: deny_all
        exceptions:
          - path: /chat/completions
            methods: [POST]
          - path: /models
            methods: [GET]
          - path: /models/{modelId}
            methods: [GET]
    '@ | Set-Content -Path openai-provider.yaml -Encoding utf8
    ```

    Then post it:

    ```powershell
    curl.exe -X POST http://localhost:9090/api/management/v1/llm-providers `
      -H "Content-Type: application/yaml" `
      -u "${env:ADMIN_USERNAME}:${env:ADMIN_PASSWORD}" `
      --data-binary "@openai-provider.yaml"
    ```

To test LLM provider traffic routing through the gateway, invoke the following request.

=== "Linux / macOS"

    ```bash
    curl -X POST https://localhost:8443/openai/latest/chat/completions \
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
    curl.exe -X POST https://localhost:8443/openai/latest/chat/completions `
      -H "Content-Type: application/json" `
      -d '{"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Hi"}]}' -k
    ```

## Deploy an LLM proxy configuration to consume an LLM provider

The API Platform Gateway provides first-class support for configuring and deploying LLM proxies. As an AI developer, run the following command to deploy a sample LLM proxy that consumes the OpenAI LLM provider the platform administrator deployed above.

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

To test LLM proxy traffic routing through the gateway and consume the LLM provider, invoke the following request.

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

## Govern this gateway from AI Workspace

The gateway you just started serves traffic on its own. [AI Workspace](../../ai-workspace/next/overview.md) is the control plane for AI traffic across your organization. One console manages LLM providers, App LLM proxies, MCP proxies, policies such as guardrails and token-based rate limits, and the credentials behind them. Register this gateway with AI Workspace to govern every AI gateway you run from one place, across every environment.

Both directions work, and you can use them together:

- **Top-down.** Configure an artifact in AI Workspace, apply policies to it, then deploy it to one or more gateways.
- **Bottom-up.** Keep deploying through the management API, as this guide does. The gateway syncs every artifact you create to AI Workspace automatically, where each one appears as a copy the gateway owns. The OpenAI provider and the `openai-assistant` proxy from this guide appear there without being re-declared. To see what a synced artifact looks like, and what stays editable, see [Manage Gateway-deployed AI artifacts in AI Workspace](../../ai-workspace/next/sync-gateway-created-artifacts.md).

The gateway keeps serving traffic either way. If AI Workspace is unreachable, the gateway carries on and the sync catches up once the connection is restored.

## Stopping the gateway

When stopping the gateway, you have two options:

**Option 1: Stop runtime, keep data (persisted proxies and configuration)**

```bash
docker compose down
```

This stops the containers but preserves the `controller-data` volume. When you restart with `docker compose up`, all your configurations are restored.

**Option 2: Complete shutdown with data cleanup (fresh start)**

```bash
docker compose down -v
```

This stops the containers and removes the `controller-data` volume. The next startup is a clean slate with no persisted templates or provider configuration.

## Next steps

- Route to more than one provider, with failover: [Multi-provider routing](./llm-proxy/multi-provider-routing.md)
- Add guardrails to a proxy, such as [PII masking](./llm-proxy/guardrails/pii-masking-regex.md) or a [JSON schema guardrail](./llm-proxy/guardrails/json-schema.md)
- Expose an MCP server through the gateway: [MCP proxy quick start guide](./mcp-proxy/quick-start-guide.md)
- Govern AI traffic across all your gateways from the control plane: [AI Workspace overview](../../ai-workspace/next/overview.md)
- Take this gateway to production on Kubernetes: [Production deployment overview](./deployment/production-deployment/overview.md)
- Register a production gateway with the control plane: [Connect to AI Workspace](./deployment/production-deployment/control-plane-connection.md)
