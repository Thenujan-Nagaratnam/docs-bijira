# Product name mappings

Not yet finalized. By default the new brand replaces "WSO2" and the rest of the
name stays. The mapping variable is in brackets; override it in `names.yml` if a
product gets a different name. Mentions are approximate, across API Platform
`main` and all 12 API Manager versions.

## Company

| Current | New | Variable |
| --- | --- | --- |
| WSO2 | `<brand>` | `brand` |
| WSO2 LLC (copyright footer) | `<brand> <legal_suffix>` | `legal_name` |
| WSO2 Inc (older text, 48) | `<brand> Inc` by default | `legal_name_old` (API Manager) |

## API Platform docs

"API Platform" is renamed to "API Management". Set `platform` (and `platform_anchor`, its heading-link form) once, and every API Platform name follows: "WSO2 API Platform Gateway" becomes "<brand> API Management Gateway", and "API Platform" without the brand (about 1,600 mentions, such as "API Platform Console" and the site name) becomes "API Management". To keep one of the longer names, override its variable in `names.yml`.

| Current | Mentions | Variable |
| --- | --- | --- |
| WSO2 API Platform | 240 | `api_platform` (`<brand> {platform}`) |
| API Platform, without the brand, in text | about 1,600 | `platform` |
| API Platform, without the brand, in code samples | 7 | `sample_platform` (defaults to `platform`) |
| `#...api-platform...` in heading links | 4 | `platform_anchor` |
| WSO2 API Platform Documentation Team (page author) | 1,081 | `docs_team` |
| WSO2 API Platform Cloud | 14 | `cloud_name` |
| WSO2 API Platform Gateway | 20 | `platform_gateway` |
| WSO2 API Platform AI Gateway | 27 | `platform_ai_gateway` |
| WSO2 API Platform Developer Portal | 1 | `platform_dev_portal` |
| WSO2 API Platform Policy Hub | 5 | `platform_policy_hub` |
| WSO2 API Gateway | 193 | `api_gateway` |
| WSO2 AI Gateway | 85 | `ai_gateway` |
| WSO2 AI Workspace | 10 | `ai_workspace` |
| WSO2 API Portal | 2 | `api_portal` |
| WSO2 Developer Portal | 153 | `dev_portal` |
| WSO2 Kubernetes Gateway | 38 | `kubernetes_gateway` |
| Bijira | 37 | `cloud_codename` |

## API Manager docs: current products

| Current | Mentions | Variable |
| --- | --- | --- |
| WSO2 API Manager | 10,326 | `api_manager` |
| WSO2 API-M | 3,527 | `api_m` |
| WSO2 APIM | 280 | `apim_short` |
| WSO2 Identity Server | 1,490 | `identity_server` |
| WSO2 IS | 986 | `is_short` |
| WSO2 Micro Integrator | 850 | `micro_integrator` |
| WSO2 MI | 186 | `mi_short` |
| WSO2 Integration Studio | 1,484 | `integration_studio` |
| WSO2 Streaming Integrator | 1,095 | `streaming_integrator` |
| WSO2 API Controller | 364 | `api_controller` |
| WSO2 APICTL | 16 | `apictl_upper` |
| WSO2 Carbon | 211 | `carbon` |
| WSO2 AI Gateway | 85 | `ai_gateway` |
| WSO2 Kubernetes Gateway | 38 | `kubernetes_gateway` |
| WSO2 Enterprise Integrator | 84 | `enterprise_integrator` |
| WSO2 EI | 172 | `ei_short` |
| WSO2 ESB | 103 | `esb` |

Every other "WSO2 …" name takes the brand in front through the generic rule, with no variable of its own. That includes:
- **Current components:** API Control Plane, Universal Gateway, Classic Gateway, Immutable Gateway, Traffic Manager, Key Manager, API Publisher, Developer Portal, Admin Portal, Management Console, Analytics, APK, Choreo Connect, Secure Vault, and Updates.
- **Older products:** Message Broker, Stream Processor, Complex Event Processor, Business Process Server, Governance Registry, Application Server, API Microgateway, API Cloud, IoT Server, and Connector Store.
- **General phrases:** Subscription, Support, Helm Repository, Private Registry, and similar.

To rename any of these differently, add a rule and a variable to `mappings/api-manager.yml`.

## Typos to fix while renaming

- WSO2 Finane API (38): Finance API
- WSO2 Steaming Integrator (4): Streaming Integrator
- WSO2 API Manager Publsiher Portal (6): Publisher Portal
- WSO2 Api Manager (18), WSO2 API-Manager (34), WSO2 APIManager (10): API Manager

## Names without "WSO2" (unchanged unless decided)

| Name | API Platform | API Manager (all versions) |
| --- | --- | --- |
| API Manager | 73 | 19,220 |
| Micro Integrator | 0 | 6,519 |
| Streaming Integrator | 0 | 4,671 |
| Choreo, including Choreo Connect | 16 | 3,417 |
| Identity Server | 4 | 2,562 |
| Integration Studio | 0 | 1,751 |
| Moesif | 536 | 349 |
| Asgardeo | 233 | 68 |
| APK | 23 | 125 |
| Ballerina | 32 | 46 |
| Bijira | 37 | 0 |

## Decisions needed

- Bijira: keep, or replace with `<brand> API Management Cloud`?
- Names built on "API Platform" (Gateway, AI Gateway, Developer Portal, Policy Hub, Cloud, Console, CLI, STS): all follow `platform` by default. Do any keep "API Platform" or take another name?
- Lowercase `api-platform` in URLs, CRD groups, Helm charts, and the GatewayClass is a code value and stays.
- In the API Manager docs, "WSO2 API Platform for Kubernetes" (the full name of APK) keeps "API Platform" through `apk_platform`.
- Asgardeo, Choreo, Choreo Connect, Devant, Moesif, Ballerina: keep the names?
- Micro Integrator, Integration Studio, Streaming Integrator, Carbon: carry over as `<brand> …`, or new names?
- Older products in old versions: rename, or leave as historical names?
- Short forms API-M, APIM, IS, MI, SI, EI, MB, SP, BPS, APICTL: keep?
- "WSO2 Labs" (internal performance lab, Scaling the Gateway page): reword, for example "Based on internal performance tests".
