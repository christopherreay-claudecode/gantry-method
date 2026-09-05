# #0023 — adopt --fresh-tools on an existing client overwrites a locally-extended tools/gantry_extract.py (cubeOnSKOS lost its R1–R10 rule entities) and appends a second briefing to CLAUDE.md with lineage level 0 while the adapter says level 1
type: bug        status: open
refs: [2] [9] [10]   opened: seed   closed-by: <sha>

**Constraints this issue makes true (Tier 2 — each traces to a plan constraint in `refs:`):**
- [2] `adopt --fresh-tools` on a client that has LOCALLY EXTENDED a tool refuses to overwrite it
  (or diffs and asks): observed 2026-09-05 — cubeOnSKOS's `tools/gantry_extract.py` carries a
  `rules` extension (adapter `rule_file`/`rules` → `rule:` entities, `refs: [R7]` edges); the
  upgrade replaced it byte-for-byte with the toolbox copy and GRAPH.md lost ten entities, #1046
  went "(floating)". Restored by cubeOnSKOS cb82e97. The message printed "kept: … the client
  owns it; not overwriting" while overwriting — the two code paths disagree.
- [2] Re-running `adopt` on an already-adopted client never appends a second briefing block to
  `CLAUDE.md`; when it does write one, the lineage level comes from the adapter (cubeOnSKOS got
  "level 0" appended while its adapter says level 1 fork).
- [9] [10] `tests/run.sh`: adopt a scratch client, modify a tool locally, re-adopt with
  `--fresh-tools` — the modification survives (or the run stops and says why); re-adopt appends
  nothing to CLAUDE.md.

**Depends on:**
nothing. Note for later: the cubeOnSKOS `rules` extension is the extractor-side twin of the
`mmt_tokens` "rule" kind (#0020) and probably belongs upstream as an adapter-declared entity kind.

**Approaches (the technical ways to satisfy the constraints; the one taken, and why):**
- Proposed: record the toolbox sha of each shipped tool in `.gantry/adapter.json` `tools_from`;
  on `--fresh-tools`, a client file that differs from THAT sha's copy is locally extended → keep
  it and print a diff hint. CLAUDE.md: look for the briefing marker before appending; read
  `lineage.level` from the adapter.
- Not taken: a three-way merge (too clever for a copy-rule world).

**Exit (what latches this):**
the test above passes; `adopt --fresh-tools ../cubeOnSKOS --no-commit` leaves its extractor and
CLAUDE.md untouched.
