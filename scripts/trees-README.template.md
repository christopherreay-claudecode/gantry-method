# trees/ — MindMapTrees (client content, committed)

One `.mmt` per tree, named `YYYY-MM-DD-<slug>.mmt`, in MindMapTreeFormat 0.1
(gantry `designDocs/MindMapTreeFormat-0.1.md`). A tree is a status, a plan, an audit or an
answer that addresses the repository's truth — issues, rules, constraints, seams, contract
sections, files, commits — by the tokens those things already have.

    python3 tools/g tree new <slug> <<'MMT' … MMT    # writes trees/<today>-<slug>.mmt, renders it,
                                                     #   prints file:// URL · lint · unresolved (--no-render: write only)
    python3 tools/g tree render [file | --all]       # re-render → .site/mmt/<name>.html (+ index)
    python3 tools/g tree render --all --open         # …and opens the index

A tree is written once — into `tree new` — and the chat carries the URL and the lint verdict.

Roots (which repositories tokens resolve in, in order) come from `.gantry/adapter.json`
`"mmt_roots": {"core": ".", "ui": "../cubeOnSKOS-ui"}`; the repo itself is the default.
Rendered pages live in `.site/mmt/` — on disk, gitignored, regenerable; never published.
