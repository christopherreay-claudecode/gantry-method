# MindMapTreeFormat 0.1

*A plain-text notation for saying n-dimensional things in a one-dimensional tree. The tree
gives containment; typed references give every other axis. It is meant to be written by
people and models, read in a terminal, grepped, and diffed.*

Status: 0.1 — the notation as used in the cubeOnSKOS / cubeOnSKOS-ui / gantry sessions of
2026-08-30 → 2026-09-05. Nothing here is enforced by a tool yet; see §9.

---

## 1. Purpose and non-goals

A MindMapTree answers "what is the state of X, along which axes, and where do the axes
cross" without linearising into paragraphs. It replaces prose for substantive answers,
status reports, plans, and audits.

It is NOT:
- a diagram language (no layout, no coordinates);
- a serialisation format (no schema, no escaping rules beyond §7);
- a replacement for the artefacts it points at (issues, specs, contracts). A tree
  *addresses* truth; it does not *hold* it.

## 2. The one rule

**The tree carries one axis: containment. Every other dimension is carried by a typed
reference.** If a fact belongs to two parents, it lives under one and is referenced from
the other. Never duplicate a node to make a second axis visible.

## 3. Lexical elements

| glyph | name | meaning |
|---|---|---|
| `@name` | address | declares this node's stable identity (kebab-case, unique in the tree) |
| `->@name` | reference | a typed edge OUT of this node to `@name`; optional `[type]` suffix |
| `=` | measured | asserted against the running system; carries a date, count, hash or path |
| `~` | derived | read off a body of text or code, not exercised |
| `?` | open | a question; MUST name its owner and what changes on either answer |
| `!` | action | a to-do; MUST name the actor and the artefact it produces |
| `x` | blocked | cannot proceed; MUST reference what unblocks it |
| `DIM:` | axis list | declares the dimensions in play (top of tree, optional but recommended) |

Glyphs are single ASCII characters placed at the start of a node's text, after the tree
drawing characters and an optional `@address`. The set is deliberately small: seven
markers plus `DIM:`. A tree that needs more glyphs needs more nodes instead.

## 4. Structure

```
@root                                   = one-line summary  (optional evidence)
├─ @child-a                             glyph text
│  ├─ leaf text
│  └─ ? question — owner · yes→consequence · no→consequence
├─ @child-b                             ->@child-a [depends]
└─ !  actor: artefact                   ->@issue-0011
```

- Tree-drawing characters: `├─`, `└─`, `│`. Two spaces of indent per level after the bar.
- The **first line** is the root; it may carry `@address`, a glyph and a summary. A root
  that reports state SHOULD be `=` with a date.
- A node is ONE line. If a fact needs a sentence, it is a leaf and the sentence stays on
  that line. Wrapping is the renderer's problem, not the author's.
- Order within a parent is meaningful only when the parent says so (`(ordered)` in the
  parent's text, or the children are numbered).
- Aligned columns (`node text        = value`) are cosmetic. Whitespace is not semantic
  beyond the indent.

## 5. Addresses and references

- `@name` is declared once. Kebab-case; may contain dots for a namespace (`@you.H`,
  `@core.tests`). Numbers are fine (`@issue-0011`, `@c17`).
- `->@name` may appear anywhere in a node's text; several per node are legal.
- `->@name` with **no matching declaration is legal**. It marks a node worth writing, the
  same way a wiki red-link does. A checker MAY list them; it MUST NOT reject them.
- `[type]` on a reference is free text but SHOULD come from a small vocabulary the tree's
  `DIM:` line names. The base vocabulary, shipped as the default `mmt_edges` in every gantry
  adapter: `depends`, `serves`, `proves`, `blocks`, `contradicts`, `same-as`, `owner`,
  `evidence`. A repository extends it in its own `.gantry/adapter.json`; the renderer notes a
  type outside the subject repository's list (a Level-2 concern, never a Level-1 failure).
- A reference is directional. If both directions matter, write both edges; do not rely on
  the reader inferring the inverse.

### 5b. External references (tokens)

A tree addresses truth that lives elsewhere. A bare token in a node's text IS a reference to the
document that defines it, and a renderer links it. **The mechanism is fixed; the vocabulary is
the repository's.** Six kinds exist in every gantry repository by construction and are built in:

| token | resolves to |
|---|---|
| `#NNNN`, `#a1-0003` | `issues/NNNN-*.md` (the tracker) |
| `c17`, `[17]` | constraint 17 in `plan.md` |
| `S1` | a seam row in `seams.md` |
| `m2`, `g1`, `Q1` | a gate / hold, via `.gantry/out/state.json` and `adapter.json` |
| `path/to/file.ext`, `path:42` | the file, at the line |
| `c0b273f` (7–40 hex) | a commit, rendered from `git show` |

Everything else a repository wants linkable is **its own token kind**, declared in its
`.gantry/adapter.json` `mmt_tokens` (gantry SPEC §6 "The adapter"): `kind` · `glob` · `line`
regex · `token`/`label` templates over the regex groups · `match` (the shape). The renderer reads
each root's own table, so a tree spanning repositories resolves every token by the grammar of the
repository it points into. Kinds declared by the repositories this format grew up in:

| token | declared by | resolves to |
|---|---|---|
| `R7` | cubeOnSKOS | a rule line in `CLAUDE.md` (`R` + number, two-space gap) |
| `U4`, `W2`, `H3` | cubeOnSKOS | a section / hypothesis row of a plan under `docs/plans/` |
| `§6.1`, `§6a`, `§17/http` | cubeOnSKOS, cubeOnSKOS-ui | a heading in `docs/contract/database-surface.md` (`/http`: `http-routes.md`) |

Glyphs are NOT extensible (§3): a formality the model did not already produce is a token tax.
Vocabulary is data; the notation is not.

Trees often span repositories. A **root prefix** pins a token to one: `core:#1013`,
`ui:#0011`, `gantry:scripts/mmt.py`, `ui:S1`. Unprefixed tokens resolve in the first
root that defines them, in the order the roots were given to the renderer — so name the
subject repository first. A token that resolves nowhere stays plain text and the renderer
lists it under "unresolved".

There is no bracketed link syntax on purpose: the tokens are already the names the
repositories use for these things, and a tree that reads well in a terminal must not carry
URLs.

## 6. Semantics of the glyphs

- `=` **measured.** The author (or their tooling) exercised the system and observed this.
  Carry the evidence inline: a date, a count, a commit hash, a file path, a port. A `=`
  without evidence is a `~` wearing the wrong glyph.
- `~` **derived.** Read from text, code, a spec, or reasoning. Honest default when nothing
  was run.
- `?` **open.** Shape: `? <question> — <owner> · <branch>→<what changes> · <branch>→<what changes>`.
  A question with no consequence named is not yet a question; it is a musing, and does not
  belong in the tree.
- `!` **action.** Shape: `! <actor>: <artefact>` optionally `->@` the thing it closes.
- `x` **blocked.** Shape: `x <what> — needs ->@unblocker`.
- Glyphs compose only by nesting, never by stacking on one line: `? ! foo` is invalid; a
  question whose answer produces an action is a `?` with a `!` child.

## 7. Text rules

- ASCII glyphs and tree characters; UTF-8 text otherwise. `·` (middle dot) is the
  conventional inline separator for parallel facts on one line; `∥` for "in parallel with";
  `→` inside a `?` branch only.
- No em-dash as a glyph. `—` is plain punctuation inside text.
- No prose paragraphs. A tree may be preceded by a one-line tag (`[immediate]`,
  `[guidance]`, `[question]`, `[MetaLand]`) and nothing else.
- On disk a tree is a `.mmt` file (the tree and nothing else), or the first ```` ```mmt ````
  fenced block in a `.md`. A DIM: line, if present, is the second line.
- In a gantry repository trees live in `trees/YYYY-MM-DD-<slug>.mmt` (committed, like issues)
  and render to `.site/mmt/` (on disk, gitignored): `tools/g tree new <slug>`,
  `tools/g tree render --all`. Roots come from `.gantry/adapter.json` `mmt_roots`.
- Code identifiers appear bare (`server/socket.mjs`, `cube:move`); no backticks inside the
  tree, since the tree itself sits in a fenced block.

## 8. Dimensions (`DIM:`)

Optional first line under the root. Names the axes the references carry, so a reader knows
which `[type]`s to expect and a checker knows which to warn on.

```
@release-status                         = 2026-09-05
DIM: time(commit) · ownership(actor) · evidence(=/~) · dependency(->[depends])
```

Time SHOULD be factored out into evidence (`= c0b273f`, `= 2026-09-05`) rather than inferred
into node names ("old-x", "new-x").

## 9. Conformance levels

- **Level 0 — readable.** Tree characters, one node per line, glyphs at node start. Any
  human can read it. This document's examples are Level 0.
- **Level 1 — addressable.** Every node that is referenced has an `@address`; every `?`
  names an owner; every `!` names an actor and artefact; every `x` references its
  unblocker. A grep-based checker can verify this.
- **Level 2 — graphable.** `DIM:` present; every `->@` carries a `[type]` from the declared
  vocabulary; no dangling references except those explicitly marked `->@name [todo]`.
  From here a tree exports to a typed edge list (node, glyph, text; edge, type) and can
  join gantry's own graph.

**Tooling (gantry `scripts/mmt.py`, symlinked `tools/mmt.py`):** renders a tree to a local
linked page (`@` anchors, `->@` links, every §5b token linked into a line-numbered copy of
its document, across named roots, each by its own `mmt_tokens`), lints Level 1 (`--strict`
exits 1) and notes `[type]`s outside `mmt_edges`. It does not yet emit the Level 2 edge list;
that is gantry #0021. See `tools/README.md`.

## 10. Worked example

```
@live-moves                                 = core #1013 · merged 2dfe0a0 · socket :6464 · flag on
DIM: evidence(=/~) · dependency(->[depends]) · ownership(->[owner])
├─ measured    A→B relay 4 ms of a 300 ms budget · 10/10 frames · no echo
├─ proved      six outcomes with real sockets  ->@spec-s8-live-moves [proves]
├─ ~ standing  tools/g check reports GRAPH.md stale at every clean HEAD — cosmetic
├─ ui-half     ->@ui-issue-0011 [depends]
│  └─ ! ui-stream a7: emit on slider input ≤10/s, render others' moves behind the toggle
└─ ? per-cube live_moves switch — owner ->@you [owner] · yes→amendment + column + edit_cube arg · no→stays server-global
```

## 11. Relationship to gantry

gantry's `state.json` is already a typed edge list (issues, refs, deps, seams). A Level 2
MindMapTree is the same shape written for a human first. The planned bridge is:
tree → edge list → gantry graph, so a status tree can be diffed against `GRAPH.md` and a
plan tree can be minted into issues. See `docs/plans/gantry-graph-subtraction.md` in
cubeOnSKOS for the enforcement-graph plan this format feeds.

## 12. Changelog

- 0.1 (2026-09-05): first written specification of the notation in use since 2026-08-30.
- 0.1 + tooling (2026-09-05): §5b external references and root prefixes; `.mmt` files and
  ```` ```mmt ```` fences; `scripts/mmt.py` renders and lints (gantry #0016).
- 0.1 + vocabulary (2026-09-05): §5b split into the six built-in kinds and repository-declared
  kinds (`mmt_tokens`); §5 edge vocabulary is `mmt_edges`; a tree is written once through
  `tools/g tree new`, which renders it (gantry #0019 #0020).
