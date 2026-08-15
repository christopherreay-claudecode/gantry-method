# gantry — seam table
*One row per PLANNED substitution point (doctrine: an interface exists only where an
implementation is scheduled to swap). Freezing a seam requires human sign-off: a closed
`freeze-request` issue that refs the S#.*

| S# | seam name | implementations (now → scheduled) | freeze event |
|----|-----------|-----------------------------------|--------------|
| S1 | fork copy rule | `git archive HEAD − default excludes` → per-base allowlist manifest (`.gantry/fork-manifest`, absorbing `fork-app.sh`) | Phase B |

Notes (not parsed): S1 is the only scheduled swap. Today `gantry fork` copies every tracked
file at the base's HEAD minus a default exclude list (plus `.gantry/fork-exclude`); the
SvelteKit base's allowlist manifest still lives in `fork-app.sh`. When the allowlist moves
into the base as `.gantry/fork-manifest`, `fork-app.sh` retires (proposals.md).
