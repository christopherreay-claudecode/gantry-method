# #0001 — M0: the tick loop stands
type: milestone        status: closed
refs: [1] [2]   opened: seed   closed-by: a1b2c3d

**Component constraint (Tier 2):** a fixed-rate tick advances the press and emits a per-tick
state hash; a replay of (program, seed) re-executes bit-identically.
**Traces to (Tier 1):** the operator's felt "always the same way" — repeatability is the feel.

Satisfies constraints 1 and 2. This milestone issue is named with a gate slug (`m0-…`), so
extract also yields the **gate `m0`**; closing this issue by commit `a1b2c3d` latches it.

Evidence: `test_m0_determinism` green; two runs byte-identical; replay corpus re-hashes.
