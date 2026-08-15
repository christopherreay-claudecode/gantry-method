# #0001 — M0: gantry — plan, seams, first gate
type: milestone        status: open
refs: [m0] [10]   opened: seed   closed-by: <sha>

**Component constraint (Tier 2):** this repo carries a plan of numbered constraints, a seam
table, and a first gate — the truth stack (SPEC §2) exists and `GRAPH.md` renders it.
**Traces to (Tier 1):** every later issue can name the felt outcome it serves, because the
narrative and constraints exist to be pointed at.

Seeded by `gantry adopt . --link-tools` — the toolbox adopting itself (constraint 10). Gate
`m0` latches when `plan.md` §2 holds the real constraints (the template placeholder is gone),
`seams.md` lists every scheduled swap, and `gantry check .` passes.
