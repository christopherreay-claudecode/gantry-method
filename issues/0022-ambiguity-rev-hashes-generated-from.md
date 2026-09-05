# #0022 — REV hashes generated_from (commit, dirty, extractor_version): the fingerprint moves at every commit even when the graph is identical, and g check prints a REV that disagrees with the committed GRAPH.md — should REV hash entities only?
type: ambiguity        status: open
refs: [7] [8]   opened: seed   closed-by: <a human sentence>

**Constraints this issue makes true (Tier 2 — each traces to a plan constraint in `refs:`):**
**The decision deliberately deferred:** `REV` = sha256(entities + `generated_from`{commit,
dirty, extractor_version}). The pre-commit hook mints GRAPH.md at parent-sha+dirty; any later
`g check` at clean HEAD computes a different REV for an identical graph, and prints "up to
date — REV X" under a file whose header says "REV Y". Observed as the standing claim
"tools/g check says GRAPH.md stale at every clean HEAD (REV embeds HEAD sha)" in cubeOnSKOS
trees/2026-09-05-status.mmt:7 and live-moves.mmt:10 — a misreading the tool invites (the check
passes; the REVs disagree). Alternatives: (a) REV hashes entities only; `generated_from` stays
a sidecar in state.json and the `@ sha[+dirty]` stamp (a REV that moves means the graph moved);
(b) keep as is and rename the printed value so nobody reads it as a fingerprint;
(c) two values: REV (entities) and BUILD (everything). Proposed in proposals.md since
2026-08-19 as "#0014" (that number has since been taken by m12); moved into the tracker here.
**Traces to (Tier 1):** an agent reading two REVs that differ concludes drift, and spends a turn
proving there is none — at every session.

**Depends on:**
nothing. Changes `canonical_hash()` and the header line; `--check` already normalises the stamp.

**Approaches (the technical ways to satisfy the constraints; the one taken, and why):**
(a) is recommended: it is what "fingerprint" means, and `--check` already treats
`generated_from` as noise by normalising the stamp. Human sign-off picks; a workorder implements.

**Exit (what latches this):**
a human sentence on `closed-by:`; then a workorder whose exit is: two extracts of the same
tree at different HEADs produce the same REV, and `tests/run.sh` asserts it.
