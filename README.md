# gantry — the constraint-based development method, complete

**A project's truth is a set of numbered constraints; everything else is derived from
them.** gantry is a self-contained specification of that method — how a project is
planned as a stack of constraints, how those constraints become a tracked issue
structure, how two git hooks keep the tracker honest, and how `GRAPH.md` — the
one-gulp map an agent reads at session start — is generated from all of it.

It is written so a person **or an LLM** can adopt the whole method from this repo
alone: the spec (`SPEC.md`) explains it from first principles, `scripts/` ships every
program required, and `examples/` is a tiny project you can actually run the pipeline
over.

## What this repo is — and what it isn't

**In scope** (gantry as the *method* machinery):
- the constraint truth-stack and the three-tier chain (lived experience → component constraint → design);
- the issue file grammar — header, `refs:` vocabulary, `deps:` grammar, typed closure authority;
- `extract` → `state.json` + `GRAPH.md` + `bodies.json`; determinism and the REV id;
- the two git hooks (graph-refresh, commit-lint) and their deliberately-opposite ownership;
- adoption: the adapter, bootstrap order, and the delta for an existing project.

**The 3D-representation goal** (where this is headed): the method's artifacts
(`state.json`, `GRAPH.md`) are what a gantry *scene* — a 3D rendering of the
development process as a construction yard — is derived from. `docs/02-projection-3d.md`
and `docs/03-pipeline.md` specify that projection: how the grammar maps onto yard
objects (gates → gantry decks, holds → amber tags, seams → jig clamps), the four
rendering laws, and the full extract → compile → view pipeline. That pipeline is the
downstream consumer this method feeds; the scene is derived data over the same truth,
never a second copy. Nothing in the 3D world is in scope of the method itself — the
method produces `state.json` and `GRAPH.md`, which stand on their own as the textual
product every agent actually reads.

## Read order

1. **`SPEC.md`** — the complete specification. Nine sections, first-principles first
   (§1 philosophy, §2 truth stack) then the concrete grammar (§3–§5), the machinery
   (§6 GRAPH generation, §7 hooks), and adoption (§8–§9).
2. **`examples/`** — a runnable toy project (`plan.md`, `seams.md`, `issues/*.md`, `adapter.json`)
   and the exact `GRAPH.md` + `state.json` the pipeline emits from it. `examples/README.md`
   walks the loop end to end.
3. **`scripts/`** — the programs, each runnable and documented in its own header.
4. **`docs/02-projection-3d.md`, `docs/03-pipeline.md`** — the 3D-representation goal this method feeds.

## 60-second quickstart

```sh
# 1. generate the map from a project's issues (deterministic; no network, no model):
python3 scripts/gantry_extract.py \
    --client examples/adapter.json --root examples \
    --out /tmp/state.json --digest examples/GRAPH.md
# → writes state.json (graph state, hashed), GRAPH.md (the map), bodies.json (issue prose)

# 2. keep a tracker's INDEX.md fresh (pointed at any client checkout):
python3 scripts/gen_index.py --root <client-repo>   # writes issues/INDEX.md
python3 scripts/gen_index.py --root <client-repo> --check   # CI: fail if stale

# 3. check a commit obeys the tracker law:
python3 scripts/lint_commit.py --message "M1: press stands (#0002)" --files src/press.c

# 4. (optional, per-machine) automate the GRAPH refresh + wire the commit lint:
sh scripts/install-graph-hook.sh   <client-repo> <adapter.json> <out-dir> [deps.json]
sh scripts/install-commit-lint.sh  <client-repo> [--core-prefix src/]
```

## Adopting this in your project — the receiving repo's view

This repo is a **toolbox**, not a library you import. Two of the six scripts are copied
*into* your project and committed there; the rest stay here and only read your repo.

| Tool | Where it lives | Why |
|---|---|---|
| `SPEC.md`, `docs/` | this repo | read-only reference; you don't copy the method, you follow it |
| `scripts/gantry_extract.py` | this repo (observer) | only ever READS your repo via `--root`; never copied in |
| `scripts/gen_index.py`, `scripts/lint_commit.py` | **your repo's `tools/`, committed** | the tracker ledger + commit law are *your* content; a clean clone must enforce itself with no gantry present |
| `scripts/install-*.sh`, `graph-refresh.sh` | this repo; they install *wiring* | hooks live in `.git/hooks` (never versioned) and point back here or at your `tools/` copies |

To adopt:

1. `cp examples/adapter.json .gantry-adapter.json` (or wherever you keep it) and fill in
   your plan/seams/tracker paths + slug maps (SPEC §6).
2. Run extract once to mint your `GRAPH.md`: `python3 scripts/gantry_extract.py
   --client .gantry-adapter.json --root . --digest GRAPH.md`. Commit it. Wire a CI check
   that fails if a fresh run drifts (determinism contract, SPEC §6).
3. `sh scripts/install-commit-lint.sh .` — copies `gen_index.py` + `lint_commit.py` into
   your `tools/`, wires the `commit-msg` shim. Commit the copies.
4. (Optional, per-machine) `sh scripts/install-graph-hook.sh . .gantry-adapter.json <out-dir>`
   — your `GRAPH.md` refreshes in the same commit that changes the tracker. Never blocks.
5. Point your session-start ritual at `GRAPH.md` — that's the map every agent reads
   instead of opening every issue (SPEC §6).

`examples/` is the same loop on a toy project — read `examples/README.md` to see every
artifact the pipeline emits, and to feel the invariants by breaking them on purpose.

## The one idea, if you read nothing else

A project's requirements are a **numbered constraint set**, each constraint tracing up to a
felt outcome for the end user and down to the components that satisfy it. Issues are
**operational pointers at that constraint graph — never a second copy of the truth**. Because
every issue *refs* a constraint (or seam, or gate) and *declares* its dependencies, the whole
tracker is a graph whose edges are constraint entailments — and that graph, not any prose
summary, is what `GRAPH.md` hands an agent at the start of every session.
