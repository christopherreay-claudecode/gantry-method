# held design — per-request in-memory SQLite over the whole network (2026-09-05, not filed)

**Status:** discussion · **Refs:** see body · **Filed:** see date in title

- what: on each call, load state.json (entities · relations · bindings) + bodies.json + the mmt
  symbol table across `mmt_roots` + tree edges into an in-memory sqlite3 (stdlib; a few thousand
  rows; milliseconds), answer one question, discard. Derived, never persisted — the only kind
  of second map the method allows; the speed is what makes that kind affordable.
- earns tokens on: transitive closure (`deps #1042 --depth 3`), reverse refs (`serves 19`),
  full text over bodies (FTS5), cross-repo joins; `tree diff` (#0021) is one such query hand-coded.
- conditions: the tool owns the grammar (verbs, `--sql` only as escape hatch); output small or a
  MindMapTree with live tokens; GRAPH.md stays step 1 of the ritual.
- status: Christopher is experimenting in the scenarios where it seems useful; revisit when he
  has cases. Not an issue until then.
