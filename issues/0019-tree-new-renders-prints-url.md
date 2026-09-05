# #0019 — tools/g tree new renders on write and prints the file:// URL + lint + unresolved — a tree is emitted once, into the tool call, never twice
type: feature        status: closed
refs: [10] [11]   opened: seed   closed-by: 49371f8

**Constraints this issue makes true (Tier 2 — each traces to a plan constraint in `refs:`):**
- [10] A substantive answer written as a MindMapTree is emitted ONCE — as the stdin of
  `tools/g tree new <slug>` (a heredoc in the tool call) — and the tool renders it in the same
  invocation, so the model never repeats the tree in chat: the chat reply is the page URL and the
  lint verdict. Token cost of a tree = the tree, plus ~4 lines.
- [10] `tree new` prints, after writing: the tree path · `file://` URL of the rendered page ·
  lint findings (each) · unresolved tokens. `--no-render` restores write-only.
- [11] `tests/run.sh` step 14 exercises the new output.

**Depends on:**
#0017 (the trees/ facet — closed 4a2cda3). Nothing open.

**Approaches (the technical ways to satisfy the constraints; the one taken, and why):**
- Taken: `cmd_tree_new` calls `cmd_tree_render` on the written file with the repo's `mmt_roots`;
  `mmt.py` prints the page path, which `tree new` turns into a `file://` URL. The ritual line
  in `tools-README.template.md` and `trees-README.template.md` says: substantive answers go
  through `tree new`, chat carries the URL.
- Not taken: rendering in chat markup or any second copy of the tree; a `--quiet` that hides lint
  (the lint IS the signal the model needs back).

**Exit (what latches this):**
step 14: `printf … | tools/g tree new smoke` output contains `file://…/.site/mmt/…-smoke.html`
and the page exists without a separate `tree render` call; `--no-render` writes the file only.
