# tools/ — the gantry development tools (client content)

These were copied into this repo by the gantry adoption script
(`scripts/adopt.sh` from the gantry-method repo). They are **this project's own
tools**: commit them, version them, keep them. A clean clone of this repo carries
its own GRAPH.md builder and tracker law — no gantry repo required.

## The short driver — `tools/g` (use this all day)

`tools/g` is the gantry entry point, committed in this repo. Prefer it over
reading files: each view prints the smallest thing that answers the question, so a
session spends tokens on the work rather than on the scaffold.

```sh
python3 tools/g map          # GRAPH.md WITHOUT its navigation index — the map you reason over
python3 tools/g open         # only the open items (+ the edges that touch them)
python3 tools/g next         # only what nothing blocks — what may be started now
python3 tools/g show 42      # one issue, with the constraints/seams its refs resolve to
python3 tools/g refresh      # regenerate GRAPH.md + INDEX.md → one line back
python3 tools/g check        # drift + lineage gate (CI)
python3 tools/g issue new -t "M2: …" -T milestone -r 3 S1 m1     # exact header, right id
python3 tools/g issue close 42 -b <landing-sha>                  # or -b "<human sentence>"
```

If the toolbox is installed on PATH (`gantry install` in the toolbox repo), the
same commands are just `gantry map`, `gantry next`, `gantry show 42`, … from
anywhere inside this repo. `tools/g` always works — a clean clone needs no toolbox.

## The tools

| Tool | What it does | When to run it |
|---|---|---|
| `g` | the driver: `map` · `open` · `next` · `show` · `refresh` · `check` · `issue new/close` · `stream …` | all day; prefer it to opening files |
| `gantry_extract.py` | truth (plan + seams + tracker + git) → `GRAPH.md` + `state.json` + `bodies.json` | after any tracker/plan/seam change — or never, if you rely on the pre-commit hook |
| `gen_index.py` | tracker → `issues/INDEX.md` (the derived ledger); `--check` fails if stale | after adding/closing issues; `--check` in CI |
| `lint_commit.py` | enforces the commit law: every commit refs an issue; `closes` never targets a human-gated type | automatically, via the `commit-msg` hook |

Config lives at `.gantry/adapter.json` (paths + slug maps); generated state lands in
`.gantry/out/`. If the adapter names a `proposals` file, its drafts render in
`GRAPH.md`'s `## proposed` annex — on the table, not in the graph; accept one by
copying it into `plan.md` / `seams.md` / `issues/` (SPEC §6).

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

## Where this repo sits (lineage — SPEC §8)

`.gantry/adapter.json` carries `issue_min` / `issue_max` / `issue_prefix` / `lineage`: this
repo's issue band or namespace and its parent (a root repo owns `#0001–#0999`; a fork sits one
level down and owns the next thousand; a stream owns a prefix namespace `#<prefix>-NNNN`).
`GRAPH.md` opens with a `lineage:` line. **Never file an issue outside it** — write issues with
`python3 <gantry-repo>/scripts/gantry issue new --repo . --title … --refs …` and the id is right
by construction; the extractor warns and `gantry check` fails otherwise. Sub-projects:
`… gantry fork <this> <new>` or `… gantry stream new --repo <this> --issue N --slug S --brief F`
(worktree beside this repo, registered in `.gantry/streams.json`; the orchestrator reads
`gantry stream report`).

## Streams — parallel work / test workorders (only if you need them)

A **stream** is a git worktree on a branch of THIS repo, spawned by one of this
repo's issues, with its own issue namespace (`#<prefix>-NNNN`) so parallel streams
never collide when they merge back. It is how an orchestrating agent runs a test
workorder, or two competing approaches, without leaving the method. The toolbox
that drives it lives at **`{{gantry_repo}}`** (`G` below).

```sh
G={{gantry_repo}}/scripts/gantry     # or just `gantry` if installed on PATH (`gantry install`)

# 0. the workorder this stream will fulfil — an issue of THIS repo, stating the
#    constraints it makes true (--refs = the plan constraints / seams it serves):
python3 tools/g issue new -t "try approach X for constraint 3" -T workorder -r 3 S1
#    → issues/00NN-try-approach-x.md ; fill the body, commit it: git commit -m "... (#00NN)"

# 1. the brief: what the stream must make true. Plain markdown; optional
#    `## issue: <title>` blocks (with optional refs:/type:/deps: lines) are
#    pre-filed as the stream's own #<prefix>-0002, -0003 … :
cat > /tmp/brief.md <<'B'
Make constraints 3 and 4 true behind seam S1. Keep the public API unchanged.

## issue: spike the adapter
refs: [3]
Write the smallest thing that satisfies constraint 3 behind S1.

## issue: exit test
refs: [4]
deps: blocks #<prefix>-0002
A test that fails before the spike and passes after.
B

# 2. spawn it (worktree lands BESIDE this repo, never inside it):
python3 $G stream new --repo . --issue 00NN --slug approach-x --brief /tmp/brief.md
#    → ../.gantry.<thisRepoDir>.streams.a<NN>/   on branch stream/00NN-approach-x
#    → registers .gantry/streams.json — COMMIT IT: git commit -m "stream approach-x opened (#00NN)"

# 3. hand it to a sub-model. The worktree carries .gantry/packet.md — a
#    self-contained first input (method in one screen · boundaries · the parent
#    workorder · the stream's issues · the constraints they resolve to ·
#    GRAPH.md head · commands). Launch runs it IN the worktree:
python3 $G stream launch a<NN> --repo .                 # default: claude -p "$(cat .gantry/packet.md)" …
python3 $G stream launch a<NN> --repo . --dry-run       # print the command, run nothing
python3 $G stream launch a<NN> --repo . --cmd 'my-agent --prompt-file .gantry/packet.md'
python3 $G stream packet a<NN> --repo . --print          # regenerate/inspect the packet

# 4. watch it — the check is the stream's GRAPH.md, not its chat output:
python3 $G stream list   --repo .
python3 $G stream report a<NN> --repo .

# 5. fold it back, or throw it away:
python3 $G stream merge a<NN> --repo .     # --no-ff; this repo's adapter kept; GRAPH.md/INDEX.md regenerated
python3 $G stream drop  a<NN> --repo .     # worktree + branch gone; the prefix stays reserved
#    then close the parent issue by its type's authority:
python3 $G issue close 00NN --by <merge-sha>
```

A stream shares THIS repo's plan and seams (read-only for it) and files only
`#<prefix>-NNNN` issues; the extractor warns if it strays. `.gantry/packet.md`
and `.gantry/run.*.json` are launch artifacts — gitignored, never truth.

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

## `tools/mmt.py` — render a MindMapTree as a linked page

A status or plan written in MindMapTreeFormat 0.1 (`designDocs/MindMapTreeFormat-0.1.md`
in gantry) renders to a local `file://` page: `@addr` anchors, `->@addr` links, and every
`#NNNN` / `R7` / `c17` / `[3]` / `S1` / `m2` / `Q1` / `§6.1` / `path:line` / commit hash
linked into a line-numbered rendering of the document that defines it.

    python3 tools/g tree new <slug> <<'MMT'             # → trees/<today>-<slug>.mmt (committed) AND
    @root  = …                                          #   .site/mmt/<name>.html; prints the file:// URL,
    └─ …                                                #   the level-1 lint and the unresolved tokens
    MMT
    python3 tools/g tree render --all --open            # re-render everything (fresh clone) + index
    python3 tools/mmt.py tree.mmt --root ui=. --root core=../core --open   # the raw renderer
    python3 tools/mmt.py - --strict < answer.txt        # level-1 lint as a gate

Roots are ordered: an unprefixed token resolves in the first root that defines it; `ui:#0011`
pins one. `tools/g tree` takes them from `.gantry/adapter.json` `"mmt_roots"` (name → path);
the repo itself is the default. Trees are client content under `trees/`; pages are `.site/mmt/`.
Never published.

**The ritual (token discipline):** a substantive answer — a status, an audit, a plan — is
written ONCE, as the heredoc of `tree new`. The tool renders it in the same call and hands back
the URL + lint; the chat reply is that URL and the verdict, not the tree again. `--no-render`
writes only. Backticks never appear inside a tree (spec §7), so a quoted heredoc is safe.
