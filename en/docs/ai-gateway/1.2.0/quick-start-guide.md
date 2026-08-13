---
title: "AI Gateway Quick Start Guide"
description: "Run API Platform AI Gateway with Docker, deploy an LLM provider and an LLM proxy, route your first LLM request, and govern the gateway from AI Workspace."
canonical_url: https://wso2.com/api-platform/docs/ai-gateway/quick-start-guide/
md_url: https://wso2.com/api-platform/docs/ai-gateway/quick-start-guide.md
tags:
  - ai-gateway
  - llm
  - mcp
  - quickstart
  - docker
author: WSO2 API Platform Documentation Team
last_updated: 2026-08-13
content_type: "quickstart"
---

# Quick Start Guide

This guide takes you from a downloaded distribution to an LLM request routed through the API Platform AI Gateway, then shows you how to govern that gateway from [AI Workspace](../../ai-workspace/1.0.0/overview.md), the control plane for AI traffic. It's written for platform administrators and AI developers.

!!! info "Watch the video walkthrough"
    [Check out this quick start on YouTube](https://youtu.be/p5xBXZWt5GU?rel=0) or watch below.

<iframe 
  width="100%" 
  src="https://www.youtube.com/embed/p5xBXZWt5GU?rel=0" 
  title="YouTube video player" 
  style="border: 0; display: block; aspect-ratio: 16 / 9;" 
  loading="lazy" 
  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" 
  allowfullscreen>
</iframe>

## Prerequisites

A Docker-compatible container runtime such as:

- Docker Desktop (Windows / macOS)
- Rancher Desktop (Windows / macOS)
- Colima (macOS)
- Docker Engine + Compose plugin (Linux)

These examples use `docker compose`. If you use another Compose-compatible runtime, use the equivalent commands.

Ensure `docker` and `docker compose` commands are available:

```bash
docker --version
docker compose version
```

This guide uses OpenAI as the upstream LLM provider. To call the OpenAI API through the 
gateway, you also need an OpenAI API key.

## Set up the Gateway

The commands below use version `1.2.0`. Substitute the API Platform AI Gateway release version you want to run in the download URL, the archive name, and the directory name.

### Step 1: Download the Gateway

Run this command in your terminal to download the AI Gateway distribution:

``` bash
wget https://github.com/wso2/api-platform/releases/download/ai-gateway/v1.2.0/wso2apip-ai-gateway-1.2.0.zip
```

Then extract the content:

```bash
unzip wso2apip-ai-gateway-1.2.0.zip
```

Go inside the root directory of the Gateway distribution folder:

```bash
cd wso2apip-ai-gateway-1.2.0/
```

### Step 2: Run the setup script

Run the following script for a one-time setup.

```bash
./scripts/setup.sh
```

This provisions the following:

* AES-256 at-rest encryption key
* The router HTTPS listener certificate
* The `api-platform.env` file
* The gateway-controller admin credentials 

The script prints the admin password once — copy it.

### Step 3: Export admin credentials

Export the admin credentials so the management-API calls below can authenticate. 
The username defaults to `admin`. Use the password the setup script `setup.sh` printed 
in the preceding step.

```bash
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD='<the password scripts/setup.sh printed>'
```

### Step 4: Start the Gateway  

Start the complete gateway stack using Docker Compose:

```bash
docker compose up -d
```

### Step 5: Verify the Gateway

Verify that the Gateway Controller is healthy::

```bash
curl http://localhost:9094/api/admin/v1/health
```

A successful response confirms the gateway is running and ready to accept API configurations.

!!! note "Running on Windows"
    The commands above assume a Linux/macOS shell. On Windows, run the one-time setup with the PowerShell script instead — it takes the same flags and provisions the same files:

    ```powershell
    powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
    ```

    Then set the admin credentials with `$env:ADMIN_USERNAME='admin'` and `$env:ADMIN_PASSWORD='<the password setup.ps1 printed>'` in place of the `export` lines.

    The remaining `curl` commands on this page pipe their YAML payload in through a shell heredoc (`--data-binary @- <<'EOF'`), which PowerShell does not support. Either run them from Git Bash or WSL, or save the YAML between `EOF` markers to a file and post that file explicitly — note the `.exe`, since `curl` is an alias for `Invoke-WebRequest` in Windows PowerShell:

    ```powershell
    curl.exe -X POST http://localhost:9090/api/management/v1/llm-providers `
      -H "Content-Type: application/yaml" `
      -u "${env:ADMIN_USERNAME}:${env:ADMIN_PASSWORD}" `
      --data-binary "@openai-provider.yaml"
    ```

!!! tip "Customizing configuration"
    The setup script (`setup.sh`, or `setup.ps1` on Windows) writes `api-platform.env`, which is loaded into the containers via Docker Compose `env_file`. To change the storage backend, connect to a control plane, or tune other settings, edit that file (or the `config.toml` interpolation tokens directly). See [Gateway Configuration and Environment Interpolation](./setup/configuration.md).

## Deploy an LLM Provider

### Step 1: Deploy an OpenAI LLM provider configuration

The API Platform Gateway includes first-class support for the OpenAI LLM provider. As a platform administrator, replace `<openai-apikey>` with your OpenAI API key and run the following command to deploy a sample OpenAI LLM provider.

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

### Step 2: Invoke the API 

To test LLM provider traffic routing through the gateway, invoke the following request.

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

## Govern this gateway from AI Workspace

The gateway you just started serves traffic on its own, and it doesn't have to run alone. [AI Workspace](../../ai-workspace/1.0.0/overview.md) is the control plane for AI traffic across your organization: one console for LLM providers, App LLM proxies, MCP proxies, policies such as guardrails and token-based rate limits, and the credentials behind them. Register this gateway with AI Workspace to govern every AI gateway you run from a single place, across every environment.

Both directions work, and you can use them together:

- **Top-down.** Configure an artifact in AI Workspace, apply policies to it, then deploy it to one or more gateways.
- **Bottom-up.** Keep deploying artifacts to the gateway through the management API, as this guide does. Every artifact you create on the gateway syncs up to AI Workspace automatically. Each one appears there as a copy the gateway owns, so the OpenAI provider and the `openai-assistant` proxy from this guide show up without being re-declared. To see what a synced artifact looks like, and what stays editable, see [Manage Gateway-deployed AI artifacts in AI Workspace](../../ai-workspace/1.0.0/sync-gateway-created-artifacts.md).

The gateway keeps serving traffic either way. If AI Workspace is unreachable, the gateway carries on and the sync catches up once the connection is restored.

## Stopping the Gateway

When stopping the gateway, you have two options:

### Keep data and configurations 

This option stops the runtime while keeping data: APIs and configurations are persisted:

```bash
docker compose down
```

This stops the containers but preserves the `controller-data` volume. When you restart with `docker compose up`, all your API configurations will be restored.

### Delete data for a fresh start

This option performs a complete shutdown with data cleanup (fresh start):

```bash
docker compose down -v
```

This stops containers and removes the `controller-data` volume. Next startup will be a clean slate with no persisted APIs or configuration.

## Next steps

- Route to more than one provider, with failover: [Multi-provider routing](./llm-proxy/multi-provider-routing.md)
- Add guardrails to a proxy, such as [PII masking](./llm-proxy/guardrails/pii-masking-regex.md) or a [JSON schema guardrail](./llm-proxy/guardrails/json-schema.md)
- Expose an MCP server through the gateway: [MCP proxy quick start guide](./mcp-proxy/quick-start-guide.md)
- Govern AI traffic across all your gateways from the control plane: [AI Workspace overview](../../ai-workspace/1.0.0/overview.md)
- Take this gateway to production on Kubernetes: [Production deployment overview](./deployment/production-deployment/overview.md)
- Register a production gateway with the control plane: [Connect to AI Workspace](./deployment/production-deployment/control-plane-connection.md)
