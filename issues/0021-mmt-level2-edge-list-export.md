# #0021 — mmt level-2 export: tree → typed node/edge JSON; mmt_edges map onto DEP_TYPES so a tree can be diffed against GRAPH.md (spec §11 bridge)
type: feature        status: closed
refs: [10] [11]   opened: seed   closed-by: eaf0721

**Constraints this issue makes true (Tier 2 — each traces to a plan constraint in `refs:`):**
- [10] `mmt.py TREE --edges out.json` emits the Level-2 shape spec §9 promises: nodes
  (`addr`, `glyph`, `depth`, `text`, `line`) and edges (`from`, `to`, `type`, `line`) including
  §5b token edges (`to` = `root:token`), so a tree is a typed edge list the way `state.json` is.
- [10] `mmt_edges` (from #0020) carries an optional map onto the extractor's `DEP_TYPES`
  (`depends→blocks`, `serves→informs`, …) so `->@` edges between issue tokens can be diffed
  against GRAPH.md's dependency edges: a status tree that says `#0019 ->@#0017 [depends]` and a
  tracker that has no such `deps:` line is a finding.
- [11] `tests/run.sh` renders the example tree with `--edges` and checks node/edge counts and one
  token edge.

**Depends on:**
#0020 (the vocabulary the export emits).

**Approaches (the technical ways to satisfy the constraints; the one taken, and why):**
- Taken: export is a flag on the existing render (one parse, two outputs); the diff against
  GRAPH.md is a separate small command `tools/g tree diff <tree>` reading `.gantry/out/state.json`,
  reporting edges present in one and absent in the other.
- Not taken: minting issues from a plan tree (spec §11 mentions it; it is a human-gated act and
  belongs to a later, separate issue).

**Exit (what latches this):**
`mmt.py examples/mmt/status-2026-09-05.mmt --edges $S/e.json` → JSON with ≥1 `[type]` edge and
≥1 token edge; `tools/g tree diff` on a tree with a deliberately wrong dependency reports it.
