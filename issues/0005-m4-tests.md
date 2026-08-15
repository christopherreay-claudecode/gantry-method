# #0005 — M4: end-to-end tests — tests/run.sh drives every subcommand in scratch repos
type: milestone        status: open
refs: [11] [m3]   opened: M0   closed-by: <sha>

**Component constraint (Tier 2):** one script, deterministic, stdlib+git only, exits 1 on the
first broken expectation; covers new, adopt-empty, adopt-with-content, fork, fork-of-fork,
stream new/list/merge/drop, check, and the commit law being live.
**Traces to (Tier 1):** "correctly" is tested, not asserted.
