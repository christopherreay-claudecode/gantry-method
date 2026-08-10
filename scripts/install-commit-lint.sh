#!/bin/sh
# gantry — bootstrap the commit lint into a NEW client repo (contract §6).
#
# Usage: install-commit-lint.sh <client-repo> [--tracker-dir issues] [--core-prefix simcore/]...
#
# Two pieces, two owners:
#   1. tools/lint_commit.py  — COPIED into the client, to be COMMITTED by the
#      client. Commit rules are the client's own law; a clean clone must
#      enforce itself with no gantry present. Refuses to overwrite an
#      existing lint (an established client already owns its own).
#   2. .git/hooks/commit-msg — unversioned shim calling the client-local copy.
#      Refuses to overwrite a hook it did not write (marker: "installed by
#      gantry"). Remove the hook file to uninstall the wiring; the lint
#      itself stays, because it is client content.
#
# --core-prefix is repeatable; each adds a path needing an issue ref to touch.

set -e

[ -n "$1" ] || { echo "usage: install-commit-lint.sh <client-repo> [--tracker-dir D] [--core-prefix P]..." >&2; exit 1; }
REPO=$(CDPATH= cd -- "$1" && pwd); shift
# bundle-local variant (fullMethodology/scripts): lint_commit.py sits NEXT to this
# installer, not at gantry's ../hooks/. Functionally identical to gantry/hooks/install-commit-lint.sh.
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
HOOK="$REPO/.git/hooks/commit-msg"
LINT="$REPO/tools/lint_commit.py"
EXTRA_ARGS="$*"

[ -d "$REPO/.git" ] || { echo "not a git repo: $REPO" >&2; exit 1; }

if [ -e "$LINT" ]; then
  echo "kept: $LINT already exists — the client owns its lint; not overwriting" >&2
  if [ -n "$EXTRA_ARGS" ]; then
    echo "note: ignoring '$EXTRA_ARGS' — the client's own lint encodes its own law" >&2
    EXTRA_ARGS=""
  fi
else
  mkdir -p "$REPO/tools"
  cp "$HERE/lint_commit.py" "$LINT"
  chmod +x "$LINT"
  echo "copied: $LINT  (client content — commit it in the client, by the client's rules)"
fi

if [ -e "$HOOK" ] && ! grep -q "installed by gantry" "$HOOK"; then
  echo "kept: $HOOK exists and was not installed by gantry — client wiring already in place" >&2
  exit 0
fi

cat > "$HOOK" <<EOF
#!/usr/bin/env bash
# installed by gantry (hooks/install-commit-lint.sh) — shim only; the lint
# itself is versioned client content at tools/lint_commit.py.
set -euo pipefail
REPO="\$(git rev-parse --show-toplevel)"
MSG="\$(cat "\$1")"
FILES="\$(git diff --cached --name-only)"
python3 "\$REPO/tools/lint_commit.py" --message "\$MSG" --files \$FILES $EXTRA_ARGS
EOF
chmod +x "$HOOK"
echo "installed: $HOOK${EXTRA_ARGS:+  (args: $EXTRA_ARGS)}"
