# 04 — Operator runbook: generating the 3D scene for an adopted client

Who this is for: the LLM operating the **visualization** machinery (compile →
`scene.gltf` + sheets → viewer) for a client repo that has adopted the method
(SPEC §7; `scripts/adopt.sh`). Read this at session start, alongside the client's
own `tools/README.md` ritual.

## The shape of an adopted client (what changed)

The client is **self-sufficient** — every input to its graph, and the builder
itself, is committed inside it:

```
<client>/
├── GRAPH.md                ← the map (committed; regenerated, never hand-edited)
├── tools/
│   ├── gantry_extract.py   ← the GRAPH.md builder (client-owned copy)
│   ├── gen_index.py        ← the issues ledger
│   ├── lint_commit.py      ← the commit law
│   └── README.md           ← the client-side ritual (its LLM reads this)
└── .gantry/
    ├── adapter.json        ← truth paths + slug maps + parts (curated)
    ├── deps.json           ← reviewed dependency edges (proposed/confirmed)
    └── out/                ← derived state (state.json, bodies.json)
```

The old observer-side inputs (`extract/clients/<client>.json`,
`depmap/<scene>/deps.json` in the gantry repo) **no longer exist** — an observer
refactor destroyed client knowledge once; that failure mode is fixed by design.
The gantry-method repo is reference only (spec, scripts, examples). Its `scripts/`
and the client's `tools/` hold **byte-identical** tools — run either.

## Files to read, in order

1. **`<client>/GRAPH.md`** — the one-gulp map: gates latched/open, seams frozen/
   provisional, open items with their refs, dependency edges. Never the issues
   first.
2. **`<client>/.gantry/adapter.json`** — where truth lives (tracker dir, plan,
   kickoff/seams), the slug maps (`seam_slugs`, `q_holds`), and the declared
   `parts` (the scene's product anatomy).
3. **`<client>/.gantry/deps.json`** — reviewed edges merged into the graph
   (`provenance: proposed|confirmed`); they already render in GRAPH.md.
4. **`<client>/plan.md`, `<client>/seams.md`, `<client>/issues/*.md`** — detail
   only when the map says you need it (SPEC §4–§5).
5. **The bodyplan for this client** — the ONE curated file (docs/02 §A): aim
   sentence → whole metaphor → seat map → law-3 audit.

## Commands (run from the gantry-method repo root, or the client's `tools/`)

```sh
# 1. (re)build the client's map — mint or refresh GRAPH.md + state.json + bodies.json
python3 scripts/gantry_extract.py \
    --client <client>/.gantry/adapter.json --root <client> \
    --out <client>/.gantry/out/state.json --digest <client>/GRAPH.md \
    --deps <client>/.gantry/deps.json

# 2. CI-style drift gate (writes nothing; exit 1 if the committed map is stale)
python3 scripts/gantry_extract.py \
    --client <client>/.gantry/adapter.json --root <client> \
    --out <client>/.gantry/out/state.json --digest <client>/GRAPH.md \
    --deps <client>/.gantry/deps.json --check

# 3. ledger freshness
python3 scripts/gen_index.py --root <client> --check

# 4. never needed during scene work, but know it exists: the client's own
#    pre-commit hook regenerates GRAPH.md in the same commit that changes the
#    tracker (never blocks); --check tolerates its +dirty stamp.
```

## Generating the scene (the compile stage)

- **Inputs**: `state.json` (fresh from extract) × the **bodyplan** (curated
  metaphor). Everything in the scene keys off gantry IDs in `state.json`.
- **Bodyplan is judgment, not parsing**: you draft it (aim sentence from the
  Tier-1 narrative → whole metaphor → seat map, per docs/02 §A), mark it
  `provenance: proposed`, and a human stamps it `confirmed`. You never edit
  `state.json` to make a nicer scene.
- **Law 3 binds you**: geometry is earned — render only what the build state
  warrants (`absent` → ghost, `stubbed` → primitive, `built` → solid,
  `frozen` → edged + stamp). The metaphor shapes *how*, never *whether*.
- **Outputs**: `scene.gltf` + sheets, deterministic from the same inputs (docs/03).

## Honesty rules (same religion as the client)

- Never hand-edit `state.json`, `GRAPH.md`, `.gantry/out/*`, `issues/INDEX.md` —
  derived data; edit truth upstream and regenerate.
- The REV in the scene's title block is the hash of `state.json`; a scene diff
  bisects to a state diff bisects to a client commit.
- The tracker never *becomes* design truth; the scene never invents state.
