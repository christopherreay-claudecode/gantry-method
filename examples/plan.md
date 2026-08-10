# widget-press — implementation plan (fullMethodology example)
*Constraint-satisfaction form. The code must result in the constraints below being true.*
*Companion (Tier-1 narrative): a press operator commits a stroke and it lands, always the
same way, so the feel of the machine is learnable rather than a lottery.*

---

## 1. Guiding role
Every derivation is judged against one thing: the operator's felt experience of a machine
that is **honest and repeatable** — a committed stroke lands identically every time.

## 2. Constraint set (the code has to result in this)

### C-CORE
1. **Deterministic tick.** The press advances on a fixed-rate tick; given (program, seed) the
   run is bit-identical on every supported machine. (Serves Tier-1: repeatability is the feel.)
2. **Replay is truth.** Every tick emits a state hash; a replay file re-executes bit-identically
   and is the CI regression gate. (Serves Tier-1: "always the same way" is auditable.)

### C-CTRL
3. **One command bus.** Every actuation flows through one arbitrated command bus; a command is
   `(source, channel, payload, at-tick)`. (Serves Tier-1: a committed stroke is a bus command.)
4. **Setpoints, not forces.** Operators emit setpoints; firmware turns setpoints into forces
   in-loop, deterministically. (Serves Tier-1: the operator commits intent, not raw force.)

## 3. Build order (risk-first; binding, not suggestions)
1. tick loop + replay + CI gate (C-CORE) — gate **M0**
2. command bus + firmware setpoint tracking (C-CTRL) — gate **M1**
3. Phase B: real rigid-body press driver (behind seam S2)
