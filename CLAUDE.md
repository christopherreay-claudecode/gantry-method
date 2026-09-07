# gantry — agent briefing

This is a Gantry repo. Gantry is a set of tools for project management. Gantry also includes cybernetic enhancements for your voice. Enter gantry at `tools/README.md`.

## This repo is the toolbox itself (self-hosting, constraint 10)

- `scripts/` holds the programs; `tools/*.py` are **symlinks** into `scripts/` (one copy of
  each program). Client repos get *copies* via `scripts/gantry adopt` / `scripts/adopt.sh`.
- `SPEC.md` and `scripts/gantry_extract.py` are one thing: change the grammar in both, in
  the same commit. `examples/` must be regenerated when the extractor's output changes.
- After any change to `scripts/gantry`, the templates, the extractor, or the hook installers:
  `sh tests/run.sh` (end-to-end, scratch repos) must pass before the commit.
- The tracker here (`issues/`) is *this* repo's; `examples/issues/` is the toy project's.
- Notify when done: `notify-send -u critical "gantry: <what>"`.
