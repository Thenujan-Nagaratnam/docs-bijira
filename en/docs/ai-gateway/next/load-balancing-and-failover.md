---
title: "Load balancing and failover"
description: "Spread AI traffic across a pool of models and move off a failing one, using round robin, weighted distribution, or a request header to select the provider."
canonical_url: https://wso2.com/api-platform/docs/ai-gateway/load-balancing-and-failover/
md_url: https://wso2.com/api-platform/docs/ai-gateway/load-balancing-and-failover.md
tags:
  - ai-gateway
  - load-balancing
  - failover
  - fallback
  - routing
author: WSO2 API Platform Documentation Team
last_updated: 2026-08-19
content_type: "concept"
---

# Load balancing and failover

One model endpoint is one quota and one point of failure. Spreading requests across several keeps throughput up when a model is saturated, and keeps traffic moving when a model starts returning errors.

## How the gateway distributes traffic

Three policies offer three strategies:

- **Round robin** sends requests to each model in the pool in turn, so allocation evens out over time and no single model carries the whole load.
- **Weighted round robin** distributes in proportion to a weight you set per model, which suits a pool whose models differ in capacity, cost, or performance.
- **Header-based routing** lets the caller, or an earlier policy, name the provider explicitly through a request header.

The failover behavior comes with the round robin policies. When a model returns a `5xx` or `429`, the policy suspends it for a configurable duration and sends traffic to the rest of the pool, rather than retrying an endpoint that is already failing.

Attach these policies on an `LlmProxy`, which is where a pool of providers is assembled. They run in the request phase, selecting the upstream before the call goes out.

## Policies for this use case

These policies are documented in the [Policy Hub](https://wso2.com/api-platform/policy-hub), the versioned reference for every API Platform policy. For policy categories and how policies chain, see the [Policy Hub overview](../../policy-hub/overview.md).

| Policy | What it does |
|--------|--------------|
| [Model Round Robin](https://wso2.com/api-platform/policy-hub/policies/model-round-robin) | Distributes requests evenly across a pool of AI model endpoints |
| [Model Weighted Round Robin](https://wso2.com/api-platform/policy-hub/policies/model-weighted-round-robin) | Distributes requests across model endpoints according to configured weights |
| [LLM Header Router](https://wso2.com/api-platform/policy-hub/policies/llm-header-router) | Selects an LLM provider for OpenAI Chat Completions requests using a configurable request header |

## Related topics

- [Multi-provider routing](multi-provider-routing.md) — the worked configuration: several providers behind one OpenAI-compatible proxy, the transformer each provider needs, and how suspension behaves in practice.
- [Set up a governed multi-model LLM proxy](../../guides/ai-and-mcp/set-up-a-governed-multi-model-llm-proxy-with-cost-controls-and-failover.md) — distributes traffic across models behind one proxy, with per-team token budgets, PII masking, and semantic caching.
- [Timeouts and resilience](timeouts-and-resilience.md) — decide how long the gateway waits before it treats an upstream as failed.
