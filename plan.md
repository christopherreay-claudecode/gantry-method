# gantry — implementation plan
*Constraint-satisfaction form: the code must result in the constraints below being true.*
*Companion (Tier-1 narrative): an LLM — or a person — lands on this repo, or on a repo that
adopted it, and can put ANY repo on the method in one command: a new directory, an empty
repo, a repo full of history, a fork of a base, a worktree stream for an orchestrator. From
then on every session starts from a map that is honest (regenerated, never hand-edited),
every commit is tied to an issue, and no sub-project ever collides with its parent's
numbering. The felt outcome is trust: the scaffold never lies and never surprises.*

---

## 1. Guiding role
Every derivation is judged against one thing: **an agent following the printed commands
ends up on the method correctly, without knowing anything the commands did not tell it.**

## 2. Constraint set (the code has to result in this)

### C-ENTRY
1. **One entry point.** Every bootstrap situation — new dir, empty repo, repo with content,
   fork of a base, worktree stream — is one `scripts/gantry` subcommand; nobody
   hand-assembles the operational layer (tools, hooks, adapter, seed issue, briefing).
   (Serves Tier-1: "in one command".)
2. **Never overwrite.** Adoption creates only what is missing, never edits client-owned
   content, and re-running it is a no-op. (Serves Tier-1: "never surprises".)
3. **Adoption obeys its own law.** The commit that lands the method references an issue of
   the repo it lands in — a seeded `M0` milestone — so no lint exemption is needed. The one
   exemption (a fork's birth commit, whose repo owns no issue yet) is stated in the commit
   itself. (Serves Tier-1: "every commit is tied to an issue" holds from the first commit.)

### C-LINEAGE
4. **Levels are thousands.** A repo at lineage level L owns issues `#L000–#L999` (level 0:
   `#0001–#0999`); every sub-project — fork or stream — sits one level below its parent;
   level 9 (`#9000–#9999`) is the deepest. (Serves Tier-1: "never collides".)
5. **Streams sub-band.** Parallel streams of one repo take disjoint hundreds inside the next
   level's thousand (ten per level), so merging any subset back cannot collide.
   (Serves Tier-1: an orchestrator can run streams in parallel and fold them in.)
6. **The band is enforced.** Extract warns on any issue below the repo's floor or above its
   ceiling that no registered stream explains; `gantry check` fails on a band that
   contradicts the level. (Serves Tier-1: "the scaffold never lies".)
7. **Lineage is visible.** `GRAPH.md` states level, kind, parent, band, and open streams —
   from the adapter and `.gantry/streams.json`, never from `state.json`. (Serves Tier-1: the
   map an agent reads first says where it stands.)

### C-DERIVED
8. **Derived files ride the commit.** The pre-commit shim refreshes `GRAPH.md` **and**
   `issues/INDEX.md` in the same commit that changes their inputs — and never blocks.
   (Serves Tier-1: "regenerated, never hand-edited" costs the agent nothing.)
9. **Worktree-safe wiring.** Hook shims resolve every path from the worktree root at run
   time, so the one hook set a repo owns serves each of its streams. (Serves Tier-1: streams
   are first-class, not a special case.)

### C-DOGFOOD
10. **Self-hosting.** This repo runs on the method it ships: adopted through its own entry
    point, tools linked (not copied) so there is one copy of each program, every commit
    issue-referenced. (Serves Tier-1: trust — the toolbox is its own first client.)
11. **Exercised end to end.** `tests/run.sh` drives every subcommand in scratch repos —
    new, adopt-empty, adopt-with-content, fork, fork-of-fork, stream new/list/merge/drop,
    check — and fails on the first broken expectation. (Serves Tier-1: "correctly" is
    tested, not asserted.)

## 3. Build order (risk-first; binding, not suggestions)
1. entry point `new` / `adopt` + templates + seed issue — gate **M1**
2. extractor + hooks: bands, streams awareness, unborn HEAD, worktree-safe shim, INDEX refresh — gate **M2**
3. `fork` (generic) + `stream new/list/merge/drop` + `check` — gate **M3**
4. end-to-end tests — gate **M4**
5. docs: SPEC §8 lineage, playbook for the LLM, READMEs — gate **M5**
6. Phase B: retire/absorb `fork-app.sh`; restore metalKnee-era rigor (state schema, deps validator) — see `proposals.md`
