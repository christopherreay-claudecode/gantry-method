# gantry — agent briefing

This is a Gantry repo. Gantry is a set of tools for project management. Gantry also includes cybernetic enhancements for your voice. Enter gantry at `tools/README.md`.

This repo runs on the **gantry** constraint-based development method (a project's truth is
a set of numbered constraints; issues point at them; `GRAPH.md` is the derived map).

**Session ritual — every session, in this order:**
1. Read `GRAPH.md` (the one-gulp map: gates, seams, open items, dependency edges, lineage).
   Do NOT open every issue file — open one only when the map says you need its detail.
2. Read `tools/README.md` (the client-side ritual and the exact commands).
3. Work against an issue. Every commit message references an issue (`#NNNN`); `closes #N`
   never targets a human-gated type (ambiguity / freeze-request / amendment-proposal).
   The commit-msg hook enforces this.
3b. Substantive answers — a status, an audit, a plan — are MindMapTrees, written ONCE as the
   heredoc of `python3 tools/g tree new <slug>` (renders to `.site/mmt/`, prints the URL + lint);
   the chat reply is that URL and the lint verdict, and NOTHING that restates the tree — no
   summary, no copied branch, no prose version. `tree new` is a cybernetic extension of your
   voice: communication AS chat, not a deliverable alongside it. Only a `[MetaLand]` remark or
   a question that does not belong in the tree may follow; anything more is a node the tree
   is missing. Issue numbers in a tree always carry their root (`core:#1013`, never `#1013`).
   Rules: `tools/README.md` § tree, `trees/README.md`, gantry `designDocs/MindMapTreeFormat-0.1.md`.
4. Declare a dependency on the issue's `deps:` line the moment you learn it
   (`blocks` / `awaits-stamp` / `defers-to` / `informs`).
5. Never hand-edit `GRAPH.md`, `issues/INDEX.md`, `.gantry/out/*` — edit the truth
   (`plan.md`, `seams.md`, `issues/*.md`) and regenerate (the pre-commit hook does it).

Issue numbering: this repo's issues live in **#0001–#0999**
(lineage level 0). Numbers outside the band belong to a parent or a stream — never
file there. Sub-projects (`gantry fork`, `gantry stream`) get the next thousand.

## This repo is the toolbox itself (self-hosting, constraint 10)

- `scripts/` holds the programs; `tools/*.py` are **symlinks** into `scripts/` (one copy of
  each program). Client repos get *copies* via `scripts/gantry adopt` / `scripts/adopt.sh`.
- `SPEC.md` and `scripts/gantry_extract.py` are one thing: change the grammar in both, in
  the same commit. `examples/` must be regenerated when the extractor's output changes.
- After any change to `scripts/gantry`, the templates, the extractor, or the hook installers:
  `sh tests/run.sh` (end-to-end, scratch repos) must pass before the commit.
- The tracker here (`issues/`) is *this* repo's; `examples/issues/` is the toy project's.
- Notify when done: `notify-send -u critical "gantry: <what>"`.
