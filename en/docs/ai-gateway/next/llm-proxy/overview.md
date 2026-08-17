---
title: "LLM proxy"
description: "Expose an LLM provider to applications through an LLM proxy: its own URL context, per-application policies, and the provider-level rules it inherits."
canonical_url: https://wso2.com/api-platform/docs/ai-gateway/llm-proxy/overview/
md_url: https://wso2.com/api-platform/docs/ai-gateway/llm-proxy/overview.md
tags:
  - ai-gateway
  - llm-proxy
  - llm
author: WSO2 API Platform Documentation Team
last_updated: 2026-08-17
content_type: "concept"
---

# LLM proxy

An LLM Proxy allows developers to create custom API endpoints that consume an LLM Provider, while inheriting administrator-enforced access control, budgeting and organization-wide policies defined at the provider level. Each proxy gets its own URL context (e.g., `/assistant`) and can have its own policies applied. This enables:

- Multiple AI applications to share a single LLM Provider
- A single OpenAI-compatible endpoint to route requests to multiple LLM providers. See [Multi-Provider Routing for LLM Proxies](./multi-provider-routing.md).
- Per-application policies such as prompt management and guardrails
- Separation between platform administration and application development

To deploy your first LLM proxy against a configured provider, see [Create and configure an LLM proxy](create-and-configure-an-llm-proxy.md).

## Who configures this

AI developers own LLM proxies. A developer creates the proxy, names the LLM provider it consumes, and attaches the policies one application needs. The access control, budgeting, and organization-wide policies set on the provider still apply.

## In this section

This section contains the following pages:

| Page | What it covers |
|------|----------------|
| [Create and configure an LLM proxy](create-and-configure-an-llm-proxy.md) | Create an LLM proxy on the AI Gateway: give it a URL context, name the LLM provider it consumes, deploy it with the management API, and route a request through it. |
| [Route across multiple providers](multi-provider-routing.md) | Route OpenAI-compatible LLM proxy requests to multiple providers using header-based selection and provider-specific transformers. |
| [Stream responses](streaming-responses.md) | Stream responses through API Platform AI Gateway chunk by chunk across LLM providers, LLM proxies, and MCP proxies, and understand how policies, analytics, and token usage behave. |

## Policies

One proxy-layer routing policy is documented in the [Policy Hub](https://wso2.com/api-platform/policy-hub), the versioned reference for every API Platform policy. For policy categories and how policies chain, see the [Policy Hub overview](../../../policy-hub/overview.md).

| Policy | What it does |
|--------|--------------|
| [LLM Header Router](https://wso2.com/api-platform/policy-hub/policies/llm-header-router) | Selects an LLM provider for OpenAI Chat Completions requests using a configurable request header |

## Related guides

- [Set up a governed multi-model LLM proxy](../../../guides/ai-and-mcp/set-up-a-governed-multi-model-llm-proxy-with-cost-controls-and-failover.md) — distributes traffic across models behind one proxy, with per-team token budgets, PII masking, and semantic caching.
- [Enforce a consistent AI persona with the prompt decorator policy](../../../guides/ai-and-mcp/using-prompt-decorator-policy.md) — prepends a persona system message to every request on an LLM proxy, without changing client code.
- [Configure Claude Code with AI Gateway](../../../guides/ai-and-mcp/ai-coding-assistants/claude-code-configuration-with-ai-gateway.md) — routes Claude Code through an Anthropic provider and an LLM proxy.
- [Configure Gemini CLI with AI Gateway](../../../guides/ai-and-mcp/ai-coding-assistants/gemini-cli-configuration-with-ai-gateway.md) — routes Google Gemini CLI through a Gemini provider and an LLM proxy.
- [Configure OpenAI Codex CLI with AI Gateway](../../../guides/ai-and-mcp/ai-coding-assistants/codex-configuration-with-ai-gateway.md) — routes OpenAI Codex CLI through an OpenAI provider and an LLM proxy.
