# gantry — agent briefing

<!-- gantry:begin — this block is gantry's: `gantry adopt` refreshes it in place. Everything outside the markers is the project's own. -->
## gantry — the development method this repo runs on

This repo runs on **gantry** (a project's truth is a set of numbered constraints; issues point
at them; `GRAPH.md` is the derived map). **Before anything else, every session reads
`tools/README.md`** — the session ritual lives there and gantry keeps it current: `GRAPH.md`
first · truth upstream, derived files never hand-edited · work against an issue, the commit law ·
MindMapTrees as your voice (`tools/g tree new`) · `deps:` · constraints first. This file does not
restate it. Issue band: **#0001–#0999** (lineage level 0); file nothing outside it.
<!-- gantry:end -->

## This repo is the toolbox itself (self-hosting, constraint 10)

- `scripts/` holds the programs; `tools/*.py` are **symlinks** into `scripts/` (one copy of
  each program). Client repos get *copies* via `scripts/gantry adopt` / `scripts/adopt.sh`.
- `SPEC.md` and `scripts/gantry_extract.py` are one thing: change the grammar in both, in
  the same commit. `examples/` must be regenerated when the extractor's output changes.
- After any change to `scripts/gantry`, the templates, the extractor, or the hook installers:
  `sh tests/run.sh` (end-to-end, scratch repos) must pass before the commit.
- The tracker here (`issues/`) is *this* repo's; `examples/issues/` is the toy project's.
- Notify when done: `notify-send -u critical "gantry: <what>"`.
