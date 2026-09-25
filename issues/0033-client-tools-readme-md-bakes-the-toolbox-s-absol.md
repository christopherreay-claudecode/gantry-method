# #0033 — client tools/README.md bakes the toolbox's absolute path at adopt time — a cloned client points at another machine; say sibling ../gantry or GANTRY_REPO instead
type: bug        status: open
refs: [1] [2]   opened: seed   closed-by: <sha>

**Constraints this issue makes true (Tier 2 — each traces to a plan constraint in `refs:`):**
[1] An adopted repo cloned onto another machine still tells its agent where the toolbox is. [2] Adoption writes nothing machine-specific into client content.

**Observed:** `scripts/tools-README.template.md` substitutes `{{gantry_repo}}` with the adopting machine's absolute path (`/home/christopher/…/gantry`) — found while planning to share cubeOnSKOS (core:#1082).

**Approaches:** the README says: the toolbox is `${GANTRY_REPO:-../gantry}` (sibling by convention, env to override); `tools/g` already carries every day-to-day command, so the toolbox path is only needed for `stream new/merge` and `adopt --fresh-tools`. `adopt` re-run with `--fresh-tools` rewrites the README.

**Exit:** tests/run.sh: an adopted scratch repo's tools/README.md contains no absolute path; `stream new` from the client copy resolves the toolbox via the sibling or the env var.
