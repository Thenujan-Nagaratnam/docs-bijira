---
title: "Access control"
description: "Control access to the AI Gateway: client authentication on proxies and providers, authentication and role-based authorization on the management API, and provider-level rules for upstream endpoints."
canonical_url: https://wso2.com/api-platform/docs/ai-gateway/access-control/overview/
md_url: https://wso2.com/api-platform/docs/ai-gateway/access-control/overview.md
tags:
  - ai-gateway
  - security
  - access-control
author: WSO2 API Platform Documentation Team
last_updated: 2026-08-17
content_type: "concept"
---

# Access control

The AI Gateway controls access on three surfaces.

An application that calls an LLM proxy or provider presents a credential with every request. Once you attach an authentication policy to an operation, the gateway rejects calls to that operation that arrive without a valid credential. For the API key walkthrough and the other authentication policies, see [Authenticate clients](authenticate-clients.md).

The management API is the REST API you use to manage gateway configuration. It authenticates callers with locally configured users, with JWTs validated against an identity provider, or with both. Authorization is role-based, and the gateway enforces it per route. For the configuration, see [Secure the management API](../setup-and-deployment/secure-the-management-api.md).

An LLM provider carries its own `accessControl` rules. These decide which upstream endpoints the provider exposes through the gateway. For a provider configuration that sets them, see [Quick Start Guide](../quick-start-guide.md).

## Who configures this

Platform administrators configure LLM providers, including the access control rules that decide which endpoints a provider exposes. They also attach the authentication policies that protect proxies and providers, and issue the API keys that applications present. AI developers send those keys from the applications they build. The management API's own authentication and role mapping live in the gateway configuration, under `controller.auth`.

## In this section

This section contains the following page:

| Page | What it covers |
|------|----------------|
| [Authenticate clients](authenticate-clients.md) | Protect an LLM proxy or provider with the `api-key-auth` policy, issue consumer API keys through the management API, and manage the key lifecycle. |
