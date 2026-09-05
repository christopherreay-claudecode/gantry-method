# #0020 — mmt_tokens / mmt_edges in adapter.json: the §5b token grammar and the ->@[type] vocabulary become per-repo bindings; collect() interprets the table per root; gantry ships the generic defaults, clients add their own
type: feature        status: open
refs: [10] [11]   opened: seed   closed-by: <sha>
deps: blocks #0021

**Constraints this issue makes true (Tier 2 — each traces to a plan constraint in `refs:`):**
- [10] The MindMapTree format core (glyphs `=~?!x`, `@`/`->@`, tree characters, L0/L1/L2) is
  fixed by the spec and travels as spec + script. The VOCABULARY — which bare tokens resolve to
  which documents (§5b), and which `->@[type]`s are legal (§5) — is per-repo data in
  `.gantry/adapter.json` (`mmt_tokens`, `mmt_edges`), copied by `adopt`/`fork` under S1 like
  every other binding table (`seam_slugs`, `q_holds`, `parts`, `mmt_roots`).
- [10] `mmt.py collect()` is a generic interpreter of a root's own `mmt_tokens` table (each entry:
  kind · file glob · line regex · token format), so a cross-repo tree resolves each root by that
  root's grammar. Today one hard-coded `collect()` is applied to every root.
- [10] gantry's own adapter ships the six generic kinds every gantry repo has by construction:
  `#NNNN` issues · `c17`/`[17]` constraints · `S1` seams · `m2`/`g1`/`Q1` gates+holds ·
  `path[:line]` · commit sha. The three that are one client's habit — `R7` rule lines in
  CLAUDE.md, `§6.1` contract headings, `U4`/`W2`/`H3` plan headings — leave the script and
  become cubeOnSKOS's adapter entries. Verified 2026-09-05: gantry has 0 R-lines, ui 0, core 9;
  only core has docs/plans.
- [10] Spec §5b is reworded as "the token mechanism + gantry's shipped defaults", §5 likewise
  for edge types; a checker warns on a `[type]` outside `mmt_edges` (L2 prep, not L1).
- [11] `tests/run.sh` covers: a scratch client whose adapter declares a custom token kind
  resolves it; the generic six resolve with no adapter entries at all.

**Depends on:**
#0017 (closed). Informs #0021 (the edge vocabulary is what L2 export emits).

**Approaches (the technical ways to satisfy the constraints; the one taken, and why):**
- Taken: declarative table, interpreted; generic defaults baked into the script AND written into
  gantry's adapter so a client can see what to copy. Paths/commits stay code (no table can say
  "any file").
- Not taken: a plugin/Python-hook mechanism per client (a copyable table is the S1 shape; code
  hooks would not survive `adopt` cleanly); making glyphs extensible (spec §3: a tree that needs
  more glyphs needs more nodes — and every formality not emergent from the model's own output is
  a token tax).
- Later: `adopt --from <repo>` copies another client's `mmt_tokens` when two repos share a
  layout.

**Exit (what latches this):**
tests/run.sh step "mmt-adapter": scratch client adapter declares
`{"kind":"spec","glob":"specs/*.md","line":"^# (S\\d+) ","token":"{1}"}`; a tree naming `S8`
links into `specs/…#L1`; cubeOnSKOS renders its existing trees with zero new unresolved tokens
after its three kinds move into its adapter.
