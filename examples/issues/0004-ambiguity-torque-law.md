# #0004 — Ambiguity: the exact setpoint→force law
type: ambiguity        status: open
refs: [4]   opened: M1   closed-by: <human sign-off>
deps: informs #0002

**The open decision:** constraint 4 says firmware turns setpoints into forces, but the exact law
`force(setpoint, position, load)` is not yet pinned. Choosing it silently in firmware code would
be accidental design.

**Traces to (Tier 1):** the law shapes how a committed stroke *feels* landing — too important to
default without a human decision.

An `ambiguity` becomes a **hold** (kind `hold`): the code must not resolve it silently; it takes
the most conservative reading until a human closes this. Its filename slug (`…-torque-law`) plus
the adapter's `q_holds: {"Q1": "torque-law"}` mean any issue that refs `[Q1]` resolves here.
`informs #0002` — the outcome shapes M1 without blocking it.
