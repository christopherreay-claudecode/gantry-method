# #0028 — gantry as installed tooling with a registry: projects register (name = the root prefix for cross-repo issue references), tools are one installation with hook points, not copies drifting per repo
type: feature        status: open
refs: [1] [2] [4] [5]   opened: seed   closed-by: <sha>

**Constraints this issue makes true (Tier 2 — each traces to a plan constraint in `refs:`):**
- [1] [2] Gantry is ONE installed toolbox (`gantry install` on PATH), not N copies in N repos. A repo
  on the method carries its truth (plan, seams, issues, adapter, GRAPH.md) and nothing of the
  toolbox's programs. Today `tools/*.py` are copies (S1) that drift and get clobbered on upgrade
  (#0023: cubeOnSKOS lost its rules extension; the `--fresh-tools` message lied) — and this week's
  changes were propagated by hand-copying five files into three repos, nine times.
- [4] [5] A **registry** — one file the toolbox owns (e.g. `~/.gantry/registry.json`, or a path the
  environment names) — in which a project **registers**: `name`, `path`, `lineage`, `band`. The name
  IS the root prefix for cross-repo references: `core:#1013`, `ui:#0011`, `base:#0019`. `mmt_roots`
  stops being per-repo hand-written config and becomes a view of the registry; the extractor, the
  commit lint and `deps:` resolve `name:#NNNN` through it (the proposal at proposals.md
  "cross-repo references" becomes the implementation of this constraint). A bare `#NNNN` outside
  the repo's own band is then an error with a name to suggest, not a "no such issue".
- [2] **Hook points, not edits.** Where a project needs behaviour of its own, the toolbox exposes a
  named hook and the project registers data or a script against it in its adapter — never an edit
  to a toolbox program. Known hook points from real divergence: entity kinds the extractor should
  mint from adapter tables (cubeOnSKOS `rules` — its interpreter comes upstream, its data stays in
  the fork; the same shape as `mmt_tokens`); token kinds for trees (`mmt_tokens`, done); edge
  vocabularies (`mmt_edges`, done); commit-lint law (core-prefix rules); pre/post extract.
- [2] A clean clone still works: the repo records the toolbox version it was last run with
  (`.gantry/adapter.json` `gantry_version`), `gantry` refuses politely when older than that, and
  `git hooks` shims call `gantry` on PATH, falling back to a vendored copy ONLY if the operator
  asks for one (`gantry vendor`).
- [11] `tests/run.sh`: two scratch repos register; a tree in one names `other:#0001` and it resolves;
  a `deps: blocks other:#0001` line is accepted and appears as a cross-repo edge; a project hook
  (adapter-declared entity kind) mints an entity without any toolbox file changing.

**Depends on:**
#0023 (what copies cost — the evidence). Supersedes the copy half of S1 (fork-copy-rule): S1 stays
for TRUTH (a fork copies plan/seams/issues once); it stops applying to programs.

**Approaches (the technical ways to satisfy the constraints; the one taken, and why):**
- Proposed: registry as a small JSON the toolbox owns; `gantry register [--name core] [path]` on
  adopt/fork/stream (a stream registers under its prefix); `gantry ls` lists it; every command
  that today reads `mmt_roots` reads the registry filtered by what the adapter opts into
  (`peers: ["core", "ui"]`) so a repo still names its neighbourhood. Hooks: adapter keys with
  interpreters upstream (data hooks) first; script hooks (`hooks: {"pre-extract": "..."}`) only
  for what a table cannot say.
- Not taken: a git submodule for tools (the same drift, worse ergonomics); a package on PyPI
  (fine later; not the problem — the problem is per-repo copies, not distribution).
- Also not taken: relying on CLAUDE.md for anything. It is not the wrong place to put a sentence;
  it is the wrong place to rely on one doing anything (2026-09-07). The channel is GRAPH.md's
  header + `tools/README.md` + the packet + the trees, and with a registry `tools/README.md`
  becomes `gantry help` — generated, never copied.

**Exit (what latches this):**
the tests above pass; the three live repos (svelteKitOnSupabase, cubeOnSKOS, cubeOnSKOS-ui) are
registered as base / core / ui, their `tools/` directories hold no toolbox programs, and
`cubeOnSKOS-ui`'s eighteen "no such issue" warnings are eighteen cross-repo edges.
