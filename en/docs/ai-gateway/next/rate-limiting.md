---
title: "Rate limiting"
description: "Cap what a client can consume through the AI Gateway, counted by requests or by tokens, so one application cannot exhaust a shared model quota."
canonical_url: https://wso2.com/api-platform/docs/ai-gateway/rate-limiting/
md_url: https://wso2.com/api-platform/docs/ai-gateway/rate-limiting.md
tags:
  - ai-gateway
  - rate-limiting
  - traffic
  - quota
  - throttling
author: WSO2 API Platform Documentation Team
last_updated: 2026-08-19
content_type: "concept"
---

# Rate limiting

A single application can exhaust a shared model quota in minutes, and nothing about the request count tells you how much of that quota it used. Rate limiting caps what each caller consumes, so one client can't starve the others.

The gateway counts two different things. Request-based limits count calls, which suits any API. Token-based limits count the tokens the model actually processed, which tracks LLM consumption far more closely than a request count does, because one request can be a sentence or a whole document.

## Where the gateway enforces it

You attach a rate limit policy in the `operationPolicies` block of an `LlmProxy`, to cap one application, or of an `LlmProvider`, to cap every proxy that consumes it.

Token-based limits read usage from the model's response, so they take effect in the response phase. The request that crosses the threshold still reaches the model; the next one is rejected. Request-based limits apply before the call goes upstream.

## Policies for this use case

These policies are documented in the [Policy Hub](https://wso2.com/api-platform/policy-hub), the versioned reference for every API Platform policy. For policy categories and how policies chain, see the [Policy Hub overview](../../policy-hub/overview.md).

| Policy | What it does |
|--------|--------------|
| [Token-Based Rate Limit](https://wso2.com/api-platform/policy-hub/policies/token-based-ratelimit) | Caps usage by token count rather than request count |
| [Rate Limit - Basic](https://wso2.com/api-platform/policy-hub/policies/basic-ratelimit) | Caps requests per time window |
| [Rate Limit - Advanced](https://wso2.com/api-platform/policy-hub/policies/advanced-ratelimit) | Multi-dimensional quotas with GCRA or fixed-window algorithms, Redis backend support, and weighted limiting |

`Rate Limit - Basic` and `Rate Limit - Advanced` apply to any API, not only to LLM traffic.

To cap spend in currency rather than in tokens, see [Cost control and budgets](cost-control-and-budgets.md). For MCP traffic, which is limited per tool, resource, prompt, or JSON-RPC method, see [Govern MCP tools](govern-mcp-tools.md).

## Related topics

- [Enforce token-based rate limiting on an LLM proxy](../../guides/ai-and-mcp/enforce-token-based-rate-limiting-on-an-llm-proxy.md) — caps token consumption on a proxy within a rolling window, so one application cannot exhaust the budget.
- [Authenticate clients](authenticate-clients.md) — issue a key per application, so a limit applies to a caller you can identify.
- [Cost control and budgets](cost-control-and-budgets.md) — enforce a monetary ceiling instead of a usage ceiling.
