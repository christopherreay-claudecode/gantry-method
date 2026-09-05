# #0017 — trees/ facet: tools/g tree new|render, adopt copies mmt.py + trees/README, mmt_roots in adapter.json — trees persist as client content, pages in .site/mmt
type: feature        status: open
refs: [10]   opened: seed   closed-by: <sha>

**Constraints this issue makes true (Tier 2 — each traces to a plan constraint in `refs:`):**
- [10] A tree is client content like an issue: `trees/YYYY-MM-DD-<slug>.mmt`, committed, rendered
  by the client's own `tools/mmt.py` copy into `.site/mmt/` on disk — it survives a reboot and a
  fresh clone (re-render), and `adopt` seeds all of it.

**Depends on:**
#0016 (the renderer and the spec).

**Approaches (the technical ways to satisfy the constraints; the one taken, and why):**
- Taken: `tools/g tree new <slug>` (stdin → file) and `tools/g tree render [files|--all]`, roots
  from `.gantry/adapter.json` `mmt_roots` so a client names its sibling repos once.
- Not taken: committing the rendered HTML (a derived artefact, hundreds of files per tree, and
  the doc copies would go stale against the sources they mirror).

**Exit (what latches this):**
`sh tests/run.sh` step 14: adopt copies `tools/mmt.py` and `trees/README.md`, gitignores `.site/`,
`tree new` writes the file, `tree render --all --strict` links `#0001` into the rendered issue.
