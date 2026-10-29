---
name: docs-rebrand
description: Rebrand the WSO2 API Platform docs (wso2/docs-bijira main) and the WSO2 API Manager docs (wso2/docs-apim, master and 3.0.0 to 4.7.0) from WSO2 to the new company name, one site and version at a time. Use when asked to rebrand, rename WSO2, apply the new brand or product names, dry-run or verify the rebrand, or add rules for a version that fails the checks.
---

# Docs rebrand

Rebrands one site and version per run: it creates a worktree, proves the rules
are safe, applies the final names as one commit per rule, and optionally builds
the site before and after to compare warnings.

| Site | Repository | Versions |
| --- | --- | --- |
| `api-platform` | `wso2/docs-bijira` | `main` only |
| `api-manager` | `wso2/docs-apim` | `master`, `4.7.0`, `4.6.0`, `4.5.0`, `4.4.0`, `4.3.0`, `4.2.0`, `4.1.0`, `4.0.0`, `3.2.0`, `3.1.0`, `3.0.0` |

## Setup

Install by placing this folder at `~/.claude/skills/docs-rebrand/`. Each person needs local clones of `wso2/docs-bijira` and `wso2/docs-apim`, git, and Python 3 with PyYAML. The skill finds a clone in this order:

1. The environment variables `DOCS_REBRAND_API_PLATFORM_REPO` and `DOCS_REBRAND_API_MANAGER_REPO`
2. A `repo` path in `config.yml`
3. The clone the command is run from, so running Claude Code inside a docs-apim clone and asking for an API Manager version just works

Version worktrees go next to the clone, in `rebrand-worktrees/`, unless `DOCS_REBRAND_WORKTREE_DIR` is set. The remote pointing at `wso2/docs-bijira` or `wso2/docs-apim` is found automatically, whatever it's called.

## Files

- `scripts/rebrand_version.py`: the command to run, with a site and a version.
- `scripts/rebrand.py`: the engine (`verify`, `check`, `apply`, `commits`). The command calls it.
- `mappings/api-platform.yml`, `mappings/api-manager.yml`: each site's rules, masks, file scope, and variables. Every variable defaults to today's value.
- `mappings/*.today.yml`: today's value of every variable. `verify` uses these files; never edit them to rebrand.
- `names.yml`: the final names. It overrides matching variables in either mapping.
- `references/product-names.md`: every product name and its new form.
- `references/gotchas.md`: problems found while building the rules, and how they were solved.
- `references/launch-checklist.md`: what changes on launch day and what stays.

## Workflow

1. **Identify the site and version.** "API Manager 4.6.0" is `api-manager 4.6.0`; "API Platform" is `api-platform main`. If the version isn't in `config.yml`, stop and ask.
2. **Check first.** Run from inside the site's clone, or set the environment variables:

   ```sh
   python3 ~/.claude/skills/docs-rebrand/scripts/rebrand_version.py <site> <version> --check-only
   ```

   This fetches the branch into the local repo from `config.yml`, creates `<worktree_dir>/<site>-<version>` on branch `rebrand/<site>-<version>`, and runs both checks. The user's own checkout isn't touched. The first run per site also creates a build environment in `~/.cache/docs-rebrand/`.

   If the user is inside a checkout of the version, run `rebrand_version.py --here --check-only` instead; the site and version are detected. To use another existing checkout, add `--repo <path>`. It uses that folder as it is, with no fetch and no worktree, on whatever branch is checked out. It needs a clean working tree, and it warns if the branch doesn't look like the version named.
3. **If `verify` fails**, a rule changes text it shouldn't. Find the rule from the printed line and narrow it, or add a mask. Don't change `*.today.yml`.
4. **If `check` fails**, some WSO2 text has no rule. Decide for each printed line, then rerun step 2:
   - **Brand or product name in text:** add or extend a product rule.
   - **Code value** (package, password, file, image, database, header, environment variable, example hostname): add a rule that maps it to a variable whose default is today's value, so it doesn't change unless someone sets that variable.
   - **A name WSO2 doesn't own, or a file path:** add a mask.
   Keep the rules shared across versions, and rerun `--check-only` on the versions already done to confirm they still pass.
5. **Confirm the names.** `names.yml` must have `brand`, `legal_suffix`, and `brand_slug`. If they're empty, ask the user. For a dry run, pass a test file with `--names`, for example one that sets the brand to `Acme`.
6. **Apply and build:**

   ```sh
   python3 ~/.claude/skills/docs-rebrand/scripts/rebrand_version.py <site> <version> --build
   ```

   This applies the names as one commit per rule, such as "Rebrand: replace "WSO2 API Manager" with "Acme API Manager"", then builds before and after. It must report 0 new warnings. Use `--no-commit` to leave the changes uncommitted instead.
7. **Report:** the branch, the number of commits, the files changed, the warning comparison, and anything that needs a decision. Don't push or open a pull request unless asked, and don't add a Co-Authored-By trailer to commits.

## Rules of thumb

- **People-facing names change; code values don't.** Product names, the legal name, site names, and example display names change. Packages (`org.wso2.*`), default credentials (`wso2carbon`), file and image names (`wso2am-4.7.0`, `wso2/wso2am`), database names (`WSO2AM_DB`), headers (`x-wso2-`), environment variables, and example hostnames (`gw.wso2.com`) keep today's value through their variables.
- **Never rename file paths or URLs.** Masks protect page file names, links to other WSO2 docs sites, and license headers.
- **A rule set is only trusted for a version after `verify` and `check` pass on it.** API Manager rules were built on 4.7.0 and proven on 4.6.0; older versions may need more rules.
- **To undo a test run**, remove the worktree and delete its `rebrand/<site>-<version>` branch.

## Known decisions still open

These are listed in `references/product-names.md`:
- whether Bijira, Asgardeo, Choreo, Devant, Moesif, and Ballerina keep their names
- what happens to older product names in old versions
- whether short forms such as API-M and IS stay
