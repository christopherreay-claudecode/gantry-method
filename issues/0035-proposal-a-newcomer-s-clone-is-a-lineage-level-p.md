# #0035 — proposal: a newcomer's clone is a lineage level — progress issues they mint carry a namespace (their branch or handle) so a later merge from upstream keeps both numberings; code merges, issues do not collide
type: amendment-proposal        status: open
refs: [4] [5]   opened: seed   closed-by: <a human sentence>

**Constraints this issue makes true (Tier 2 — each traces to a plan constraint in `refs:`):**
[4]/[5] The lineage law already answers this for forks and streams: a sub-project owns a band or a prefix, so any subset merges back with no renumbering. A NEWCOMER'S CLONE is the missing case — it is neither a fork (a new repo) nor a stream (a worktree the parent registers): the parent never learns it exists until a pull.

**The situation (cubeOnSKOS-system, 2026-09-25):** the interviews tell a newcomer's LLM to mint a progress issue per interview in their clone. Their numbers start at the next free number and collide with upstream's on any later pull. The owner's shape: "a merge for the code, and rename the issues so they keep the same numbers but have branch names in them".

**Approaches:**
1. **Clone-side prefix, declared by the clone (taken as the proposal).** `gantry adopt --as <handle>` (or `stream new --local`) writes `issue_prefix: <handle>` into the clone's adapter, so everything they mint is `#<handle>-NNNN` — exactly a stream's namespace, but unregistered upstream. On pull the numbers never meet; on a contribution upstream `stream merge` can register the prefix after the fact from the clone's adapter. The interviews then mint `#john-0001`, not `#0003`.
2. **Rename on pull.** A post-merge step rewrites the clone's bare-numbered issues into a namespace. Works, but rewrites history the clone has already committed against; the commit law's `#NNNN` references then point at renamed files.
3. **Upstream reserves a band per collaborator.** Requires upstream to know the collaborators first; fails the "given the repositories and nothing else" test.

**Exit:** tests/run.sh: a clone adopted with a handle mints prefixed issues; a merge of upstream main into it leaves both trackers valid and `check: ok`; extract warns on a bare-numbered issue in a handled clone.
