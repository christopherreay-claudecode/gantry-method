# #0029 — trees address other spaces: a namespace may resolve to a URL template — LINKS: foot in the tree (markdown reference definitions) and mmt_links in the adapter; one lookup chain tree → repo → family → generic
type: feature        status: closed
refs: [10] [11]   opened: seed   closed-by: 4dbd84a

**Constraints this issue makes true (Tier 2 — each traces to a plan constraint in `refs:`):**
- [10] A tree addresses spaces beyond the repositories in `mmt_roots` with NO new token grammar:
  `<ns>:<id>` (the shape of `core:#1013`) where the namespace resolves to a URL template instead
  of a directory. Spec §5b's rule stands — no URLs in the reading line; the tool builds the href.
- [10] **`LINKS:` foot** — a trailing block in the tree file (as `DIM:` is a head), holding markdown
  reference definitions verbatim and nothing else:
  ```
  LINKS:
    [patent]: https://patents.google.com/patent/{id}
    [spec-live]: https://example.org/spec/s8
  ```
  A definition with `{id}` is a namespace (`patent:US10123456` in the body); one without is a
  one-off anchor referenced by bare name (`spec-live`). One file, one emission — the sidecar
  lives inside the tree, below the reading line. `.mmt` and the ```` ```mmt ```` fence both carry it.
- [10] **`mmt_links` in the adapter** — the same table at repo scope (`{"patent": "https://…/{id}",
  "rfc": "https://www.rfc-editor.org/rfc/rfc{id}"}`), copied under S1 like `mmt_tokens`; the
  interpreter lives upstream (#0020's shape).
- [10] **One lookup chain, most specific first:** tree `LINKS:` → adapter `mmt_links` → `mmt_roots`
  (repositories, then their token tables) → the generic six. First hit wins; a namespace that
  resolves nowhere is reported unresolved exactly as today.
- [10] Rendering: an external link is an `<a>` with the label "`<ns>: <id>`" and `rel="noopener"`;
  external targets are NOT fetched or stored — the content-addressed store stops at the repo
  boundary, stated in the page's roots block ("external: patent, rfc — not snapshotted").
- [10] Level 2: token edges to external namespaces export as `to: "<ns>:<id>"`, unchanged shape.
- [10] A bare URL or a `[text](url)` in the reading line is tolerated (rendered as a link) and the
  lint NOTES it ("prefer a named link: define it under LINKS:") — never a failure.
- [11] `tests/run.sh`: a tree with a `LINKS:` foot resolves `patent:X` to the template and
  `spec-live` to the anchor; the adapter's `mmt_links` resolves without a foot; the foot overrides
  the adapter for the same name; an undefined namespace is unresolved; a bare URL yields the note.

**Depends on:**
#0020 (closed): the per-root table interpreter this extends. Informs #0027 (symbols.js must carry
the external table too) and #0028 (the registry is the family-scope home for shared namespaces).

**Approaches (the technical ways to satisfy the constraints; the one taken, and why):**
- Proposed: `parse_tree` splits a trailing `LINKS:` block (lines after it that match
  `^\s*\[([\w.\-]+)\]:\s*(\S+)`); `Site.resolve_tok` gains a first step over a merged links dict
  (tree over adapter); `token_re` gains the declared namespace names as prefixes. ~60 lines.
- Not taken: inline markdown links as the idiom (URLs in the reading line — §5b's reason holds; a
  model-typed URL is also the least verifiable string it produces); a sidecar `.links.json`
  (two artefacts per answer, invisible in chat); a `name = url` spelling (markdown's `[name]: url`
  is already known to every model — emergent formality, not imposed); fetching external pages
  at render time (network in a local renderer; an opt-in archive can come later).

**Exit (what latches this):**
the test step above; a cubeOnSKOS tree naming `rfc:9110` and a `LINKS:` anchor renders with
both live and reports 0 unresolved.
