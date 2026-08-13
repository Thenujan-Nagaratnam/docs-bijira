---
title: "MCP proxy"
description: "Route Model Context Protocol traffic through the AI Gateway with an MCP proxy, and apply authentication, authorization, and access control to that traffic."
canonical_url: https://wso2.com/api-platform/docs/ai-gateway/mcp-proxy/overview/
md_url: https://wso2.com/api-platform/docs/ai-gateway/mcp-proxy/overview.md
tags:
  - ai-gateway
  - mcp
  - mcp-proxy
author: WSO2 API Platform Documentation Team
last_updated: 2026-08-12
content_type: "concept"
---

# MCP proxy

An MCP Proxy routes Model Context Protocol traffic to MCP servers. MCP is a protocol that enables AI assistants to interact with external tools and data sources. With MCP Proxies, you can:

- Expose MCP servers through a centralized gateway
- Apply authentication and access control to MCP traffic
- Manage multiple MCP servers from a single control plane

## In this section

This section contains the following page:

| Page | What it covers |
|------|----------------|
| [Create an MCP proxy](create-an-mcp-proxy.md) | Run API Platform AI Gateway with Docker Compose, configure an MCP proxy, and route your first MCP traffic through the gateway. |

## Policies

MCP proxy policies are documented in the [Policy Hub](https://wso2.com/api-platform/policy-hub), the versioned reference for every API Platform policy. For policy categories and how policies chain, see the [Policy Hub overview](../../../policy-hub/overview.md).

| Policy | What it does |
|--------|--------------|
| [MCP Authentication](https://wso2.com/api-platform/policy-hub/policies/mcp-auth) | Secures MCP server traffic per the MCP specification authorization profile |
| [MCP Authorization](https://wso2.com/api-platform/policy-hub/policies/mcp-authz) | Validates access to MCP tools, resources, and prompts using JWT claims or OAuth scopes |
| [MCP Access Control](https://wso2.com/api-platform/policy-hub/policies/mcp-acl-list) | Controls which tools, resources, and prompts a caller can reach using allow/deny lists |
| [MCP Rewrite](https://wso2.com/api-platform/policy-hub/policies/mcp-rewrite) | Defines user-facing tool names and maps them to backend capability names |
| [MCP Rate Limit](https://wso2.com/api-platform/policy-hub/policies/mcp-ratelimit) | Applies rate limits to MCP traffic per tool, resource, prompt, or JSON-RPC method |
| [Semantic Tool Filtering](https://wso2.com/api-platform/policy-hub/policies/semantic-tool-filtering) | Filters MCP tools to only those semantically relevant to the user query |

## Related guides

- [Build an AI agent that uses aggregated MCP tools from multiple APIs](../../../guides/ai-and-mcp/build-ai-agent-with-multiple-mcp-servers.md) — connects an agent to three independently governed MCP servers through the gateway.
- [Convert a REST API into an MCP tool for Claude Desktop](../../../guides/ai-and-mcp/convert-rest-api-to-mcp-server.md) — exposes a REST API as a governed MCP server and enforces OAuth2 at the gateway.
- [Find and connect to an enterprise MCP server from the MCP Hub](../../../guides/ai-and-mcp/find-and-connect-to-an-enterprise-mcp-server-from-the-mcp-hub.md) — discovers MCP servers in the MCP Hub and connects a client to one.
