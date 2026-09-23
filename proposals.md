# gantry — proposals (on the table, not in the graph)

## issues
- #0012 — retire fork-app.sh into gantry fork + a per-base manifest
  type: workorder        status: open
  refs: [1] [S1]   opened: seed
- #0013 — restore metalKnee-era rigor: state.schema.json + validate_deps.py
  type: workorder        status: open
  refs: [8]   opened: seed

## routes
- route A (finish the lineage story first): #0012 → #0013 (the REV ambiguity was filed as #0022 on 2026-09-05)

## propositions (one file each, under proposals/ — discussion, not graph)
- [interaction-modes](proposals/interaction-modes.md) — interaction modes (how a session talks to the human — one is built, one is on the table)
- [sqlite-view](proposals/sqlite-view.md) — held design — per-request in-memory SQLite over the whole network (2026-09-05, not filed)
- [cross-repo-references](proposals/cross-repo-references.md) — proposed — cross-repo references: a root prefix is a namespace, mmt_roots is the table of namespaces (2026-09-05)
- [gantryd-and-hooks](proposals/gantryd-and-hooks.md) — proposed — gantry as a resident service (gantryd) + the hook catalogue (2026-09-23, discussion)
- [browser-facet](proposals/browser-facet.md) — a gantry project owns its browsers as widgets: permanent + transient profiles, Playwright wrapper, recorded evidence, record repo outside, agent research visible beside human research (2026-09-23)
