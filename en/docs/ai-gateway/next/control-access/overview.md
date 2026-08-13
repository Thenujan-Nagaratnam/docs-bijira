---
title: "Control access"
description: "Control access to the AI Gateway: authentication and role-based authorization on the management API, and provider-level rules for upstream endpoints."
canonical_url: https://wso2.com/api-platform/docs/ai-gateway/control-access/overview/
md_url: https://wso2.com/api-platform/docs/ai-gateway/control-access/overview.md
tags:
  - ai-gateway
  - security
  - access-control
author: WSO2 API Platform Documentation Team
last_updated: 2026-08-12
content_type: "concept"
---

# Control access

The AI Gateway controls access on two surfaces.

The management API is the REST API you use to manage gateway configuration. It authenticates callers with locally configured users, with JWTs validated against an identity provider, or with both. Authorization is role-based, and the gateway enforces it per route.

An LLM provider carries its own `accessControl` rules. These decide which upstream endpoints the provider exposes through the gateway. For a provider configuration that sets them, see [Quick Start Guide](../quick-start-guide.md).

## Who configures this

Platform administrators configure LLM providers, including the access control rules that decide which endpoints a provider exposes. The management API's own authentication and role mapping live in the gateway configuration, under `controller.auth`.

## In this section

This section contains the following page:

| Page | What it covers |
|------|----------------|
| [Secure the management API](secure-the-management-api.md) | Configure Basic Auth or JWT/IDP authentication and role-based authorization for the AI Gateway Controller REST API. |
