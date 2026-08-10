# 02 — Projecting the grammar into 3D (metaphor-first)

Why 3D at all: the grammar's hard pairs are **containment** (parts inside parts
inside the product) and the **reference graph** (workorders → constraints/seams/gates,
many-to-many). 2D dies on both at once — nesting plus cross-references becomes
line-crossing spaghetti, and every "look inside" is a hand-authored cutaway. In 3D,
containment is literal (the camera goes inside; a clipping plane *is* the look-inside
operation), and reference edges route through space without crossing ambiguity.
The bar is **accuracy, not beauty**: primitives, flat shading, and labels are enough,
and are more honest than art the state cannot warrant.

## §A The metaphor is curated, never derived

The scene renders two different things, and they must never be confused:

- **What exists** — the graph: gates latched, holds open, seams frozen. Derived,
  deterministic, earned.
- **What it means** — the project's aim. That lives upstream in the **Tier-1
  narrative** (lived-experience constraints), not in the graph.

The metaphor is the lens that maps the second onto the first. The designer reads the
Tier-1 narrative — "this is a machine learning to move under delay" — and chooses the
whole: a gantry for a mech, a clockwork orrery, a nervous system. Then the scene
renders the *derived* state through that lens. The bodyplan is the **ONE curated
layer** in the entire pipeline: the only place judgment enters, human-stamped, and
checked by law 3 below. The metaphor may shape *how* something is shown; it may never
decide *whether* it exists. A capsule for a sim that believes it's a capsule; a
constellation of lanterns for a project that thinks of itself as stars.

```
truth (Tier-1 narrative) → metaphor (curated, human-stamped) → scene (state × metaphor)
```

No circle: the metaphor is the human's reading of the aim; the scene is the state's
rendering of that reading.

### The metaphor document — the deliverable

Every visualization starts as a short curated document, drafted by an LLM, reviewed
and stamped by a human (`provenance: proposed → confirmed`, exactly like dependency
edges):

1. **The aim in one sentence** — drawn from the Tier-1 narrative, not from the tracker.
2. **The whole metaphor** — one object-system the project *is* when seen at bay scale:
   a gantry around a giant mech; a factory floor; a clockwork orrery; an abstract
   constellation. If the metaphor needs no explanation beyond the sentence, it is
   right; if it requires a legend, it is too clever.
3. **The seat map** — for each process object, the question *"what is a <gate> in this
   metaphor?"* — see §B.
4. **The law-3 audit** — a note that no seat invents geometry: every seat's shape is
   warranted by build state alone (§C).

## §B The seat map

Seating is a question, not a table: for each process object, ask what it *is* in this
metaphor, and answer from the aim sentence. The gantry yard is the worked example that
founded the method — its answer is below — but it is an *instance*, not the law. An
abstract metaphor (say, a night sky: gates as constellations slowly brightening,
holds as stars that refuse to be fixed until observed) is just as legitimate, provided
the seat map is explicit and law 3 holds.

The founding worked example — a **construction yard** for a machine being built:

| Process object | Yard object (this metaphor's answer) |
|---|---|
| gate (milestone) | gantry deck, stacked in build order; wireframe while open, plated + latched green when closed |
| phase | a bay; future phases are adjacent bays holding phantom scaffold only |
| workorder | a work-order tag hanging from the scaffold, wired to what it refs — the refs graph becomes literal cabling you can follow by eye |
| hold (ambiguity) | an amber HOLD tag at the exact part it defers ("do not machine past this point") |
| freeze-request | a stamp plate mounted at the seam's jig, awaiting the inspector |
| stamp | the inspector's mark on the plate; the jig clamp is struck |
| CI / replay corpus | umbilicals from the gantry into the product's telemetry port; every merge, the yard re-measures the product |
| stubs / temporary implementations | the **buck** — the temporary form a coachbuilt body is beaten over; visibly yard-colored, never product-colored |
| unseated rack | a shelf on the scaffold holding anything the bodyplan hasn't seated yet |

## §C The four laws — the rendering constitution

Metaphor-independent; they bind any seat map, any scene.

### Law 1 — the scaffold is never load-bearing

The product stands in the middle of the scene. Everything processual is furniture
around it — whatever the metaphor makes of "around": outside the hull, behind the
glass, on the far side of the sky. Strike the scaffold and the product must stand
alone.

### Law 2 — explosion distance = interface stability

The continuous scalar 2D cannot do. Along each seam's axis:

```
FROZEN        parts mated flush · weld bead · stamp decal
PROVISIONAL   parts held apart a fixed gap · jig clamp visible in the gap
SCHEDULED     the incoming implementation's ghost floats outside the hull,
              aligned on the seam axis, waiting to slide in
COMPLETE      ghost mates · buck struck · explosion collapses to zero
```

Watching the project mature is watching the product collapse from exploded to whole.
This is the scene's single deepest visual claim, and it is pure data: tier and
substitution schedule, straight from the seam table.

### Law 3 — geometry is earned

Mesh fidelity encodes build state, never taste:

- `absent` → point-cloud / faint wireframe ghost at the seat
- `stubbed` → simple primitive, yard-marked (the buck)
- `built` → flat-shaded solid
- `frozen` (seams) → edged solid, weld bead, stamp decal

If the client's own model of itself is crude, the scene is crude *there* — a capsule
hull for a sim that believes its body is a capsule. Vagueness is not an art
direction; it is the honest rendering of absent knowledge. **The law binds the
metaphor too**: a seat that renders detail the state does not warrant is a lie,
however beautiful.

### Law 4 — text stays flat

Specification text (constraint bodies, issue text, function signatures) renders on 2D
**sheets**: drawing-sheet SVGs generated from the same state, shown as HUD overlays
or in-world clipboards. Sheets use drafting vocabulary — balloon callouts for
constraints, revision clouds for open holds, phantom lines for the planned, a REV
table for gate history, a title block whose revision ID is the state hash.
Data-carrying marks keep drafting vocabulary **at every zoom register**; only surface
rendering changes register, never semantics.

## §D Camera stations = the truth stack

Preset bookmarks, one per truth layer, so zooming is *reading the project in its
prescribed order*:

```
station 0  the bay        narrative register — silhouette, the whole metaphor, atmosphere
station 1  the cutaway    rationale register — hull opened, organs named
station 2  the sheets     plan register — a clipboard faced square-on
station 3  the detail     code register — DETAIL callouts, real signatures, test names
```

Station 0 is where the aim sentence meets the eye: the whole metaphor at once. The
other stations are metaphor-independent — they are the same four reading moves in any
world.

## §E Interaction minimums

Orbit + user-draggable clipping plane; click any part/tag → its source text (the
issue body, the constraint) in a side panel, linked back to the client repo path;
hover → ID + status axes; a scrubber over **gate history only** (reconstructing past
scenes from git is derived data too) — never ambient autoplay motion.
