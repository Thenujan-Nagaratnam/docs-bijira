#!/usr/bin/env python3
"""Rebrand a docs repository from a mapping file of rules and variables.

Usage:

    rebrand.py --repo PATH --mapping FILE verify
        Rewrite with today's values (<mapping>.today.yml); nothing may change.
    rebrand.py --repo PATH --mapping FILE check
        List WSO2/Bijira text that no rule or mask covers.
    rebrand.py --repo PATH --mapping FILE [--names FILE] apply [--write]
        Rewrite the docs with the mapping's vars, overridden by --names.
    rebrand.py --repo PATH --mapping FILE [--names FILE] commits [--trailer LINE]
        Same rewrite, as one git commit per rule. Needs a clean working tree.

Each rule finds a pattern and replaces it with a value built from {variables}.
Text a rule has replaced is never touched by a later rule, so a value that
still contains "wso2" (an unchanged GitHub org, say) stays as it is.
"""

import argparse
import collections
import os
import re
import subprocess
import sys

import yaml

ROOT = os.getcwd()  # the repository being rebranded; set from --repo in main()
SKIP_DIRS = {".git", "venv", "site", "__pycache__", "node_modules"}
DESCRIPTION_RE = re.compile(r'(?m)^description:\s*"?(.*?)"?\s*$')
DESCRIPTION_LIMIT = 158


def read(path):
    # newline="" keeps CRLF files as CRLF.
    with open(os.path.join(ROOT, path), encoding="utf-8", newline="") as f:
        return f.read()


def write(path, text):
    with open(os.path.join(ROOT, path), "w", encoding="utf-8", newline="") as f:
        f.write(text)


# Markdown segmentation into prose and code
FENCE_RE = re.compile(r"^[ \t>]*(`{3,}|~{3,})")
# Inline code: backtick spans, and raw HTML <code> and <pre> elements in Markdown.
INLINE_CODE_RE = re.compile(r"(`+)([^`\n]+?)\1|<(pre|code)\b[^>]*>.*?</\3>", re.S)


def segments(text, is_markdown):
    """Yield (kind, chunk) pairs that concatenate back to text."""
    if not is_markdown:
        yield "prose", text
        return
    fence = None
    prose_buf = []

    def flush():
        if prose_buf:
            chunk = "".join(prose_buf)
            prose_buf.clear()
            pos = 0
            for m in INLINE_CODE_RE.finditer(chunk):
                if m.start() > pos:
                    yield "prose", chunk[pos:m.start()]
                yield "code", m.group(0)
                pos = m.end()
            if pos < len(chunk):
                yield "prose", chunk[pos:]

    for line in text.splitlines(keepends=True):
        m = FENCE_RE.match(line)
        if fence is None:
            if m:
                yield from flush()
                fence = m.group(1)
                yield "code", line
            else:
                prose_buf.append(line)
        else:
            yield "code", line
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) \
                    and line.strip() == m.group(1):
                fence = None
    yield from flush()



def files_in_scope(mapping):
    """Files the rules apply to, from the mapping's scope section."""
    scope = mapping["scope"]
    exts = tuple(scope.get("extensions", [".md"]))
    excluded = [os.path.normpath(e) for e in scope.get("exclude", [])]
    for entry in scope["paths"]:
        path = os.path.join(ROOT, entry)
        if os.path.isfile(path):
            yield entry
            continue
        for dirpath, dirnames, filenames in os.walk(path):
            rel_dir = os.path.relpath(dirpath, ROOT)
            dirnames[:] = sorted(
                d for d in dirnames
                if d not in SKIP_DIRS and os.path.normpath(os.path.join(rel_dir, d)) not in excluded
            )
            for name in sorted(filenames):
                if name.endswith(exts):
                    yield os.path.relpath(os.path.join(dirpath, name), ROOT)

# Set from --mapping in main(); today.yml sits next to it as <name>.today.yml.
MAPPING_FILE = None
TODAY_FILE = None

VAR_RE = re.compile(r"\{(\w+)\}")
MASK_MARK = "\x00{}\x00"
MASK_MARK_RE = re.compile("\x00(\\d+)\x00")
DONE_MARK = "\x01{}\x01"
DONE_MARK_RE = re.compile("\x01(\\d+)\x01")
ARTICLE_RE = re.compile("\\b([Aa]n?) (\x01(\\d+)\x01)")
LEFTOVER_RE = re.compile(r"wso2|bijira", re.I)


def load_mapping():
    with open(MAPPING_FILE, encoding="utf-8") as f:
        return yaml.safe_load(f)


NAMES_FILE = None  # set from --names in main()


def current_values():
    """The mapping's vars, overridden by any matching keys in the names file."""
    raw = dict(load_mapping()["vars"])
    if NAMES_FILE:
        with open(NAMES_FILE, encoding="utf-8") as f:
            names = yaml.safe_load(f) or {}
        for key, value in names.items():
            if key in raw and value is not None:
                raw[key] = value
    return resolve_vars(raw)


def resolve_vars(raw):
    resolved = {}

    def value(name, chain):
        if name in resolved:
            return resolved[name]
        if name not in raw:
            sys.exit(f"Unknown variable {{{name}}} in mapping.yml (used by {' -> '.join(chain)})")
        if name in chain:
            sys.exit(f"Variable cycle in mapping.yml: {' -> '.join(chain + [name])}")
        text = str(raw[name])
        resolved[name] = VAR_RE.sub(lambda m: value(m.group(1), chain + [name]), text)
        return resolved[name]

    for name in raw:
        value(name, [])
    return resolved


class Rewriter:
    def __init__(self, mapping, values):
        self.masks = [re.compile(m["find"]) for m in mapping["masks"]]
        self.rules = []
        for rule in mapping["rules"]:
            # Fill in {variables}; escape backslashes in values so only \1-style
            # group references in the rule itself are special.
            template = VAR_RE.sub(lambda m: values[m.group(1)].replace("\\", "\\\\"), rule["replace"])
            self.rules.append({
                "id": rule["id"],
                "find": re.compile(rule["find"]),
                "template": template,
                "context": rule.get("context", "any"),
                "when": re.compile(rule["when"]) if rule.get("when") else None,
                "label": rule.get("label", ""),
            })

    def rewrite(self, text, is_markdown, counts):
        """Apply every rule and return the final text."""
        return self.materialize(self.mark(text, is_markdown, counts), len(self.rules))

    def mark(self, text, is_markdown, counts):
        """Run every rule once, recording each replacement instead of making it.

        Returns the text with masks and replacements swapped for markers, the
        masked text, and one (rule index, original, replacement) per match.
        """
        masked, done = [], []

        def mask(m):
            masked.append(m.group(0))
            return MASK_MARK.format(len(masked) - 1)

        for rx in self.masks:
            text = rx.sub(mask, text)

        # Context-free rules first, on whole lines so "when" sees the full line;
        # then prose- and code-specific rules per Markdown segment.
        for index, rule in enumerate(self.rules):
            if rule["context"] == "any":
                text = self._apply(index, rule, text, done, counts)
        out = []
        for kind, chunk in segments(text, is_markdown):
            for index, rule in enumerate(self.rules):
                if rule["context"] == kind:
                    chunk = self._apply(index, rule, chunk, done, counts)
            out.append(chunk)
        return "".join(out), masked, done

    @staticmethod
    def materialize(marked, upto):
        """Text with the replacements of rules [0, upto) made and the rest undone."""
        text, masked, done = marked

        def made(i):
            return done[i][0] < upto

        # "a" or "an" before a replaced value, by its first letter.
        def article(m):
            i = int(m.group(3))
            if not made(i):
                return m.group(0)
            starts_with_vowel = done[i][2][:1].lower() in "aeiou"
            new = "an" if starts_with_vowel else "a"
            return (new.capitalize() if m.group(1)[0].isupper() else new) + " " + m.group(2)

        def expand(s):
            s = ARTICLE_RE.sub(article, s)
            return DONE_MARK_RE.sub(lambda m: expand(piece(int(m.group(1)))), s)

        def piece(i):
            _, original, replacement = done[i]
            return replacement if made(i) else original

        return MASK_MARK_RE.sub(lambda m: masked[int(m.group(1))], expand(text))

    @staticmethod
    def _apply(index, rule, text, done, counts):
        def replace(m):
            replacement = m.expand(rule["template"])
            if rule["id"].endswith("anchor") and m.re.groups:
                replacement = _anchor_article(m.group(1) or "", replacement)
            done.append((index, m.group(0), replacement))
            if replacement != m.group(0):
                counts[rule["id"]] += 1
            return DONE_MARK.format(len(done) - 1)

        if rule["when"] is None:
            return rule["find"].sub(replace, text)
        lines = text.splitlines(keepends=True)
        for i, line in enumerate(lines):
            if rule["when"].search(line):
                lines[i] = rule["find"].sub(replace, line)
        return "".join(lines)


def _anchor_article(prefix, replacement):
    """In a heading link, "a" or "an" before the replaced name, as in #monitoring-an-acme-product."""
    m = re.search(r"(^|-)(an?)-$", prefix)
    if not m:
        return replacement
    value = replacement[len(prefix):]
    article = "an" if value[:1].lower() in "aeiou" else "a"
    return prefix[: m.start(2)] + article + "-" + value


def run(values, write_files, counts=None):
    """Rewrite every scoped file; return {path: (old, new)} for files that change."""
    mapping = load_mapping()
    rewriter = Rewriter(mapping, values)
    counts = counts if counts is not None else collections.Counter()
    changed = {}
    for path in files_in_scope(mapping):
        try:
            text = read(path)
        except UnicodeDecodeError:
            continue
        new = rewriter.rewrite(text, path.endswith(".md"), counts)
        if new != text:
            changed[path] = (text, new)
            if write_files:
                write(path, new)
    return changed


def cmd_apply(args):
    counts = collections.Counter()
    changed = run(current_values(), args.write, counts)
    print(f"{'Changed' if args.write else 'Would change'} {len(changed)} files.")
    long_descriptions = []
    for path, (old, new) in changed.items():
        before, after = DESCRIPTION_RE.search(old), DESCRIPTION_RE.search(new)
        if before and after and before.group(1) != after.group(1) and len(after.group(1)) >= DESCRIPTION_LIMIT:
            long_descriptions.append((path, len(after.group(1))))
    if long_descriptions:
        print(f"{len(long_descriptions)} changed descriptions reach {DESCRIPTION_LIMIT} characters or more:")
        for path, n in long_descriptions:
            print(f"  {path}: {n}")
    if not args.write:
        print("Dry run. Re-run with --write to apply.")


def cmd_verify(args):
    with open(TODAY_FILE, encoding="utf-8") as f:
        today = yaml.safe_load(f)
    missing = set(load_mapping()["vars"]) - set(today)
    if missing:
        sys.exit("today.yml has no value for: " + ", ".join(sorted(missing)))
    changed = run(resolve_vars(today), False)
    if not changed:
        print("OK: the mapping reproduces the docs exactly.")
        return
    print(f"{len(changed)} files would change:")
    for path, (old, new) in changed.items():
        for a, b in zip(old.splitlines(), new.splitlines()):
            if a != b:
                print(f"  {path}\n    - {a.strip()[:150]}\n    + {b.strip()[:150]}")
                break
    sys.exit(1)


def cmd_check(args):
    # Empty every variable, so any WSO2 or Bijira left after the rules is text
    # no rule or mask covers.
    values = {name: "" for name in load_mapping()["vars"]}
    mapping = load_mapping()
    masks = [re.compile(m["find"]) for m in mapping["masks"]]
    hits = []
    for path, (_, new) in run(values, False).items():
        for rx in masks:
            new = rx.sub("", new)
        for line in new.splitlines():
            if LEFTOVER_RE.search(line):
                hits.append(f"  {path}: {line.strip()[:160]}")
    if not hits:
        print("Every WSO2 and Bijira reference is covered by a rule or a mask.")
        return
    print(f"{len(hits)} lines with uncovered references:")
    print("\n".join(hits))
    sys.exit(1 if args.strict else 0)


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout


def cmd_commits(args):
    """Apply the rebrand as one commit per rule, in rule order."""
    dirty = [line for line in git("status", "--porcelain", "--untracked-files=no").splitlines()]
    if dirty:
        sys.exit("Commit or stash your changes first; the working tree must be clean:\n" + "\n".join(dirty))

    mapping = load_mapping()
    rewriter = Rewriter(mapping, current_values())
    marked, current = {}, {}
    examples = collections.defaultdict(collections.Counter)
    for path in files_in_scope(mapping):
        try:
            text = read(path)
        except UnicodeDecodeError:
            continue
        result = rewriter.mark(text, path.endswith(".md"), collections.Counter())
        if result[2]:
            marked[path], current[path] = result, text
            for index, original, replacement in result[2]:
                original = DONE_MARK_RE.sub("", original)
                if original != replacement:
                    examples[index][(original, replacement)] += 1

    made = 0
    for index, rule in enumerate(rewriter.rules):
        if not examples[index]:
            continue
        touched = []
        for path, result in marked.items():
            new = Rewriter.materialize(result, index + 1)
            if new != current[path]:
                write(path, new)
                current[path] = new
                touched.append(path)
        if not touched:
            continue
        pairs = examples[index].most_common()
        total = sum(n for _, n in pairs)
        original, replacement = pairs[0][0]
        subject = f'Rebrand: replace "{original}" with "{replacement}"'
        if len(pairs) > 1:
            subject += " and similar"
        if rule["label"]:
            subject += f" {rule['label']}"
        body = [f"Rule {rule['id']}: {total} replacements in {len(touched)} files.", ""]
        body += [f'- "{o}" -> "{r}" ({n})' for (o, r), n in pairs[:10]]
        if len(pairs) > 10:
            body.append(f"- and {len(pairs) - 10} more forms")
        if args.trailer:
            body += [""] + args.trailer
        git("add", "--", *touched)
        git("commit", "-q", "-m", subject, "-m", "\n".join(body))
        made += 1
        print(f"{made:>3}. {rule['id']}: {total} replacements in {len(touched)} files")

    # The last commit must equal the single-pass rewrite.
    for path, result in marked.items():
        if current[path] != Rewriter.materialize(result, len(rewriter.rules)):
            sys.exit(f"Mismatch with the single-pass result in {path}")
    print(f"Made {made} commits; the result matches a single-pass apply.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", default=os.getcwd(), help="repository to rebrand (default: current directory)")
    parser.add_argument("--mapping", required=True, help="mapping file with the rules and variables")
    parser.add_argument("--names", help="YAML file of final names that override the mapping's vars")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("apply", help="rewrite the docs with the vars in mapping.yml")
    p.add_argument("--write", action="store_true")
    p.set_defaults(func=cmd_apply)
    p = sub.add_parser("verify", help="check that today's values (today.yml) reproduce the docs exactly")
    p.set_defaults(func=cmd_verify)
    p = sub.add_parser("commits", help="apply the rebrand as one git commit per rule")
    p.add_argument("--trailer", action="append", default=[],
                   help='line to end every commit message with, for example "Co-Authored-By: ..."')
    p.set_defaults(func=cmd_commits)
    p = sub.add_parser("check", help="list WSO2 and Bijira text that no rule or mask covers")
    p.add_argument("--strict", action="store_true", help="exit 1 when anything is uncovered")
    p.set_defaults(func=cmd_check)
    args = parser.parse_args()
    global ROOT, MAPPING_FILE, TODAY_FILE, NAMES_FILE
    ROOT = os.path.abspath(args.repo)
    MAPPING_FILE = os.path.abspath(args.mapping)
    TODAY_FILE = os.path.splitext(MAPPING_FILE)[0] + ".today.yml"
    NAMES_FILE = os.path.abspath(args.names) if args.names else None
    args.func(args)


if __name__ == "__main__":
    main()
