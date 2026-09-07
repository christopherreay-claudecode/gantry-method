# #0024 — designDocs/METHOD-shape.md — the method described as a shape for reuse: a fixed attractor, mirrors at every scale, closures as the unit of progress, latches, human gates; pipeline vs convergence settled
type: workorder        status: closed
refs: [1] [10]   opened: seed   closed-by: 37ef5bf

**Constraints this issue makes true (Tier 2 — each traces to a plan constraint in `refs:`):**
- [10] A store blob is the document itself — escaped, line-numbered, nothing else — so its hash is
  a statement about the document: the same file at the same version has the same hash in every
  tree and under every renderer version (input-addressed, the Nix property proper). Today the
  blob is the rendered page, so text ⊗ resolution context ⊗ renderer version share one hash.
- [10] The vantage point is its own small artefact: `<tree>/symbols.js` — the tree's roots, its
  token→target table (from each root's `mmt_tokens` + the generic six), its edges, its
  mmt_edges vocabulary. Two trees' symbols files diff meaningfully ("§17/http started resolving").
- [10] Python is the ONLY owner of the grammar. `mmt.py` emits the table and the compiled patterns
  into symbols.js; `viewer.js` (a shipped tool file, copied by adopt like mmt.py) matches
  longest-first against that table and wraps — it has no regex of its own. Lint, unresolved and
  the four lines the agent reads back stay in Python at `tree new` time.
- [10] Works from `file://`: fetch()/XHR are blocked there, `<script src>` is not — so blobs are
  `.js` files carrying the document as a string; the per-tree `doc/` entry is a wrapper page of
  three script tags (symbols.js · viewer.js · the blob) and a div. The tree page may be the same:
  its blob is the .mmt itself.
- [10] A no-JS reader sees a plain numbered listing; blobs stay grep-able text.
- [11] `tests/run.sh`: same document in two trees → one blob; a renderer change (CSS/markup)
  does NOT change blob hashes; a rendered page (via a headless check or a JS-free assertion on
  the emitted symbols table) links the same tokens the Python lint reports as resolved.

**Depends on:**
#0019 #0020 (closed) — the store and the token tables exist; this refactors what they hold.

**Approaches (the technical ways to satisfy the constraints; the one taken, and why):**
- Proposed: keep `store_page()`'s shape, change its input: `store_doc(rel, lines)` writes
  `store/<sha256(source bytes)>.js` = `window.__mmtDoc = {root, path, lines: [...]}`; the tree's
  `doc/<slug>.html` wrapper inlines nothing, loads symbols.js + viewer.js + the blob. `symbols.js`
  = `window.__mmtSymbols = {roots, tokens: [{re, kind}], syms: {tok: {root, path, line, label}},
  edges}`; Python's `token_re()` output is serialised as JS-compatible source (avoid Python-only
  regex features — assert at emit time).
- Not taken: fetch-based loading (file:// forbids it); a JS-side token grammar (drift); giving
  up the store (the snapshot is the feature).
- Later: the tree page rendered from the raw .mmt by the same viewer — then a tree's blob is the
  tree, and the site is entirely raw artefacts + one viewer.

**Exit (what latches this):**
`tests/run.sh` step: render two trees naming the same document → one blob; touch CSS in mmt.py,
re-render → blob hashes unchanged, symbols.js unchanged; a token the lint reports resolved is
present in symbols.js with the href the wrapper will produce.
