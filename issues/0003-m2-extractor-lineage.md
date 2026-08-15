# #0003 — M2: extractor + hooks know lineage — bands, streams, unborn HEAD, worktree-safe shim, INDEX refresh
type: milestone        status: closed
refs: [6] [7] [8] [9] [m1]   opened: M0   closed-by: c63c534
deps: blocks #0004

**Component constraint (Tier 2):** `gantry_extract.py` (0.5.0) warns on issues outside the
adapter's `issue_min`–`issue_max` band unless a registered stream band explains them, reads
`.gantry/streams.json`, renders a lineage block in `GRAPH.md` (digest only — never in
`state.json`/REV), and tolerates an unborn HEAD (stamp `0000000+dirty`) so the birth
commit's hook can mint the map. The pre-commit shim derives every path from the worktree
root and refreshes `issues/INDEX.md` alongside `GRAPH.md`.
**Traces to (Tier 1):** "the scaffold never lies"; streams are first-class.

Exit test: `tests/run.sh` step 7's out-of-band warning and merged-band silence; step 1's
single birth commit carrying `GRAPH.md`.
