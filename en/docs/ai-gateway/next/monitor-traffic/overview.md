---
title: "Monitor traffic"
description: "See what the AI Gateway is doing: collect logs centrally, trace requests across hops, and publish request and response data to an analytics backend."
canonical_url: https://wso2.com/api-platform/docs/ai-gateway/monitor-traffic/overview/
md_url: https://wso2.com/api-platform/docs/ai-gateway/monitor-traffic/overview.md
tags:
  - ai-gateway
  - observability
  - analytics
author: WSO2 API Platform Documentation Team
last_updated: 2026-08-17
content_type: "concept"
---

# Monitor traffic

This section covers the three ways you observe traffic through the AI Gateway: logs, traces, and analytics. Logging and tracing tell you what the gateway did with a request; analytics tells you how your APIs are used over time.

Each page configures a different backend, so you can adopt them independently.

## In this section

This section contains the following pages:

| Page | What it covers |
|------|----------------|
| [Gateway logging](logging.md) | Configure centralized log collection for API Platform AI Gateway using Fluent Bit, OpenSearch, and alternative logging stacks. |
| [Gateway tracing](tracing.md) | Configure distributed tracing for API Platform AI Gateway using OpenTelemetry and Jaeger, with support for cloud-native tracing backends. |
| [Moesif analytics](moesif-analytics.md) | Configure Moesif in API Platform AI Gateway to capture and publish API request and response data. |
| [Analytics header filter](analytics-header-filter.md) | Control which request and response headers are sent to analytics backends using allow or deny mode in API Platform AI Gateway. |
