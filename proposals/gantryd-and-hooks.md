# proposed — gantry as a resident service (gantryd) + the hook catalogue (2026-09-23, discussion)

**Status:** discussion · **Refs:** see body · **Filed:** see date in title

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
