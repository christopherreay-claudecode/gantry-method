# #0006 — hold: stream sub-band size — 100 issues × 10 concurrent streams per level?
type: ambiguity        status: open
refs: [5] [Q1]   opened: M0   closed-by: <a human sentence>
deps: informs #0004

**The decision deliberately deferred:** a level's thousand is split into ten hundreds, one
per concurrent stream. Alternatives: (a) keep 10×100; (b) 20×50 for many short test
workorders; (c) allocate variable-width bands on demand (`--band-size`) recorded in
`streams.json`. The code takes (a); it must not silently become (b)/(c).
**Traces to (Tier 1):** an orchestrator's parallelism ceiling is a felt limit.

Human sign-off closes this. Until then `gantry stream new` refuses an 11th open stream at a
level and says why.
