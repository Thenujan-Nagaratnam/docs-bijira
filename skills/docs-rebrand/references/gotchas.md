# Rebrand gotchas

Problems found while building and testing the rules, and how each is handled.

## Both sites

- **Order matters, and replaced text is protected.** Specific rules (such as "WSO2 API Platform") run before generic ones (such as "WSO2"). Once a rule replaces text, later rules can't touch it, so a code value kept at "wso2" isn't rewritten again by the generic rule.
- **Variables default to today's value.** `verify` rewrites with `*.today.yml` and expects zero changes. It caught every rule that changed more than it should.
- **Keep wording that differs in its own rule.** "WSO2 API Gateway" and "WSO2 API Platform Gateway" are separate rules, so each comes back exactly as written with today's names.
- **Code in Markdown includes raw HTML.** Old pages wrap code in `<pre><code>` (Confluence macros), not fences. The engine treats `<code>` and `<pre>` as code. Without that, `-Dorg.wso2.…` was treated as prose and renamed.
- **"a" or "an" follows the new name**, in text and in heading links. For example, "a WSO2 product" becomes "an Acme product", and `#monitoring-a-wso2-product` becomes `#monitoring-an-acme-product`.
- **Heading links must match the renamed headings.** Link fragments like `#configuring-wso2-api-manager` are rewritten with `brand_anchor`, which must equal how MkDocs turns the new heading into an id.
- **The footer needs its own rule.** It's `<a href="https://wso2.com/">WSO2</a> LLC.`, so the brand and the legal suffix are split by a link.
- **Passing checks isn't enough; read the changes.** `verify` and `check` prove the rules are safe with today's names and cover every mention. They can't tell whether a change is right. A manual read of every distinct change found link addresses, product values, and possessives that both checks passed.
- **Never change a link address.** The catch-all rules renamed `wso2` inside URLs: external articles (`dzone.com/...-in-wso2-api-manager`), GitHub source paths (`/org/wso2/carbon/`), Maven paths, social profiles, and paths to our own pages. The `url-keep` rule now protects every `https://` address and `{{base_path}}` path after the domain and GitHub rules run. Its pattern also starts at an engine marker (`\x01<n>\x01`), because a domain rule may already have replaced the start of the address. Heading links after `#` still follow renamed headings.
- **Keep rules (`keep: true`, `replace: '\g<0>'`)** protect text after earlier rules ran, unlike masks, which run first. `check` blanks kept text, because it's covered rather than left over.
- **Values the product defines stay** even when they look like sample names: see each mapping's `product-values` rule. A rule's lookbehind must not depend on text another rule protected first, so `product-values` runs first.
- **Three forms of the name.** The company form ("xxxxx Labs") is only for "WSO2" acting or with nothing after it ("WSO2 recommends", "managed by WSO2,"). "WSO2's" takes the brand, because it usually precedes a product ("WSO2's Centralized API Management"). A line ending in "WSO2" keeps the brand, because product names wrap across lines.
- **CRLF files exist.** The engine reads and writes with `newline=""`, so line endings are kept.

## API Platform (docs-bijira main)

- Product rules cover API Platform, AI Gateway, API Gateway, AI Workspace, API Portal, Developer Portal, Policy Hub, Kubernetes Gateway, and Cloud (Bijira), plus the page author "WSO2 API Platform Documentation Team".
- Built-in values the product defines get identifier variables: `managedBy: wso2`, LLM provider template IDs (`wso2-openai`), the GatewayClass `wso2-api-platform`, telemetry keys (`wso2.*`), and the domain verification record `wso2-domain-verification`.
- File paths that contain "bijira" are masked; renaming them would change URLs.

## API Manager (docs-apim)

- **Mostly code values.** Each has its own variable: Java packages (`org.wso2.*`, `-Dorg.wso2.*`, `org-wso2-` loggers), `wso2carbon` and `WSO2CARBON`, uppercase identifiers (`WSO2AM_DB`, `WSO2_SERVER_HOME`), headers (`x-wso2-`, `X-WSO2-`), product slugs (`wso2am`, `wso2is`, `wso2mi`, `wso2apip`), Docker images (`wso2/wso2am*`), `.wso2apictl`, `wso2server.sh`, and fused identifiers such as `wso2user`, `wso2truststore.jks`, and `Wso2@am70`.
- **Example hostnames are not the website.** `gw.wso2.com`, `am.wso2.com`, `websocket.wso2.com`, and about 40 more use `example_domain`. Real sites (`wso2.com`, `helm.`, `registry.`, `maven.wso2.org`, `apim.docs.`) have their own variables.
- **Mask `.md` paths everywhere.** The mkdocs.yml nav lists files like `getting-started-with-wso2-api-controller.md`. Renaming them broke 19 nav entries.
- **Masked external names:** other WSO2 docs sites (`is.docs`, `mi.docs`, …), Carbon XML namespaces (`*.carbon.wso2.org`), the Asgardeo org `/t/wso2devtools`, and OSGi build suffixes (`.wso2v16`).
- **Downloadable samples** under `en/docs/assets` (TOML, scripts, WSDL, archives) are code and out of scope.
- **"WSO2 Labs"** is the internal performance lab, in one sentence on the Scaling the Gateway page. Reword it rather than rename it.
- docs-apim pins MkDocs 1.5.3, so it needs its own build environment (created automatically).
- **Test results:**
  - **4.7.0:** 482 files and about 2,900 replacements. The build had the same 85 warnings as before, and every checked code value count was unchanged. One heading link was already broken in the original (`#configuring-…-api-m-to-perform-regular-cleaning`).
  - **4.6.0:** passed `verify` and `check` with no new rules. Applying it made 22 per-rule commits, and the build had the same 25 warnings before and after, 0 new.
- **Older versions (4.3.0 and earlier)** add Streaming Integrator and EI content: product folders (`<SI_HOME>/wso2/server`), install folders (`/Library/WSO2`, `C:\Program Files\WSO2`), escaped database names (`WSO2\_CARBON\_DB`), configuration keys (`wso2.datasources`), Prometheus metrics (`org_wso2_...`), Choreo Connect images, and leftover Confluence anchors (`#...forWSO2APIManager-...`).
- **Final test (October 30, 2026):** every version from `master` to 3.0.0 passes `verify` and `check`, and every distinct change was read. With test names, no link address changes except local sample addresses. Builds of API Platform `main` (43 warnings, 1,830 pages) and API Manager 4.7.0 (85 warnings, 1,319 pages) match before and after. API Manager 3.0.0 doesn't build in the shared environment even before the rebrand (`partials/palette.html` not found), because it needs older theme packages.
- **Don't pass `-q` to `mkdocs build`** when comparing warnings. It hides them, so both builds report 0.
