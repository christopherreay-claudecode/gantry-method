# #0031 — gantry install --system: one installation on PATH (~/.local/bin or /usr/local/bin), tools/g in a client becomes a thin shim to it, with a vendored fallback only on request
type: feature        status: open
refs: [1] [2]   opened: seed   closed-by: <sha>
deps: informs #0032

**Constraints this issue makes true (Tier 2 — each traces to a plan constraint in `refs:`):**
- [1] ONE installation of gantry on the machine: `gantry install` puts the entry point on PATH
  (`~/.local/bin/gantry` by default, `--system` → `/usr/local/bin` with sudo) — today's command,
  kept — and `gantry` on PATH is what every hook shim and every `tools/g` calls.
- [2] A client's `tools/g` becomes a THIN SHIM: it execs `gantry` from PATH with `--repo <its
  own root>`; if `gantry` is not on PATH it says so and how to install (or, if the operator ran
  `gantry vendor`, execs the vendored full copy beside it). The extractor, lint and mmt stay
  client copies until #0028 (they are what a clean clone needs offline).
- [2] `gantry --version` prints the toolbox sha + path; `g check` warns when the shim's gantry and
  the adapter's `gantry_version` disagree by more than the operator allows.
- [1] Nothing about the method changes: same commands, same files; only the number of copies of
  the driver program goes from N+1 to 1.

**Depends on:**
#0030 (upgrade must exist before shims replace copies, so a client can be moved back).

**Approaches (the technical ways to satisfy the constraints; the one taken, and why):**
- Proposed: `scripts/templates/g.shim` (~15 lines: locate gantry on PATH via shutil.which, else
  `tools/gantry` if vendored, else a clear message; `os.execv` with `--repo` resolved from the
  shim's own location). `adopt`/`upgrade` install the shim; `gantry vendor <repo>` copies the full
  driver beside it and the shim prefers it. Hook shims (`pre-commit`, `commit-msg`) unchanged —
  they already call `tools/*.py` by path.
- Not taken: a Python package on PyPI (distribution is not the problem; copies are);
  system-wide extractor/lint (a clean clone must still regenerate GRAPH.md offline — #0028 decides).

**Exit (what latches this):**
`tests/run.sh`: `gantry install --bin $S/bin`; adopt a client; its `tools/g` is the shim; with
`$S/bin` on PATH `python3 tools/g map` works; with PATH stripped it fails with the install hint;
after `gantry vendor` it works again with PATH stripped. The three live repos run on the shim.
