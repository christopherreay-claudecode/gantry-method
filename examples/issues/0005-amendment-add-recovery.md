# #0005 — Amendment: add a jam-recovery constraint
type: amendment-proposal        status: closed
refs: [1]   opened: M1   closed-by: signed off by Owner 2026-02-02

**Proposed change to the plan (Tier 1):** add a constraint that a jammed stroke recovers to a safe
rest state deterministically, rather than stalling. This is a change to *truth*, so it does not
edit a constraint in place — it is an `amendment-proposal`, decided by a human, landing as a new
plan version.

**Traces to (Tier 1):** an honest machine fails predictably; a jam that stalls unrepeatably breaks
the "always the same way" promise.

`amendment-proposal` is **human-gated**: closed here by Owner sign-off. On landing, the plan gains
the new numbered constraint (with an alias/supersedes note if it splits an existing one), and
issues may then ref it. Refs constraint 1 as the anchor it extends.
