# scripts — the programs the method requires

Every program named in `../SPEC.md`, runnable. The three Python tools are standalone (stdlib
only, no network, no model); the three shell scripts wire git hooks.

| Script | What it is | Owner (SPEC §7) |
|---|---|---|
| `gantry_extract.py` | truth (plan + seams + tracker + git) → `state.json` + `GRAPH.md` + `bodies.json`. Deterministic. | observer |
| `gen_index.py` | tracker → `issues/INDEX.md` (the derived ledger). `--check` fails if stale. | client |
| `lint_commit.py` | enforce commit/tracker law: every commit refs an issue; `closes` never targets a human-gated type. | client |
| `graph-refresh.sh` | pre-commit hook **body**: if staged changes touch the extract inputs, re-extract and stage `GRAPH.md`. Never blocks (any failure → exit 0). | observer |
| `install-graph-hook.sh` | write the pre-commit shim into a client's `.git/hooks` (points back here). | observer |
| `install-commit-lint.sh` | copy `lint_commit.py` into the client's `tools/` and wire the `commit-msg` shim. | client |

## Running them

```sh
# extract (the core): produces the map + graph state + prose sidecar
python3 gantry_extract.py --client <adapter.json> --root <client-repo> \
        --out <out>/state.json [--digest <client-repo>/GRAPH.md] [--deps <deps.json>]

# index ledger (run inside the client repo; expects a sibling issues/ dir)
python3 gen_index.py            #   writes issues/INDEX.md
python3 gen_index.py --check    #   CI: exit 1 if stale

# commit lint (what the commit-msg hook calls)
python3 lint_commit.py --message "M1: press stands (#0002)" \
        --files src/press.c [--tracker-dir issues] [--core-prefix src/]

# install the hooks on THIS machine (hooks are never versioned):
sh install-graph-hook.sh  <client-repo> <adapter.json> <out-dir> [deps.json]
sh install-commit-lint.sh <client-repo> [--tracker-dir issues] [--core-prefix src/]
```

## Note: these are the bundle-local copies

The canonical homes are `gantry/extract/gantry_extract.py`, `gantry/hooks/*.sh`,
`gantry/hooks/lint_commit.py`, and each client's `tools/gen_index.py`. The copies here are
**functionally identical**, with one deliberate change: the three shell scripts reference their
**own directory** (`$HERE/...`) rather than gantry's `../extract/` and `../hooks/` layout, so the
whole method runs self-contained from this folder. Each edited script carries a "bundle-local
variant" comment at the change. If you prefer the canonical installers, run the ones in
`gantry/hooks/` instead — they wire the same behavior against the gantry repo layout.

`gantry_extract.py`, `gen_index.py`, and `lint_commit.py` are byte-identical to their canonical
sources (they compute paths from arguments or their own location and need no adjustment).
