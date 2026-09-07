# trees/ — MindMapTrees (client content, committed)

One `.mmt` per tree, named `yyyymmdd-HHMMSS-<slug>.mmt` (a tree is a moment; the index lists newest first), in MindMapTreeFormat 0.1
(gantry `designDocs/MindMapTreeFormat-0.1.md`). A tree is a status, a plan, an audit or an
answer that addresses the repository's truth — issues, rules, constraints, seams, contract
sections, files, commits — by the tokens those things already have. Issue numbers ALWAYS carry
their root (`core:#1013`, `ui:#0011`, `<thisRepo>:#0007`): a bare `#0007` is rejected by the lint.

    python3 tools/g tree new <slug> <<'MMT' … MMT    # writes trees/<now>-<slug>.mmt, renders it,
                                                     #   prints file:// URL · lint · unresolved (--no-render: write only)
    python3 tools/g tree render [file | --all]       # re-render → .site/mmt/<name>/index.html + doc/ (+ site index)
    python3 tools/g tree render --all --open         # …and opens the index

`tree new` is a cybernetic extension of the model's voice — communication AS chat, not a deliverable
alongside it. A tree is written once — into `tree new` — and the chat carries the URL and the lint verdict,
nothing that restates the tree (no summary, no copied branch). A `[MetaLand]` remark or a question
that does not fit the tree may follow; anything else belongs in the tree as a node.

Roots (which repositories tokens resolve in, in order) come from `.gantry/adapter.json`
`"mmt_roots": {"core": ".", "ui": "../cubeOnSKOS-ui"}`; the repo itself is the default.
Document pages are content-addressed: `.site/mmt/store/<sha256>.html` holds each distinct rendered
page once, and a tree's `doc/` entries are symlinks into it — two trees that saw the same version of
a document share one file; a changed document is a new hash. `tree render --all` prunes the store.
Rendered pages live in `.site/mmt/<name>/` — one directory per tree, holding the page and a `doc/`
snapshot of every document and commit the tree pointed at, as they were when it was rendered.
On disk, gitignored, regenerable; never published.
