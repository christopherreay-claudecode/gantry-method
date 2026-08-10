# #0002 — M1: the press completes one cycle
type: milestone        status: open
refs: [3] [S1] [m0]   opened: M0   closed-by: <sha>
deps: defers-to #0004; informs #0003

**Component constraint (Tier 2):** an operator setpoint, issued through the command bus, drives
firmware that closes one press cycle; the executed stream replays bit-identically.
**Traces to (Tier 1):** a committed stroke lands — the operator commits intent, the machine
completes it identically every time.

Satisfies constraints 3 and 4; builds on gate `m0` (#0001) and the S1 setpoint interface. Named
with the gate slug `m1-…`, so extract yields the open **gate `m1`**.

Dependencies declared at the moment they were known:
- `defers-to #0004` — the exact setpoint→force law is an open decision; this milestone takes the
  conservative reading and defers the real law.
- `informs #0003` — landing firmware is what makes S1 ready to freeze.
