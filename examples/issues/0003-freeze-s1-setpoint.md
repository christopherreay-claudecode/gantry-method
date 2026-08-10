# #0003 — S1 ready to freeze: the setpoint interface
type: freeze-request        status: closed
refs: [S1] [4]   opened: M1   closed-by: signed off by Owner 2026-02-01

**Component constraint (Tier 2):** the operator→firmware boundary (seam S1) is stable enough that
changes require amendment, not ad-hoc edits.
**Traces to (Tier 1):** a learnable machine needs a stable command surface — the stroke means the
same thing tomorrow as today.

`freeze-request` is a **human-gated** type: it closes only by a person's sign-off (never a bare
sha). This one is closed by "signed off by Owner …", so extract marks seam **S1 frozen**. Had it
been closed by a sha, extract would override it back to OPEN and warn (invariant 2) — a design
surface cannot be frozen by accident.
