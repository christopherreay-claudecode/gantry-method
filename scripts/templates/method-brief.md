## The method, in one screen (gantry — SPEC.md §1, §2, §8)

- **Constraints are the first-order language; work is how they are solved.** The plan
  (`plan.md` §2) is a numbered constraint set: the highest constraints are the lived experience
  of the users/roles; beneath them, networks of technical constraints that make the higher ones
  true. Seams (`seams.md`) are the planned substitution points: build and test the lowest levels
  behind a seam first, then reach up.
- **One truth upstream.** Issues *point at* constraints, seams and gates (`refs:`); they never
  restate or amend them. `plan.md` / `seams.md` change only by amendment (a human decides) —
  **you do not edit them**; if a constraint seems wrong, open an `amendment-proposal` issue.
- **`GRAPH.md` is the map, regenerated, never hand-edited.** Read it first, every session; open
  an issue file only when the map says you need its detail. The pre-commit hook regenerates it
  (and `issues/INDEX.md`) in the same commit that changes the tracker.
- **Every workorder states its own constraints** (what is true when it closes, each tracing to a
  plan number), what it depends on (`deps:` — `blocks` / `awaits-stamp` / `defers-to` /
  `informs`), then the approaches, then the exit test. Write issues with
  `gantry issue new` — the header grammar is exact and a mistake floats silently.
- **Every commit references an issue** (`#<id>`); `closes #<id>` never targets a human-gated type
  (`ambiguity`, `freeze-request`, `amendment-proposal` close only by a human sentence). Close an
  issue by editing it (`gantry issue close <id> --by <sha|sentence>`) in a follow-up commit.
- **Everything you do must show in `GRAPH.md`.** An issue per piece of work, closed by its type's
  authority, is how the orchestrator sees your result.
