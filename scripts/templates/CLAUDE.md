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
3b. Substantive answers — a status, an audit, a plan — are MindMapTrees written ONCE as the
   heredoc of `python3 tools/g tree new <slug>`; the chat reply is the URL + lint verdict and
   NOTHING that restates the tree (no summary, no copied branch). Only a `[MetaLand]` remark
   or a question that does not fit the tree may follow. `tools/README.md` § tree has the rules.
4. Declare a dependency on the issue's `deps:` line the moment you learn it
   (`blocks` / `awaits-stamp` / `defers-to` / `informs`).
5. Never hand-edit `GRAPH.md`, `issues/INDEX.md`, `.gantry/out/*` — edit the truth
   (`plan.md`, `seams.md`, `issues/*.md`) and regenerate (the pre-commit hook does it).

Issue numbering: this repo's issues live in **{{band}}** (lineage level {{level}}).
Numbers outside that belong to a parent, a fork, or a stream — never file there. Write
issues with `gantry issue new` (exact header grammar); a fork gets the next thousand, a
stream gets its own prefix namespace (`#<prefix>-NNNN`).

**Constraints first.** The plan's constraints descend from the lived experience of the
users/roles; each issue is a workorder that states the constraints *it* makes true, what it
depends on, and the technical approach — and seams let you build and test the lowest levels
first, then reach up.
