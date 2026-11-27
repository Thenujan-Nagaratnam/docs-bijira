---
title: "Configure OpenAI Codex CLI with AI Gateway"
description: "Route OpenAI Codex CLI requests through the AI Gateway using an OpenAI LLM service provider to apply guardrails and rate limiting."
canonical_url: https://wso2.com/api-platform/docs/guides/ai-and-mcp/ai-coding-assistants/codex-configuration-with-ai-gateway/
md_url: https://wso2.com/api-platform/docs/guides/ai-and-mcp/ai-coding-assistants/codex-configuration-with-ai-gateway.md
tags:
  - guides
  - ai-and-mcp
  - ai-coding-assistants
  - codex-cli
author: Choreo API Platform Documentation Team
last_updated: 2026-11-26
content_type: "how-to"
---

# Configuring OpenAI Codex CLI with AI Gateway

This guide explains how to configure OpenAI Codex CLI to send requests through Choreo API Platform using an AI Gateway and an OpenAI LLM service provider.

By routing requests through Choreo API Platform instead of invoking OpenAI directly, you can apply security, traffic control, and governance policies such as guardrails and rate limiting. The Gateway acts as an intermediary, forwarding requests from Codex CLI to OpenAI while enforcing these controls.

---

## Prerequisites

Before you begin, make sure you have:

- [OpenAI Codex CLI](https://developers.openai.com/codex/cli) installed
- An [OpenAI API key](https://platform.openai.com/api-keys)
- An agent control plane account. [Sign up for free](https://console.cloud.choreolabs.com/agent-management/)
- Docker and Docker Compose, to run the self-hosted gateway

---

## Step 1: Start an AI Gateway on the agent control plane

!!! note
    If an AI Gateway is already created and active, continue to Step 2.

If an AI Gateway is not already created, follow these steps:

1. In the left navigation menu, under **Infrastructure**, select **Gateways**.
2. Select **Add gateway**.
3. Enter the following values:

    | Field | Value |
    |---|---|
    | **Display Name** | My AI Gateway |
    | **Name** | `my-ai-gateway` |
    | **Environment** | Select your environment. |
    | **Public URL** | `https://localhost:8443` |

4. Select **Create**.

After you select **Create**, the console shows a **Set up My AI Gateway** panel with four steps for the **Docker** tab. Run them on the machine that hosts the gateway:

1. Download and unzip the gateway package with the command that the panel shows.
2. Open the unzipped directory, and run `./scripts/setup.sh`. The script creates the listener certificate, the at-rest encryption key, and the `api-platform.env` file. It prints the admin password once, so copy it.
3. Select **Copy** next to the third step, and run the command. It appends the control plane host and your gateway token to `api-platform.env`.
4. Start the gateway with `docker compose up`.

!!! warning
    The console shows the gateway token only once, when you create the gateway. Run the command in step 3 before you close the panel.

!!! note
    If a default gateway port is already in use on your machine, edit the port mappings in the `docker-compose.yaml` file before you start the gateway, and use the same host port in the **Public URL**.

**Expected result:** The **Gateways** page shows your gateway with the **Active** and **Self-hosted** labels.

The following image shows the **Gateways** page with the active self-hosted gateway:

![Gateways page listing My AI Gateway as a self-hosted egress gateway with the Active status](../../../assets/img/guides/ai-and-mcp/agent-control-plane/gateways-list-active.png){.cInlineImage-full}

Once the AI Gateway is active, you can continue to create the OpenAI LLM service provider.

---

## Step 2: Create and Deploy an OpenAI LLM Service Provider

1. In the left navigation menu, under **Resources**, select **LLM service providers**.
2. Select **Add service provider**.
3. Under **Basic Details**, enter the following values:

    | Field | Value |
    |---|---|
    | **Name** | OpenAI Codex |
    | **Version** | v1.0 |
    | **Context path** | `/codexcli` |

    !!! note
        The Console builds the provider ID from the name, so each provider in an organization needs a different name. If you already created a provider named `OpenAI`, use another name, such as `OpenAI Codex`.

4. Under **Provider Template**, select **OpenAI**.
5. Under **Runtime Configuration**, paste your OpenAI API key in **API key / Credential**.
6. Under **Deployment Configuration**, select the environment that your gateway belongs to. Open the gateway list that appears, and select **My AI Gateway**. The list defaults to the managed gateway, so change it.
7. Select **Add provider**.

**Expected result:** The provider page opens. The **Deployment** tab shows **My AI Gateway** with the **Deployed** status.

---

## Step 3: Generate an API Key for Codex CLI

Codex CLI needs an API key from Choreo API Platform to invoke the deployed OpenAI LLM service provider.

1. On the provider page, open the **API Keys** tab.
2. Select **Create API key**.
3. Enter a **Display name**, and select **Create**.
4. Copy and save the generated API key. The console shows it only once.

    This is the API key that must be provided to Codex CLI using the `API-Key` custom header.

5. Open the **Overview** tab, and copy the **Invoke URL**.

You will use these values when configuring Codex CLI.

---

## Step 4: Configure Codex CLI to Use the OpenAI LLM Service Provider

Codex CLI can be configured to use a custom OpenAI-compatible provider by updating its `config.toml` file.

1. Open the Codex CLI configuration file located at:

    ```bash
    ~/.codex/config.toml
    ```

    If the file does not already exist, create it:

    ```bash
    mkdir -p ~/.codex
    touch ~/.codex/config.toml
    ```

2. Add the following configuration to `~/.codex/config.toml`, replacing the `base_url` with the Invoke URL copied from the LLM service provider overview page:

    ```toml
    model = "gpt-5.4"
    model_provider = "openaicustom"

    [model_providers.openaicustom]
    name = "CHOREO OPEN AI PROVIDER"
    base_url = "<INVOKE URL>"
    env_key = "OPENAI_AUTH_TOKEN"
    wire_api = "responses"
    env_http_headers = { "API-Key" = "OPENAI_AUTH_TOKEN" }
    ```

    The configuration above instructs Codex CLI to use the Choreo API Platform LLM service provider endpoint and send the Choreo API Platform API key using the `API-Key` header.


### Configure Environment Variables for Codex CLI

1. Open a terminal session where you want to run Codex CLI.

2. Export the API key generated from Choreo API Platform:

    ```bash
    export OPENAI_AUTH_TOKEN="<API PLATFORM API KEY>"
    ```

    Replace `<API PLATFORM API KEY>` with the API key generated for the LLM service provider.

!!! note
    This environment variable must be set in the same terminal session where Codex CLI is executed. Alternatively, it can be configured as a permanent environment variable.

---

## Step 5: Configure the Gateway Certificate for Codex CLI

When using a local Choreo API Platform AI Gateway over HTTPS, Codex CLI must be able to trust the certificate presented by the Gateway.

!!! note
    If the AI Gateway uses a valid CA-signed certificate, no additional certificate configuration is required.

If the Gateway uses a self-signed certificate, Codex CLI fails to connect because of certificate verification errors. In such cases, add the Gateway certificate to your operating system's trust store before running the client.

1. Extract the Gateway certificate and save it as `gateway_certificate.pem` in the current directory.

    ```bash
    echo -n | openssl s_client -connect localhost:8443 2>/dev/null | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > gateway_certificate.pem
    ```

    On Windows, run this command in Git Bash.

2. Add the certificate to your operating system's trust store.

    === "macOS"

        ```bash
        security add-trusted-cert -r trustRoot -k ~/Library/Keychains/login.keychain-db gateway_certificate.pem
        ```

    === "Linux (Ubuntu or Debian)"

        ```bash
        sudo cp gateway_certificate.pem /usr/local/share/ca-certificates/gateway_certificate.crt
        sudo update-ca-certificates
        ```

    === "Windows (PowerShell)"

        ```powershell
        certutil -user -addstore Root gateway_certificate.pem
        ```

3. Open a new terminal window before you run Codex CLI.

!!! warning "SSL_CERT_FILE does not work with the default certificate"
    Codex CLI rejects the self-signed certificate that the local AI Gateway generates when you pass it through `SSL_CERT_FILE`, and then repeats `Reconnecting... waiting for network`. Add the certificate to the operating system's trust store instead, and do not set `SSL_CERT_FILE`.

!!! note "Local testing only"
    For local testing only, you can use the Gateway's HTTP endpoint instead of the Invoke URL, for example `http://localhost:8080/<PROVIDER CONTEXT PATH>`. Do not use HTTP in production, because the API key and prompts are sent unencrypted.

---

## Step 6: Run the Codex CLI Client

Execute Codex CLI:

```bash
codex
```

Requests will now be routed through Choreo API Platform.

---

## Use case examples

### Implement Choreo AI Gateway Guardrails for Enhanced Control

Choreo API Platform AI Gateway guardrails enable granular control over the data exchanged between Codex CLI and the OpenAI API.

By applying guardrails, you can enforce security and compliance policies.

For example, a **PII Masking Regex Guardrail** can be configured on the provider's **Guardrails** tab to prevent Personally Identifiable Information (PII) from reaching the OpenAI API. If a user submits a prompt containing PII, the guardrail evaluates the request against defined patterns and redacts them before they reach the OpenAI API.

[![Codex CLI terminal showing phone number redacted as asterisks after confirming PII masking guardrail intercepted the value](../../../assets/img/guides/ai-and-mcp/ai-coding-assistants/codex/codex-guardrail-redacted-example.png)](../../../assets/img/guides/ai-and-mcp/ai-coding-assistants/codex/codex-guardrail-redacted-example.png)

For more information on AI Guardrails, refer to the official [Choreo API Platform Documentation](https://wso2.com/api-platform/docs/ai-gateway/llm/guardrails/pii-masking-regex/)

---

### Rate Limiting at AI Gateway

The Choreo API Platform AI Gateway supports request-based and token-based rate limiting for AI APIs. This allows you to control Codex CLI usage when requests are routed through the Gateway.

For example, set a consumer-level token limit on the provider's **Rate Limiting** tab. Each developer's key then gets its own quota, and the gateway returns `HTTP 429` once a developer reaches it. For the steps, see [Enforce token-based rate limiting on an LLM service provider](../enforce-token-based-rate-limiting-on-an-llm-proxy.md).

This helps control token consumption and avoid unexpected costs.

The following screenshot illustrates Codex CLI operating under a configured AI Gateway rate limit.

[![Codex CLI terminal showing a working indicator at the bottom while processing a WSO2-related query](../../../assets/img/guides/ai-and-mcp/ai-coding-assistants/codex/codex-rate-limit-example.png)](../../../assets/img/guides/ai-and-mcp/ai-coding-assistants/codex/codex-rate-limit-example.png)

For more information on Rate Limiting and other policies, refer to the official [Choreo API Platform documentation](https://wso2.com/api-platform/docs/ai-workspace/policies/overview/)

---

### Prompt Decorator

The Choreo API Platform AI Gateway supports Prompt Decorators, which allow you to modify or enrich prompts before they are sent to the backend AI provider. This is useful for enforcing consistent instructions, adding system-level context, or guiding model behavior without requiring changes in the client application.

As a simple example, you can configure a Prompt Decorator on the provider's **Guardrails** tab to prepend a system instruction to all incoming prompts:

```text
You are operating behind an enterprise AI gateway. Follow these rules:
1. Be concise and direct.
2. Never output secrets, tokens, or credentials.
3. When editing code, explain the change briefly.
4. When unsure, state the assumption explicitly.
5. At the end of every response, add the text: 'Routed through WSO2 AI Gateway'.
```

Once configured, every request sent from Codex CLI is automatically modified by the Gateway to include this instruction before being forwarded to OpenAI.

[![Codex CLI terminal showing response ending with "Routed through WSO2 AI Gateway" footer added by Prompt Decorator](../../../assets/img/guides/ai-and-mcp/ai-coding-assistants/codex/codex-prompt-decorator-example.png)](../../../assets/img/guides/ai-and-mcp/ai-coding-assistants/codex/codex-prompt-decorator-example.png)

For more information on Prompt Management, refer to the official [Choreo API Platform documentation](https://wso2.com/api-platform/docs/ai-gateway/llm/prompt-management/prompt-decorator/)
