# Proposals — on the table, NOT part of the graph

Drafts from the Tier-1 interview and working sessions. Nothing here has entered
the plan, the seam table, or the tracker yet; a human stamps each item in
(copy it into `plan.md` / `seams.md` / `issues/` and re-run extract — it then
renders in the core sections) or out (delete it). The extractor warns on
anything it cannot parse — nothing is silently dropped.

## constraints

- **idle-timeout.** An unattended press session times out and returns to a safe state.
- **pressure-curve-memory.** The press remembers the last good pressure curve per material.

## seams

- **S3 telemetry-writer.** local log → supabase telemetry; freeze at M2

## issues

- #1007 — hold: material presets UX
  type: ambiguity        status: open
  refs: [3]   opened: seed
  Should presets be per-material or per-operator?
