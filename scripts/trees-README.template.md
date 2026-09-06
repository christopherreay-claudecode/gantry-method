# trees/ — MindMapTrees (client content, committed)

One `.mmt` per tree, named `yyyymmdd-HHMMSS-<slug>.mmt` (a tree is a moment; the index lists newest first), in MindMapTreeFormat 0.1
(gantry `designDocs/MindMapTreeFormat-0.1.md`). A tree is a status, a plan, an audit or an
answer that addresses the repository's truth — issues, rules, constraints, seams, contract
sections, files, commits — by the tokens those things already have.

    python3 tools/g tree new <slug> <<'MMT' … MMT    # writes trees/<now>-<slug>.mmt, renders it,
                                                     #   prints file:// URL · lint · unresolved (--no-render: write only)
    python3 tools/g tree render [file | --all]       # re-render → .site/mmt/<name>.html (+ index)
    python3 tools/g tree render --all --open         # …and opens the index

A tree is written once — into `tree new` — and the chat carries the URL and the lint verdict,
nothing that restates the tree (no summary, no copied branch). A `[MetaLand]` remark or a question
that does not fit the tree may follow; anything else belongs in the tree as a node.

Roots (which repositories tokens resolve in, in order) come from `.gantry/adapter.json`
`"mmt_roots": {"core": ".", "ui": "../cubeOnSKOS-ui"}`; the repo itself is the default.
Rendered pages live in `.site/mmt/` — on disk, gitignored, regenerable; never published.
