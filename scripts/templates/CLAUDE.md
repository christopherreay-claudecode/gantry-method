# {{name}} — agent briefing

This repo runs on the **gantry** constraint-based development method (a project's truth is
a set of numbered constraints; issues point at them; `GRAPH.md` is the derived map).

**Session ritual — every session, in this order:**
1. Read `GRAPH.md` (the one-gulp map: gates, seams, open items, dependency edges, lineage).
   Do NOT open every issue file — open one only when the map says you need its detail.
2. Read `tools/README.md` (the client-side ritual and the exact commands).
3. Work against an issue. Every commit message references an issue (`#NNNN`); `closes #N`
   never targets a human-gated type (ambiguity / freeze-request / amendment-proposal).
   The commit-msg hook enforces this.
4. Declare a dependency on the issue's `deps:` line the moment you learn it
   (`blocks` / `awaits-stamp` / `defers-to` / `informs`).
5. Never hand-edit `GRAPH.md`, `issues/INDEX.md`, `.gantry/out/*` — edit the truth
   (`plan.md`, `seams.md`, `issues/*.md`) and regenerate (the pre-commit hook does it).

Issue numbering: this repo's issues live in **#{{issue_min_padded}}–#{{issue_max_padded}}**
(lineage level {{level}}). Numbers outside the band belong to a parent or a stream — never
file there. Sub-projects (`gantry fork`, `gantry stream`) get the next thousand.
