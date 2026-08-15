# #0004 — M3: sub-projects — gantry fork (generic, next level) + gantry stream new/list/merge/drop + check
type: milestone        status: closed
refs: [4] [5] [6] [7] [m2]   opened: M0   closed-by: ae26ba2
deps: defers-to #0006; informs #0007

**Component constraint (Tier 2):** `gantry fork <base> <new>` births a separate repo at
level+1 (band the next thousand; inherited issues closed as a reference set; birth commit
exempt and says so; adopt + mint). `gantry stream new --issue N --slug S` adds a worktree on
`stream/N-S` with its own adapter band (a free hundred inside the next level's thousand),
records it in the parent's `.gantry/streams.json`; `merge` folds it back keeping the parent's
adapter and regenerating derived files; `drop` discards; `list` reports; `check` is the CI
gate.
**Traces to (Tier 1):** "never collides"; an orchestrator can run streams in parallel.

Exit test: `tests/run.sh` steps 5–7. Sub-band size is an open decision (#0006).
