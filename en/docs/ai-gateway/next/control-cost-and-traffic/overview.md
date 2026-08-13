---
title: "Control cost and traffic"
description: "Keep LLM spend and traffic volume predictable: distribute requests across model endpoints, cache equivalent prompts, and set timeouts on a resource."
canonical_url: https://wso2.com/api-platform/docs/ai-gateway/control-cost-and-traffic/overview/
md_url: https://wso2.com/api-platform/docs/ai-gateway/control-cost-and-traffic/overview.md
tags:
  - ai-gateway
  - cost
  - traffic
author: WSO2 API Platform Documentation Team
last_updated: 2026-08-12
content_type: "concept"
---

# Control cost and traffic

The policies in this section keep LLM spend and traffic volume predictable. They spread requests across a pool of model endpoints, and they avoid an upstream call altogether when a semantically equivalent prompt has already been answered.

Timeouts work differently. You configure them through the `resilience` block on an `LlmProvider`, `LlmProxy`, or `Mcp` resource, rather than by attaching a policy.

## In this section

This section contains the following page:

| Page | What it covers |
|------|----------------|
| [Timeouts](timeouts.md) | Configure gateway-level and API-level timeouts (connect, route, idle, and HTTP connection manager) in the API Platform AI Gateway to protect against slow or unreachable backends and slow clients. |

## Policies

These policies are documented in the [Policy Hub](https://wso2.com/api-platform/policy-hub), the versioned reference for every API Platform policy. For policy categories and how policies chain, see the [Policy Hub overview](../../../policy-hub/overview.md).

| Policy | What it does |
|--------|--------------|
| [LLM Cost](https://wso2.com/api-platform/policy-hub/policies/llm-cost) | Calculates the monetary cost of each LLM call and stores it for downstream policies |
| [LLM Cost-Based Rate Limit](https://wso2.com/api-platform/policy-hub/policies/llm-cost-based-ratelimit) | Enforces monetary budget quotas on LLM usage |
| [Token-Based Rate Limit](https://wso2.com/api-platform/policy-hub/policies/token-based-ratelimit) | Caps usage by token count rather than request count |
| [Semantic Cache](https://wso2.com/api-platform/policy-hub/policies/semantic-cache) | Caches LLM responses using vector similarity, returning cached results for semantically equivalent prompts |
| [Prompt Compressor](https://wso2.com/api-platform/policy-hub/policies/prompt-compressor) | Compresses prompt text to reduce token usage before upstream calls |
| [Model Round Robin](https://wso2.com/api-platform/policy-hub/policies/model-round-robin) | Distributes requests evenly across a pool of AI model endpoints |
| [Model Weighted Round Robin](https://wso2.com/api-platform/policy-hub/policies/model-weighted-round-robin) | Distributes requests across model endpoints according to configured weights |
| [Respond](https://wso2.com/api-platform/policy-hub/policies/respond) | Returns an immediate response without forwarding to the upstream backend |

## Related guides

- [Enforce token-based rate limiting on an LLM proxy](../../../guides/ai-and-mcp/enforce-token-based-rate-limiting-on-an-llm-proxy.md) — caps token consumption on a proxy within a rolling window, so one application cannot exhaust the budget.
- [Set up a governed multi-model LLM proxy](../../../guides/ai-and-mcp/set-up-a-governed-multi-model-llm-proxy-with-cost-controls-and-failover.md) — distributes traffic across models behind one proxy, with per-team token budgets, PII masking, and semantic caching.
