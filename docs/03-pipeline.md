# 03 — Pipeline: extract, compile, view

Three stages, one direction of flow, one curated layer in the middle. gantry never
writes into a client repository. **Status of this doc:** `extract` is shipped and
exercised in `scripts/gantry_extract.py`; `compile` and `viewer` are the
3D-representation goal this method feeds (see `docs/02-projection-3d.md` for the
projection itself). The pipeline is specified whole here so the downstream stages
have a contract to build against.

```
CLIENT REPO (truth)                         GANTRY (derived)
constraints · seam table                    ┌──────────────────────────────┐
tracker (issues/*.md) · git log     ──────► │ scripts/gantry_extract.py    │
                                            │   deterministic, no model,   │
                                            │   no net                     │
                                            └──────────────┬───────────────┘
                                                           ▼
                                            state.json   (generated header,
                                                          never hand-edited,
                                                          content-hashed)
bodyplan/<plan>.yaml  ─────────────────────────┐        │
  the ONE curated file: stable-ID              ▼        ▼
  bindings + metaphor seats             ┌──────────────────────────────┐
                                        │ compile/  state × bodyplan    │
                                        └──────────────┬───────────────┘
                                                       ▼
                                        scene.gltf + sheets/*.svg
                                                       │
                                        ┌──────────────▼───────────────┐
                                        │ viewer/  static three.js page │
                                        └──────────────────────────────┘
```

## Determinism contract

- Same client-repo commit + same bodyplan ⟹ **byte-identical** `state.json`,
  `scene.gltf`, and sheets. No wall-clock, no randomness, no network in extract or
  compile. (The first client enforces exactly this discipline on itself; the yard
  obeys the sim's own religion.)
- `state.json` carries `generated_from: {repo, commit, extractor_version}` and a
  content hash. That hash is the scene's **REV id**, stamped in the sheet title block
  and the glTF asset metadata. A scene diff bisects to a state diff bisects to a
  client commit.
- CI mode: regenerate and fail on unexpected diff — visualization drift is a build
  break, same severity as any derived-data drift.

## Why glTF (and not an engine)

The requirements are: text-authored, diffable, deterministic to emit, zero-install
for consumers, importable elsewhere. glTF is an open JSON scene standard: the
artifact is portable (any viewer, Blender, or a game-engine importer later), and a
Python emitter needs no GPU. The viewer is one static page — three.js, orbit
controls, clipping planes, click-to-source — no build step for consumers. Engines
(Unreal, Godot) fail the adoption test for a lightweight derived-data tool: binary
assets that don't diff, heavyweight installs, headless CI pain. An engine importer
remains an *output* option precisely because the artifact is glTF.

Every glTF node carries `extras: {id, kind, status axes, bindings}` — the viewer and
the sheets key off **gantry IDs only** (the `state.json` entity ids), so the same
state can be re-skinned by a different bodyplan without touching extract or viewer.

## Where a model may help — and where it may not

The mapping from a client's entities to metaphor seats is judgment, not parsing. An
LLM may **propose patches to curated files only** (bodyplan, narrative docs):
it drafts the binding for a new issue, a seat for a new part, a one-line label. Its
output arrives as a reviewable diff and becomes checked-in data — the circularity is
contained exactly the way the first client contains it (generated ledger, curated
truth, human stamp). Extract and compile stay deterministic and model-free, forever.
A proposed binding is marked `provenance: proposed` until a human reviews it to
`provenance: confirmed`; the compiler renders unconfirmed bindings visibly tentative
(yard-tagged), so the scene never launders a guess into a fact.

## Sheets are not an afterthought

The 2D drawing sheets (law 4) are compiled from the same state as the scene, keyed by
the same IDs, and are the accessibility fallback: everything the scene claims must be
readable flat — every entity appears on at least one sheet. A gantry deployment with
the 3D viewer deleted is still a complete, if less legible, statement of the project.

## Hook mode (the client automates itself)

Adoption (`scripts/adopt.sh`) copies the extractor into the client as
`tools/gantry_extract.py` — committed, client content — and
`scripts/install-graph-hook.sh` writes a small shim into the client's
`.git/hooks/pre-commit`. Git hooks are never versioned or cloned, which is exactly
the point: the client's *committed* content is fully self-sufficient — a clean
clone builds, lints, and regenerates its own `GRAPH.md` with no gantry repo
present. The shim is a property of one machine, installed by the human who owns
the repo, not a property of the project.

What the shim does on each commit:

- If the staged changes don't touch the extract inputs (tracker dir, plan,
  kickoff), it does nothing.
- Otherwise it re-runs extract (the client's own `tools/gantry_extract.py`) and
  stages the refreshed `GRAPH.md`, so the digest rides in the **same commit** that
  changed the issues.
- It **never blocks a commit**: missing python3, missing extractor, or a failed
  extract prints a note and exits 0. Stale-but-committed beats fresh-but-mandatory.

The commit stamp is made honest by the dirty marker: at pre-commit time HEAD is
by definition behind the tree, so hook-generated digests read `@ <sha>+dirty` —
`<sha>` is the parent commit, and the "+dirty" changes are the very commit that
carries the digest. Extract records the same fact in
`generated_from.dirty` (scoped to the input paths only; unrelated noise in the
client tree does not count as dirty). A digest with no `+dirty` marker was
generated from exactly the named commit.

There is a second, separate hook: the commit lint (spec §7 — every commit refs an
issue; `closes` never targets a human-gated type). `scripts/install-commit-lint.sh
<client-repo> [--tracker-dir D] [--core-prefix P]...` copies `scripts/lint_commit.py`
(and `gen_index.py`) into the client's `tools/` — where the CLIENT commits and
owns them, because commit rules are the client's own law and must survive a clean
clone — and wires the unversioned `.git/hooks/commit-msg` shim. If the client
already has a lint, the installer keeps it, drops any requested flags (the
client's lint encodes its own law), and only wires the shim. In short: the
builder and the lint are the client's own tools, committed in its repo; the
`.git/hooks` shims are unversioned wiring on each machine.

## The bodies sidecar (why issue text is not in state.json)

The viewer's reader pane needs the issue markdown, but issue prose is **not graph
state**: rewording a paragraph must not move the REV, or every copy-edit would
invalidate a scene that is structurally identical. So extract writes a second,
separate artifact beside `state.json`:

    bodies.json   { schema_version, state_hash, bodies: { <entity-id>: {file, number, title, type, text} } }

- Written **after** the hash and never fed into `canonical_hash()` — editing prose
  changes `bodies.json` only; adding an issue, closing a gate, or declaring a dep
  changes `state.json` and the REV. `state_hash` records which state it accompanies.
- Keyed by entity id, so a milestone issue is reachable from its workorder *and*
  from the gate it latches; ids absent from the graph are dropped.
- Entities with no tracker issue behind them (constraints, seams, parts) carry no
  body by design: their truth is upstream, and the panel says so rather than
  inventing a page.

The viewer renders it with a ~70-line markdown subset (headings, lists, fenced
code, pipe tables, blockquotes, inline code/bold/links) — escaping first, always.
Vendoring a full parser would outweigh the disciplined prose it renders. Two
client-specific touches earn their keep: the `type:/status:/refs:/deps:` header
block renders as one monospace strip, and every `#NNNN` becomes a live
cross-reference that selects the target entity and swings the camera onto it.
