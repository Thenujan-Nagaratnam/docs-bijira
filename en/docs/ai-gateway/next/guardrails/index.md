---
title: "Guardrails"
description: "AI Gateway guardrails: LLM-aware policies for content filtering, safety, and compliance, with per-policy reference in the WSO2 API Platform Policy Hub."
canonical_url: https://wso2.com/api-platform/docs/ai-gateway/guardrails/
md_url: https://wso2.com/api-platform/docs/ai-gateway/guardrails.md
tags:
  - ai-gateway
  - guardrails
  - llm-proxy
author: WSO2 API Platform Documentation Team
last_updated: 2026-08-17
content_type: "concept"
---

# Guardrails

Guardrails are policies that run in the LLM Proxy's request and response pipeline to validate, filter, or transform content before it reaches an LLM or is returned to the client.

AI Guardrails allow you to enforce safety, content, and compliance policies on AI traffic flowing through the AI Gateway. They can be applied at the LLM Provider level (organization-wide), at the LLM Proxy level (per-application), or on MCP Proxies.

Guardrails use the same underlying policy engine as [API Gateway policies](../../../api-gateway/next/policies/overview.md). Each guardrail declares which execution phases it participates in, and the engine calls the appropriate hook for each phase.

## What guardrails do

- **Content filtering**: Block or flag requests and responses that violate configured topic, word, or content policies.
- **PII detection and masking**: Detect and mask or redact personally identifiable information in prompts and responses.
- **Schema validation**: Enforce structure on requests or responses using JSON Schema.
- **Pattern matching**: Detect prohibited content using regular expressions.
- **Length and count limits**: Enforce word count, sentence count, and byte length constraints on prompts and responses.
- **External validation**: Delegate content validation to managed services such as AWS Bedrock Guardrails or Azure Content Safety.

## Available guardrails

Guardrail policies are documented in the [Policy Hub](https://wso2.com/api-platform/policy-hub), the versioned reference for every API Platform policy. For policy categories and how policies chain, see the [Policy Hub overview](../../../policy-hub/overview.md).

| Guardrail | What it checks |
|-----------|----------------|
| [Regex Guardrail](https://wso2.com/api-platform/policy-hub/policies/regex-guardrail) | Validates content against a regular expression |
| [JSON Schema Guardrail](https://wso2.com/api-platform/policy-hub/policies/json-schema-guardrail) | Enforces a JSON Schema on request or response payloads |
| [Word Count Guardrail](https://wso2.com/api-platform/policy-hub/policies/word-count-guardrail) | Enforces word-count limits on payloads |
| [Sentence Count Guardrail](https://wso2.com/api-platform/policy-hub/policies/sentence-count-guardrail) | Enforces sentence-count limits on payloads |
| [Content Length Guardrail](https://wso2.com/api-platform/policy-hub/policies/content-length-guardrail) | Enforces byte-length limits on payloads |
| [URL Guardrail](https://wso2.com/api-platform/policy-hub/policies/url-guardrail) | Validates URLs found in request or response bodies |
| [PII Masking](https://wso2.com/api-platform/policy-hub/policies/pii-masking-regex) | Masks or redacts PII from request/response bodies using configurable regex patterns |
| [Semantic Prompt Guard](https://wso2.com/api-platform/policy-hub/policies/semantic-prompt-guard) | Blocks or allows prompts based on semantic similarity to configured allow/deny phrases |
| [Azure Content Safety](https://wso2.com/api-platform/policy-hub/policies/azure-content-safety-content-moderation) | Screens content against Azure Content Safety API |
| [AWS Bedrock Guardrail](https://wso2.com/api-platform/policy-hub/policies/aws-bedrock-guardrail) | Validates content against AWS Bedrock Guardrails |
| [Granite Guardian Prompt Injection](https://wso2.com/api-platform/policy-hub/policies/granite-guardian-prompt-injection) | Detects prompt injection and jailbreak attempts in LLM API requests using IBM Granite Guardian 3.3 8B |
| [NeMo Guard Content Safety](https://wso2.com/api-platform/policy-hub/policies/nvidia-nemoguard-content-safety) | Validates request and/or response content using NVIDIA NeMo Guard (llama-3.1-nemoguard-8b-content-safety) |

## Prompt management

Guardrails judge a prompt. A separate set of policies reshapes one — injecting standing instructions, applying templates, or compressing text before it goes upstream. See [Prompt management](../prompt-management.md).

## Custom guardrails

You can extend the AI Gateway with custom guardrail policies by building a custom gateway image using the `ap` CLI. See [Customizing the Gateway by Adding and Removing Policies](../../../tools/cli/customizing-gateway-policies.md).

## How guardrails execute

When multiple guardrails are attached to an LLM Proxy, they run as an ordered chain across request and response phases. The AI Gateway's architecture — with a separate LLM Proxy chain and LLM Provider chain — means every request passes through two chains in sequence.

For a full explanation of phase execution, multi-guardrail ordering, and the dual-hop execution model specific to AI Gateway, see [Guardrail execution order](execution-order.md).
