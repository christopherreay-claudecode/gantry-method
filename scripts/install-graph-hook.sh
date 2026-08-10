#!/bin/sh
# gantry — install the pre-commit graph-refresh shim into a client repo.
#
# Usage: install-graph-hook.sh <client-repo> [--adapter .gantry/adapter.json] [--deps deps.json]
#
# Writes <client>/.git/hooks/pre-commit. The shim is SELF-CONTAINED: it calls
# the client's OWN copy of the extractor (<client>/tools/gantry_extract.py,
# copied and committed by adopt.sh) and derives the adapter/out paths from the
# repo at runtime. It never references the gantry repo — a clean clone
# regenerates its own GRAPH.md with no gantry present.
#
# Never blocks a commit: any missing piece (python3, extractor, adapter) or a
# failed extract prints a note and exits 0.
#
# Refuses to overwrite a pre-commit hook it did not write itself
# (marker line: "installed by gantry"). Remove the hook file to uninstall.

set -e

usage() { echo "usage: install-graph-hook.sh <client-repo> [--adapter PATH] [--deps PATH]" >&2; exit 1; }
[ -n "$1" ] || usage
REPO=$(CDPATH= cd -- "$1" && pwd); shift

ADAPTER="$REPO/.gantry/adapter.json"
DEPS=""
while [ -n "$1" ]; do
  case "$1" in
    --adapter) [ -n "$2" ] || usage; ADAPTER=$(CDPATH= cd -- "$(dirname -- "$2")" && pwd)/$(basename -- "$2"); shift 2 ;;
    --deps)    [ -n "$2" ] || usage; DEPS=$(CDPATH= cd -- "$(dirname -- "$2")" && pwd)/$(basename -- "$2"); shift 2 ;;
    *) usage ;;
  esac
done

HOOK="$REPO/.git/hooks/pre-commit"

[ -d "$REPO/.git" ] || { echo "not a git repo: $REPO" >&2; exit 1; }
if [ -e "$HOOK" ] && ! grep -q "installed by gantry" "$HOOK"; then
  echo "refusing: $HOOK exists and was not installed by gantry" >&2
  exit 1
fi

cat > "$HOOK" <<EOF
#!/bin/sh
# installed by gantry (scripts/install-graph-hook.sh) — local automation, not repo
# content. Regenerates GRAPH.md (via the client's OWN tools/gantry_extract.py)
# when a commit changes the tracker/plan inputs; safe no-op on any failure.
# Remove this file to uninstall.
REPO="\$(git rev-parse --show-toplevel)"
EXTRACT="\$REPO/tools/gantry_extract.py"
ADAPTER="$ADAPTER"
DEPS="$DEPS"

note() { printf 'gantry hook: %s (commit proceeds; GRAPH.md may be stale)\n' "\$1" >&2; }

command -v python3 >/dev/null 2>&1 || { note "python3 not found"; exit 0; }
[ -f "\$EXTRACT" ] || { note "extractor missing: \$EXTRACT — re-run adopt.sh"; exit 0; }
[ -f "\$ADAPTER" ] || { note "adapter missing: \$ADAPTER — fill it in and re-run adopt.sh"; exit 0; }

INPUTS=\$(python3 -c 'import json,sys
a = json.load(open(sys.argv[1]))
print(a["tracker_dir"], a["plan"], a["kickoff"])' "\$ADAPTER" 2>/dev/null) \\
  || { note "adapter unreadable: \$ADAPTER"; exit 0; }

# only act when the staged changes touch the process inputs
STAGED=\$(git -C "\$REPO" diff --cached --name-only -- \$INPUTS 2>/dev/null || true)
[ -n "\$STAGED" ] || exit 0

if python3 "\$EXTRACT" --client "\$ADAPTER" --root "\$REPO" \
     --out "\$REPO/.gantry/out/state.json" --digest "\$REPO/GRAPH.md" \
     \${DEPS:+--deps "\$DEPS"} >&2; then
  git -C "\$REPO" add GRAPH.md
  printf 'gantry hook: GRAPH.md refreshed and staged\n' >&2
else
  note "extract failed"
fi
exit 0
EOF
chmod +x "$HOOK"

echo "installed: $HOOK"
echo "  extractor (client-owned): $REPO/tools/gantry_extract.py"
echo "  adapter: $ADAPTER"
if [ -n "$DEPS" ]; then echo "  deps:    $DEPS"; fi
