#!/bin/sh
# gantry — install the pre-commit graph-refresh shim into a client repo.
#
# Usage: install.sh <client-repo> <adapter.json> <out-dir> [deps.json]
#
# Writes <client>/.git/hooks/pre-commit. This is LOCAL automation only: git
# hooks are never versioned or cloned, so the client's committed content
# stays fully regenerable from a clean clone with no gantry dependency. The
# client is "aware" of gantry only through its own committed GANTRY.md; the
# hook is this machine's convenience, not the client's obligation.
#
# Refuses to overwrite a pre-commit hook it did not write itself
# (marker line: "installed by gantry"). Remove the hook file to uninstall.

set -e

usage() { echo "usage: install.sh <client-repo> <adapter.json> <out-dir> [deps.json]" >&2; exit 1; }
[ -n "$1" ] && [ -n "$2" ] && [ -n "$3" ] || usage

REPO=$(CDPATH= cd -- "$1" && pwd)
ADAPTER=$(CDPATH= cd -- "$(dirname -- "$2")" && pwd)/$(basename -- "$2")
mkdir -p "$3"
OUT=$(CDPATH= cd -- "$3" && pwd)
DEPS=""
if [ -n "$4" ]; then
  DEPS=$(CDPATH= cd -- "$(dirname -- "$4")" && pwd)/$(basename -- "$4")
fi
# graph-refresh.sh sits next to this installer, in the same gantry repo

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
HOOK="$REPO/.git/hooks/pre-commit"

[ -d "$REPO/.git" ] || { echo "not a git repo: $REPO" >&2; exit 1; }
[ -f "$ADAPTER" ] || { echo "adapter not found: $ADAPTER" >&2; exit 1; }
if [ -e "$HOOK" ] && ! grep -q "installed by gantry" "$HOOK"; then
  echo "refusing: $HOOK exists and was not installed by gantry" >&2
  exit 1
fi

cat > "$HOOK" <<EOF
#!/bin/sh
# installed by gantry (scripts/install-graph-hook.sh) — local automation, not repo
# content. Regenerates GRAPH.md when a commit changes the tracker/plan inputs; safe
# no-op on machines without gantry. Remove this file to uninstall.
#
# The "never blocks a commit" guarantee lives in the body — but only if the body
# RUNS. If gantry is moved, renamed, or deleted after install, exec'ing a missing
# path fails and would hard-block EVERY commit in this repo. So the existence check
# lives here, in the shim, ahead of the exec.
BODY="$HERE/graph-refresh.sh"
if [ ! -x "\$BODY" ]; then
  printf 'gantry hook: body missing (%s) — skipping GRAPH refresh; commit proceeds. Re-run install-graph-hook.sh to fix.\n' "\$BODY" >&2
  exit 0
fi
exec "\$BODY" "$REPO" "$ADAPTER" "$OUT" "$DEPS"
EOF
chmod +x "$HOOK"

echo "installed: $HOOK"
echo "  scripts: $HERE"
echo "  adapter: $ADAPTER"
echo "  out:     $OUT"
if [ -n "$DEPS" ]; then echo "  deps:    $DEPS"; fi
