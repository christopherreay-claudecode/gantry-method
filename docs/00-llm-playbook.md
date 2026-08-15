# 00 — The LLM playbook: your situation → the exact command

You are an LLM (or a person in a hurry) looking at the gantry repo. You want a repo to run
on the method. **Do not hand-assemble anything** — every situation below is one command of
`scripts/gantry`, and the command prints what to do next. Run it from anywhere; paths are
resolved. Everything it creates in the target repo is *that repo's* content (commit it);
only `.git/hooks/*` shims are unversioned wiring.

```
gantry (this repo)
├─ scripts/gantry            ← the ONE entry point   (python3, stdlib, shells out to git)
│    new · adopt · fork · stream new|list|report|merge|drop · issue new|close · check
├─ scripts/adopt.sh          ← what `adopt` calls for tools + hooks (also usable alone)
├─ scripts/templates/        ← what a new repo receives (plan, seams, adapter, seed issue, CLAUDE.md)
├─ SPEC.md                   ← the method; §8 = adoption + lineage law
└─ tests/run.sh              ← every command exercised in scratch repos (run it if you changed anything here)
```

## Which situation are you in?

| You have… | Run | What happens |
|---|---|---|
| **nothing** — an empty or non-existent directory that should become a project | `python3 scripts/gantry new <dir> [--name N] [--core-prefix src/]` | mkdir · `git init` · then exactly `adopt` |
| **an empty git repo** (init'd, no files or no commits) | `python3 scripts/gantry adopt <repo>` | scaffold + tools + hooks + seed issue `#0001` + **one commit** carrying `GRAPH.md` |
| **a repo full of content and history** | `python3 scripts/gantry adopt <repo> [--core-prefix src/]...` | same, but creates **only what is missing**: your `README`, `CLAUDE.md` (a gantry section is appended), `.gitignore` (lines appended), any existing `plan.md`/`issues/` are kept. Then one commit `gantry adopted (#0001)`. |
| **a gantry-adopted base** (e.g. the SvelteKit-on-Supabase base) and want a **new product repo** from it | `python3 scripts/gantry fork <base> <new-dir> [--name N] [--fresh-tools]` | a *separate* repo (no link): tracked files at the base's HEAD minus derived/secret paths; **level = base + 1** so its issues number from the next thousand; inherited issues closed as a reference set; exempt birth commit; hooks; `GRAPH.md` minted |
| **an orchestrator** wanting to run a **test workorder or a parallel development stream** in the same repo | `python3 scripts/gantry stream new --repo <repo> --issue NNNN --slug try-a [--brief brief.md]` | a git worktree **beside** the repo at `../.gantry.<repoDirName>.streams.<prefix>` on branch `stream/NNNN-try-a`; its own issue **namespace** by prefix (`#a42-0001…` for stream a of `#0042`); seeded with `#<prefix>-0001` = your brief (the constraints / workorders to fulfil); registered in `<repo>/.gantry/streams.json` (commit that, refs `#NNNN`) |
| the orchestrator checking on streams | `gantry stream report [prefix] --repo <repo>` | reads each open stream's **`GRAPH.md`** (worktree, or `git show stream/…:GRAPH.md`): lineage, gates, open/closed items, the prefixed issues, commits since spawn. All work in a stream must surface there |
| a stream that finished | `gantry stream merge <prefix> --repo <repo>` · or · `gantry stream drop <prefix> --repo <repo>` | merge: `--no-ff` back into the parent branch, parent adapter kept, `GRAPH.md`/`INDEX.md` regenerated, worktree removed, stream marked `merged`. drop: worktree + branch removed, prefix stays reserved, marked `dropped`. Real-content conflicts stop the tool: resolve, `git add`, then `gantry stream merge <prefix> --finish`. |
| **a new issue** — any repo, any stream | `gantry issue new --repo <repo> --title "M1: …" --type milestone --refs 3 S1 m0 [--deps "blocks #0004"]` · `gantry issue close <id> --by <sha or sentence>` | writes the exact header (a mistake there floats silently) and the workorder body — *constraints this makes true · depends on · approaches · exit* — at the next free id in the repo's band or the stream's namespace; `close` refuses a sha on a human-gated type |
| CI, or "is this repo honest right now?" | `python3 scripts/gantry check <repo>` | `extract --check` + `gen_index --check` + lineage sanity; exit 1 on drift |
| the toolbox itself (this repo) | `python3 scripts/gantry adopt . --link-tools --core-prefix scripts/` | already done — `tools/*.py` are symlinks into `scripts/` |

Every command is **idempotent** and **never overwrites** anything you own. Re-running
`adopt` on an adopted repo is a no-op (no re-seed, no stamp-only commit).

## What you do right after `new` / `adopt` (the same for both)

The command seeds one issue, `#0001 — M0: <name> — plan, seams, first gate`, so the adoption
commit itself references an issue — the commit law holds from the very first commit, no
exemption. Your job is to make that milestone true:

1. **Read `GRAPH.md`** (the map) and `tools/README.md` (the ritual). Always, every session.
2. **Constraint interview → `plan.md` §2** (`docs/01-constraint-interview.md` is the protocol).
   Constraints are the first-order language: the highest are the *lived experience of the
   users / roles* — ask what they must feel / be able to do (specific or vague; vague is refined
   downward, not ignored); beneath, the networks of technical constraints that solve them.
   Write the narrative at the top, then `N. **Bold Name.** one testable sentence. (Serves
   Tier-1: which beat.)`, grouped under `### C-GROUP`. For a repo with existing code: **analyse
   the code base first, then interview the human** — the constraints are what the code already
   promises its users, confirmed and named by a person, never invented by you.
3. **`seams.md`** — one row per *scheduled* substitution (`| S1 | name | now → later | freeze event |`).
   Add each `S#` to `seam_slugs` in `.gantry/adapter.json`. No speculative interfaces — but do
   use seams to **build bottom-up**: stub the lowest levels behind a seam, test them against
   their own constraints, then reach up toward the highest.
4. **Gates + tracker seed** — one `milestone` issue per near-phase gate (file name
   `NNNN-m1-<slug>.md` → the extractor derives gate `m1`), one placeholder per far phase, one
   `ambiguity` hold per already-known open question (add `Q#` to `q_holds`). Nothing else.
   Write them with `gantry issue new`; every workorder states *its own* constraints, what it
   depends on (`deps:`), and only then the approaches.
5. **Land the plan** with a commit whose message says `… (closes #0001)`; then edit `#0001`
   to `status: closed   … closed-by: <that sha>` in the next commit. Gate `m0` latches.
6. From here: every commit refs an issue (`#NNNN`); `closes #N` never targets a human-gated
   type; declare `deps:` the moment you learn them; never hand-edit derived files.

## The numbering law (SPEC §8) — the one thing you must not get wrong

```
level 0  root repo                 #0001–#0999
level L  FORK of a level-(L-1) repo #L000–#L999            (a separate repo: the whole thousand; L ≤ 9)
         STREAM of any repo         #<prefix>-0001, #<prefix>-0002 …   prefix = <parent prefix><letter><issue seq>
                                    stream a of #0042 → a42 · stream b of #0042 → b42 · sub-stream b of #a42-0003 → a42b3
```

- Your band / namespace is in `.gantry/adapter.json` (`issue_min`, `issue_max`, `issue_prefix`,
  `lineage`) and in the first lines of `GRAPH.md` (`lineage: level L · kind of parent · issues …`).
- **Numbers outside it are never yours to file.** Below the floor = inherited history (a fork
  keeps the base's issues, closed). Above the ceiling = a fork's. A bare `#NNNN` filed inside a
  stream = a collision at merge time. The extractor warns on all three; `gantry check` fails.
- Forks take a *level* (position — they are separate repos and never meet). Streams take a
  *prefix* (identity — they merge back, in any subset, with no renumbering).
- A stream's issues `refs:` the *shared* plan (same `plan.md`, same constraints); after a merge
  they sit in the parent's tracker under their prefix and `streams.json` explains them.

## The orchestrator's loop (streams)

```
1. file the workorder in the parent (constraints it must make true; deps):
     gantry issue new --title "try approach X for C-CTRL 3" --refs 3 S1 --type workorder   → #0042
2. write the brief (the constraints, or the workorders derived from them) → brief.md
     gantry stream new --repo . --issue 42 --slug approach-x --brief brief.md   → ../.gantry.<repo>.streams.a42
     git add .gantry/streams.json && git commit -m "stream approach-x opened (#0042)"
3. run an agent IN the worktree — its CLAUDE.md says: this is stream a42, spawned by #0042, start
   from #a42-0001 (the brief); every piece of work is an issue #a42-NNNN (gantry issue new) that
   states its constraints; EVERYTHING must show in GRAPH.md
4. gantry stream report a42 --repo .        ← the check: read the stream's GRAPH.md, not its stdout
5. gantry stream merge a42 --repo .   or   gantry stream drop a42 --repo .
   then close #0042 in the parent by its type's authority (the merge sha, or a sentence)
```

Streams nest (a stream can spawn a stream: prefix `a42b3`), but the sane place to orchestrate is
the level you are at.

## If something looks wrong

- `GRAPH.md` says `(floating)` → the issue refs nothing resolvable — fix its `refs:` line
  (all three keys `refs: … opened: … closed-by: …` on **one** line, SPEC §4).
- extractor warns `below issue_min` on inherited issues after a fork → expected, history.
- extractor warns `above issue_max` / `prefix … neither this repo's own … nor a stream registered`
  / `unprefixed issue filed in stream` → someone filed outside their band or namespace; renumber
  the file + title (`gantry issue new` picks the right id), or register the stream.
- the commit lint rejects your commit → add the `#NNNN`; do not `--no-verify` (the only
  sanctioned exemption is a fork's birth commit, made by the tool).
- `gantry stream merge` stops on conflicts → resolve real content, `git add`, then
  `gantry stream merge <slug> --finish`.
