#!/usr/bin/env python3
"""Regenerate issues/INDEX.md from the issue files.

INDEX.md is DERIVED DATA (kickoff §5a): the issue files are the truth. Never
hand-edit INDEX.md. Run this after adding/closing an issue.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ISSUES = REPO / "issues"

HEADER_RE = re.compile(r"^#\s*#(\d+)\s*[—-]\s*(.+?)\s*$")
FIELD_RE = re.compile(r"^type:\s*(\S+)\s+status:\s*(\S+)")


def parse_issue(path: Path):
    num = title = itype = status = None
    with path.open() as f:
        for line in f:
            if num is None:
                m = HEADER_RE.match(line)
                if m:
                    num, title = int(m.group(1)), m.group(2)
                    continue
            if itype is None:
                m = FIELD_RE.match(line.strip())
                if m:
                    itype, status = m.group(1), m.group(2)
                    break
    if num is None:
        raise SystemExit(f"{path.name}: no '# #NNNN — title' header")
    if itype is None:
        raise SystemExit(f"{path.name}: no 'type:/status:' line")
    return num, title, itype, status, path.name


def main():
    rows = []
    for path in sorted(ISSUES.glob("[0-9][0-9][0-9][0-9]-*.md")):
        rows.append(parse_issue(path))
    rows.sort(key=lambda r: r[0])

    out = ["# Issue Index (generated — do not hand-edit; run tools/gen_index.py)", ""]
    out.append("| # | Title | Type | Status | File |")
    out.append("|---|-------|------|--------|------|")
    for num, title, itype, status, fname in rows:
        out.append(f"| #{num:04d} | {title} | {itype} | {status} | [{fname}]({fname}) |")
    out.append("")
    text = "\n".join(out)

    index = ISSUES / "INDEX.md"
    if "--check" in sys.argv:
        current = index.read_text() if index.exists() else ""
        if current != text:
            print("INDEX.md is stale — run tools/gen_index.py", file=sys.stderr)
            return 1
        print("INDEX.md up to date.")
        return 0
    index.write_text(text)
    print(f"Wrote {index} ({len(rows)} issues).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
