# Docs rebrand skill

A Claude Code skill that rebrands the API Platform docs (`wso2/docs-bijira`,
`main`) and the API Manager docs (`wso2/docs-apim`, `master` and 3.0.0 to 4.7.0)
from WSO2 to the new company name, one site and version at a time.

For each version it does the following, then stops and tells you what it did:

1. Creates a separate worktree on a `rebrand/<site>-<version>` branch, so your own checkout isn't touched.
2. Checks that the rules are safe: rewriting with today's names must change nothing, and every WSO2 mention must be covered by a rule.
3. Applies the final names as one commit per kind of change, such as "Rebrand: replace "WSO2 API Manager" with "xxxxx API Manager"".
4. Optionally builds the site before and after, and reports any new build warnings.

It never pushes or opens a pull request.

## Set up

1. **Install the prerequisites:** [Claude Code](https://docs.claude.com/en/docs/claude-code), git, and Python 3 with PyYAML:

   ```sh
   python3 -m pip install pyyaml
   ```

2. **Install the plugin.** In Claude Code, add this marketplace, then install the plugin from it:

   ```text
   /plugin marketplace add Thenujan-Nagaratnam/docs-bijira#rebrand-skill
   /plugin install docs-rebrand@wso2-docs-rebrand
   ```

   Or from a terminal:

   ```sh
   claude plugin marketplace add Thenujan-Nagaratnam/docs-bijira#rebrand-skill
   claude plugin install docs-rebrand@wso2-docs-rebrand
   ```

   Run `/reload-plugins` or start a new session, and `docs-rebrand` appears among your skills.

3. **Have local clones of both docs repositories.** Each needs a remote that points at the WSO2 repository (`wso2/docs-bijira` or `wso2/docs-apim`). The remote can have any name, such as `upstream` or `origin`. If yours is a fork, add one:

   ```sh
   git -C ~/path/to/docs-apim remote add upstream https://github.com/wso2/docs-apim.git
   ```

   The skill uses the clone you run Claude Code in. To run it from anywhere else, set:

   ```sh
   export DOCS_REBRAND_API_PLATFORM_REPO=~/path/to/docs-bijira
   export DOCS_REBRAND_API_MANAGER_REPO=~/path/to/docs-apim
   export DOCS_REBRAND_WORKTREE_DIR=~/path/to/rebrand-worktrees   # optional; default: next to the clone
   ```

Each site gets a build environment in `~/.cache/docs-rebrand/` the first time it runs, which takes a few minutes.

### Update

The final names live in `skills/docs-rebrand/names.yml` in this repository, so everyone gets them with the plugin. When the names or rules change, update your copy:

```text
/plugin marketplace update wso2-docs-rebrand
```

Then open `/plugin`, go to the **Installed** tab, and select **Update now**. Or turn on auto-update for the marketplace under `/plugin` > **Marketplaces**.

## Use it

### Ask Claude

Open Claude Code inside your docs-apim or docs-bijira clone, and ask, for example:

- "Check the rebrand rules for API Manager 4.5.0."
- "Rebrand API Manager 4.6.0 and build it."
- "Dry-run the rebrand on API Platform main with the brand Acme."

### Or run the script

From inside the matching clone, with the path to the installed skill (Claude Code keeps it under `~/.claude/plugins/cache/wso2-docs-rebrand/docs-rebrand/`):

```sh
SKILL=$(ls -d ~/.claude/plugins/cache/wso2-docs-rebrand/docs-rebrand/*/skills/docs-rebrand | tail -1)

# Check that the rules cover a version (no changes are made)
python3 $SKILL/scripts/rebrand_version.py api-manager 4.5.0 --check-only

# Rebrand a version and compare builds
python3 $SKILL/scripts/rebrand_version.py api-manager 4.6.0 --build

# Dry run with test names instead of names.yml
printf 'brand: Acme\ncompany: Acme Labs\nbrand_slug: acme\n' > /tmp/test-names.yml
python3 $SKILL/scripts/rebrand_version.py api-platform main --build --names /tmp/test-names.yml

# Use the current checkout as it is, with the site and version detected
python3 $SKILL/scripts/rebrand_version.py --here --check-only
```

| Option | What it does |
| --- | --- |
| `--check-only` | Runs the two checks and stops. Nothing changes. |
| `--build` | Builds the site before and after, and reports new warnings. |
| `--no-commit` | Applies the names without committing. |
| `--names FILE` | Uses another names file, such as one for a dry run. |
| `--here` | Uses the current checkout as it is, and detects the site and version. |
| `--repo PATH` | Uses that checkout as it is: no fetch, no worktree. |

To undo a run, remove its worktree and delete its `rebrand/<site>-<version>` branch.

## What it changes and what it leaves

It changes what people read: the company name, product names, the legal name in the footer, site names, page titles, and example names in code samples.

It leaves anything readers copy into a terminal or config file unchanged until the product itself is renamed:
- package names (`org.wso2.carbon`)
- default passwords and keystores (`wso2carbon`)
- download, file, and image names (`wso2am-4.7.0`, `wso2/wso2am`)
- database names, headers, and environment variables
- example hostnames (`gw.wso2.com`)
- domains and GitHub links

Page file names and URLs are never renamed.

## Status

| Site and version | Status |
| --- | --- |
| API Platform `main` | Checks pass; changes read by hand; a test build had the same 43 warnings and 1,830 pages before and after |
| API Manager 4.7.0 | Checks pass; changes read by hand; a test build had the same 85 warnings and 1,319 pages before and after |
| API Manager `master`, 4.6.0 to 3.0.0 | Checks pass; changes read by hand |

Builds with `--build` use one environment per site. API Manager 3.0.0 and other old versions may need older theme packages, so their build can fail before the rebrand too.

## Files

| Path | Contents |
| --- | --- |
| `.claude-plugin/marketplace.json`, `plugin.json` | The marketplace and the plugin |
| `skills/docs-rebrand/SKILL.md` | Instructions Claude follows |
| `skills/docs-rebrand/scripts/rebrand_version.py` | The command: one site and version, end to end |
| `skills/docs-rebrand/scripts/rebrand.py` | The rewrite engine (`verify`, `check`, `apply`, `commits`) |
| `skills/docs-rebrand/mappings/` | Each site's rules, protected patterns, file scope, and name variables, plus today's names used to check them |
| `skills/docs-rebrand/names.yml` | The final names. Fill these in here, in the repository. |
| `skills/docs-rebrand/config.yml` | Versions, and optional clone paths |
| `skills/docs-rebrand/references/` | Product name mappings, known problems and fixes, and the launch-day checklist |
