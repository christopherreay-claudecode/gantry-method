# proposed — cross-repo references: a root prefix is a namespace, mmt_roots is the table of namespaces (2026-09-05)

**Status:** discussion · **Refs:** see body · **Filed:** see date in title

- observed: trees resolve `core:#1013` / `ui:S1` / `gantry:scripts/mmt.py` across `mmt_roots` (#0016 #0020);
  the graph does not. cubeOnSKOS-ui's extractor emits 10 warnings "#0011: body mentions #1006 — no such
  issue" — those are core's issues, read as dangling; `deps: blocks ui:#0011` is not a legal line; the ui
  commit lint rejected "(gantry #0020)". Streams already have the mechanism for children (`#a1-0003`,
  prefix namespace in ISSUE_ID); it was never generalised to siblings.
- proposal (one rule, four surfaces):
  - grammar: ISSUE_ID gains an optional root prefix drawn from `mmt_roots` — `refs: [ui:#0011]`,
    `deps: blocks ui:#0011`, body `core:#1006`, commit `(ui:#0011)`. Stream prefixes unchanged.
  - extractor: a prefixed ref becomes an external entity `ext:<root>:<NNNN>`, resolved against the
    sibling's `.gantry/out/state.json` when the `mmt_roots` path is reachable (label, status), else
    marked "unverified" — never "no such issue", never counted against the band.
  - GRAPH.md: a "cross-repo edges" block; the ui's 10 warnings become 10 edges.
  - lint_commit: accepts `root:#NNNN` when `root` is in `mmt_roots`.
  - SPEC: §5 grammar + §8 lineage ("a sibling is addressed by root prefix; a child by stream prefix").
  type: feature   refs: [4] [5] [7]   — touches the extractor + SPEC in one commit (constraint 10), tests/run.sh step.
- open question ⛭human: does a cross-repo `blocks` edge participate in "must resolve first" ordering,
  or is it informational only until the sibling's state.json confirms the target closed?
