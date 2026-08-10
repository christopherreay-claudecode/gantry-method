# Example — widget-press, end to end

A deliberately tiny project that exercises **every** feature in `../SPEC.md`, so you can see the
whole loop — constraints → issues → `GRAPH.md` — on one screen. All artifacts here are real
output of the bundled scripts, not hand-drawn.

## Files

| File | Layer (SPEC §2) | Shows |
|---|---|---|
| `plan.md` | plan (Tier-1 formalized) | 4 numbered constraints in 2 groups (`## 2.`, `### C-CORE`/`### C-CTRL`), each tracing to a Tier-1 beat |
| `seams.md` | seams | 2 substitution points (`S1` freezes at M1; `S2` provisional to Phase B) |
| `issues/*.md` | tracker | one issue per type — milestone, freeze-request, ambiguity, amendment-proposal, placeholder |
| `adapter.json` | — | paths + slug maps that tell extract where truth lives |
| `deps.json` | — | one **reviewed** (`provenance: proposed`) dependency edge with an evidence quote |
| `issues/INDEX.md` | derived | the generated ledger (`gen_index.py` format) |
| `GRAPH.md`, `state.json`, `bodies.json` | derived | the extractor's three outputs |

## Regenerate (deterministic — same inputs, same bytes)

```sh
# from fullMethodology/
python3 scripts/gantry_extract.py \
    --client examples/adapter.json --root examples \
    --out examples/state.json --digest examples/GRAPH.md \
    --deps examples/deps.json
```

Re-running produces **byte-identical** `GRAPH.md` and `state.json` (verified). The REV in the
header is a hash of `state.json`; editing an issue's *prose* changes `bodies.json` only and does
**not** move the REV — structure moves the REV, wording does not (SPEC §6).

> The GRAPH header shows `@ <sha>+dirty` because this example lives inside the gantry repo, so
> extract reads that repo's git HEAD, and the example files are uncommitted at generation time.
> In real use, `--root` is the *client's* repo and the sha is the client's commit.

## What the generated `GRAPH.md` demonstrates (mapped to the spec)

```
gates latched: m0 · open: m1 · phases open: b     ← milestone #0001 (closed by sha) LATCHED gate m0;
                                                     #0002 open → gate m1 open; #0006 → phase b   (§3, §4)
seams provisional: S2                             ← S2 has no freeze issue → provisional          (§3)
seams frozen: S1                                  ← freeze-request #0003 CLOSED BY SIGN-OFF froze S1 (§3)

open items (kind · refs → upstream anchors):
  #0002 workorder m1-press-cycle → 3,S1,m0,m1     ← refs resolved to constraint 3, seam S1, gate m0,
                                                     + its own auto-gate m1                        (§4)
  #0004 hold      torque-law ⛭human → 4           ← ambiguity → HOLD; ⛭human = human-gated closure (§3)
  #0006 workorder phaseb-placeholder → b,S2       ← anchored by [S2] even though [PhaseB] self-refs (§4)

dependency edges (blocks = must resolve first):
  #0002 —defers-to→ #0004 [parsed]                ← author-declared on the deps: line              (§5)
  #0002 —informs→ #0003 [parsed]
  #0004 —defers-to→ #0002 [proposed]              ← from deps.json, a REVIEWED edge with evidence   (§5)
  #0004 —informs→ #0002 [parsed]

closed/resolved: #0001 #0003 #0005                ← the two human-gated closures (#0003, #0005) +
                                                     the sha-closed milestone (#0001)
```

## Things worth trying (to feel the invariants)

- **Break a ref:** change `#0002`'s `refs:` to `[99]` (no such constraint) → extract warns
  `ref [99]: constraint not found`. Remove all resolvable refs → it becomes `(floating)` (SPEC §5,
  invariant 1).
- **Forge a freeze:** set `#0003`'s `closed-by:` to a sha like `deadbee` → extract overrides it to
  OPEN and warns; S1 goes back to *provisional* (SPEC §3, invariant 2 — a design surface cannot be
  frozen by accident).
- **Move `closed-by` to the type line** on any issue → its `refs:` line stops matching and the
  issue floats. This is the single most common adoption mistake (SPEC §4).
- **Edit only prose** in an issue body → re-run: the REV is unchanged (SPEC §6, the bodies sidecar).
