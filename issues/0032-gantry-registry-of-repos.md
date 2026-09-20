# #0032 — registry of gantry repos on this machine: ~/.gantry/registry.json — new/adopt/fork/stream register; gantry ls / gantry check --all / gantry upgrade --all walk it; names are the root prefixes
type: feature        status: open
refs: [4] [5]   opened: seed   closed-by: <sha>
deps: informs #0028

**Constraints this issue makes true (Tier 2 — each traces to a plan constraint in `refs:`):**
- [4] [5] The machine has ONE list of its gantry repos: `~/.gantry/registry.json` (path from
  `$GANTRY_HOME` if set) — entries `{name, path, lineage, band, gantry_version, registered}`.
  `new`, `adopt`, `fork` and `stream new` register (a stream under its prefix, marked as such);
  `stream merge/drop` and a missing path deregister or mark stale.
- [4] `gantry ls` prints the registry (name · path · level/band · tools version · last check);
  `gantry check --all`, `gantry upgrade --all` (#0030) and `gantry tree render --all-repos` walk it.
- [5] The registered NAME is the root prefix for cross-repo references (`core:#1013`): `mmt_roots`
  becomes optional — a tree resolves any registered name; an adapter's `mmt_roots` still narrows
  or renames the neighbourhood. This is the first half of #0028's registry; the extractor/lint
  half (`deps: blocks ui:#0011`) stays in #0028.
- [2] The registry is derived state about the machine, never truth: losing it costs a
  `gantry register` per repo; `gantry ls --discover <dir>` rebuilds it by finding `.gantry/adapter.json`.

**Depends on:**
#0031 (one installation is what makes one registry natural). Informs #0028.

**Approaches (the technical ways to satisfy the constraints; the one taken, and why):**
- Proposed: `registry.py` in scripts/ (load/save/register/deregister/discover); `_tree_roots`
  falls back to the registry when `mmt_roots` is absent; `cmd_ls`, `--all` flags on check/upgrade.
  The live three register as `base` (svelteKitOnSupabase), `core` (cubeOnSKOS), `ui` (cubeOnSKOS-ui),
  matching the prefixes their trees already use.
- Not taken: a registry inside any repo (it is about the machine, not a project); scanning the
  whole filesystem at every call (`--discover` is explicit).

**Exit (what latches this):**
`tests/run.sh` with `GANTRY_HOME=$S/home`: new/adopt/fork/stream register; `gantry ls` shows
them; a tree in one scratch repo names the other by its registered name with no `mmt_roots` and
resolves; `check --all` runs every repo; `--discover` rebuilds from scratch. The live three are
registered and `gantry ls` shows base / core / ui.
