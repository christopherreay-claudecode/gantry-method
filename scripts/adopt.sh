#!/bin/sh
# gantry — one-command adoption of the method into a client repo.
#
# Usage: adopt.sh <client-repo> [--core-prefix P]... [--deps deps.json]
#
# Does the whole operational layer in one run:
#   1. copies the client-side tools (gen_index.py, lint_commit.py) into
#      <client>/tools/ and wires the commit-msg lint shim;
#   2. writes a stub adapter (<client>/.gantry/adapter.json) if none exists,
#      and says LOUDLY what to fill in;
#   3. wires the pre-commit graph-refresh hook (observer-side; never blocks);
#   4. runs extract once to mint <client>/GRAPH.md (after the adapter is real).
#
# Idempotent: re-run after filling the adapter to mint GRAPH.md. Installers
# refuse to overwrite existing client-owned content and non-gantry hooks.
# The hooks are per-machine wiring; only tools/ + GRAPH.md + the adapter are
# committed by the client.

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
OUT="$REPO/.gantry/out"
ADAPTER_READY=1

echo "== gantry adopt: $REPO"
echo "   1. client-side tools + commit-msg lint"
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

echo "   3. pre-commit graph-refresh hook (observer-side, never blocks)"
if [ "$ADAPTER_READY" -eq 1 ]; then
  sh "$HERE/install-graph-hook.sh" "$REPO" "$ADAPTER" "$OUT" ${DEPS:+"$DEPS"}
else
  echo "   skipped (adapter is a stub — re-run adopt.sh after filling it in)"
fi

echo "   4. mint GRAPH.md"
if [ "$ADAPTER_READY" -eq 1 ]; then
  if ! git -C "$REPO" rev-parse HEAD >/dev/null 2>&1; then
    echo "   skipped — no commits yet in $REPO; extract stamps the commit it"
    echo "   reads, so: make your first commit, then re-run adopt.sh to mint GRAPH.md."
  elif python3 "$HERE/gantry_extract.py" --client "$ADAPTER" --root "$REPO" \
       --out "$OUT/state.json" --digest "$REPO/GRAPH.md" ${DEPS:+--deps "$DEPS"}; then
    echo "   GRAPH.md minted at $REPO/GRAPH.md — commit it (and tools/, and the adapter)."
  else
    echo "   extract failed — fix the adapter and re-run adopt.sh" >&2
  fi
else
  echo "   skipped (adapter is a stub — re-run adopt.sh after filling it in)"
fi

echo ""
echo "   From here, the ritual (SPEC.md):"
echo "     - every session starts by reading GRAPH.md — not the issue files"
echo "     - declare dependencies on the issue's 'deps:' line the moment you"
echo "       learn them; reviewed proposals land in deps.json (--deps)"
echo "     - the commit lint enforces: every commit refs an issue; 'closes'"
echo "       never targets a human-gated type"
echo "     - add a CI step that regenerates GRAPH.md and fails on drift"
