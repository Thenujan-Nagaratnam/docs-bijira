# Launch day checklist

The team's copy lives in Notion ("Launch Day Checklist"). This is the summary.

## Before you start
- Content freeze is on for both sites.
- Final names are in `names.yml`: brand, legal suffix, lowercase brand, and any product overrides.
- New logo and favicon files are ready.
- The "WSO2 is now <brand>" page is written.

## Changes on launch day
- **API Platform docs (`main`):** company name, product names, legal name in the footer, site name and page titles, page author, logo and favicon, header and footer, community links, example names in code samples, the home page with a link to the rename page, and `llms.txt`.
- **API Manager docs:** `master` and 4.7.0 to 3.0.0. In each, the company name, product names, legal name, site name ("WSO2 API Manager Documentation") and page titles, logo and favicon, header and footer, community links, example names, and the home page.
- **Run per version:** `rebrand_version.py <site> <version> --build`. The logo, favicon, and rename page are separate manual changes.

## Leave unchanged
- Package names (`org.wso2.carbon`)
- Default passwords and keystores (`wso2carbon`)
- Download, file, and image names (`wso2am-4.7.0`, `wso2apip-ai-gateway-1.2.0.zip`, `wso2/wso2am`)
- Environment variables, headers, and database names (`WSO2AM_DB`, `x-wso2-`)
- Example hostnames (`gw.wso2.com`)
- Domains and URLs
- GitHub links
- Screenshots

## Deploy and check
- Deploy both sites.
- On each site:
  - The home page shows the new name and logo.
  - Pages from each product and version show the new name.
  - The version selector works.
  - Search shows the new names.
  - The 404 page and browser tab show the new brand.
  - An install command still works.
  - No "WSO2" text is left except the items above.

## Finish
- Publish the rename page and link it from both home pages.
- End the content freeze.
- Tell the team.
