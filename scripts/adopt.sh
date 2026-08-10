#!/bin/sh
# gantry — one-command adoption of the method into a client repo.
#
# Usage: adopt.sh <client-repo> [--core-prefix P]... [--deps deps.json]
#
# Does the whole operational layer in one run. Everything it creates becomes
# CLIENT CONTENT — committed by the client, surviving a clean clone with no
# gantry repo present:
#   1. copies the client-side tools into <client>/tools/: gantry_extract.py
#      (the GRAPH.md builder), gen_index.py, lint_commit.py, plus a
#      tools/README.md describing the ritual;
#   2. wires the commit-msg lint shim (calls the client's own tools/ copy);
#   3. writes a stub adapter (<client>/.gantry/adapter.json) if none exists,
#      and says LOUDLY what to fill in;
#   4. wires the pre-commit graph-refresh shim (self-contained: calls the
#      client's own extractor; never blocks);
#   5. runs the client's own extractor once to mint <client>/GRAPH.md.
#
# Idempotent: re-run after filling the adapter to mint GRAPH.md. Installers
# refuse to overwrite existing client-owned content and non-gantry hooks.
# Only the .git/hooks shims are unversioned wiring — everything else the
# client commits.

set -e

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

usage() { echo "usage: adopt.sh <client-repo> [--core-prefix P]... [--deps deps.json]" >&2; exit 1; }
[ -n "$1" ] || usage
REPO=$(CDPATH= cd -- "$1" && pwd); shift
[ -d "$REPO/.git" ] || { echo "not a git repo: $REPO" >&2; exit 1; }

CORE_PREFIXES=""
DEPS=""
while [ -n "$1" ]; do
  case "$1" in
    --core-prefix) [ -n "$2" ] || usage; CORE_PREFIXES="$CORE_PREFIXES --core-prefix $2"; shift 2 ;;
    --deps)        [ -n "$2" ] || usage; DEPS=$(CDPATH= cd -- "$(dirname -- "$2")" && pwd)/$(basename -- "$2"); shift 2 ;;
    *) usage ;;
  esac
done

ADAPTER="$REPO/.gantry/adapter.json"
ADAPTER_READY=1

echo "== gantry adopt: $REPO"
echo "   1. client tools -> $REPO/tools/  (commit these: they are client content)"
mkdir -p "$REPO/tools"
for tool in gantry_extract.py gen_index.py lint_commit.py; do
  if [ -e "$REPO/tools/$tool" ]; then
    echo "   kept: tools/$tool (client already owns it)"
  else
    cp "$HERE/$tool" "$REPO/tools/$tool"
    chmod +x "$REPO/tools/$tool"
    echo "   copied: tools/$tool"
  fi
done
if [ -e "$REPO/tools/README.md" ]; then
  echo "   kept: tools/README.md"
else
  cp "$HERE/tools-README.template.md" "$REPO/tools/README.md"
  echo "   copied: tools/README.md (the ritual — read it first)"
fi

echo "   2. commit-msg lint shim"
sh "$HERE/install-commit-lint.sh" "$REPO" $CORE_PREFIXES

if [ -f "$ADAPTER" ]; then
  echo "   adapter: kept $ADAPTER"
else
  ADAPTER_READY=0
  mkdir -p "$(dirname "$ADAPTER")"
  cp "$HERE/../examples/adapter.json" "$ADAPTER"
  echo ""
  echo "   !!!  FILL IN THE ADAPTER: $ADAPTER"
  echo "   !!!  it is a STUB copied from examples/. Set client (the label),"
  echo "   !!!  tracker_dir, plan, kickoff (seams), seam_slugs, q_holds, and"
  echo "   !!!  parts to this repo's reality (SPEC.md §6). Until then the graph"
  echo "   !!!  hook stays inert (it never blocks a commit) and GRAPH.md cannot"
  echo "   !!!  be minted."
  echo ""
fi

echo "   3. pre-commit graph-refresh shim (self-contained, never blocks)"
if [ "$ADAPTER_READY" -eq 1 ]; then
  sh "$HERE/install-graph-hook.sh" "$REPO" ${DEPS:+--deps "$DEPS"}
else
  echo "   skipped (adapter is a stub — re-run adopt.sh after filling it in)"
fi

echo "   4. mint GRAPH.md (with the client's own extractor)"
if [ "$ADAPTER_READY" -eq 1 ]; then
  if ! git -C "$REPO" rev-parse HEAD >/dev/null 2>&1; then
    echo "   skipped — no commits yet in $REPO; extract stamps the commit it"
    echo "   reads, so: make your first commit, then re-run adopt.sh to mint GRAPH.md."
  elif python3 "$REPO/tools/gantry_extract.py" --client "$ADAPTER" --root "$REPO" \
       --out "$REPO/.gantry/out/state.json" --digest "$REPO/GRAPH.md" ${DEPS:+--deps "$DEPS"}; then
    echo "   GRAPH.md minted at $REPO/GRAPH.md — commit it (and tools/, and the adapter)."
  else
    echo "   extract failed — fix the adapter and re-run adopt.sh" >&2
  fi
else
  echo "   skipped (adapter is a stub — re-run adopt.sh after filling it in)"
fi

echo ""
echo "   From here, the ritual (tools/README.md in the client):"
echo "     - every session starts by reading GRAPH.md — not the issue files"
echo "     - declare dependencies on the issue's 'deps:' line the moment you"
echo "       learn them; reviewed proposals land in deps.json (--deps)"
echo "     - the commit lint enforces: every commit refs an issue; 'closes'"
echo "       never targets a human-gated type"
echo "     - add a CI step that regenerates GRAPH.md + INDEX.md and fails on drift"
