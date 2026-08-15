# The Constraint-Based Development Method — Specification

*Complete, self-contained. Companion artifacts: `scripts/` (every program named here),
`examples/` (a runnable project). Where this spec states a grammar rule, that rule is exactly
what `scripts/gantry_extract.py` parses — the spec and the parser are one thing.*

---

## §1 Philosophy — constraints are the currency

The method rests on a single conviction: **a project's truth is a set of constraints, and
everything else is derived from them.** Requirements are not prose to be interpreted; they are
numbered acceptance criteria that the code must make true. Work items are not the plan; they are
*pointers* at constraints, tracking who is satisfying which. The dependency structure between
work items is not invented by a scheduler; it *is* the entailment structure between constraints —
if satisfying constraint B requires constraint A first, the issue for B declares it, and that
declaration is the edge.

This is why the method scales without a design rotting: **there is exactly one copy of the
truth**, upstream, and every downstream artifact is regenerable from it. Delete the issue
tracker and the requirements are untouched. Delete `GRAPH.md` and it regenerates. The one thing
you may never do is let an operational artifact (an issue, a commit message, a status board)
*become* a second source of truth — because then two copies drift, and drift is where projects die.

### The three-tier chain

Every constraint, and therefore every issue, sits on a chain of three tiers. An issue that
cannot name its place on this chain is not yet specified:

```
TIER 1   lived-experience constraints     what must the END USER feel / be able to do?
   │     (the highest authority; the reason anything below exists)
   │        expressed as: a narrative of use + the numbered plan constraints that
   │        formalize it. Every lower tier must trace UP to a Tier-1 beat.
   ▼
TIER 2   component constraints            what must THIS component guarantee to satisfy Tier 1?
   │     (one or more per component; each refs the Tier-1 constraint it descends from)
   ▼
TIER 3   component design                 the mechanism / data structures that meet Tier 2.
         (lives in code + the issue body; the most volatile tier, freely revised)
```

The discipline is directional and non-negotiable: **you specify top-down and verify bottom-up.**
A component is justified only by the Tier-2 constraint it satisfies; a Tier-2 constraint is
justified only by the Tier-1 experience it serves. When you write or review an issue, you state
its component constraint *and* trace it to the lived-experience beat — "this exists because the
user must feel X." Citing a plan-constraint number is necessary but not sufficient; the number
is a handle, the felt outcome is the reason.

### Constraints are the first-order language; work is how they are solved

Everything in the method is *spoken* in constraints, and *done* as work against them:

- **The highest constraints are the lived experience of the users / roles** of what is being
  built. They may be very specific ("a committed stroke lands identically every time") or
  deliberately vague ("an operator trusts the machine") — vagueness at the top is allowed; it is
  refined downward, never ignored.
- **Beneath them, networks of technical constraints solve them.** A technical constraint exists
  only because it helps make a higher one true; it names which. The plan is this network,
  numbered.
- **Seams are how you build.** A seam is a planned substitution point; you use seams to build and
  test the *lowest* levels of the tool first — a stub behind the seam, a real implementation
  later — and then reach *up* toward the highest constraints, level by level, each level tested
  against its own constraints before the next depends on it.
- **Every workorder is expressed as its own constraints** — the ones *it* makes true when it
  closes — plus the issues it depends on (declared on `deps:`), and only then the technical
  ways of solving them (approaches weighed, one taken). `gantry issue new` writes that shape;
  a workorder that cannot state its constraints is not yet a workorder.
- **A stream is a workorder given a worktree**: an orchestrator spawns it with a brief — the
  constraints (or the workorders derived from them) to fulfil — and reads the result off the
  stream's `GRAPH.md` (§8).

A worked instance: in the reference project the Tier-1 source is a **prose narrative of the
user's experience** (a pilot learning to move under a fixed control delay). "The control delay is
fixed, therefore learnable" is a lived-experience constraint. It formalizes into plan constraints
("the executed stream is bit-identical on every machine", "commands are held H ticks then
executed"). Those become component constraints on specific modules (the command bus holds and
releases on an exact tick; the replica replays the executed stream and hashes equal). Each such
issue *refs* the plan-constraint number **and** its body says which beat of the narrative it
serves. That is the whole method in one column.

---

## §2 The truth stack

Design truth is kept in an ordered stack, each layer answering a different question, each
subordinate in authority to the one above it. Beside the stack — never inside it — sits the
operational layer (the tracker).

| Layer | Question it answers | Authority to change |
|---|---|---|
| **narrative** | what should it *feel* like? (Tier 1) | the design conversation (human) |
| **rationale** | *why* is it this way? | the design conversation (human) |
| **plan** | what *must* be true? — the numbered constraints (Tier 1 formalized) | amendment only (human) |
| **charter** | which *numbers* are fixed? (units, rates, tolerances) | amendment only (human) |
| **seams** | where may implementations *swap*? — the interface table | freeze/amend (human sign-off) |
| **code** | what *is*? (Tier 3) | ordinary commits |
| — operational — | | |
| **tracker** | who is doing what, against which constraint? | per issue type (see §3) |

The load-bearing rule, from which the whole method and every extractor invariant descends:

> **One truth upstream. Issues point at constraints, seams, and gates; they may never restate,
> extend, or amend them.**

An issue that needs to *change* a constraint does not edit it — it opens an `amendment-proposal`,
which a human decides, which lands as a new plan version. This separation is what makes "the
scaffold is never load-bearing" literally true: strike the tracker and the product still stands.

### Reconciliation — the consistency loop

One-truth-upstream says *where* truth lives; it does not, by itself, keep the truth and the build
in agreement. That is a second, active discipline: **the constraint set and the design are kept
mutually consistent by verification, and any drift forces a decision.**

- **Verify new work against the constraints.** Every new requirement, design, or spec is checked
  against the existing numbered constraints before it is accepted — does it satisfy them, and does
  it contradict any?
- **A conflict forces a one-sided update — never both, never neither.** Either the new work is
  wrong (revise it to satisfy the constraints), or the constraint is stale (open an
  `amendment-proposal`, decide it, land a new plan version). The plan is the default authority:
  new work never *silently* overrides a constraint, and a constraint is never *silently* left
  contradicting shipped design.
- **You may not live in the conflict.** An unreconciled contradiction between design and
  constraints is a **tracked defect** (an open issue), not a resting state.

A corollary for anyone citing the plan: the constraint set is **versioned and grows by
amendment** — cite constraints as "in vN," never as a fixed cardinality. What is stable across
versions is constraint *identity* (the named slug), not the *count*; splitting and merging are
allowed, and the extractor tracks identity through them. Treating "there are N constraints" as a
fixed fact is the same category error as treating an issue as design truth.

---

## §3 Entities, status, and closure authority

### Entities

| Entity | What it is | Who may close it |
|---|---|---|
| **constraint** | a numbered acceptance criterion in the plan; may be grouped (`C-CORE`, `C-CTRL`…) | amendment only (human) |
| **part** | a unit of the product an implementation realizes (a module/subsystem) | — (pointer only) |
| **seam** | a planned substitution point: one real impl now, one *scheduled* later; carries a stability tier | freeze requires sign-off |
| **gate** | a milestone/phase exit: a test set that must latch green before work above it starts | mechanical (CI) or human |
| **phase** | an ordered band of gates with an entry condition and a do-not-start list | — |
| **workorder** | a tracker item, typed (see below) | per type |
| **hold** | an `ambiguity`-typed workorder: a decision deliberately deferred; code must not resolve it silently | human sign-off |
| **stamp** | a granted human sign-off (a freeze landing, a hold closing) | human, definitionally |

Workorder **types**: `milestone`, `ambiguity`, `freeze-request`, `bug`, `amendment-proposal`.
The reference project also uses descriptive types freely (`spec`, `roadmap`, `nexus`, `workorder`,
`consideration`) — the parser accepts any single token as the type; only the **human-gated set**
below has enforced semantics.

### Status axes — kept orthogonal, never conflated

- **build**: `absent → stubbed → built` — does an implementation exist? (A stub is a first-class,
  disposable-by-design state, not a failure.)
- **stability**: `provisional → frozen` — a seam's contract tier. *Independent of build:* a seam
  can be fully built and still provisional.
- **decision**: `open → resolved` — a hold's state. *Independent of build:* the code stays green
  while a decision is deliberately open.
- **gate**: `open → latched` — has the exit test gone green (and, where required, been stamped)?
- **work**: `open → closed` — a workorder's state.
- **closure authority** (cross-cutting): `mechanical | human`. Some things a commit may close;
  some only a person may. The commit lint enforces it; the extractor renders it and *refuses to
  render a human-gated item closed by a bare sha* (invariant 2).

### Closure authority is typed

`milestone` and `bug` are **commit-closable** — `closed-by: <sha>`. The human-gated types —
`ambiguity`, `freeze-request`, `amendment-proposal` — are **sign-off-only**: `closed-by: <a human
sentence>`. This is enforced twice: the commit lint rejects `closes #N` where `#N` is human-gated,
and the extractor, seeing a human-gated issue marked `closed` with a sha-shaped `closed-by`,
overrides it to **open** and emits a warning. Design decisions cannot be closed by accident.

---

## §4 The issue file — structure and grammar

Files live in the tracker directory (conventionally `issues/`), named `NNNN-short-slug.md`,
sequentially numbered. An issue filed **inside a stream** carries the stream's prefix in its id
and file name — `#a42-0003`, `a42-0003-short-slug.md` (`prefix` = `[a-z][a-z0-9]{0,11}`, §8) — so
issues from parallel streams never collide when they merge back; everywhere below, "`#NNNN`"
means "`#NNNN` or `#<prefix>-NNNN`". The **header block is the first lines of the file** (the parser reads only
the first 6 lines for header fields) and is exact:

```
# #0002 — M1: the press completes one cycle
type: milestone        status: open
refs: [3] [S1] [m0] [Q1]   opened: M1   closed-by: <sha>
deps: defers-to #0004; informs #0003
```

Line by line, each rule is precisely what the parser matches:

- **Title** — `# #NNNN — Title`. A literal `#`, space, `#NNNN` (four digits, optionally
  `<prefix>-` before them), space, an **em-dash `—`**, space, then the title. (A hyphen will not
  match; it must be the em-dash. `gantry issue new` writes this line so you never have to.)
  Numbering need not start at `0001`: the adapter's `issue_min` (SPEC §6) sets this repo's
  floor. A repo forked from a base keeps the base's issues (`#0001`–`#0013`, a *closed
  reference set*) below the floor and numbers its own work from `#1000` — the extractor
  warns on any issue under the floor, so a fresh issue filed at `#0007` gets flagged.
- **`type:` / `status:`** — `type: <token>   status: <token>`, both single tokens.
- **`refs:` … `opened:` … `closed-by:`** — all three keys **on one line, in this order.**
  `refs:` is zero or more `[token]` groups; `opened:` is a free label (a gate name or `seed`);
  `closed-by:` is a sha *or* a human sentence. (A very common adoption bug: putting `closed-by:`
  on the `type:` line. Then the `refs:` line fails to match and the issue's refs silently vanish —
  it becomes "floating scaffold." Keep all three on the refs line.)
- **`deps:`** — optional fourth line; see §5.

### The `refs:` vocabulary — the resolvable anchors

`refs:` is how an issue attaches to the constraint graph. Each `[token]` resolves as:

| Token form | Resolves to | Example |
|---|---|---|
| bare digits | a **constraint** number in the plan | `[3]` → `constraint:one-command-bus` |
| `S` + digit | a **seam** | `[S1]` → `seam:setpoint-iface` |
| `m`/`a`/`g` + digits | a **gate** | `[m0]`, `[a3]`, `[g1]` |
| `Phase` + word | a **phase** | `[PhaseB]` → `phase:b` |
| `Q` + digits | a **hold** (an open question), via the adapter's `q_holds` map | `[Q1]` → `hold:torque-law` |

Any other token is skipped with a warning. **Every workorder must ref ≥1 resolvable anchor**
(invariant 1) — an issue with no resolvable ref is *floating scaffold*: real, but attached to
nothing, and flagged as such. This is the mechanical embodiment of "trace to a constraint": an
issue that refs nothing has not earned its place on the chain.

### The body

Free markdown. Two body conventions are machine-read:

- **`#NNNN` in prose** becomes a `mentions` edge (a parsed cross-link) to that issue.
- The header block re-renders as a compact strip in the viewer's reader pane.

Everything else — test lists, evidence, first-principles reasoning, the Tier-1 trace — lives in
the body. **Requirements never live here**; they live in the plan, and the body *refs* them.

---

## §5 Relations, dependencies, provenance

Edges come in two strata.

**Stratum 1 — `refs` and `mentions`** (parsed, deterministic): an issue's `refs:` anchors, and
the `#NNNN` cross-links in its body. These say *what an issue is about*.

**Stratum 2 — the dependency types** (the ordering structure): exactly four, and **never invented
by extraction** — either an author declares them, or a reviewer proposes them with evidence:

| Type | Meaning |
|---|---|
| `blocks` | this issue must resolve **before** the target can legitimately close/latch |
| `awaits-stamp` | this issue's closure waits on the human sign-off tracked in the target |
| `defers-to` | work named here is explicitly deferred to the target (issue or gate) |
| `informs` | this issue's outcome materially shapes the target, without blocking it |

These are what turn the scaffold from decoration into structure: critical-path, gate-readiness,
and "what unblocks if I close X" all run on the dependency edges. Author-declared deps live on the
`deps:` header line:

```
deps: <type> <target>[ <target>…]; <type> <target> …
```

Targets are `#NNNN` or a refs-vocabulary token (`a3`, `S4`, `PhaseB`). Clauses are
semicolon-separated; the first word of each clause is the type (one of the four — anything else
warns and is skipped), the rest are targets. **Declare a dependency at the moment you learn it,
in the issue where you learned it.** An author-declared edge is `provenance: parsed` and is
stronger than any later machine proposal.

**Provenance** has three levels, so the graph never launders a guess into a fact:

- `parsed` — deterministically extracted (a `refs`, a `mentions`, or a `deps:` clause). Authoritative.
- `proposed` — a model or reviewer drafted it, carrying a **verbatim `evidence` quote** from an
  issue body; renders tentative. Supplied out-of-band via a reviewed `deps.json` (§6), never
  minted by the extractor.
- `confirmed` — a human reviewed a proposal to fact.

### Invariants checked at extract time

1. **Every workorder refs ≥1 upstream anchor** — else *floating scaffold* (flagged).
2. **No entity is closed by an authority its type forbids** — a human-gated type "closed" by a
   bare sha is rendered **open** and warned (see §3).
3. **Every seam names its scheduled substitute or its freeze stamp** — a seam with neither
   contradicts the seam definition.
4. **Nothing bound is silently dropped** — unresolvable refs, dangling edges, duplicate/ bad ids,
   and body-mentions of non-existent issues all warn. Silent truncation reads as "covered
   everything" when it didn't.

---

## §6 GRAPH.md and the extract pipeline

`extract` is a **deterministic, stdlib-only, model-free, network-free** parser. Same client
commit + same adapter ⟹ byte-identical outputs. It reads the plan, the seam table, and the
tracker, and writes three artifacts. In an adopted project the extractor is **client
content**: `adopt.sh` copies it to `tools/gantry_extract.py`, the developer LLM runs it by
hand whenever the map is needed, and the pre-commit shim calls the same copy (SPEC §7).

```
CLIENT REPO (truth)                       extract (deterministic)         ARTIFACTS
plan.md (## 2. constraints)      ─┐
seam table (| S# | … |)          ─┼──►  scripts/gantry_extract.py  ──►    state.json   (graph state, HASHED)
issues/*.md  +  git HEAD         ─┘         │                             GRAPH.md     (the map — for humans/agents)
adapter.json (paths, slug maps)  ──────────┘                             bodies.json  (issue prose — SIDECAR, not hashed)
[deps.json]  (reviewed edges)    ──────────►  merged in
```

### `state.json` — the graph state, and the REV

`state.json` is the canonical entity/relation graph. Its **REV id** is
`sha256` of the document with the `hash` field removed, canonicalized (sorted keys, NFC). The REV
is stamped into `GRAPH.md`'s header and is the project's structural fingerprint: **a scene diff
bisects to a state diff bisects to a client commit.** In CI you regenerate and fail on unexpected
diff — visualization drift is a build break, same severity as any derived-data drift. The gate is
`extract --check`: builds the fresh map in memory, compares it to the committed `GRAPH.md`
(normalizing the header commit stamp, since hook-refreshed digests legitimately differ in `@
<sha>[+dirty]`), and exits 1 on any other drift.

`generated_from` records `{repo, commit, dirty, extractor_version}`. **`dirty` is scoped to the
input paths only** (tracker dir, plan, seam table) — unrelated noise in the client tree does not
count. A digest with no `+dirty` marker was generated from exactly the named commit.

### `GRAPH.md` — the one-gulp map

The digest an agent **reads at session start** instead of opening every issue. Its shape:

```
# GRAPH — <repo> @ <sha>[+dirty] · REV <hash12>
# generated by gantry extract — do NOT hand-edit; change the issues and re-run.

lineage: level 1 · fork of <base> @ <sha> · issues #1000–#1999      ← only when the adapter has a band
streams open (band · slug · parent issue · branch):                  ← only when streams.json has open streams
  #2000–#2099 0042-approach-x · #0042 · stream/0042-approach-x

gates latched: m0 … · open: m1 … · phases open: b c
seams provisional: S2 …
seams frozen: S1 …

open items (kind · refs → upstream anchors):
  #0002 workorder m1-press-cycle → 3,S1,m0
  #0004 hold      torque-law ⛭human → 4
  …

dependency edges (blocks = must resolve first):
  #0002 —defers-to→ #0004 [parsed]
  …

closed/resolved: #0001 #0003 …

sources — where the full content lives:
  plan.md      → constraints 1–4
  seams.md     → seams S1, S2
  proposals.md → proposed content (on the table)
  issues/0002-m1-press-cycle.md → gate m1
  issues/0008-gantry-adoption.md → #0008
  business content (external, curated in the adapter):
    ../sister-repo/legal/comm-log.md → one-line description
```

`⛭human` marks a human-gated item; `(floating)` marks an item with no resolvable ref. Everything
in the map is regenerated; the truth is upstream. **Never hand-edit it** — it will be overwritten.

The **sources** section is the navigation index: it maps every entity name in the map to the file
that holds its full content — the plan (constraint numbers collapsed into ranges), the seam table
(S-numbers), the optional proposals file, and one line per issue file (a milestone issue that
yields both a gate and a workorder shows the gate, not the redundant `#NNNN`; a plain workorder
shows its `#NNNN`). It renders only in `GRAPH.md`, never in `state.json` or the REV.

### `bodies.json` — why issue prose is a sidecar

The viewer needs issue markdown, but **prose is not graph state**: rewording a paragraph must not
move the REV, or every copy-edit would invalidate a structurally-identical graph. So the issue
text is written to a *separate* artifact, **after** the hash, never fed into it. Adding an issue,
closing a gate, or declaring a dep changes `state.json` and the REV; editing prose changes only
`bodies.json`. `state_hash` records which state a given `bodies.json` accompanies.

### The adapter

One JSON file per client tells extract where truth lives and how to slug it:

```json
{
  "client": "<repo label for the GRAPH header>",
  "tracker_dir": "issues",
  "issue_min": 1000,            "issue_max": 1999,
  "lineage": { "level": 1, "kind": "fork",
               "parent": { "repo": "<base label>", "commit": "<sha>" } },
  "plan": "plan.md",            "plan_source": "plan-v1",
  "kickoff": "seams.md",
  "proposals": "proposals.md",
  "seam_slugs": { "S1": "setpoint-iface", "S2": "press-driver" },
  "q_holds":    { "Q1": "torque-law" },
  "constraint_slug_overrides": {},
  "content": [ { "path": "../sister-repo/legal/comm-log.md", "note": "one-line description" } ],
  "parts": [ { "id": "part:...", "label": "...", "bindings": [ ... ] } ]
}
```

`issue_min` / `issue_max` (optional, default 0 = unchecked) are this repo's **issue band**
(§8 lineage law). Extract warns on any issue below the floor ("copied-in history is fine; new
issues must stay at or above it") and on any issue above the ceiling that no registered
stream band explains (`.gantry/streams.json`, §8). `lineage` (optional) records where the
repo sits — `level`, `kind` (`root` | `fork` | `stream`), and `parent` (`repo`, `commit`, and
for a stream the spawning `issue` and `branch`). Both are written by `scripts/gantry` and read
into `GRAPH.md`'s lineage block; **neither enters `state.json` or the REV** — where a repo sits
in a family is operational metadata, not graph structure. Setting the band costs nothing and
catches the classic fork mistake: filing a new issue at `#0007` because that's where the
base's numbering left off.

`content` (optional) is a list of external business files — each an entry `{"path": …,
"note": …}` (`note` optional) — pointing at curated files outside the client's own truth
stack. Extract renders them as a "business content" block in `GRAPH.md`'s sources section:
a navigation aid for a reader who must also consult files that are not part of the graph
(legal, commercial, sister-repo documents). It is **not** graph state: it never enters
`state.json` or the REV, and the human-curated order is preserved verbatim.

The plan is parsed inside its `## 2.` section: numbered items `N. **Bold Name.** body`, optionally
grouped under `### C-GROUP` headings; the bold lead name becomes the constraint's stable slug. The
seam table is any markdown table with rows `| S# | name | impls (now → later) | freeze event |`.

### The proposed annex — content on the table, not in the graph

`proposals` (optional) names a curated file of **proposed content** — drafts from the
Tier-1 interview and working sessions that a human is weighing. It parses four kinds of
block:

```
## decision: presets             ← a matrix row: ONE open decision
- **per-material.** ...          ← its candidate answers; promote exactly one
- **per-operator.** ...

## seams
- **S3 telemetry-writer.** local log → supabase telemetry; freeze at M2

## issues
- #1007 — hold: presets UX
  type: ambiguity        status: open
  refs: [3]   opened: seed

## routes
- route A (defaults): presets[per-material] × auth[passwordless-default]
  ← prose combinations over the matrix, proposed by the LLM, weighed by a
  human. Not parsed further — a route is a recommendation, never a container.
```

The **decision matrix** is the structure: one `## decision:` block per open
decision, its candidate answers beneath it (constraint-style `**name.**` claims
or draft issue blocks). Decisions are mutually exclusive *within* a block —
promote exactly one — and the extractor warns if a draft issue number appears
under two decisions (it can be promoted only once). **Routes** are prose lines
the LLM proposes ("the coherent combination I'd take is route A"); they render
last in the annex and cost nothing structurally, so the matrix stays small and
one-gulp — no combinatorial explosion of containers. Do not branch proposals
into git branches: checkout is exclusive, so an agent reading `GRAPH.md` at
session start would see one branch, not the matrix.

The grammar mirrors the core grammars deliberately: **promotion is a copy**, not a
rewrite — accept a proposal by copying it into `plan.md` / `seams.md` / `issues/` (the
tracker numbering floor applies), delete it to reject. Until then it renders only in
the digest's `## proposed` annex, and it is subject to three exclusions:

- **Never in `state.json`, never in the REV.** Proposals churn is the bodies.json case
  (prose, not graph state): weighing a draft must not move the structural fingerprint
  of the shipped graph. Accepting it moves the REV — because that *is* structural change.
- **Nothing silently dropped.** Unparsable proposals warn (invariant 4).
- **Not refs.** A proposal is not an upstream anchor; no issue may `refs:` it, and a
  body `#NNNN` mention of a proposed issue warns as unresolved (it is not real yet).

`proposals.md` is a truth input like the rest — editing it refreshes `GRAPH.md` in the
same commit (the hook's input scope includes it) and counts toward `dirty`.

---

## §7 The hooks — client law in, wiring out

The method uses two git hooks whose ownership is **deliberately opposite** — and
deliberately framed so that the *adopted project* is self-sufficient. After
`adopt.sh`, everything the client needs to build its own map and enforce its own
law is **committed inside the client**; only the `.git/hooks` shims are unversioned
(git never versions hooks). A clean clone of the client builds, lints, and reasons
about itself with zero knowledge that a gantry repo exists.

```
                    GRAPH REFRESH                         COMMIT LINT
what it does        re-extract + stage GRAPH.md           reject a commit that breaks tracker law
                    (the developer LLM's session map)
whose law           the CLIENT's own development flow     the CLIENT's own law
lives where         tools/gantry_extract.py — INSIDE,     tools/lint_commit.py — INSIDE, committed
                    committed (.git/hooks shim unversioned)
survives clean clone?   yes — the builder is committed    yes — the lint is client content
may block a commit?     NEVER (any failure → exit 0)      YES (that is its whole job)
installer           scripts/adopt.sh → install-graph-hook.sh   scripts/adopt.sh → install-commit-lint.sh
```

**Graph refresh** (shim wired by `install-graph-hook.sh`): the pre-commit shim is
self-contained — it calls the client's **own** `tools/gantry_extract.py` and
`tools/gen_index.py`, derives the adapter/out paths from the **worktree root** at
runtime (so one hook set serves every stream, §8), and never references the gantry
repo. On each commit, *if the staged changes touch the extract inputs* (tracker
dir, plan, kickoff, proposals, adapter, extractor, deps, `streams.json`), it re-runs
extract and `git add GRAPH.md` — and regenerates and stages `issues/INDEX.md` — so
the refreshed digest and ledger ride in the **same commit** that changed the issues. It is a hard rule that
it **never blocks**: missing python3, missing extractor, or a failed extract prints
a note and `exit 0`. *Stale-but-committed beats fresh-but-mandatory.* Because HEAD
is by definition behind the tree at pre-commit time, hook-generated digests read
`@ <sha>+dirty` — `<sha>` is the parent, and the `+dirty` is the very commit
carrying the digest. The developer LLM may also run the builder by hand any time —
that is the point of it being client content: the map is a tool in the project,
not a service outside it.

**Commit lint** (`lint_commit.py`, wired by `install-commit-lint.sh`): every commit
references ≥1 issue (`#NNNN`); a `closes`/`fixes`/`resolves #N` never targets a
human-gated type; no core-code path (declared via `--core-prefix`) is touched
without an issue ref. The lint is **copied into the client's `tools/` and committed
there** — commit rules are the client's own law and must survive a clean clone. If
the client already owns a lint, the installer keeps it and only wires the shim.

Read the maxim off the table: **the builder and the lint are the client's own tools
and live in its repo, committed; the `.git/hooks` shims are unversioned wiring on
each machine.**

---

## §8 Adoption and lineage

### The entry point — `scripts/gantry`

Every bootstrap situation is one subcommand; nobody hand-assembles the operational layer.
`docs/00-llm-playbook.md` is the "your situation → the exact command" table; this section is
the law those commands implement.

| Situation | Command | Contract |
|---|---|---|
| empty/absent directory | `gantry new <dir>` | mkdir, `git init`, then `adopt` |
| existing repo — empty or with content | `gantry adopt [<repo>]` | scaffold **only what is missing** (`plan.md`, `seams.md`, `issues/`, `.gantry/adapter.json`, a gantry section in `CLAUDE.md`, `.gitignore` lines), copy tools + wire both hooks (`adopt.sh`), seed `#<floor> — M0`, commit `gantry adopted (#<floor>)`. Idempotent; never overwrites client content; re-run is a no-op |
| new separate repo from a gantry-adopted base | `gantry fork <base> <new>` | see *Forking* below; level = base + 1 |
| worktree stream of the same repo | `gantry stream new --issue N --slug S [--brief F]` · `list` · `report` · `merge` · `drop` | see *Streams* below; level = repo + 1, own prefix namespace |
| a new issue, correctly formed | `gantry issue new --title T --refs …` · `issue close <id> --by …` | writes the exact header + the workorder body (constraints · depends on · approaches · exit); closes by the type's authority |
| CI / honesty gate | `gantry check [<repo>]` | `extract --check` + `gen_index --check` + lineage sanity; exit 1 on drift |

**The adoption commit obeys the commit law.** `adopt` seeds one milestone issue —
`#<floor> — M0: <name> — plan, seams, first gate`, `refs: [m0]` (its own gate, so it is not
floating) — and the adoption commit references it. No lint exemption. The seed's exit test is
the bootstrap order below; landing the plan closes it and latches `m0`. The extractor
tolerates an unborn HEAD (stamp `0000000+dirty`, by the hook convention "the stamp is the
parent") so the pre-commit shim mints `GRAPH.md` *into* the birth commit — one commit, map
included.

### Delta for an existing constraint-first project

If a project already plans constraint-first with a typed tracker (the reference project did), the
entire adoption is three points:

1. **`GRAPH.md` now exists** — read it at session start for the current map; open issue files only
   for detail.
2. **You may declare `deps:`** — the optional fourth header line, four types, precisely. Prefer
   declaring a dep at issue-writing time over leaving it for a model to propose.
3. **Nothing else changes** — same issue format, same refs vocabulary, same closure authorities,
   same one-truth-upstream law. `gantry adopt` keeps every existing file and only adds the seed.

### Bootstrap order for a new project (what the seed issue asks of you)

1. **Write the plan, constraints first** — named, numbered, grouped under `### C-GROUP`; then the
   build order and phase boundaries (binding, not suggestions). Each constraint traces to a Tier-1
   beat.
2. **Write the seam table** — one row per *scheduled* substitution the phase map implies. No
   speculative interfaces; an interface exists only where an implementation is planned to swap.
3. **Define gates** — milestones with exit tests, per phase.
4. **Seed the tracker** — one milestone issue per near-phase gate, one placeholder per far phase,
   one hold per already-known open question. Nothing else: issues are event-driven from here
   (doctrine: no speculative decomposition of unbuilt phases).
5. **Onboard extract** — the adapter is written; the hooks are wired; run `gantry check` in CI so
   `GRAPH.md` and `INDEX.md` stay fresh.

### The lineage law — forks take a level, streams take a prefix

A gantry repo may have **sub-projects**: a *fork* (a separate repo born from it) or a *stream*
(a worktree on a branch of it). Both sit **one level below** their parent. Numbering is by
identity where collisions can happen and by level where they cannot:

```
level 0  root                          #0001–#0999
level L  FORK  (1 ≤ L ≤ 9)             #L000–#L999   — a separate repo: the whole next thousand
         STREAM of any repo            #<prefix>-0001, #<prefix>-0002 …   — its own namespace
         prefix = <parent's own prefix><letter><parent issue seq>
                  stream a of #0042 → a42;  its sub-stream b from #a42-0003 → a42b3
level 9  the deepest fork              #9000–#9999
```

- **Numbers outside a repo's band or namespace are never its to file.** Below the floor is
  inherited history (a fork keeps the base's issues, closed); above the ceiling belongs to a fork;
  a bare number filed *inside* a stream is a collision waiting for the merge. Extract warns on all
  three; `gantry check` fails on a band that contradicts the level.
- **Streams are identity, not position.** Two parallel streams of `#0042` are `a42` and `b42`;
  letters are allocated per parent issue and never re-used (`.gantry/streams.json`, committed by
  the parent, is the ledger). Any subset merges back with no renumbering.
- **The extractor enforces it.** A prefixed issue whose prefix is neither the repo's own
  `issue_prefix` nor a registered stream warns; a stream (adapter has `issue_prefix`) filing an
  unprefixed number above the parent's `issue_high` at spawn time warns.
- **Lineage is visible.** `GRAPH.md` opens with `lineage: level L · kind of parent @ sha ·
  issues …` and the open streams (`prefix · slug · parent issue · branch`). From the adapter and
  `streams.json` only — never `state.json`, never the REV: where a repo sits is operational, not
  structural.
- **A stream's issues ref the shared plan.** Same `plan.md`, same constraints; the stream's
  `refs:` resolve exactly as the parent's do; its entity ids carry the prefix
  (`workorder:a42-<slug>`) so they never collide with the parent's.

### Forking an app out of a base (the copy, not the link)

`gantry fork <base> <new-dir>` (generic; `scripts/fork-app.sh` is the older SvelteKit-manifest
variant, scheduled to be absorbed — seam S1 in this repo) copies the base's *starting truth +
machinery* into a completely separate repo — no links, no submodules, no shared state:

- **What is copied**: every file tracked at the base's HEAD (`git archive`), minus derived and
  secret paths (`.gantry/out/`, `.gantry/streams*`, `GRAPH.md`, `issues/INDEX.md`, `.env`,
  `node_modules`, `METALAND/`), minus `--exclude` paths and the base's optional
  `.gantry/fork-exclude` list. Uncommitted changes in the base are not copied (and the tool says so).
- **The inherited issues are a closed reference set.** Their work belonged to the base; the app
  is not doing it. Every inherited open issue is marked `closed` — commit-closable types get the
  base's fork-point sha; human-gated types get `reference: inherited from base @ <sha>` (closure
  authority respected in both directions). `--keep-open` opts out.
- **The app numbers its own issues from the next thousand** — level = base + 1, `issue_min` /
  `issue_max` / `lineage` land in the adapter; `--level` or `--issue-min` override.
- **The birth commit is exempt from commit law** and says so in its message: it cannot reference
  an issue that does not exist yet (`repo born from <base> @ <sha>`). From the first app issue
  (`#L000`) on, the ordinary law applies. `adopt.sh` then wires the hooks and mints `GRAPH.md` +
  `INDEX.md`, which the operator commits together with that first issue.

### Streams — worktrees for an orchestrating agent

`gantry stream new --repo <repo> --issue N --slug S [--brief FILE|-]` is how an orchestrator runs
**test workorders** and **parallel development streams** without leaving the method:

1. a stream is always **spawned by an issue** in the parent (`#N` must exist — the workorder
   whose constraints the stream is to fulfil);
2. it is a **git worktree beside the repo** — `../.gantry.<repoDirName>.streams.<prefix>` — on
   branch `stream/N-S`, sharing the parent's `.git/hooks` (the shims resolve every path from the
   worktree root). Beside, not inside: an agent's glob over the parent tree must not see N copies
   of the repo;
3. it gets its **prefix** (`<parent prefix><letter><N's seq>`), written into *its own* adapter on
   *its* branch (`issue_prefix`, `lineage: {kind: stream, parent: {issue, branch, commit,
   issue_high}}`) with a `CLAUDE.md` that names the stream, its namespace, its workorder, and the
   rule *everything you do must show in `GRAPH.md`*;
4. it is **seeded with `#<prefix>-0001`** — a `workorder` whose `refs:` are the spawning issue's
   anchors and whose body is the orchestrator's **brief**: the constraints to make true, or the
   workorders derived from them (`--brief`; default text points at the parent issue). The stream's
   agent starts from constraints, never from nothing;
5. the parent's **`.gantry/streams.json`** records `{slug, prefix, issue, branch, worktree, from,
   status}` — the orchestrator commits it (`refs #N`);
6. **the orchestrator's check is `GRAPH.md`**: `gantry stream report [prefix]` reads each open
   stream's map (from the worktree, or `git show stream/…:GRAPH.md` once removed) — lineage,
   gates, open items, closed items, the prefixed issues and their status, commits since spawn.
   All work in a stream must surface there: an issue per piece of work, closed by its type's
   authority. If the orchestrator gets no direct output from the sub-model, this is what it reads;
7. `gantry stream merge <prefix>` merges `--no-ff` back into the parent branch, keeps the
   **parent's** adapter, ledger and briefing, regenerates `GRAPH.md` / `INDEX.md`, marks the stream
   `merged`, removes the worktree (branch kept unless `--delete-branch`); real-content conflicts
   stop the tool (`--finish` completes the bookkeeping after you resolve them);
8. `gantry stream drop <prefix>` removes worktree and branch and marks it `dropped`; the prefix
   stays reserved.

The stream's closing note belongs in the parent issue's body; the parent issue closes by its own
type's authority (the merge sha, or a sentence).

---

## §9 The scripts (reference)

Everything named above ships in `scripts/`, each runnable and self-documented:

| Script | Role | Typical invocation |
|---|---|---|
| `gantry` | **the entry point** (§8): `new` · `adopt` · `fork` · `stream new/list/report/merge/drop` · `issue new/close` · `check` — the only thing an LLM needs to run | `python3 scripts/gantry <cmd> …` |
| `templates/` | what `new`/`adopt`/`issue new` scaffold: `plan.md`, `seams.md`, `adapter.json`, `issue-seed.md`, `issue-workorder.md`, `CLAUDE.md`, `gitignore.snippet` | — |
| `adopt.sh` | tools + both hooks + GRAPH.md mint into a client (§7); called by `gantry adopt`, usable alone | `sh adopt.sh <repo> [--core-prefix P]` |
| `fork-app.sh` | fork a new app repo out of a gantry-adopted base: manifest copy, identity edits, inherited issues closed as a reference set, fresh init + birth commit, adopt, verify (§8) | `sh fork-app.sh <base> <app> --issue-min N [--name N] [--fresh-tools] [--local-stack]` |
| `gantry_extract.py` | truth → `state.json` + `GRAPH.md` + `bodies.json` (§6); copied into adopting clients as `tools/gantry_extract.py` | `python3 gantry_extract.py --client A.json --root R --out S.json [--deps D.json]` |
| `gen_index.py` | tracker → `issues/INDEX.md` (derived ledger) | `python3 gen_index.py [--root R]` · `--check` in CI |
| `lint_commit.py` | enforce commit/tracker law (§7) | `lint_commit.py --message M --files … [--core-prefix P]` |
| `install-graph-hook.sh` | write the self-contained pre-commit shim (calls the client's own extractor + ledger; worktree-safe; never blocks) | `install-graph-hook.sh <repo> [--deps D]` |
| `../tests/run.sh` | end-to-end exercise of every `gantry` subcommand in scratch repos (§8) | `sh tests/run.sh` |
| `install-commit-lint.sh` | copy `lint_commit.py` + `gen_index.py` into a client + wire the shim (client-owned) | `install-commit-lint.sh <repo> [--core-prefix src/]` |

Determinism holds across all of them: no wall-clock, no randomness, no network in extract, index,
or lint. The graph obeys the same religion its first client imposes on its own code — which is the
whole point: **the observer is honest because it is derived, and derived the same way, every time.**

---

*See `examples/` for a tiny project exercised end to end: `plan.md`, `seams.md`, `issues/*.md`,
`adapter.json`, and the exact `GRAPH.md` + `state.json` this pipeline emits from them.*
