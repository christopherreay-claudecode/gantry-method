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
sequentially numbered. The **header block is the first lines of the file** (the parser reads only
the first 6 lines for header fields) and is exact:

```
# #0002 — M1: the press completes one cycle
type: milestone        status: open
refs: [3] [S1] [m0] [Q1]   opened: M1   closed-by: <sha>
deps: defers-to #0004; informs #0003
```

Line by line, each rule is precisely what the parser matches:

- **Title** — `# #NNNN — Title`. A literal `#`, space, `#NNNN` (four digits), space, an
  **em-dash `—`**, space, then the title. (A hyphen will not match; it must be the em-dash.)
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
| `m`/`a` + digits | a **gate** | `[m0]`, `[a3]` |
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
```

`⛭human` marks a human-gated item; `(floating)` marks an item with no resolvable ref. Everything
in the map is regenerated; the truth is upstream. **Never hand-edit it** — it will be overwritten.

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
  "issue_min": 1000,
  "plan": "plan.md",            "plan_source": "plan-v1",
  "kickoff": "seams.md",
  "proposals": "proposals.md",
  "seam_slugs": { "S1": "setpoint-iface", "S2": "press-driver" },
  "q_holds":    { "Q1": "torque-law" },
  "constraint_slug_overrides": {},
  "parts": [ { "id": "part:...", "label": "...", "bindings": [ ... ] } ]
}
```

`issue_min` is optional and defaults to 0: the floor for this repo's issue numbers.
Extract warns on any issue below it ("copied-in history is fine; new issues must
stay at or above it") — the guardrail for a forked repo that inherits a closed
reference set (`#0001`–…) but numbers its own work from `#1000`. Setting it costs
nothing and catches the classic fork mistake: filing a new issue at `#0007` because
that's where the base's numbering left off.

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
self-contained — it calls the client's **own** `tools/gantry_extract.py`, derives
the adapter/out paths from the repo at runtime, and never references the gantry
repo. On each commit, *if the staged changes touch the extract inputs* (tracker
dir, plan, kickoff), it re-runs extract and `git add GRAPH.md`, so the refreshed
digest rides in the **same commit** that changed the issues. It is a hard rule that
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

## §8 Adoption

### Delta for an existing constraint-first project

If a project already plans constraint-first with a typed tracker (the reference project did), the
entire adoption is three points:

1. **`GRAPH.md` now exists** — read it at session start for the current map; open issue files only
   for detail.
2. **You may declare `deps:`** — the optional fourth header line, four types, precisely. Prefer
   declaring a dep at issue-writing time over leaving it for a model to propose.
3. **Nothing else changes** — same issue format, same refs vocabulary, same closure authorities,
   same one-truth-upstream law.

### Bootstrap order for a new project

1. **Write the plan, constraints first** — named, numbered, grouped under `### C-GROUP`; then the
   build order and phase boundaries (binding, not suggestions). Each constraint traces to a Tier-1
   beat.
2. **Write the seam table** — one row per *scheduled* substitution the phase map implies. No
   speculative interfaces; an interface exists only where an implementation is planned to swap.
3. **Define gates** — milestones with exit tests, per phase.
4. **Seed the tracker** — one milestone issue per near-phase gate, one placeholder per far phase,
   one hold per already-known open question. Nothing else: issues are event-driven from here
   (doctrine: no speculative decomposition of unbuilt phases).
5. **Onboard extract** — write the adapter json; run extract in CI so `GRAPH.md` stays fresh;
   optionally install the two hooks on your machine.

### Forking an app out of a base (the copy, not the link)

When the base is a gantry-adopted tooling repo and the app is a product built on it,
`scripts/fork-app.sh` copies the base's *starting truth + machinery* into a completely
separate repo — no links, no submodules, no shared state; the app lives alone. The script's
manifest is the contract: plan, seams, tracker, specs, supabase migrations (0000–0008),
src/tests/tools/scripts, the drift workflow, and the adapter — nothing else (`.git`,
`.env`, `.gantry/out/`, `METALAND/`, `node_modules`, build output are all excluded, each
for a stated reason; anything unlisted is reported, not copied).

Three decisions make the fork coherent under this spec:

- **The inherited issues are a closed reference set.** Their work belonged to the base;
  the app is not doing it. `fork-app.sh` marks every inherited open issue `closed`
  (commit-closable types get the base's fork-point sha; human-gated types get a
  "reference: inherited from base @ <sha>" sentence — closure authority is respected in
  both directions).
- **The app numbers its own issues from `--issue-min`** (a required fork flag; lands as
  `issue_min` in the adapter). The inherited `#0001`–`#0013` sit below the floor as history;
  extract warns on any *new* issue filed under it.
- **The birth commit is exempt from commit law.** It cannot reference an issue that does
  not exist yet, so it is made with the lint bypassed and carries the message
  `app repo born from base @ <sha>`. From the first app issue (`#1000`) on, the ordinary
  law applies.

`fork-app.sh` then runs adopt.sh (hooks), npm install, the app's own check/build/test
scripts (and optionally the local supabase stack with `--local-stack`), and mints
`GRAPH.md` + `issues/INDEX.md` — which the operator commits together with the first app
issue. Remaining secrets (`.env`) are copied by hand, outside git, never via the fork.

---

## §9 The scripts (reference)

Everything named above ships in `scripts/`, each runnable and self-documented:

| Script | Role | Typical invocation |
|---|---|---|
| `adopt.sh` | one-command adoption: copies the three tools into a client, writes the ritual, wires both hooks, mints GRAPH.md (§7) | `sh adopt.sh <repo> [--core-prefix P]` |
| `fork-app.sh` | fork a new app repo out of a gantry-adopted base: manifest copy, identity edits, inherited issues closed as a reference set, fresh init + birth commit, adopt, verify (§8) | `sh fork-app.sh <base> <app> --issue-min N [--name N] [--fresh-tools] [--local-stack]` |
| `gantry_extract.py` | truth → `state.json` + `GRAPH.md` + `bodies.json` (§6); copied into adopting clients as `tools/gantry_extract.py` | `python3 gantry_extract.py --client A.json --root R --out S.json [--deps D.json]` |
| `gen_index.py` | tracker → `issues/INDEX.md` (derived ledger) | `python3 gen_index.py [--root R]` · `--check` in CI |
| `lint_commit.py` | enforce commit/tracker law (§7) | `lint_commit.py --message M --files … [--core-prefix P]` |
| `install-graph-hook.sh` | write the self-contained pre-commit shim (calls the client's own extractor; never blocks) | `install-graph-hook.sh <repo> [--deps D]` |
| `install-commit-lint.sh` | copy `lint_commit.py` + `gen_index.py` into a client + wire the shim (client-owned) | `install-commit-lint.sh <repo> [--core-prefix src/]` |

Determinism holds across all of them: no wall-clock, no randomness, no network in extract, index,
or lint. The graph obeys the same religion its first client imposes on its own code — which is the
whole point: **the observer is honest because it is derived, and derived the same way, every time.**

---

*See `examples/` for a tiny project exercised end to end: `plan.md`, `seams.md`, `issues/*.md`,
`adapter.json`, and the exact `GRAPH.md` + `state.json` this pipeline emits from them.*
