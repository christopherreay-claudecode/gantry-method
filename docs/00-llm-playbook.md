# 00 — The LLM playbook: your situation → the exact command

You are an LLM (or a person in a hurry) looking at the gantry repo. You want a repo to run
on the method. **Do not hand-assemble anything** — every situation below is one command of
`scripts/gantry`, and the command prints what to do next. Run it from anywhere; paths are
resolved. Everything it creates in the target repo is *that repo's* content (commit it);
only `.git/hooks/*` shims are unversioned wiring.

```
gantry (this repo)
├─ scripts/gantry            ← the ONE entry point   (python3, stdlib, shells out to git)
│    new · adopt · fork · stream new|list|merge|drop · check
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
| **an orchestrator** wanting to run a **test workorder or a parallel development stream** in the same repo | `python3 scripts/gantry stream new --repo <repo> --issue NNNN --slug try-a` | a git worktree at `<repo>/.gantry/streams/NNNN-try-a` on branch `stream/NNNN-try-a`, with its own issue sub-band (a free hundred in the next level's thousand), registered in `<repo>/.gantry/streams.json` (commit that, refs `#NNNN`) |
| a stream that finished | `gantry stream merge NNNN-try-a --repo <repo>` · or · `gantry stream drop NNNN-try-a --repo <repo>` | merge: `--no-ff` back into the parent branch, parent adapter kept, `GRAPH.md`/`INDEX.md` regenerated, worktree removed, stream marked `merged`. drop: worktree + branch removed, band stays reserved, marked `dropped`. Real-content conflicts stop the tool: resolve, `git add`, then `gantry stream merge <slug> --finish`. |
| CI, or "is this repo honest right now?" | `python3 scripts/gantry check <repo>` | `extract --check` + `gen_index --check` + lineage sanity; exit 1 on drift |
| the toolbox itself (this repo) | `python3 scripts/gantry adopt . --link-tools --core-prefix scripts/` | already done — `tools/*.py` are symlinks into `scripts/` |

Every command is **idempotent** and **never overwrites** anything you own. Re-running
`adopt` on an adopted repo is a no-op (no re-seed, no stamp-only commit).

## What you do right after `new` / `adopt` (the same for both)

The command seeds one issue, `#0001 — M0: <name> — plan, seams, first gate`, so the adoption
commit itself references an issue — the commit law holds from the very first commit, no
exemption. Your job is to make that milestone true:

1. **Read `GRAPH.md`** (the map) and `tools/README.md` (the ritual). Always, every session.
2. **Tier-1 interview → `plan.md` §2.** Ask what the *end user must feel / be able to do*;
   write it as the narrative at the top, then formalize it into numbered constraints
   `N. **Bold Name.** one testable sentence. (Serves Tier-1: which beat.)`, grouped under
   `### C-GROUP`. For a repo with existing code, derive the constraints from what the code
   already promises — do not invent. Delete the template comment when the first constraint lands.
3. **`seams.md`** — one row per *scheduled* substitution (`| S1 | name | now → later | freeze event |`).
   Add each `S#` to `seam_slugs` in `.gantry/adapter.json`. No speculative interfaces.
4. **Gates + tracker seed** — one `milestone` issue per near-phase gate (file name
   `NNNN-m1-<slug>.md` → the extractor derives gate `m1`), one placeholder per far phase, one
   `ambiguity` hold per already-known open question (add `Q#` to `q_holds`). Nothing else.
5. **Land the plan** with a commit whose message says `… (closes #0001)`; then edit `#0001`
   to `status: closed   … closed-by: <that sha>` in the next commit. Gate `m0` latches.
6. From here: every commit refs an issue (`#NNNN`); `closes #N` never targets a human-gated
   type; declare `deps:` the moment you learn them; never hand-edit derived files.

## The numbering law (SPEC §8) — the one thing you must not get wrong

```
level 0  root repo            #0001–#0999
level 1  fork/stream of it    #1000–#1999      streams: #1000–#1099, #1100–#1199, … #1900–#1999
level 2  fork/stream of that  #2000–#2999      streams: #2000–#2099, …
…
level 9  the deepest          #9000–#9999
```

- Your band is in `.gantry/adapter.json` (`issue_min`, `issue_max`, `lineage`) and in the
  first lines of `GRAPH.md` (`lineage: level L · kind of parent · issues #lo–#hi`).
- **Numbers outside your band are never yours to file.** Below the floor = inherited history
  (a fork keeps the base's issues, closed). Above the ceiling = a sub-project's. The extractor
  warns; `gantry check` fails.
- A **fork** takes the whole next thousand. A **stream** takes one hundred of it, so ten
  streams can run in parallel at a level and any subset can merge back without collision
  (the size is an open hold in this repo: `#0006`).
- A stream's own issues `refs:` the *shared* plan (same `plan.md`, same constraints); when it
  merges, they arrive in the parent's tracker inside their band and the parent's `GRAPH.md`
  shows them; `.gantry/streams.json` explains why they sit above the parent's ceiling.

## The orchestrator's loop (streams)

```
1. file a workorder in the parent:  issues/0042-try-approach-x.md  (refs the constraint it tests)
2. gantry stream new --repo . --issue 42 --slug approach-x        → .gantry/streams/0042-approach-x
   git add .gantry/streams.json && git commit -m "stream approach-x opened (#0042)"
3. run an agent IN the worktree — its CLAUDE.md says: this is stream 0042-approach-x,
   band #1000–#1099, work the workorder, file your issues in-band, note results in #0042's body
4. gantry stream list --repo .                                     → band · status · open/closed · branch
5. gantry stream merge 0042-approach-x --repo .   or   gantry stream drop 0042-approach-x --repo .
   (then close #0042 in the parent with the merge sha, or a sentence, per its type)
```

Streams nest: a stream can spawn a stream (level+1 again) — but the sane place to
orchestrate is the level you are at.

## If something looks wrong

- `GRAPH.md` says `(floating)` → the issue refs nothing resolvable — fix its `refs:` line
  (all three keys `refs: … opened: … closed-by: …` on **one** line, SPEC §4).
- extractor warns `below issue_min` on inherited issues after a fork → expected, history.
- extractor warns `above issue_max … in no registered stream band` → someone filed outside
  the band; move the issue into the band (renumber the file + title) or register the stream.
- the commit lint rejects your commit → add the `#NNNN`; do not `--no-verify` (the only
  sanctioned exemption is a fork's birth commit, made by the tool).
- `gantry stream merge` stops on conflicts → resolve real content, `git add`, then
  `gantry stream merge <slug> --finish`.
