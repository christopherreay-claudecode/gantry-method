# #0002 — M1: one entry point — gantry new / adopt (+ templates, seed issue)
type: milestone        status: open
refs: [1] [2] [3] [m0]   opened: M0   closed-by: <sha>
deps: informs #0003; blocks #0004

**Component constraint (Tier 2):** `scripts/gantry new <dir>` and `scripts/gantry adopt
[<repo>]` produce a correctly adopted repo — templates for plan/seams/adapter/CLAUDE.md/
.gitignore, tools + both hooks (via `adopt.sh`), a seeded `M0` issue, and an adoption commit
that passes the commit law — creating only what is missing.
**Traces to (Tier 1):** "in one command", "never surprises".

Exit test: `tests/run.sh` steps 1–4 (new; commit law live; adopt empty; adopt with content,
own CLAUDE.md/.gitignore preserved, `--core-prefix` enforced; re-adopt is a no-op).
