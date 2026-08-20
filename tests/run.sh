#!/bin/sh
# gantry — end-to-end exercise of the entry point (scripts/gantry) in scratch dirs.
#
#   sh tests/run.sh [scratch-dir]
#
# Covers, in order: new (empty dir) · adopt (empty repo) · adopt (repo with
# content + prior commits) · fork (level 1, #1000–#1999) · stream (level 1
# sub-band #1000–#1099, worktree, merge back) · check on every result.
# Exit 1 on the first failed expectation. Deterministic; needs git + python3.

set -e
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
G="$HERE/../scripts/gantry"
S=${1:-$(mktemp -d)}
rm -rf "$S"; mkdir -p "$S"
export GIT_AUTHOR_NAME=gantry-test GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=gantry-test GIT_COMMITTER_EMAIL=t@t
fail() { echo "FAIL: $*" >&2; exit 1; }
expect() { # file pattern
  grep -q -- "$2" "$1" || fail "$1 lacks: $2"
}
n=0; step() { n=$((n+1)); echo; echo "#### $n. $*"; }

step "new — empty dir → gantry repo, one commit, GRAPH.md minted by the hook"
python3 "$G" new "$S/alpha" >/dev/null 2>&1
[ "$(git -C "$S/alpha" rev-list --count HEAD)" = 1 ] || fail "alpha: expected 1 commit"
expect "$S/alpha/GRAPH.md" "gates latched:  · open: m0"
expect "$S/alpha/GRAPH.md" "lineage: level 0 · root · issues #0001–#0999"
expect "$S/alpha/issues/0001-m0-bootstrap.md" "refs: \[m0\]"
git -C "$S/alpha" log -1 --format=%s | grep -q "(#0001)" || fail "alpha: birth commit lacks #0001 ref"
git -C "$S/alpha" ls-files | grep -q "^GRAPH.md$" || fail "alpha: GRAPH.md not committed"
python3 "$G" check "$S/alpha" >/dev/null || fail "alpha: check"
python3 "$G" adopt "$S/alpha" >/dev/null   # idempotent
[ "$(git -C "$S/alpha" rev-list --count HEAD)" = 1 ] || fail "alpha: re-adopt made a commit"

step "commit law is live in the new repo"
echo x > "$S/alpha/x.txt"; git -C "$S/alpha" add x.txt
if git -C "$S/alpha" commit -q -m "no ref here" 2>/dev/null; then fail "alpha: lint let an unref'd commit through"; fi
git -C "$S/alpha" commit -q -m "x (#0001)" || fail "alpha: ref'd commit rejected"

step "adopt — empty repo (git init, no commits)"
mkdir "$S/beta"; git -C "$S/beta" init -q
python3 "$G" adopt "$S/beta" >/dev/null 2>&1
[ "$(git -C "$S/beta" rev-list --count HEAD)" = 1 ] || fail "beta: expected 1 commit"
python3 "$G" check "$S/beta" >/dev/null || fail "beta: check"

step "re-adopt — a materially changed map is KEPT (not reverted to HEAD); no commit without a seed"
python3 "$G" issue new --repo "$S/beta" --title "M1: second gate" --type milestone --refs m0 --slug m1-second >/dev/null 2>&1
python3 "$G" adopt "$S/beta" --fresh-tools >/dev/null 2>&1
git -C "$S/beta" status --porcelain | grep -q "GRAPH.md" || fail "beta: fresh GRAPH.md was reverted over the operator's change"
grep -q "m1-second" "$S/beta/GRAPH.md" || fail "beta: GRAPH.md does not carry the new issue"
[ "$(git -C "$S/beta" rev-list --count HEAD)" = 1 ] || fail "beta: re-adopt made a commit with no seed issue"
grep -q "gantry stream new" "$S/beta/tools/README.md" || fail "beta: tools/README.md lacks the stream commands"
grep -q "{{gantry_repo}}" "$S/beta/tools/README.md" && fail "beta: toolbox path placeholder not substituted"
grep -qE "^G=/.*/scripts/gantry" "$S/beta/tools/README.md" || fail "beta: toolbox path not an absolute gantry path"
git -C "$S/beta" add -A && git -C "$S/beta" commit -q -m "second gate + tools refresh (#0002)"
python3 "$G" adopt "$S/beta" >/dev/null 2>&1
[ -z "$(git -C "$S/beta" status --porcelain)" ] || fail "beta: re-adopt left stamp-only churn behind"

step "the short driver — tools/g views (map/open/next/show/refresh) and PATH install"
[ -x "$S/beta/tools/g" ] || fail "beta: tools/g not installed"
python3 "$S/beta/tools/g" refresh | grep -q "GRAPH.md + INDEX.md refreshed · REV" || fail "g refresh"
python3 "$S/beta/tools/g" map | grep -q "sources —" && fail "g map still carries the navigation index"
python3 "$S/beta/tools/g" map | grep -q "open items" || fail "g map lost the open items"
python3 "$S/beta/tools/g" open | grep -q "m1-second" || fail "g open"
python3 "$S/beta/tools/g" next | grep -q "ready (nothing open blocks these)" || fail "g next"
python3 "$S/beta/tools/g" show 2 | grep -q "M1: second gate" || fail "g show"
python3 "$G" install --bin "$S/bin" --name gy >/dev/null 2>&1 || fail "gantry install"
[ -L "$S/bin/gy" ] || fail "install: no symlink"
python3 "$S/bin/gy" next --repo "$S/beta" >/dev/null || fail "installed entry point does not run"

step "a compressed tracker — archived issues still exist (lint) and their numbers are never re-used"
mkdir -p "$S/beta/issues/archive"; git -C "$S/beta" mv issues/0001-m0-bootstrap.md issues/archive/ 2>/dev/null || mv "$S/beta/issues/0001-m0-bootstrap.md" "$S/beta/issues/archive/"
python3 "$S/beta/tools/g" issue new -t "after the archive" -r m0 --slug after-archive >/dev/null 2>&1
[ -e "$S/beta/issues/0003-after-archive.md" ] || { ls "$S/beta/issues"; fail "archived number re-used (expected #0003)"; }
python3 "$S/beta/tools/lint_commit.py" --message "touch (#0001)" --files x >/dev/null 2>&1 || fail "lint: archived issue reported missing"
python3 "$S/beta/tools/g" show 1 | grep -q "M0" || fail "g show: archived issue not found"
git -C "$S/beta" add -A && git -C "$S/beta" commit -q -m "compress the tracker; new issue after it (#0003)"

step "adopt — repo WITH content and history; own CLAUDE.md, .gitignore, src/"
mkdir -p "$S/gamma/src"; git -C "$S/gamma" init -q
echo "# gamma" > "$S/gamma/README.md"; echo "print(1)" > "$S/gamma/src/main.py"
printf '# my agent notes\nkeep it simple\n' > "$S/gamma/CLAUDE.md"; echo "*.pyc" > "$S/gamma/.gitignore"
git -C "$S/gamma" add -A; git -C "$S/gamma" commit -q -m "initial content"
python3 "$G" adopt "$S/gamma" --core-prefix src/ >/dev/null 2>&1
[ "$(git -C "$S/gamma" rev-list --count HEAD)" = 2 ] || fail "gamma: expected 2 commits"
expect "$S/gamma/CLAUDE.md" "keep it simple"
expect "$S/gamma/CLAUDE.md" "## gantry"
expect "$S/gamma/.gitignore" "\*.pyc"
expect "$S/gamma/.gitignore" ".gantry/out/"
python3 "$G" check "$S/gamma" >/dev/null || fail "gamma: check"
echo y >> "$S/gamma/src/main.py"; git -C "$S/gamma" add -A
if git -C "$S/gamma" commit -q -m "touch core without ref" 2>/dev/null; then fail "gamma: core-prefix not enforced"; fi
git -C "$S/gamma" commit -q -m "core (#0001)"

step "adopt — existing adapter with its own plan/kickoff paths: no second plan scaffolded; deps.json auto-wired"
mkdir -p "$S/delta/.gantry" "$S/delta/tracker"; git -C "$S/delta" init -q
printf '# delta plan\n\n## 2. constraints\n1. **Only One.** one.\n' > "$S/delta/PLAN-v1.md"; printf '| S# | n | i | f |\n|--|--|--|--|\n' > "$S/delta/KICKOFF.md"
cat > "$S/delta/.gantry/adapter.json" <<'A'
{"client":"delta","tracker_dir":"tracker","plan":"PLAN-v1.md","plan_source":"plan-v1","kickoff":"KICKOFF.md","seam_slugs":{},"q_holds":{},"constraint_slug_overrides":{},"parts":[]}
A
echo '[]' > "$S/delta/.gantry/deps.json"
git -C "$S/delta" add -A; git -C "$S/delta" commit -q -m "delta truth"
python3 "$G" adopt "$S/delta" >/dev/null 2>&1 || true
[ ! -e "$S/delta/plan.md" ] && [ ! -e "$S/delta/seams.md" ] || fail "delta: scaffolded a second plan beside the adapter's"
grep -q 'DEPS="\$REPO/.gantry/deps.json"' "$S/delta/.git/hooks/pre-commit" || fail "delta: deps.json not auto-wired"
python3 "$G" check "$S/delta" >/dev/null || fail "delta: check (unbanded adapter must pass)"

step "duplicate issue numbers are reported"
cp "$S/gamma/issues/0001-m0-bootstrap.md" "$S/gamma/issues/0001-a-second-file-same-number.md"
python3 "$S/gamma/tools/g" refresh 2>&1 | grep -q "DUPLICATE issue number" || fail "duplicate number not reported"
rm "$S/gamma/issues/0001-a-second-file-same-number.md"; python3 "$S/gamma/tools/g" refresh >/dev/null
git -C "$S/gamma" checkout -- . 2>/dev/null || true

step "fork — level 1, band #1000–#1999, inherited issues closed, birth commit exempt"
python3 "$G" fork "$S/alpha" "$S/alpha-fork" >/dev/null 2>&1
expect "$S/alpha-fork/GRAPH.md" "lineage: level 1 · fork of alpha @"
expect "$S/alpha-fork/GRAPH.md" "issues #1000–#1999"
expect "$S/alpha-fork/issues/0001-m0-bootstrap.md" "status: closed"
grep -q '"issue_min": 1000' "$S/alpha-fork/.gantry/adapter.json" || fail "fork: issue_min"
[ -e "$S/alpha-fork/x.txt" ] || fail "fork: tracked file not copied"
[ "$(git -C "$S/alpha-fork" rev-list --count HEAD)" = 1 ] || fail "fork: expected 1 commit"
# the first fork issue must be at 1000; a commit needs it
cat > "$S/alpha-fork/issues/1000-m1-first.md" <<'I'
# #1000 — M1: first fork milestone
type: milestone        status: open
refs: [m0]   opened: seed   closed-by: <sha>
I
git -C "$S/alpha-fork" add -A; git -C "$S/alpha-fork" commit -q -m "first fork issue (#1000)"
python3 "$G" check "$S/alpha-fork" >/dev/null || fail "fork: check"
expect "$S/alpha-fork/GRAPH.md" "#1000 workorder m1-first"

step "fork of a fork — level 2, #2000"
python3 "$G" fork "$S/alpha-fork" "$S/alpha-fork2" >/dev/null 2>&1
expect "$S/alpha-fork2/GRAPH.md" "lineage: level 2 · fork of alpha-fork"
expect "$S/alpha-fork2/GRAPH.md" "issues #2000–#2999"

step "stream — spawned by an issue, prefix namespace, sibling worktree, brief seed, report, merge back"
cat > "$S/brief.md" <<'B'
Make x.txt say hello.

## issue: write the greeting file
refs: [m0]
Create x.txt containing "hello".

## issue: verify the greeting
deps: blocks #a1-0002
Confirm x.txt reads hello.
B
python3 "$G" stream new --repo "$S/alpha" --issue 1 --slug try-a --brief "$S/brief.md" >/dev/null 2>&1
WT="$S/.gantry.alpha.streams.a1"
[ -d "$WT" ] || fail "stream: sibling worktree missing ($WT)"
[ ! -e "$S/alpha/.gantry/streams/" ] || fail "stream: worktree must not be inside the repo"
expect "$WT/GRAPH.md" "lineage: level 1 · stream of alpha @ .* (parent issue #0001) · issues #a1-0001…"
expect "$WT/GRAPH.md" "#a1-0001 workorder a1-try-a"
expect "$WT/issues/a1-0001-try-a.md" "Make x.txt say hello"
expect "$WT/CLAUDE.md" "stream \`0001-try-a\`"
expect "$WT/CLAUDE.md" "Boundaries"
[ -e "$WT/issues/a1-0002-write-the-greeting-file.md" ] || fail "brief: ## issue block not seeded"
expect "$WT/issues/a1-0003-verify-the-greeting.md" "deps: blocks #a1-0002"
expect "$WT/GRAPH.md" "#a1-0003 —blocks→ #a1-0002"
expect "$WT/.gantry/packet.md" "The parent workorder — #0001"
expect "$WT/.gantry/packet.md" "Make x.txt say hello"
expect "$WT/.gantry/packet.md" "Constraints are the first-order language"
python3 "$G" stream launch a1 --repo "$S/alpha" --dry-run | grep -q "cd $WT && claude -p" || fail "launch dry-run"
python3 "$G" stream packet a1 --repo "$S/alpha" >/dev/null || fail "packet regen"
grep -q '"issue_prefix": "a1"' "$WT/.gantry/adapter.json" || fail "stream: adapter prefix"
git -C "$S/alpha" add .gantry/streams.json; git -C "$S/alpha" commit -q -m "stream try-a opened (#0001)"
expect "$S/alpha/GRAPH.md" "streams open (prefix"
expect "$S/alpha/GRAPH.md" "a1 · 0001-try-a · #0001 · stream/0001-try-a"
# a second stream from the same issue gets the next letter
python3 "$G" stream new --repo "$S/alpha" --issue 1 --slug try-b >/dev/null 2>&1
[ -d "$S/.gantry.alpha.streams.b1" ] || fail "stream: second prefix b1"
git -C "$S/alpha" add -A; git -C "$S/alpha" commit -q -m "stream try-b opened (#0001)"
# work inside stream a: an issue via 'gantry issue new' + a code file; close it
python3 "$G" issue new --repo "$WT" --title "M2: stream work" --type milestone --refs m0 --slug m2-stream-work >/dev/null 2>&1
[ -e "$WT/issues/a1-0004-m2-stream-work.md" ] || fail "issue new: prefixed id"
echo hello > "$WT/x.txt"; git -C "$WT" add -A; git -C "$WT" commit -q -m "stream work (#a1-0004)"
expect "$WT/GRAPH.md" "#a1-0004 workorder a1-m2-stream-work"
python3 "$G" issue close a1-0004 --by "$(git -C "$WT" rev-parse --short HEAD)" --repo "$WT" >/dev/null 2>&1
git -C "$WT" add -A; git -C "$WT" commit -q -m "close #a1-0004"
expect "$WT/GRAPH.md" "closed/resolved: #a1-0004"
# a bare-numbered NEW issue in the stream warns
cat > "$WT/issues/0009-bad.md" <<'I'
# #0009 — bare number filed in a stream
type: milestone        status: open
refs: [m0]   opened: seed   closed-by: <sha>
I
python3 "$WT/tools/gantry_extract.py" --client "$WT/.gantry/adapter.json" --root "$WT" --out "$S/o.json" --digest "$S/g.md" | grep -q "unprefixed issue filed in stream 'a1'" || fail "stream: bare number not warned"
rm "$WT/issues/0009-bad.md"
# lint: a human-gated close is refused; a prefixed ref works
python3 "$G" issue new --repo "$WT" --title "hold: which greeting" --type ambiguity --refs m0 >/dev/null 2>&1
if python3 "$G" issue close a1-0005 --by deadbeef --repo "$WT" >/dev/null 2>&1; then fail "issue close: sha on human-gated accepted"; fi
python3 "$G" issue close a1-0005 --by "operator decided: hello" --repo "$WT" >/dev/null 2>&1 || fail "issue close: sentence refused"
git -C "$WT" add -A; git -C "$WT" commit -q -m "hold decided (#a1-0005)"
# report + list
python3 "$G" stream report a1 --repo "$S/alpha" | grep -q "closed/resolved: #a1-0004 #a1-0005" || fail "stream report"
python3 "$G" stream list --repo "$S/alpha" | grep -q "^a1 .*open .*#0001" || fail "stream list"
python3 "$G" stream merge a1 --repo "$S/alpha" >/dev/null 2>&1
[ -e "$S/alpha/x.txt" ] && grep -q hello "$S/alpha/x.txt" || fail "merge: stream file missing in parent"
[ -e "$S/alpha/issues/a1-0004-m2-stream-work.md" ] || fail "merge: stream issue missing in parent"
grep -q '"issue_min": 1,' "$S/alpha/.gantry/adapter.json" && ! grep -q issue_prefix "$S/alpha/.gantry/adapter.json" || fail "merge: parent adapter clobbered"
expect "$S/alpha/GRAPH.md" "closed/resolved: #a1-0004 #a1-0005"
expect "$S/alpha/GRAPH.md" "streams closed: a1\[merged\]"
[ ! -d "$WT" ] || fail "merge: worktree not removed"
python3 "$S/alpha/tools/gantry_extract.py" --client "$S/alpha/.gantry/adapter.json" --root "$S/alpha" --out "$S/o.json" --digest "$S/g.md" | grep -q "prefix 'a1'" && fail "merge: parent warns on registered prefix"
python3 "$G" stream drop b1 --repo "$S/alpha" >/dev/null 2>&1
git -C "$S/alpha" add -A; git -C "$S/alpha" commit -q -m "stream try-b dropped (#0001)"
python3 "$G" check "$S/alpha" >/dev/null || fail "alpha: final check"
# nested: a stream spawned inside a stream gets prefix a1<letter><seq>
python3 "$G" stream new --repo "$S/alpha" --issue 1 --slug try-c >/dev/null 2>&1
WTC="$S/.gantry.alpha.streams.c1"
python3 "$G" stream new --repo "$WTC" --issue c1-0001 --slug nested >/dev/null 2>&1
[ -d "$S/.gantry.alpha.streams.c1a1" ] || { ls -d "$S"/.gantry.* ; fail "nested stream prefix c1a1"; }
expect "$S/.gantry.alpha.streams.c1a1/GRAPH.md" "issues #c1a1-0001"

echo; echo "ALL PASSED  (scratch: $S)"
