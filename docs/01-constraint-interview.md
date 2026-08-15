# 01 — The constraint interview: from a code base (or an idea) to `plan.md`

The tool scaffolds a repo in seconds; the plan is where adoptions stall. This is the protocol
for producing `plan.md` §2 — the numbered constraint set — with a human, whether the repo is
empty or full of code. It is a conversation, not a form: the LLM analyses, the human decides.

## The doctrine it implements (SPEC §1)

```
constraints are the first-order language; work is how they are solved
├─ TOP     lived experience of the users / roles      ← may be specific or vague; vague is refined DOWN, never dropped
├─ MIDDLE  networks of technical constraints          ← each exists to make a higher one true, and says which
├─ BUILD   seams: stub the lowest levels, test them against their own constraints, reach UP level by level
└─ WORK    every workorder = its own constraints + the issues it depends on + then the approaches
```

## Step 0 — analyse before you ask (existing code base only)

Read the repo *as its users would meet it*, not as its files are laid out. Produce, for the
human, a one-screen sketch — nothing longer; it is a prompt for the interview, not a report:

- **roles**: who touches this? (end users, operators, admins, other systems, the developers)
- **entry points**: how does each role arrive? (UI routes, CLI commands, API endpoints, jobs)
- **promises the code already keeps**: what does it *guarantee* today, evidenced by tests,
  validation, invariants, migrations, error handling? Quote the evidence (file:line).
- **promises implied but unkept**: TODOs, half-built paths, config that hints at a scheduled swap.
- **swaps already present**: adapters, interfaces, feature flags, "for now" implementations →
  candidate seams.

Do not write constraints yet. Do not invent intent. Everything above is *observation*.

## Step 1 — the lived-experience layer (Tier 1), role by role

For each role, ask the human — in their words, and write their words down:

1. *"When this works, what does <role> feel / what can they do that they could not before?"*
2. *"What must never happen to <role>?"* (the negative space is often the sharpest constraint)
3. *"Which of these is a hard promise, and which is 'nice, if it comes'?"*
4. *"Is this specific enough to test, or deliberately vague for now?"* — vague is allowed at the
   top; write it as vague and mark it so ("refined by constraints N, M").

Output: the **narrative** paragraph at the top of `plan.md` (one beat per role), and the
Tier-1 constraints — usually 2–6, each `**Bold Name.** one sentence. (Serves Tier-1: <role>,
<beat>.)`.

## Step 2 — the technical network (Tier 2)

For each Tier-1 constraint, ask: *"what must be true of the system for this to hold?"* — and
keep asking of each answer until the constraint is something a test or an observation can
check. Every technical constraint names the higher one it serves. Group them (`### C-GROUP`).
For an existing code base, most of these are already *kept* by the code (Step 0's evidence) —
name them, cite the evidence in the constraint's line, and they are true from day one; the
ones the code does not yet keep are the work.

Rules the human enforces and the LLM proposes:
- a technical constraint with no parent is not a constraint; it is a preference — drop or lift it;
- two constraints that cannot both hold is a **hold** (`ambiguity` issue), not a compromise
  written into the plan;
- a number the human fixes (rates, units, tolerances) is charter, cited by the constraint.

## Step 3 — seams: how it will be built, bottom-up

Ask: *"where will an implementation be swapped — a stub now, the real thing later; a local
thing now, a service later?"* Each answer is a seam row: `| S# | name | now → scheduled |
freeze event |`. The build order follows the seams from the bottom: the lowest level (the one
nothing else can be tested without) is stubbed behind its seam, built, tested against **its
own** constraints, then the next level up depends on it. Freeze events are the gates.

No speculative seams: an interface exists only where a swap is scheduled.

## Step 4 — gates and the first workorders

From the build order: one milestone issue per near-phase gate, one placeholder per far phase,
one hold per open question surfaced in Steps 1–3. Each workorder, written with
`gantry issue new`, states:

- **the constraints it makes true** when it closes (Tier-2 lines, each tracing to a plan number),
- **what it depends on** — the issues that must land first (`deps: blocks / awaits-stamp /
  defers-to / informs`),
- **the approaches** — the technical ways of solving them, the one taken, and what a seam
  would let you swap later,
- **the exit** — the test or observation that latches it.

## Step 5 — land it

Commit `plan.md`, `seams.md`, the issues, and the adapter's `seam_slugs` / `q_holds` with a
message that `closes #<seed>` (the M0 milestone the tool seeded), then close the seed issue
with that sha. `GRAPH.md` now shows the constraint set as the anchors every issue points at.

## What the interview is not

- Not a requirements dump: fewer, sharper constraints beat many. Cite as "in v1"; amend later.
- Not the LLM's opinion of what the product should be: observations and questions from the
  LLM, decisions from the human.
- Not finished: the constraint set grows by amendment (`amendment-proposal`), and any conflict
  between a constraint and shipped design forces a one-sided update (SPEC §2) — never both,
  never neither.
