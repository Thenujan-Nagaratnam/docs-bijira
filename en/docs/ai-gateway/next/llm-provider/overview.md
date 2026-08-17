---
title: "LLM provider"
description: "Connect the AI Gateway to an LLM backend: what an LLM Provider holds, who configures it, and the OpenAI, Anthropic, and AWS Bedrock connection guides."
canonical_url: https://wso2.com/api-platform/docs/ai-gateway/llm-provider/overview/
md_url: https://wso2.com/api-platform/docs/ai-gateway/llm-provider/overview.md
tags:
  - ai-gateway
  - llm-provider
  - llm
author: WSO2 API Platform Documentation Team
last_updated: 2026-08-17
content_type: "concept"
---

# LLM provider

An LLM Provider represents a connection to an AI backend service such as OpenAI, Azure OpenAI, or other LLM APIs. Platform administrators configure LLM Providers to define:

- The LLM Provider Template
- The upstream LLM service URL
- Authentication credentials (API keys, tokens)
- Access control rules for which endpoints are exposed
- Budget control policies, such as token-based rate limiting
- Organization-wide policies such as guardrails

Once configured, the LLM Provider allows traffic to flow through the gateway to the AI backend.

## Who configures this

Platform administrators own LLM providers. An administrator holds the upstream credentials, decides which endpoints the provider exposes, and sets the organization-wide policies that every LLM proxy consuming the provider inherits.

## In this section

The three provider pages carry connection documentation: the upstream URL, the authentication each provider expects, and a working definition you can deploy as it stands. The gateway ships more provider templates than these three; [Provider templates](llm-templates.md) lists every one it loads at startup.

This section contains the following pages:

| Page | What it covers |
|------|----------------|
| [Create and configure an LLM provider](create-and-configure-an-llm-provider.md) | Create an LLM provider on the AI Gateway: choose a template, set the upstream URL and credentials, deploy it with the management API, and test the connection. |
| [OpenAI](supported-providers/openai.md) | Connect the AI Gateway to OpenAI: the upstream URL, API key authentication, the endpoints the provider exposes, and a request that tests the connection. |
| [Anthropic](supported-providers/anthropic.md) | Connect the AI Gateway to the Anthropic Messages API: the upstream URL, x-api-key authentication, and the endpoint the provider exposes. |
| [AWS Bedrock](supported-providers/aws-bedrock.md) | Connect API Platform AI Gateway to AWS Bedrock using a bearer API key or AWS Signature Version 4 authentication, then invoke a model through the gateway. |
| [Provider templates](llm-templates.md) | Reference for LLM Provider Templates in API Platform AI Gateway, covering built-in templates for OpenAI, Anthropic, Gemini, and more. |

## Related guides

- [Set up a governed multi-model LLM proxy](../../../guides/ai-and-mcp/set-up-a-governed-multi-model-llm-proxy-with-cost-controls-and-failover.md) — adds Azure OpenAI as an LLM provider, then distributes requests across models behind a single proxy.
