# docs-shared

Hosts the artifacts every product+version branch depends on at runtime/build
time, so they're maintained in exactly one place instead of copy-pasted
across dozens of branches:

- `assets/theme.js` - client-side cross-product navigation, version
  dropdowns, search breadcrumbs. Every product+version deployment loads this
  via `extra_javascript` in its own `mkdocs.yml`.
- `assets/root-index.json` - the single list of every product's slug, title,
  and `manifestUrl` (where to fetch that product's cross-product nav data),
  plus `_liveSiteBase` (fallback URL for a version not present in the current
  build). `theme.js` fetches this at runtime to build the cross-product
  sidebar.
- `docs_shared_hooks/` - the mkdocs build-hook logic (manifest building,
  cache-busting, redirects, `{BASE_URL}` resolution). Installed by every
  product+version branch via `pip install git+https://github.com/<fork>/docs-api-platform.git@<tag>`
  (see `requirements.txt` in any product branch) - never copied.

This branch deploys as its own tiny nginx-only Choreo component (see
`Dockerfile`) - no mkdocs/Python build stage, just static files.

## Choreo config mount

**`root-index.json` is the one file in this whole architecture meant to be
overridden via Choreo's config-file-mount feature**, since it's the only
place a `manifestUrl` lives and it's read at runtime (fetched by the
browser), not baked into any build.

- **File to mount:** `root-index.json`
- **Container path:** `/usr/share/nginx/html/root-index.json`
- **Content:** the `{"products": {...}, "_liveSiteBase": "..."}` structure -
  see the current committed `assets/root-index.json` for the exact shape.

No other file here, and no other branch in this whole project, needs a
config mount. Everything else (the `theme.js` URL baked into each product's
`extra_javascript`, the `docs-shared-hooks` git tag pin in each product's
`requirements.txt`, this branch's own `SHARED_BASE` constant inside
`theme.js`) is baked in at build time and requires an actual commit + rebuild
to change - see each product branch's own `README.md` for that gotcha.

## Tagging

Cut a new `shared-vN` tag whenever `docs_shared_hooks` or `theme.js`
actually changes, then bump every product branch's `requirements.txt` pin to
match - a branch left on an old tag silently keeps using old hook logic with
no warning.

## Shared files under each build's own prefix

MkDocs writes a site's shared files at the site root: `assets/` (theme CSS/JS,
fonts, images), `search/`, `js/` and `sitemap.xml`. Every product+version is a
separate build behind one URL space, so those root paths look the same for
every build, and the reverse proxy can send them to only one backend. Every
product then loads that one build's (possibly stale) images, styles and search
index.

So after the build, `docs_shared_hooks` moves them under the build's own prefix
(e.g. `api-gateway/1.2.0/assets/`), which the proxy already routes to the right
deployment, and points every page at the new location (including Material's
`base`, which search, its worker and `sitemap.xml` are read from). The search
index is rewritten to match, and `sitemap.xml` keeps only the build's own pages.

- The prefix is the one `<slug>/<version>` of `extra.versioned_sections` that
  the build's navigation has pages under, or its one `extra.unversioned_sections`
  slug. Set `extra.assets_prefix` in `mkdocs.yml` to override it (`""` keeps the
  files at the root).
- A build that serves several sections at the root (platform-common) keeps its
  files at the root. Once every product+version build is on a hooks tag with this
  change, the root `/assets/` and `/search/` should be routed to platform-common.
