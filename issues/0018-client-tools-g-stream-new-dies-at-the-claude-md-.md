# #0018 — client tools/g stream new dies at the CLAUDE.md template step AFTER creating the worktree — half-registered stream, emptied streams.json and deleted CLAUDE.md in the worktree
type: bug        status: closed
refs: [10]   opened: seed   closed-by: 523ae08

**Constraints this issue makes true (Tier 2 — each traces to a plan constraint in `refs:`):**
[10] A client's copied `tools/g` either completes `stream new` or leaves nothing behind.

**Observed (cubeOnSKOS, 2026-09-05, three times):** `python3 tools/g stream new --issue 1057 --slug notes`
printed `gantry: template CLAUDE.md not found at <client>/tools/templates/CLAUDE.md — run this subcommand
from the gantry toolbox` — AFTER `git worktree add` and after the worktree's adapter/CLAUDE.md were touched.
Result: worktree present, branch present, no seed commit, nothing in the parent's `.gantry/streams.json`;
inside the worktree `CLAUDE.md` was deleted and `.gantry/streams.json` emptied (the builder agent restored
both by hand). `stream merge` then said `no stream 'a1059'`; after hand-registering, it hit #0015 and landed
only metadata. Running the same command from the toolbox (`../gantry/scripts/gantry stream new --repo .`)
works.

**Depends on:**
#0015 (merge lands nothing) — same family: a step that can fail after state has changed.

**Approaches:**
- Check for the template BEFORE `git worktree add` (preflight every input), or ship the templates with the
  client copy (`adopt` copies `scripts/templates/` to `tools/templates/`), or make `tools/g` locate the
  toolbox via the path recorded in `tools/README.md` / an env var. The first is mandatory; one of the others
  is the fix.
- On any die() after the worktree exists: remove the worktree and branch (or say exactly what was left).

**Exit:**
`tests/run.sh`: a client copy of `tools/g` with no `tools/templates/` either completes `stream new` or exits
non-zero having created nothing (no worktree, no branch, streams.json unchanged).
