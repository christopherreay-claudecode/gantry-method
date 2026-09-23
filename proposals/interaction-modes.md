# interaction modes (how a session talks to the human — one is built, one is on the table)

**Status:** discussion · **Refs:** see body · **Filed:** see date in title

- built: **substantive answers are MindMapTrees** (`designDocs/MindMapTreeFormat-0.1.md`, `tools/g tree new`,
  #0016 #0017 #0019). Dense by design; the density is the signal.
- proposed: **blueprinter** — a separate tool a gantry repo can request, NOT part of the core ritual: given
  "ensure X", it generates an N-step process plus a dimensional scoring rubric, then interviews the human
  until the process and the scores stop moving under further answers and the requirements are clear;
  the converged output is what enters `plan.md` / issues. Relation to `docs/01-constraint-interview.md`:
  that doc is the manual protocol for one artefact (plan.md §2); blueprinter is the generalised,
  convergence-gated form for any X. Kept separate so the core briefing stays one screen.
  type: ambiguity   refs: [10]   opened: 2026-09-05 — decide: own repo (gantry-blueprinter, adopted) vs a
  `tools/g blueprint` subcommand vs a docs/ protocol only.
