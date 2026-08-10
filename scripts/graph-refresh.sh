#!/bin/sh
# gantry — pre-commit graph refresh (hook body; lives in the gantry repo).
#
# Called by a shim installed at <client>/.git/hooks/pre-commit (see install.sh).
# If the STAGED changes touch the extract inputs (tracker dir, plan, kickoff),
# re-runs extract and stages the refreshed GRAPH.md so the digest rides in the
# SAME commit that changed the issues. The digest header will read
# "@ <sha>+dirty": <sha> is the parent commit; the "+dirty" changes are the
# very commit that carries the digest.
#
# Never blocks a commit: any missing piece (python3, gantry, adapter) or an
# extract failure prints a note to stderr and exits 0. The client repo must
# stay fully usable on machines without gantry.
#
# Input paths from the adapter must not contain whitespace.

REPO="$1"; ADAPTER="$2"; OUT="$3"; DEPS="$4"
# the extractor sits next to this script, in the same gantry repo

HERE="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
EXTRACT="$HERE/gantry_extract.py"

note() { printf 'gantry hook: %s (commit proceeds; GRAPH.md may be stale)\n' "$1" >&2; }

command -v python3 >/dev/null 2>&1 || { note "python3 not found"; exit 0; }
[ -f "$EXTRACT" ] || { note "extractor missing: $EXTRACT"; exit 0; }
[ -f "$ADAPTER" ] || { note "adapter missing: $ADAPTER"; exit 0; }

INPUTS=$(python3 -c 'import json,sys
a = json.load(open(sys.argv[1]))
print(a["tracker_dir"], a["plan"], a["kickoff"])' "$ADAPTER" 2>/dev/null) \
  || { note "adapter unreadable: $ADAPTER"; exit 0; }

# only act when the staged changes touch the process inputs
STAGED=$(git -C "$REPO" diff --cached --name-only -- $INPUTS)
[ -n "$STAGED" ] || exit 0

set -- --client "$ADAPTER" --root "$REPO" --out "$OUT/state.json" --digest "$REPO/GRAPH.md"
if [ -n "$DEPS" ] && [ -f "$DEPS" ]; then
  set -- "$@" --deps "$DEPS"
fi

if python3 "$EXTRACT" "$@" >&2; then
  git -C "$REPO" add GRAPH.md
  printf 'gantry hook: GRAPH.md refreshed and staged\n' >&2
else
  note "extract failed"
fi
exit 0
