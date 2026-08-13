---
title: "Connect LLM providers"
description: "Connect the AI Gateway to an LLM backend: what an LLM Provider holds, who configures it, and the provider templates and AWS Bedrock setup available."
canonical_url: https://wso2.com/api-platform/docs/ai-gateway/connect-llm-providers/overview/
md_url: https://wso2.com/api-platform/docs/ai-gateway/connect-llm-providers/overview.md
tags:
  - ai-gateway
  - llm-provider
  - llm
author: WSO2 API Platform Documentation Team
last_updated: 2026-08-12
content_type: "concept"
---

# Connect LLM providers

An LLM Provider represents a connection to an AI backend service such as OpenAI, Azure OpenAI, or other LLM APIs. Platform administrators configure LLM Providers to define:

- The LLM Provider Template
- The upstream LLM service URL
- Authentication credentials (API keys, tokens)
- Access control rules for which endpoints are exposed
- Budget control policies, such as token-based rate limiting
- Organization-wide policies such as guardrails

Once configured, the LLM Provider allows traffic to flow through the gateway to the AI backend.

To connect the gateway to AWS Bedrock, see [Configure an AWS Bedrock LLM Provider](configure-aws-bedrock-provider.md). The guide covers both Bedrock bearer API keys and AWS Signature Version 4 (SigV4) authentication.

## Who configures this

Platform administrators own LLM providers. An administrator holds the upstream credentials, decides which endpoints the provider exposes, and sets the organization-wide policies that every LLM proxy consuming the provider inherits.

## In this section

This section contains the following pages:

| Page | What it covers |
|------|----------------|
| [Provider templates](llm-templates.md) | Reference for LLM Provider Templates in API Platform AI Gateway, covering built-in templates for OpenAI, Anthropic, Gemini, and more. |
| [Configure an AWS Bedrock LLM provider](configure-aws-bedrock-provider.md) | Connect API Platform AI Gateway to AWS Bedrock using a bearer API key or AWS Signature Version 4 authentication, then invoke a model through the gateway. |

## Related guides

- [Set up a governed multi-model LLM proxy](../../../guides/ai-and-mcp/set-up-a-governed-multi-model-llm-proxy-with-cost-controls-and-failover.md) — adds Azure OpenAI as an LLM provider, then distributes requests across models behind a single proxy.
