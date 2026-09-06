# #0026 — stream new overwrites the worktree's CLAUDE.md with the generic briefing and it rides the merge into the parent (lost cubeOnSKOS R1–R10 and cubeOnSKOS-ui U1–U8 twice); with --brief the seeded .gantry/brief.md can be a previous stream's
type: bug        status: open
refs: [2] [5]   opened: seed   closed-by: <sha>

**Constraints this issue makes true (Tier 2 — each traces to a plan constraint in `refs:`):**
[2] Never overwrite: a client's CLAUDE.md is client content; a stream must not replace it, and a merge must not carry a briefing into the parent.
[5] A stream's identity (prefix, briefing, brief.md, packet.md) is worktree-local and never reaches the parent.

**Observed (2026-09-05/06, cubeOnSKOS and cubeOnSKOS-ui):** `stream new` writes the worktree's CLAUDE.md as
"# <repo> · stream <slug> — agent briefing" (the generic method text), losing the client's rules (R1–R10 / U1–U8).
Builders then cannot find the rules the brief cites. On `git merge --no-ff stream/...` the parent's CLAUDE.md is
replaced by the briefing (twice observed; restored by hand from history both times). Also: with `--brief`, the
seeded `.gantry/brief.md` in one worktree (a15) contained the PREVIOUS stream's brief (a13) — the packet was right.
And `.gantry/adapter.json` (with issue_prefix + lineage) rides the merge into the parent unless restored by hand
(#0018 family).

**Approaches:** (1) the briefing goes to `.gantry/BRIEFING.md` (or is appended as a clearly delimited section that
`stream merge` strips), never replacing CLAUDE.md; (2) `stream merge` restores parent-owned files (CLAUDE.md,
adapter.json, streams.json) from the parent side by policy — `git merge` with `-X ours` on those paths or a
post-merge checkout; (3) `--brief` writes the given file verbatim and asserts its content before commit.

**Exit:** tests/run.sh: after `stream new`, the worktree's CLAUDE.md still contains the client's own text; after
`stream merge`, the parent's CLAUDE.md, adapter.json and streams.json equal the pre-merge parent versions except
for the stream's status; a `--brief` file round-trips byte for byte.
