#!/bin/sh
# gantry — fork a new app repo out of a gantry-adopted base repo.
#
# Usage: fork-app.sh <base-repo> <new-app-dir> [--name NAME] [--keep-open]
#                    [--local-stack] [--fresh-tools] [--no-install] [--no-commit]
#
# A fork is a COMPLETELY SEPARATE repo: it copies the base's starting truth
# and machinery, then lives alone. The manifest below is the contract — copy
# exactly these paths, nothing else (everything the manifest does not name is
# reported, not copied; add paths to the list when a base needs them).
#
# The copy is then given its own identity, its own numbering floor, and its
# own first commit:
#   1. copy the manifest (truth + machinery)
#   2. small edits: adapter client + issue_min, supabase project_id,
#      package.json name, README ritual header
#   3. close the inherited issues as a REFERENCE SET (their work belongs to
#      the base's history; the app's own issues start at #1000) — unless
#      --keep-open
#   4. fresh git init + birth commit (exempt from commit law: no issue exists
#      yet — the commit-msg lint would reject it, and nothing is open to ref)
#   5. adopt.sh for the hooks, npm install, verify, mint GRAPH.md + INDEX.md
#   6. stop. The operator files the first app issue (#1000) and commits it —
#      that commit (and every one after) carries the issue ref the lint wants.
#
# Not copied, each for a reason:
#   .git/                fresh init — the "completely separate" part
#   .env                 secrets; copied by hand (outside git), not via git
#   .gantry/out/         derived, gitignored, regenerates
#   METALAND/            the base's genesis material, not the app's concern
#   node_modules .svelte-kit build/   regenerated

set -e

HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

usage() { echo "usage: fork-app.sh <base-repo> <new-app-dir> [--name NAME] [--keep-open] [--local-stack] [--fresh-tools] [--no-install] [--no-commit]" >&2; exit 1; }
[ -n "$1" ] || usage
BASE=$(CDPATH= cd -- "$1" && pwd); shift
[ -n "$1" ] || usage
APP_ARG="$1"; shift
[ -d "$BASE/.git" ] || { echo "not a git repo: $BASE" >&2; exit 1; }
mkdir -p "$APP_ARG"
APP=$(CDPATH= cd -- "$APP_ARG" && pwd)
[ -z "$(ls -A "$APP" 2>/dev/null)" ] || { echo "refusing: $APP is not empty" >&2; exit 1; }

NAME=$(basename "$APP")
KEEP_OPEN=0
LOCAL_STACK=0
FRESH_TOOLS=0
NO_INSTALL=0
NO_COMMIT=0
while [ -n "$1" ]; do
  case "$1" in
    --name)        [ -n "$2" ] || usage; NAME="$2"; shift 2 ;;
    --keep-open)   KEEP_OPEN=1; shift ;;
    --local-stack) LOCAL_STACK=1; shift ;;
    --fresh-tools) FRESH_TOOLS=1; shift ;;
    --no-install)  NO_INSTALL=1; shift ;;
    --no-commit)   NO_COMMIT=1; shift ;;
    *) usage ;;
  esac
done

BASESHA=$(git -C "$BASE" rev-parse HEAD | cut -c1-7)

echo "== gantry fork: $BASE -> $APP  (name: $NAME, base @ $BASESHA)"

# ---------------------------------------------------------------- 1. copy ----
# The manifest. Root files first, then directories/globs.
ROOT_FILES="plan.md seams.md CLAUDE.md README.md package.json package-lock.json
            svelte.config.js tsconfig.json vite.config.ts .gitignore .env.example .mcp.json"
DIRS="issues specs src tests tools scripts"
SUPABASE_PARTS="templates config.toml exit-tests .gitignore"
WORKFLOW=".github/workflows/gantry-drift.yml"

copy_if_present() { # base_path rel_dest
  if [ -e "$1" ]; then
    cp -R "$1" "$2"
    echo "   copied: ${1#"$BASE"/}"
  else
    echo "   skipped (absent in base): ${1#"$BASE"/}"
  fi
}

for f in $ROOT_FILES; do
  copy_if_present "$BASE/$f" "$APP/"
done
for d in $DIRS; do
  copy_if_present "$BASE/$d" "$APP/"
done

# supabase: only migrations 0000-0008 + the named parts
if [ -d "$BASE/supabase" ]; then
  mkdir -p "$APP/supabase/migrations"
  n=0
  for m in "$BASE"/supabase/migrations/000[0-8]_* "$BASE"/supabase/migrations/000[0-8]-*; do
    [ -e "$m" ] || continue
    cp -R "$m" "$APP/supabase/migrations/"
    n=$((n+1))
  done
  [ "$n" -gt 0 ] || echo "   skipped (absent in base): supabase/migrations/0000-0008"
  echo "   copied: supabase/migrations/ (0000-0008, $n files)"
  for p in $SUPABASE_PARTS; do
    copy_if_present "$BASE/supabase/$p" "$APP/supabase/"
  done
else
  echo "   skipped (absent in base): supabase/"
fi

mkdir -p "$APP/.github/workflows"
copy_if_present "$BASE/$WORKFLOW" "$APP/.github/workflows/"
mkdir -p "$APP/.gantry"
copy_if_present "$BASE/.gantry/adapter.json" "$APP/.gantry/"
if [ "$FRESH_TOOLS" -eq 1 ]; then
  for tool in gantry_extract.py gen_index.py lint_commit.py; do
    cp "$HERE/$tool" "$APP/tools/$tool"
    chmod +x "$APP/tools/$tool"
    echo "   refreshed: tools/$tool (from the gantry meta repo — current extractor/lint)"
  done
fi

echo "   not copied (each for a reason):"
for e in $(ls -A "$BASE"); do
  case "$e" in
    .git)        echo "     .git/            fresh init — the completely separate part" ;;
    .env)        echo "     .env             secrets — copy by hand, outside git" ;;
    node_modules|.svelte-kit|build) echo "     $e/              regenerated by install/build" ;;
    METALAND)    echo "     METALAND/        the base's genesis material, not the app's concern" ;;
    .gantry)     [ -e "$BASE/.gantry/out" ] && echo "     .gantry/out/     derived, gitignored, regenerates" ;;
    .github)     for f in $ROOT_FILES; do [ "$e" = "$f" ] && continue 2; done
                 [ -e "$BASE/.github/workflows/gantry-drift.yml" ] && [ ! -e "$APP/.github/workflows/gantry-drift.yml" ] \
                   && echo "     .github/workflows/gantry-drift.yml (absent in base)" ;;
    issues|specs|supabase|src|tests|tools|scripts) : ;;
    *)
      for f in $ROOT_FILES; do [ "$e" = "$f" ] && continue 2; done
      echo "     $e/              not in the manifest — add it above if the app needs it" ;;
  esac
done

# ------------------------------------------------------------------ 2. edits ----
echo "== identity edits"
if grep -q '"issue_min"' "$APP/.gantry/adapter.json" 2>/dev/null; then
  echo "   kept: .gantry/adapter.json issue_min (already set)"
else
  sed -i '/^[[:space:]]*"tracker_dir":/a\  "issue_min": 1000,' "$APP/.gantry/adapter.json"
  echo "   set: .gantry/adapter.json issue_min: 1000 (issues numbered from here)"
fi
sed -i 's/"client": "[^"]*"/"client": "'"$NAME"'"/' "$APP/.gantry/adapter.json"
echo "   set: .gantry/adapter.json client: $NAME"
if [ -f "$APP/supabase/config.toml" ]; then
  sed -i 's/project_id = "[^"]*"/project_id = "'"$NAME"'"/' "$APP/supabase/config.toml"
  echo "   set: supabase/config.toml project_id: $NAME (own local-stack containers)"
fi
if [ -f "$APP/package.json" ]; then
  sed -i '0,/^[[:space:]]*"name":[[:space:]]*"[^"]*"/s//"name": "'"$NAME"'"/' "$APP/package.json"
  echo "   set: package.json name: $NAME"
fi
cat > "$APP/README.md.forkhead" <<EOF
# $NAME

> Born from **$(basename "$BASE")** @ $BASESHA — a gantry fork. This repo's
> issues are numbered from **#1000**; issues #0001-#0013 are the closed
> reference set inherited from the base. Session start: read \`GRAPH.md\`, then
> \`tools/README.md\`.

EOF
cat "$APP/README.md.forkhead" "$APP/README.md" > "$APP/README.md.new" && mv "$APP/README.md.new" "$APP/README.md"
rm -f "$APP/README.md.forkhead"
echo "   set: README.md fork header + title"

# ------------------------------------------------------- 3. reference set ----
if [ "$KEEP_OPEN" -eq 1 ]; then
  echo "== inherited issues kept OPEN (--keep-open)"
else
  echo "== close the inherited issues (reference set; work belongs to the base)"
  python3 - "$APP/issues" "$BASESHA" <<'PY'
import re, sys
from pathlib import Path
d, sha = sys.argv[1], sys.argv[2]
human_types = {"ambiguity", "freeze-request", "amendment-proposal"}
closed = 0
for p in sorted(Path(d).glob("[0-9][0-9][0-9][0-9]-*.md")):
    lines = p.read_text().splitlines()
    typ = st = None
    for line in lines[:6]:
        m = re.match(r"^type:\s*(\S+)\s+status:\s*(\S+)", line)
        if m:
            typ, st = m.group(1), m.group(2)
    if st != "open":
        continue
    for i, line in enumerate(lines[:6]):
        m = re.match(r"^type:\s*(\S+)\s+status:\s*(\S+)", line)
        if m:
            lines[i] = m.group(1) and line.replace("status: " + m.group(2), "status: closed", 1)
            break
    for i, line in enumerate(lines[:6]):
        if line.startswith("refs:"):
            cb = ("reference: inherited from base @ " + sha) if typ in human_types else sha
            if "closed-by:" in line:
                lines[i] = re.sub(r"closed-by:\s*.*$", "closed-by: " + cb, line)
            else:
                lines[i] = line.rstrip() + "   closed-by: " + cb
            break
    p.write_text("\n".join(lines) + "\n")
    closed += 1
    print("   closed:", p.name, "(human-gated)" if typ in human_types else "(commit-closable)")
print("   %d inherited issues closed (reference set)" % closed)
PY
fi

# ------------------------------------------------------------- 4. git init ----
echo "== fresh git init + birth commit"
git init -q "$APP"
if [ "$NO_COMMIT" -eq 1 ]; then
  echo "   --no-commit: leaving the tree staged for the operator"
  git -C "$APP" add -A
else
  git -C "$APP" add -A
  git -C "$APP" commit -q --no-verify \
    -m "app repo born from base @ $BASESHA" \
    -m "Fork of $(basename "$BASE"). Inherited issues #0001-#0013 are a closed reference set; this repo's issues are numbered from #1000. (Birth commit is exempt from commit law: no issue exists yet — the first app issue, #1000, will carry the ref from here on.)"
  echo "   committed: \"app repo born from base @ $BASESHA\""
fi

# ----------------------------------------------------------- 5. adopt/verify ----
echo "== adopt.sh (hooks; GRAPH.md mint skipped until HEAD exists)"
sh "$HERE/adopt.sh" "$APP" 2>&1 | sed 's/^/   /' || true

if [ "$NO_INSTALL" -eq 1 ]; then
  echo "== --no-install: skipping npm install / verify (run them by hand)"
else
  if command -v npm >/dev/null 2>&1 && [ -f "$APP/package.json" ]; then
    echo "== npm install"
    (cd "$APP" && npm install --no-fund --no-audit) 2>&1 | tail -2 | sed 's/^/   /'
    for s in check build test; do
      if grep -q "\"$s\"" "$APP/package.json"; then
        echo "== npm run $s"
        (cd "$APP" && npm run "$s") 2>&1 | tail -4 | sed 's/^/   /' || echo "   (failed — fix and re-verify)"
      fi
    done
  else
    echo "   npm not available or no package.json — skipping npm steps"
  fi

  if [ "$LOCAL_STACK" -eq 1 ]; then
    if command -v supabase >/dev/null 2>&1; then
      echo "== local supabase stack (config.toml project_id: $NAME)"
      (cd "$APP" && supabase start) 2>&1 | tail -4 | sed 's/^/   /'
      echo "   run the exit-tests/harness by hand now, then:"
      (cd "$APP" && supabase stop) 2>&1 | tail -1 | sed 's/^/   /'
    else
      echo "   supabase CLI not found — start the local stack by hand"
    fi
  fi
fi

# -------------------------------------------------------------- 6. mint ----
echo "== mint GRAPH.md + INDEX.md (HEAD now exists)"
if python3 "$APP/tools/gantry_extract.py" --client "$APP/.gantry/adapter.json" --root "$APP" \
     --out "$APP/.gantry/out/state.json" --digest "$APP/GRAPH.md" >/dev/null 2>&1; then
  echo "   GRAPH.md minted (uncommitted — commit it with the first app issue)"
else
  echo "   extract failed — check .gantry/adapter.json (run adopt.sh again after fixing)"
fi
if python3 "$APP/tools/gen_index.py" --root "$APP" >/dev/null 2>&1; then
  echo "   issues/INDEX.md minted (uncommitted)"
fi

echo ""
echo "   NEXT STEPS (the operator):"
echo "     - copy .env by hand (secrets — never via git)"
echo "     - file the first app issue: issues/1000-<slug>.md  (refs the base constraint it serves)"
echo "     - commit it WITH GRAPH.md + issues/INDEX.md — that commit carries the #1000 ref"
echo "     - the 'below issue_min 1000' warnings on inherited issues are expected (copied history)"
