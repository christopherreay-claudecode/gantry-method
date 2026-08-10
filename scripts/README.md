# scripts — the programs the method requires

Every program named in `../SPEC.md`, runnable. The three Python tools are standalone (stdlib
only, no network, no model); the three shell scripts wire git hooks.

| Script | What it is | Home (SPEC §7) |
|---|---|---|
| `adopt.sh` | **one-command adoption**: copies the client tools, wires both hooks, mints GRAPH.md (after the adapter is filled). Idempotent. | both |
| `gantry_extract.py` | truth (plan + seams + tracker + git) → `state.json` + `GRAPH.md` + `bodies.json`. Deterministic. | **observer** — runs from the gantry repo; never copied into the client |
| `gen_index.py` | tracker → `issues/INDEX.md` (the derived ledger). `--check` fails if stale. | **client** — copied into `<client>/tools/` and committed there |
| `lint_commit.py` | enforce commit/tracker law: every commit refs an issue; `closes` never targets a human-gated type. | **client** — copied into `<client>/tools/` and committed there |
| `graph-refresh.sh` | pre-commit hook **body**: if staged changes touch the extract inputs, re-extract and stage `GRAPH.md`. Never blocks (any failure → exit 0). | observer — wired by the installer |
| `install-graph-hook.sh` | write the pre-commit shim into a client's `.git/hooks` (points back here). | observer |
| `install-commit-lint.sh` | copy `lint_commit.py` **and** `gen_index.py` into the client's `tools/` and wire the `commit-msg` shim. | client |

## Which tools live where — read this before running anything

The repo is a **toolbox for a project that adopts the method**. Tools have two homes:

1. **Observer tools stay here** (the gantry repo). `gantry_extract.py` only ever READS the
   client (its `--root` argument points at a client checkout); it is never copied into one.
2. **Client tools get copied into the client and committed there** — `gen_index.py` and
   `lint_commit.py`. They are the *client's* own law and must survive a clean clone with no
   gantry present. Convention: `<client>/tools/gen_index.py`, `<client>/tools/lint_commit.py`.
   `install-commit-lint.sh` does this copy for you.

## Running them

```sh
# extract (the core — observer side; produces the map + graph state + prose sidecar):
python3 gantry_extract.py --client <adapter.json> --root <client-repo> \
        --out <out>/state.json [--digest <client-repo>/GRAPH.md] [--deps <deps.json>]

# index ledger — two equivalent ways:
#   a) pointed at any client checkout (observer side, no copying needed):
python3 gen_index.py --root <client-repo>
python3 gen_index.py --root <client-repo> --check      # CI: exit 1 if stale
#   b) as the client's own tool, after install-commit-lint.sh copied it:
#      (run from the client repo; the client root is the script's parent.parent)
python3 tools/gen_index.py
python3 tools/gen_index.py --check

# commit lint (what the commit-msg hook calls — client side, from tools/):
python3 lint_commit.py --message "M1: press stands (#0002)" \
        --files src/press.c [--tracker-dir issues] [--core-prefix src/]

# install the hooks on THIS machine (hooks are never versioned):
sh install-graph-hook.sh  <client-repo> <adapter.json> <out-dir> [deps.json]
sh install-commit-lint.sh <client-repo> [--tracker-dir issues] [--core-prefix src/]
```

The client-side copies (`tools/gen_index.py`, `tools/lint_commit.py`) compute paths from
arguments or their own location, so the same byte-identical file works from both homes —
copy, don't edit.

## Adoption checklist (the receiving project's view)

1. **`sh scripts/adopt.sh <client-repo> [--core-prefix src/] [--deps deps.json]`** — the whole
   operational layer in one run: copies `lint_commit.py` + `gen_index.py` into the
   project's `tools/`, wires the commit-msg shim, writes a stub adapter to
   `.gantry/adapter.json`, and (once the adapter is real) wires the pre-commit
   graph-refresh hook and mints `GRAPH.md`. Idempotent — re-run freely.
2. Fill in `.gantry/adapter.json` (paths + slug maps, SPEC §6) and re-run adopt.sh to
   mint `GRAPH.md`.
3. Commit everything gantry created (`tools/`, `GRAPH.md`, `.gantry/adapter.json`) —
   it is client content now. Add a CI step that regenerates `GRAPH.md` and fails on
   drift (determinism contract, SPEC §6).
4. From here: every session starts by reading `GRAPH.md`; declare dependencies on the
   issue's `deps:` line the moment you learn them; reviewed proposals land in
   `deps.json`; the lint enforces the commit law.

The individual pieces (what adopt.sh calls) are below for the curious or for
custom wiring.
