# #{{number}} — M0: {{title}}
type: milestone        status: open
refs: [m0]   opened: seed   closed-by: <sha>

**Component constraint (Tier 2):** this repo carries a plan of numbered constraints, a seam
table, and a first gate — the truth stack (SPEC §2) exists and `GRAPH.md` renders it.
**Traces to (Tier 1):** every later issue can name the felt outcome it serves, because the
narrative and constraints exist to be pointed at.

Exit test (gate `m0` latches when):
- `plan.md` §2 holds ≥1 real constraint, each tracing to a Tier-1 beat (the template
  placeholder is gone);
- `seams.md` lists every *scheduled* substitution (possibly none);
- the near-phase gates each have a milestone issue; every known open question has a hold;
- `python3 tools/gantry_extract.py … --check` and `python3 tools/gen_index.py --check` pass.

Close this issue with the commit that lands the plan (`… (closes #{{number}})`).
{{lineage_note}}
