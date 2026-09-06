# The shape of the method — for reuse

*Companion to `SPEC.md` §1 (constraints are the currency) and to the practice of
2026-08 → 2026-09 on cubeOnSKOS, cubeOnSKOS-ui and gantry itself. SPEC says what the
artefacts are; this says what SHAPE the work has, so it can be recognised and carried to
another project.*

## 1. Not a pipeline, not a convergence — an attractor with mirrors

A pipeline is a sequence with a direction and an end. A convergence is many things
approaching one point. The method is neither on its own:

- **The constraint set is a fixed point, not a destination.** `plan.md` does not move while
  work happens. Work does not converge *to* it the way an iteration converges to a limit;
  work converges *onto* it the way water finds a shape that was already there. That is an
  **attractor**: it is fixed, everything else is pulled to it, and it moves only when a
  human moves it (an amendment, a freeze, an answered ambiguity).
- **Every artefact is a mirror of something upstream of it**, and a test observes whether
  the mirror is faithful. The same shape recurs at every scale:

| upstream text | downstream artefact | the observer |
|---|---|---|
| plan constraint | issue (refs) | extract invariants, GRAPH.md |
| slice spec (R10) | migration · route · contract entry · tests | review = the 1:1 mapping |
| contract file | the other repository's code | contract-conformance test |
| journey text | pages and controls | mirror test · no-orphan-controls · a naive reader (Haiku) |
| issue exit sentence | the closing commit | the observation named in the exit |

The rule is always the same: **the text is upstream; the artefact catches up; a test says
whether it has.** When a builder finds the text wrong, the text is corrected first and the
artefact follows (the UI's driven test correcting core's §14 is the canonical case). The
mirror going red is not a failure — it is the propagation signal between people and agents
who never share a context.

## 2. The unit of progress is a closure, and closures are local pipelines

Inside one issue, the work IS a pipeline: spec → template → artefact → contract → test →
commit, in that order, with the exit named before the first line is written. An issue
closes when its exit OBSERVATION holds — a sha, or for a human-gated type, a sentence. So:

- the project is not one pipeline; it is **a sequence of closures**, each a short pipeline,
  each ending in an observation, each pointing at the constraints it made true;
- closures are **monotone**: a gate that latched stays latched (a milestone is a latch, not
  a status). Time is factored out of the constraints and into the closures — the
  constraints are timeless, an issue has an `opened` and a `closed-by`, a tree is a moment.

"Sequence of convergences" is right if a convergence means a *gate*: several closures
land, the gate's exit holds, it latches. Between gates the closures are partially ordered
(deps), not sequenced.

## 3. Parallel work converges at the merge, by construction not by care

Streams are worktrees with disjoint file sets and their own issue namespace. Two builders
never share a tree, so they cannot stage each other's half-written files; they converge in
ONE merge pass the orchestrator reads. What makes this safe is not the tooling but the
shape: each stream mirrors the same upstream text, so two faithful mirrors of one text
merge cleanly, and a conflict is a *text* ambiguity surfacing — which is what the
human-gated `ambiguity` type is for.

What breaks it (observed, 2026-09-05): a merge tool that reports success and lands nothing
(gantry #0015); a hand merge that folds the stream's identity (adapter prefix) into the
parent (#0018). Both are the same defect class: a step that can fail after state has changed.
The method's weak layer is the observation layer's dependence on live externals (Google
TLS resets, a socket that someone stopped) — flakiness there reads as red mirrors that are
not.

## 4. Where humans sit

Humans are upstream and only upstream: they write and amend constraints, freeze seams,
answer ambiguities, and read trees. Every other act is downstream and reversible. A
human-gated issue closes by a sentence; a machine-closed issue closes by a sha. This is
why the attractor can be trusted to stay still while dozens of agent-hours run against it.

## 5. The reasoning surface

Trees (MindMapTreeFormat) are how status, plans and audits are spoken: containment in the
tree, every other dimension as a typed reference, every token a link back into the truth
stack. They are written once, rendered, and read; they are moments, not truth.

## 6. The transferable kernel (what to carry to a new project)

1. Numbered constraints in one file; amendments through a human gate.
2. Issues that cite constraints; a derived map never hand-edited; every commit names an issue.
3. Closure authority typed: sha for machine work, sentence for human-gated types.
4. For every artefact class, an upstream text and a template that maps 1:1 onto it; review
   is the mapping.
5. Exit = an observation named before the work, never "add a test".
6. Text-first for anything a person reads (journeys), with a naive-reader test.
7. One written contract between repositories; conformance tested on both sides.
8. Parallel streams with disjoint files, own namespaces, one merge pass.
9. Trees as the reasoning surface; the chat carries the URL.

## 7. One sentence

**A fixed set of constraints that only humans may move, mirrored downward through
templated artefacts whose faithfulness is observed by tests, advanced by monotone closures,
parallelised in disjoint streams that converge at one merge, and reasoned about in trees.**
