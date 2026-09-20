# #0030 — gantry upgrade <repo>: refresh a client's tools/ in one command — diverged tools are kept and named, never overwritten; gantry_version recorded in the adapter
type: feature        status: open
refs: [2] [9]   opened: seed   closed-by: <sha>

**Constraints this issue makes true (Tier 2 — each traces to a plan constraint in `refs:`):**
- [2] `gantry upgrade [<repo>]` refreshes a client's `tools/` (g · gantry_extract.py · gen_index.py ·
  lint_commit.py · mmt.py · templates/ · README.md) from the toolbox in ONE command, and NEVER
  overwrites a tool the client has changed: it compares the client's copy against the toolbox
  copy at the version the adapter records (`gantry_version`, a toolbox sha written on every
  upgrade/adopt); a copy that differs from THAT is locally extended → kept, named, with the
  three-way diff hint (`git diff <old-sha>:scripts/x.py tools/x.py`). Today `adopt --fresh-tools`
  overwrites unconditionally and prints "kept … not overwriting" while doing so (#0023).
- [2] `--force <tool>` overwrites a named diverged tool deliberately; `--dry-run` lists what would change.
- [9] `tools/README.md` and `tools/templates/` are always refreshed (gantry's, never client-edited).
- [9] `gantry_version` in the adapter lets `g check` note "tools are behind the toolbox by N commits".

**Depends on:**
#0023 (the defect this replaces). Informs #0031, #0032 (upgrade --all walks the registry).

**Approaches (the technical ways to satisfy the constraints; the one taken, and why):**
- Proposed: `cmd_upgrade` reads `gantry_version` (absent → treat every differing file as
  diverged, i.e. safe by default); for each shipped tool: identical → skip; equal to the
  toolbox copy at `gantry_version` (`git show <sha>:scripts/<tool>`) → refresh; otherwise →
  keep + report. Writes the new `gantry_version`. `adopt --fresh-tools` becomes an alias.
- Not taken: three-way merge of program text (S1 chose copies to avoid merge machinery);
  a per-tool version header inside each file (the adapter already carries repo-level state).
- The cubeOnSKOS extractor's rules extension is the standing diverged case; upstreaming it as an
  adapter-declared entity kind (#0028's data-hook shape) is what makes that repo upgradeable.

**Exit (what latches this):**
`tests/run.sh`: adopt a scratch client, edit its `tools/gen_index.py`, run `gantry upgrade` →
the edit survives and is named; `--force gen_index.py` replaces it; `gantry_version` is written;
a second `upgrade` is a no-op. Run against cubeOnSKOS with `--dry-run`: the extractor is reported
diverged, nothing else.
