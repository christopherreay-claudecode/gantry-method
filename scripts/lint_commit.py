#!/usr/bin/env python3
"""Commit lint — gantry's bootstrap template for the client contract §6.

Origin: metalKnee-physics-2 tools/lint_commit.py (kickoff §5a), generalized.
This file is NOT run from the gantry repo: hooks/install-commit-lint.sh copies
it into a client's tools/ where the CLIENT versions it — commit rules are the
client's own law and must survive a clean clone with no gantry present.

Verifies, for a given commit (default: staged / HEAD):
  1. Every commit message references >=1 issue as #NNNN.
  2. Referenced issues actually exist as files.
  3. `closes #NNNN` targets are NOT human-gated issue types
     (ambiguity / freeze-request / amendment-proposal close only by sign-off).
  4. No commit touches a core path (--core-prefix) without an issue ref.

Usage:
  tools/lint_commit.py --message "<msg>" --files a b c   # commit-msg hook style
  tools/lint_commit.py --rev HEAD                         # inspect a commit
Options:
  --tracker-dir issues        tracker directory relative to repo root
  --core-prefix simcore/      repeatable; paths needing an issue ref to touch
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

HUMAN_GATED = {"ambiguity", "freeze-request", "amendment-proposal"}
REF_RE = re.compile(r"#(\d{1,4})\b")
CLOSES_RE = re.compile(r"\b(?:closes|closed|fixes|resolves)\s+#(\d{1,4})\b", re.I)


def issue_path(tracker: Path, num: int):
    hits = list(tracker.glob(f"{num:04d}-*.md"))
    return hits[0] if hits else None


def issue_type(tracker: Path, num: int):
    p = issue_path(tracker, num)
    if not p:
        return None
    for line in p.read_text().splitlines():
        m = re.match(r"^type:\s*(\S+)", line.strip())
        if m:
            return m.group(1)
    return None


def lint(message: str, files, tracker: Path, core_prefixes):
    errors = []
    refs = [int(n) for n in REF_RE.findall(message)]
    closes = [int(n) for n in CLOSES_RE.findall(message)]

    touches_core = any(f.startswith(p) for f in files for p in core_prefixes)

    if not refs:
        if touches_core:
            errors.append("commit touches core paths but references no issue (#NNNN required)")
        else:
            errors.append("commit references no issue (#NNNN required)")

    for n in refs:
        if issue_path(tracker, n) is None:
            errors.append(f"referenced issue #{n:04d} does not exist")

    for n in closes:
        t = issue_type(tracker, n)
        if t is None:
            errors.append(f"closes #{n:04d}: issue does not exist")
        elif t in HUMAN_GATED:
            errors.append(
                f"closes #{n:04d}: type '{t}' is human-gated and may not be closed by commit"
            )
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--message")
    ap.add_argument("--files", nargs="*")
    ap.add_argument("--rev")
    ap.add_argument("--tracker-dir", default="issues")
    ap.add_argument("--core-prefix", action="append", default=[])
    args = ap.parse_args()

    tracker = REPO / args.tracker_dir

    if args.rev:
        message = subprocess.check_output(
            ["git", "log", "-1", "--format=%B", args.rev], cwd=REPO, text=True
        )
        files = subprocess.check_output(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", args.rev],
            cwd=REPO, text=True,
        ).split()
    else:
        message = args.message or ""
        files = args.files or []

    errors = lint(message, files, tracker, args.core_prefix)
    if errors:
        print("commit lint FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("commit lint OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
