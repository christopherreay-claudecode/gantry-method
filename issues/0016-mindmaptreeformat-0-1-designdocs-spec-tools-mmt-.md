# #0016 — MindMapTreeFormat 0.1: designDocs spec + tools/mmt.py — render a tree as a linked local page across roots, lint level 1
type: feature        status: closed
refs: [10]   opened: seed   closed-by: 024dab7

**Constraints this issue makes true (Tier 2 — each traces to a plan constraint in `refs:`):**
- [10] The notation the method's own sessions answer in is written down in this repo
  (`designDocs/MindMapTreeFormat-0.1.md`) and rendered by a tool this repo ships
  (`scripts/mmt.py` → `tools/mmt.py`), exercised by `tests/run.sh` like every other tool.

**Depends on:**
nothing — reads `CLAUDE.md`, `plan.md`, `seams.md`, `issues/`, `.gantry/out/state.json`,
`docs/contract`, `docs/plans` and git, in any gantry-shaped repo.

**Approaches (the technical ways to satisfy the constraints; the one taken, and why):**
- Taken: one stdlib script; roots are ordered repositories; tokens (§5b of the spec) resolve
  to `<root>/<path>#L<line>`; only documents the tree reaches are rendered (one hop), so the
  site stays small; level-1 lint (`?` owner+consequence, `!` actor:artefact, `x` unblocker,
  dangling `->@`) runs in the same pass, `--strict` gates.
- Not taken: bracketed link syntax in the tree (URLs in a terminal answer), or reusing
  cubeOnSKOS's `tools/linksite.py` (repo-specific symbol tables; this one is generic).
- Later: emit the level-2 edge list so a tree can be diffed against `GRAPH.md`.

**Exit (what latches this):**
`sh tests/run.sh` step "mmt": the example tree renders, every href and anchor in the site
resolves, and `--strict` rejects a `?` with no owner.
