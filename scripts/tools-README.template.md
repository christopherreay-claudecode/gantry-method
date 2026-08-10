# tools/ — the gantry development tools (client content)

These were copied into this repo by the gantry adoption script
(`scripts/adopt.sh` from the gantry-method repo). They are **this project's own
tools**: commit them, version them, keep them. A clean clone of this repo carries
its own GRAPH.md builder and tracker law — no gantry repo required.

## The three tools

| Tool | What it does | When to run it |
|---|---|---|
| `gantry_extract.py` | truth (plan + seams + tracker + git) → `GRAPH.md` + `state.json` + `bodies.json` | after any tracker/plan/seam change — or never, if you rely on the pre-commit hook |
| `gen_index.py` | tracker → `issues/INDEX.md` (the derived ledger); `--check` fails if stale | after adding/closing issues; `--check` in CI |
| `lint_commit.py` | enforces the commit law: every commit refs an issue; `closes` never targets a human-gated type | automatically, via the `commit-msg` hook |

Config lives at `.gantry/adapter.json` (paths + slug maps); generated state lands in
`.gantry/out/`.

## The ritual (the developer LLM's session start)

1. **Read `GRAPH.md` first** — it is the one-gulp map of this project: gates,
   seams, open items, dependency edges. Do not open every issue file; open one
   only when the map says you need its detail.
2. **Keep it fresh**: the pre-commit hook regenerates `GRAPH.md` (staged in the
   same commit) whenever a commit touches the tracker inputs, and never blocks a
   commit. If you changed issues and the map looks stale, regenerate by hand:
   `python3 tools/gantry_extract.py --client .gantry/adapter.json --root . \
   --out .gantry/out/state.json --digest GRAPH.md`
3. **Declare dependencies on the issue's `deps:` line** the moment you learn them
   (`blocks` / `awaits-stamp` / `defers-to` / `informs`). Reviewed proposals from a
   model land in `.gantry/deps.json`, never minted by the extractor.
4. **Never hand-edit `GRAPH.md`, `issues/INDEX.md`, `.gantry/out/*`** — they are
   derived data; edit the truth (issues, plan, seams) and regenerate.

## CI

Add a drift gate: regenerate and fail on any diff — visualization/report drift is
derived-data drift, same severity as any other.

```sh
python3 tools/gantry_extract.py --client .gantry/adapter.json --root . \
    --out .gantry/out/state.json --digest GRAPH.md --check
python3 tools/gen_index.py --check
```

`--check` builds the fresh map in memory and compares it to the committed
`GRAPH.md` (the header commit stamp is normalized, so hook-refreshed digests
pass); exit 1 on drift.
