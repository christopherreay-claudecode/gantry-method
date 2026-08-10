# scripts — the programs the method requires

Every program named in `../SPEC.md`, runnable. The three Python tools are standalone (stdlib
only, no network, no model); the three shell scripts wire git hooks.

| Script | What it is | Home (SPEC §7) |
|---|---|---|
| `adopt.sh` | **one-command adoption**: copies the client tools (incl. the GRAPH.md builder), writes the ritual (`tools/README.md`), wires both hooks, mints GRAPH.md (after the adapter is filled). Idempotent. | both |
| `gantry_extract.py` | truth (plan + seams + tracker + git) → `state.json` + `GRAPH.md` + `bodies.json`. Deterministic. | **both**: runnable from the gantry repo (observer), and copied into the client as `tools/gantry_extract.py` — committed, client-owned |
| `gen_index.py` | tracker → `issues/INDEX.md` (the derived ledger). `--check` fails if stale. | client — copied into `<client>/tools/` and committed there |
| `lint_commit.py` | enforce commit/tracker law: every commit refs an issue; `closes` never targets a human-gated type. | client — copied into `<client>/tools/` and committed there |
| `install-commit-lint.sh` | copy `lint_commit.py` **and** `gen_index.py` into the client's `tools/` and wire the `commit-msg` shim. | client |
| `install-graph-hook.sh` | write the pre-commit shim: self-contained, calls the client's **own** `tools/gantry_extract.py`, derives paths from the repo at runtime, never blocks. | observer wiring only |

## Which tools live where — read this before running anything

The repo is a **toolbox for a project that adopts the method**. After `adopt.sh`,
the adopting project is self-sufficient: everything it needs is **committed inside
it** and survives a clean clone with no gantry repo present.

| Tool | Where it lives after adoption | Why |
|---|---|---|
| `gantry_extract.py` (the GRAPH.md builder) | **`<client>/tools/`, committed** | the developer LLM regenerates the map from inside the project; the pre-commit shim calls this copy |
| `gen_index.py`, `lint_commit.py` | `<client>/tools/`, committed | the tracker ledger + commit law are *client* content; a clean clone enforces itself |
| `.gantry/adapter.json`, `.gantry/out/` | `<client>/.gantry/` | adapter is curated client content — commit it. `out/` (state.json + bodies.json) is derived state: GRAPH.md is the committed product, so `out/` may be gitignored or committed — pick once and keep the CI drift check consistent |
| `.git/hooks/*` shims | unversioned wiring | git never versions hooks; the shims call the client's own `tools/` copies |

Only `.git/hooks/` is unversioned. The gantry repo itself remains a reference and
the source of `adopt.sh` — a convenient place to run extract from while developing,
but not a dependency of the adopted project.

## Running them

```sh
# extract (the core — from EITHER home; produces the map + graph state + prose sidecar):
python3 gantry_extract.py --client <adapter.json> --root <client-repo> \
        --out <out>/state.json [--digest <client-repo>/GRAPH.md] [--deps <deps.json>]
# CI drift gate: build in memory, compare the committed GRAPH.md, exit 1 on drift
# (header stamp normalized — hook-refreshed digests pass):
python3 gantry_extract.py --client <adapter.json> --root <client-repo> \
        --out <out>/state.json --digest <client-repo>/GRAPH.md --check

# index ledger — two equivalent ways:
#   a) pointed at any client checkout (no copying needed):
python3 gen_index.py --root <client-repo>
python3 gen_index.py --root <client-repo> --check      # CI: exit 1 if stale
#   b) as the client's own tool, after adoption copied it:
#      (run from the client repo; the client root is the script's parent.parent)
python3 tools/gen_index.py
python3 tools/gen_index.py --check

# commit lint (what the commit-msg hook calls — client side, from tools/):
python3 lint_commit.py --message "M1: press stands (#0002)" \
        --files src/press.c [--tracker-dir issues] [--core-prefix src/]

# install the hooks on THIS machine (hooks are never versioned):
sh install-graph-hook.sh  <client-repo> [--adapter .gantry/adapter.json] [--deps deps.json]
sh install-commit-lint.sh <client-repo> [--tracker-dir issues] [--core-prefix src/]
```

The client-side copies (`tools/gantry_extract.py`, `tools/gen_index.py`,
`tools/lint_commit.py`) compute paths from arguments or their own location, so the
same byte-identical file works from both homes — copy, don't edit.

## Adoption checklist (the receiving project's view)

1. **`sh scripts/adopt.sh <client-repo> [--core-prefix src/] [--deps deps.json]`** — the whole
   operational layer in one run: copies `gantry_extract.py` (the GRAPH.md builder) +
   `gen_index.py` + `lint_commit.py` into the project's `tools/` (with a
   `tools/README.md` ritual), wires the commit-msg shim, writes a stub adapter to
   `.gantry/adapter.json`, and (once the adapter is real) wires the self-contained
   pre-commit graph-refresh shim and mints `GRAPH.md`. Idempotent — re-run freely.
2. Fill in `.gantry/adapter.json` (paths + slug maps, SPEC §6) and re-run adopt.sh to
   mint `GRAPH.md`.
3. Commit everything gantry created (`tools/`, `GRAPH.md`, `.gantry/adapter.json`) —
   it is client content now, and the project carries its own GRAPH.md builder from
   here on. Add a CI step that regenerates `GRAPH.md` + `INDEX.md` and fails on
   drift (determinism contract, SPEC §6).
4. From here: every session starts by reading `GRAPH.md` (the ritual is in the
   client's `tools/README.md`); declare dependencies on the issue's `deps:` line the
   moment you learn them; reviewed proposals land in `deps.json`; the lint enforces
   the commit law.

The individual pieces (what adopt.sh calls) are below for the curious or for
custom wiring.
