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

step "stream — spawned by an issue, worktree, sub-band #1000–#1099, work inside, merge back"
python3 "$G" stream new --repo "$S/alpha" --issue 1 --slug try-a >/dev/null 2>&1
WT="$S/alpha/.gantry/streams/0001-try-a"
[ -d "$WT" ] || fail "stream: worktree missing"
expect "$WT/GRAPH.md" "lineage: level 1 · stream of alpha @ .* (parent issue #0001) · issues #1000–#1099"
git -C "$S/alpha" add .gantry/streams.json; git -C "$S/alpha" commit -q -m "stream try-a opened (#0001)"
expect "$S/alpha/GRAPH.md" "streams open"
expect "$S/alpha/GRAPH.md" "#1000–#1099 0001-try-a · #0001 · stream/0001-try-a"
# a second stream gets the next sub-band
python3 "$G" stream new --repo "$S/alpha" --issue 1 --slug try-b >/dev/null 2>&1
expect "$S/alpha/.gantry/streams/0001-try-b/GRAPH.md" "issues #1100–#1199"
# work inside stream a: an issue in-band + a code file
cat > "$WT/issues/1000-m2-stream-work.md" <<'I'
# #1000 — M2: stream work
type: milestone        status: open
refs: [m0]   opened: seed   closed-by: <sha>
I
echo stream-a > "$WT/a.txt"; git -C "$WT" add -A; git -C "$WT" commit -q -m "stream work (#1000)"
expect "$WT/GRAPH.md" "#1000 workorder m2-stream-work"
# an out-of-band issue in the stream warns
cat > "$WT/issues/1200-bad.md" <<'I'
# #1200 — out of band
type: milestone        status: open
refs: [m0]   opened: seed   closed-by: <sha>
I
python3 "$WT/tools/gantry_extract.py" --client "$WT/.gantry/adapter.json" --root "$WT" --out "$S/o.json" --digest "$S/g.md" | grep -q "above issue_max 1099" || fail "stream: out-of-band not warned"
rm "$WT/issues/1200-bad.md"
git -C "$S/alpha" add -A; git -C "$S/alpha" commit -q -m "stream try-b opened (#0001)"
python3 "$G" stream list --repo "$S/alpha" | grep -q "#1000–#1099 open" || fail "stream list"
python3 "$G" stream merge 0001-try-a --repo "$S/alpha" >/dev/null 2>&1
[ -e "$S/alpha/a.txt" ] || fail "merge: stream file missing in parent"
[ -e "$S/alpha/issues/1000-m2-stream-work.md" ] || fail "merge: stream issue missing in parent"
grep -q '"issue_min": 1,' "$S/alpha/.gantry/adapter.json" || fail "merge: parent adapter clobbered"
expect "$S/alpha/GRAPH.md" "#1000 workorder m2-stream-work"
expect "$S/alpha/GRAPH.md" "streams closed: 0001-try-a\[merged\]"
[ ! -d "$WT" ] || fail "merge: worktree not removed"
# no 'above issue_max' warning in the parent for merged-in #1000
python3 "$S/alpha/tools/gantry_extract.py" --client "$S/alpha/.gantry/adapter.json" --root "$S/alpha" --out "$S/o.json" --digest "$S/g.md" | grep -q "above issue_max" && fail "merge: parent warns on merged stream band"
python3 "$G" stream drop 0001-try-b --repo "$S/alpha" >/dev/null 2>&1
git -C "$S/alpha" add -A; git -C "$S/alpha" commit -q -m "stream try-b dropped (#0001)"
python3 "$G" check "$S/alpha" >/dev/null || fail "alpha: final check"

echo; echo "ALL PASSED  (scratch: $S)"
