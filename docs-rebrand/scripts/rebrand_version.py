#!/usr/bin/env python3
"""Rebrand one version of the API Platform or API Manager docs.

    rebrand_version.py SITE VERSION [--build] [--no-commit] [--names FILE] [--repo PATH]
    rebrand_version.py --here [--build] ...     (run in the current folder; site and version detected)

    SITE      api-platform or api-manager
    VERSION   a branch listed for the site in config.yml (main, master, 4.7.0, ...)

Steps:
  1. Fetch the version's branch and create a worktree on rebrand/<site>-<version>,
     or with --repo, use an existing local checkout as it is.
  2. verify: today's names must reproduce the docs exactly.
  3. check: every WSO2 and Bijira mention must be covered by a rule or a mask.
  4. Apply the final names from names.yml, as one commit per rule
     (--no-commit leaves the changes uncommitted instead).
  5. --build: build the site before and after, and compare the warnings.

It stops at the first step that fails and never pushes.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
CACHE = os.path.expanduser("~/.cache/docs-rebrand")


def sh(cmd, cwd=None, check=True, capture=False):
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=capture)
    if check and result.returncode != 0:
        if capture:
            sys.stderr.write(result.stdout + result.stderr)
        sys.exit(f"Failed: {' '.join(cmd)}")
    return result


def step(title):
    print(f"\n== {title}", flush=True)


def load_yaml(path):
    # PyYAML may be missing from the system Python; read with the site venv.
    import yaml
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def site_python(site, worktree):
    """A Python with the site's build requirements (and PyYAML), created once and cached."""
    venv = os.path.join(CACHE, f"venv-{site}")
    python = os.path.join(venv, "bin", "python")
    if not os.path.exists(python):
        step(f"Creating the {site} build environment in {venv}")
        sh([sys.executable, "-m", "venv", venv])
        sh([python, "-m", "pip", "install", "-q", "-r", os.path.join(worktree, "en", "requirements.txt"),
            "setuptools<80"])
    return python


ENV_REPO = {"api-platform": "DOCS_REBRAND_API_PLATFORM_REPO", "api-manager": "DOCS_REBRAND_API_MANAGER_REPO"}
GITHUB_REPO = {"api-platform": "wso2/docs-bijira", "api-manager": "wso2/docs-apim"}


def clone_from_cwd(site):
    """The clone of the site's repository that the current folder is in, if any."""
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], text=True, capture_output=True)
    if top.returncode != 0:
        return None
    root = top.stdout.strip()
    remotes = subprocess.run(["git", "-C", root, "remote", "-v"], text=True, capture_output=True).stdout
    if GITHUB_REPO[site] in remotes.replace(":", "/"):
        # In a linked worktree, use the main clone so new worktrees sit beside it.
        common = subprocess.run(["git", "-C", root, "rev-parse", "--path-format=absolute", "--git-common-dir"],
                                text=True, capture_output=True).stdout.strip()
        return os.path.dirname(common) if common.endswith(".git") else root
    return None


def local_repo(site_cfg, site):
    """The local clone: an environment variable, else config.yml, else the clone you're in."""
    repo = os.environ.get(ENV_REPO[site]) or site_cfg.get("repo") or clone_from_cwd(site) or ""
    repo = os.path.abspath(os.path.expanduser(repo)) if repo else ""
    if not repo or not os.path.exists(os.path.join(repo, ".git")):
        sys.exit(f"Couldn't find a local clone of {GITHUB_REPO[site]}. Run from inside your clone, "
                 f"set {ENV_REPO[site]}, or pass --repo PATH.")
    return repo


def wso2_remote(repo, site):
    """The remote that points at the WSO2 repository, whatever it's called."""
    lines = sh(["git", "-C", repo, "remote", "-v"], capture=True).stdout.splitlines()
    for line in lines:
        name, url = line.split()[:2]
        if GITHUB_REPO[site] in url.replace(":", "/"):
            return name
    sys.exit(f"{repo} has no remote pointing at {GITHUB_REPO[site]}. "
             f"Add one: git -C {repo} remote add upstream https://github.com/{GITHUB_REPO[site]}.git")


def prepare_worktree(cfg, site_cfg, site, version):
    repo = local_repo(site_cfg, site)
    remote = wso2_remote(repo, site)
    branch = f"rebrand/{site}-{version}"
    worktree_dir = os.environ.get("DOCS_REBRAND_WORKTREE_DIR") or cfg.get("worktree_dir") \
        or os.path.join(os.path.dirname(repo), "rebrand-worktrees")
    path = os.path.join(os.path.expanduser(worktree_dir), f"{site}-{version}")
    step(f"Preparing {path} on {branch} from {remote}/{version}")
    sh(["git", "-C", repo, "fetch", "-q", remote, version])
    if os.path.isdir(path):
        status = sh(["git", "-C", path, "status", "--porcelain", "--untracked-files=no"], capture=True).stdout
        if status.strip():
            sys.exit(f"{path} has uncommitted changes. Commit, stash, or remove the worktree first.")
        current = sh(["git", "-C", path, "branch", "--show-current"], capture=True).stdout.strip()
        if current != branch:
            sys.exit(f"{path} is on {current}, not {branch}. Remove it or choose another worktree_dir.")
        print(f"Reusing the existing worktree on {branch}.")
        return path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    exists = sh(["git", "-C", repo, "rev-parse", "--verify", "--quiet", branch], check=False, capture=True)
    if exists.returncode == 0:
        sh(["git", "-C", repo, "worktree", "add", "-q", path, branch])
    else:
        sh(["git", "-C", repo, "worktree", "add", "-q", "-b", branch, path, f"{remote}/{version}"])
    return path


def git_toplevel(path):
    result = sh(["git", "-C", path, "rev-parse", "--show-toplevel"], check=False, capture=True)
    if result.returncode != 0:
        sys.exit(f"{path} isn't inside a git repository.")
    return result.stdout.strip()


def detect_site_version(repo, cfg):
    """Guess the site from the remote URLs and the version from the branch."""
    remotes = sh(["git", "-C", repo, "remote", "-v"], capture=True).stdout
    site = "api-manager" if "docs-apim" in remotes else "api-platform" if "docs-bijira" in remotes else None
    if not site:
        return None, None
    versions = [str(v) for v in cfg["sites"][site]["versions"]]
    upstream = sh(["git", "-C", repo, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
                  check=False, capture=True).stdout.strip()
    branch = sh(["git", "-C", repo, "branch", "--show-current"], capture=True).stdout.strip()
    for candidate in (upstream.split("/", 1)[-1] if upstream else "", branch):
        if candidate in versions:
            return site, candidate
    for candidate in (upstream, branch):
        for v in sorted(versions, key=len, reverse=True):
            if candidate.endswith(v) or f"-{v}" in candidate or f"/{v}" in candidate:
                return site, v
    return site, None


def use_local_checkout(path, version):
    """Run in an existing checkout instead of creating a worktree."""
    path = os.path.abspath(os.path.expanduser(path))
    step(f"Using the local checkout {path}")
    if not os.path.isdir(os.path.join(path, "en", "docs")):
        sys.exit(f"{path} doesn't look like a docs repository (no en/docs).")
    status = sh(["git", "-C", path, "status", "--porcelain", "--untracked-files=no"], capture=True).stdout
    if status.strip():
        sys.exit(f"{path} has uncommitted changes. Commit or stash them first.")
    branch = sh(["git", "-C", path, "branch", "--show-current"], capture=True).stdout.strip()
    upstream = sh(["git", "-C", path, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
                  check=False, capture=True).stdout.strip()
    print(f"Branch: {branch or '(detached)'}" + (f", tracking {upstream}" if upstream else ""))
    if version not in branch and not upstream.endswith("/" + version):
        print(f"Warning: this branch doesn't look like {version}. The rules still run on whatever is checked out.")
    return path


def build(python, worktree, out_dir, log):
    with open(log, "w") as f:
        result = subprocess.run([python, "-m", "mkdocs", "build", "-d", out_dir],
                                cwd=os.path.join(worktree, "en"), stdout=f, stderr=subprocess.STDOUT)
    warnings = set()
    with open(log, encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "WARNING" in line:
                warnings.add(line.replace("\x1b[33m", "").replace("\x1b[0m", "").strip())
    return result.returncode, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("site", nargs="?", choices=["api-platform", "api-manager"],
                        help="optional with --here, which detects it")
    parser.add_argument("version", nargs="?", help="optional with --here, which detects it")
    parser.add_argument("--names", default=os.path.join(SKILL, "names.yml"),
                        help="final names (default: names.yml in the skill)")
    parser.add_argument("--build", action="store_true", help="build before and after, and compare warnings")
    parser.add_argument("--no-commit", action="store_true", help="apply without committing")
    parser.add_argument("--check-only", action="store_true", help="stop after verify and check")
    parser.add_argument("--repo", help="use this local checkout as it is: no fetch, no worktree")
    parser.add_argument("--here", action="store_true",
                        help="use the current folder as the checkout, and detect the site and version")
    args = parser.parse_args()

    cfg = load_yaml(os.path.join(SKILL, "config.yml"))
    if args.here:
        args.repo = git_toplevel(os.getcwd())
        site, version = detect_site_version(args.repo, cfg)
        args.site = args.site or site
        args.version = args.version or version
        if not args.site or not args.version:
            sys.exit("Couldn't detect the site or version here; pass them, for example: api-manager 4.7.0 --here")
        print(f"Detected {args.site} {args.version} in {args.repo}")
    elif not args.site or not args.version:
        parser.error("site and version are required unless --here is used")
    site_cfg = cfg["sites"][args.site]
    if args.version not in [str(v) for v in site_cfg["versions"]]:
        sys.exit(f"{args.version} isn't a {args.site} version in config.yml: "
                 f"{', '.join(str(v) for v in site_cfg['versions'])}")
    mapping = os.path.join(SKILL, "mappings", f"{args.site}.yml")

    if args.repo:
        worktree = use_local_checkout(args.repo, args.version)
    else:
        worktree = prepare_worktree(cfg, site_cfg, args.site, args.version)
    python = site_python(args.site, worktree)
    engine = [python, os.path.join(HERE, "rebrand.py"), "--repo", worktree, "--mapping", mapping]

    step("verify: today's names must reproduce the docs exactly")
    if sh(engine + ["verify"], check=False).returncode != 0:
        sys.exit("verify failed. A rule changes text it shouldn't; fix the mapping and run again.")

    step("check: every WSO2 and Bijira mention must be covered")
    if sh(engine + ["check", "--strict"], check=False).returncode != 0:
        sys.exit("check failed. Add a rule or a mask for the lines above, then run again.")

    if args.check_only:
        print(f"\nChecks passed. Worktree: {worktree}")
        return

    names = load_yaml(args.names) or {}
    missing = [k for k in ("brand", "legal_suffix", "brand_slug") if not names.get(k)]
    if missing:
        sys.exit(f"Set {', '.join(missing)} in {args.names} before applying.")
    engine_names = engine + ["--names", args.names]

    tmp = tempfile.mkdtemp(prefix=f"rebrand-{args.site}-{args.version}-")
    if args.build:
        step("Building the site before the rebrand")
        code, before = build(python, worktree, os.path.join(tmp, "site-before"), os.path.join(tmp, "before.log"))
        if code != 0:
            sys.exit(f"The original build fails; see {tmp}/before.log")
        print(f"{len(before)} warnings")

    if args.no_commit:
        step("Applying the final names (not committed)")
        sh(engine_names + ["apply", "--write"])
    else:
        step("Applying the final names as one commit per rule")
        sh(engine_names + ["commits"])

    if args.build:
        step("Building the site after the rebrand")
        code, after = build(python, worktree, os.path.join(tmp, "site-after"), os.path.join(tmp, "after.log"))
        if code != 0:
            sys.exit(f"The rebranded build fails; see {tmp}/after.log")
        new = sorted(after - before)
        print(f"{len(after)} warnings; {len(new)} new")
        for line in new:
            print("  " + line)
        print(f"Built sites: {tmp}/site-before and {tmp}/site-after")
    else:
        shutil.rmtree(tmp, ignore_errors=True)

    branch = sh(["git", "-C", worktree, "branch", "--show-current"], capture=True).stdout.strip()
    print(f"\nDone. Branch {branch} in {worktree}. Nothing was pushed.")


if __name__ == "__main__":
    main()
