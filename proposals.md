# gantry — proposals (on the table, not in the graph)

## issues
- #0012 — retire fork-app.sh into gantry fork + a per-base manifest
  type: workorder        status: open
  refs: [1] [S1]   opened: seed
- #0013 — restore metalKnee-era rigor: state.schema.json + validate_deps.py
  type: workorder        status: open
  refs: [8]   opened: seed

## routes
- route A (finish the lineage story first): #0012 → #0013 (the REV ambiguity was filed as #0022 on 2026-09-05)

## interaction modes (how a session talks to the human — one is built, one is on the table)
- built: **substantive answers are MindMapTrees** (`designDocs/MindMapTreeFormat-0.1.md`, `tools/g tree new`,
  #0016 #0017 #0019). Dense by design; the density is the signal.
- proposed: **blueprinter** — a separate tool a gantry repo can request, NOT part of the core ritual: given
  "ensure X", it generates an N-step process plus a dimensional scoring rubric, then interviews the human
  until the process and the scores stop moving under further answers and the requirements are clear;
  the converged output is what enters `plan.md` / issues. Relation to `docs/01-constraint-interview.md`:
  that doc is the manual protocol for one artefact (plan.md §2); blueprinter is the generalised,
  convergence-gated form for any X. Kept separate so the core briefing stays one screen.
  type: ambiguity   refs: [10]   opened: 2026-09-05 — decide: own repo (gantry-blueprinter, adopted) vs a
  `tools/g blueprint` subcommand vs a docs/ protocol only.

## held design — per-request in-memory SQLite over the whole network (2026-09-05, not filed)
- what: on each call, load state.json (entities · relations · bindings) + bodies.json + the mmt
  symbol table across `mmt_roots` + tree edges into an in-memory sqlite3 (stdlib; a few thousand
  rows; milliseconds), answer one question, discard. Derived, never persisted — the only kind
  of second map the method allows; the speed is what makes that kind affordable.
- earns tokens on: transitive closure (`deps #1042 --depth 3`), reverse refs (`serves 19`),
  full text over bodies (FTS5), cross-repo joins; `tree diff` (#0021) is one such query hand-coded.
- conditions: the tool owns the grammar (verbs, `--sql` only as escape hatch); output small or a
  MindMapTree with live tokens; GRAPH.md stays step 1 of the ritual.
- status: Christopher is experimenting in the scenarios where it seems useful; revisit when he
  has cases. Not an issue until then.

## proposed — cross-repo references: a root prefix is a namespace, mmt_roots is the table of namespaces (2026-09-05)
- observed: trees resolve `core:#1013` / `ui:S1` / `gantry:scripts/mmt.py` across `mmt_roots` (#0016 #0020);
  the graph does not. cubeOnSKOS-ui's extractor emits 10 warnings "#0011: body mentions #1006 — no such
  issue" — those are core's issues, read as dangling; `deps: blocks ui:#0011` is not a legal line; the ui
  commit lint rejected "(gantry #0020)". Streams already have the mechanism for children (`#a1-0003`,
  prefix namespace in ISSUE_ID); it was never generalised to siblings.
- proposal (one rule, four surfaces):
  - grammar: ISSUE_ID gains an optional root prefix drawn from `mmt_roots` — `refs: [ui:#0011]`,
    `deps: blocks ui:#0011`, body `core:#1006`, commit `(ui:#0011)`. Stream prefixes unchanged.
  - extractor: a prefixed ref becomes an external entity `ext:<root>:<NNNN>`, resolved against the
    sibling's `.gantry/out/state.json` when the `mmt_roots` path is reachable (label, status), else
    marked "unverified" — never "no such issue", never counted against the band.
  - GRAPH.md: a "cross-repo edges" block; the ui's 10 warnings become 10 edges.
  - lint_commit: accepts `root:#NNNN` when `root` is in `mmt_roots`.
  - SPEC: §5 grammar + §8 lineage ("a sibling is addressed by root prefix; a child by stream prefix").
  type: feature   refs: [4] [5] [7]   — touches the extractor + SPEC in one commit (constraint 10), tests/run.sh step.
- open question ⛭human: does a cross-repo `blocks` edge participate in "must resolve first" ordering,
  or is it informational only until the sibling's state.json confirms the target closed?

## proposed — gantry as a resident service (gantryd) + the hook catalogue (2026-09-23, discussion)
Not an issue yet: a proposition to work on. Converges #0028 (no copies), #0031 (one installation),
#0032 (registry), the held SQLite view and an MCP surface into one shape.

- **the one law:** the service NEVER holds truth. plan/seams/issues/trees/adapter stay in git,
  cloneable, offline. The service is a cache of every registered repo plus an event bus; kill it
  and every repo still works (hooks still extract, GRAPH.md is still committed) — only slower and alone.
- **event source = commits, not the filesystem.** A commit is the aggregation boundary the method
  already defines (GRAPH.md is minted into it, the lint runs on it, the REV names it). inotify is an
  exhaustible per-directory resource that fires on typing, temp files and checkouts; the service
  would spend its life debouncing noise into the boundary git already draws. So: post-commit /
  post-merge / post-checkout shims → `gantry event <repo> <sha>`, plus a slow HEAD poll over the
  registry as fallback. The one pre-commit artefact that wants a page — a tree — is already rendered
  synchronously by `tree new`.
- **first piece to build: the MCP server**, daemon-absent (each call re-parses; fine at these sizes).
  Tools = verbs: map · open · next · show · tree new · deps N --depth · packet P · ready-to-merge ·
  view NAME. Every result small-or-tree. `tree new` over MCP = the heredoc as a tool call, the URL as
  the result — the "written once" ritual in any harness that speaks MCP; CLAUDE.md is then genuinely
  just the project's contract, the method arrives as tools. The daemon is an optimisation of
  something already in use, which is the right order.
- **then:** the daemon (systemd user unit) — registry-wide cache, cross-repo edges resolved live, the
  doc store deduped across repos, localhost site (one reader; "never published" holds), streams
  launched/watched/merged as checked events, notify-send on drift and on every-issue-closed.
- **hooks a repo gets — three kinds, all declared in `.gantry/adapter.json`, interpreted by the one
  installation; no program copy is ever edited; `g check` lists every hook in force:**
  - TABLE hooks — "what counts as a thing here": `mmt_tokens` · `mmt_links` · `mmt_edges` (built);
    `entities` (kinds the extractor mints from files — the cubeOnSKOS rules extension as data, so
    `refs: [R7]` is a real edge everywhere); `issue_types` (the repo's own types, each with closure
    authority sha|human); `lint` (core prefixes, required trailers, "a commit touching
    supabase/migrations must ref a migration issue"); `gates` (what latches one: a test command, a
    file, a sentence — so `g check` says WHY m5 is open); `views` (named projections → `g view ops`).
  - EVENT hooks — "what happens when the graph moves": pre-extract · post-extract · on-issue-open ·
    on-issue-close · on-gate-latch · on-tree · on-stream-open · on-stream-merge · on-check-fail.
    `hooks: {"on-gate-latch": "scripts/deploy-preview.sh"}`, JSON payload on stdin (repo, event,
    entity, sha), exit status advisory — never blocks a commit.
  - TEMPLATE hooks — "how gantry's artefacts read here": `.gantry/templates/` overrides
    `scripts/templates/` (issue-workorder.md · method-brief.md · seed issue · README sections · tree
    CSS); resolution repo → toolbox; `g check` reports overrides. This is the proper home for "the
    ritual text a repo wants its agents to see": versioned in the repo, rendered by gantry, never
    hand-merged into CLAUDE.md.
- **costs, honestly:** a daemon to run/restart/log; two paths (daemon present / absent) kept
  equivalent by the test suite; and the standing temptation for state to migrate into the server —
  the one law is the whole defence.
- **open, for discussion:** MCP first vs registry first · which event hooks are worth having before
  anyone asks · whether `views` belong in the adapter or in trees (a view is a query; a tree is an
  answer) · the forge as one more watched source (gh issue list on an interval).
