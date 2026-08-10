# 02 — Projecting the grammar into 3D

Why 3D at all: the grammar's hard pairs are **containment** (parts inside parts
inside the product) and the **reference graph** (workorders → constraints/seams/gates,
many-to-many). 2D dies on both at once — nesting plus cross-references becomes
line-crossing spaghetti, and every "look inside" is a hand-authored cutaway. In 3D,
containment is literal (the camera goes inside; a clipping plane *is* the look-inside
operation), and reference edges route through space without crossing ambiguity.
The bar is **accuracy, not beauty**: primitives, flat shading, and labels are enough,
and are more honest than art the state cannot warrant.

## The scene, by law

### Law 1 — the scaffold is never load-bearing

The product stands in the middle of the scene. Everything processual is yard
furniture around it:

| Process object | Yard object |
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
direction; it is the honest rendering of absent knowledge.

### Law 4 — text stays flat

Specification text (constraint bodies, issue text, function signatures) renders on 2D
**sheets**: drawing-sheet SVGs generated from the same state, shown as HUD overlays
or in-world clipboards on the scaffold. Sheets use drafting vocabulary — balloon
callouts for constraints, revision clouds for open holds, phantom lines for the
planned, a REV table for gate history, a title block whose revision ID is the state
hash. Data-carrying marks keep drafting vocabulary **at every zoom register**; only
surface rendering changes register, never semantics.

## Camera stations = the truth stack

Preset bookmarks, one per truth layer, so zooming is *reading the project in its
prescribed order*:

```
station 0  the bay        narrative register — silhouette, scaffold, atmosphere-dark
station 1  the cutaway    rationale register — hull opened, organs named
station 2  the sheets     plan register — a clipboard faced square-on
station 3  the detail     code register — DETAIL callouts, real signatures, test names
```

## Interaction minimums

Orbit + user-draggable clipping plane; click any part/tag → its source text (the
issue body, the constraint) in a side panel, linked back to the client repo path;
hover → ID + status axes; a scrubber over **gate history only** (reconstructing past
scenes from git is derived data too) — never ambient autoplay motion.
