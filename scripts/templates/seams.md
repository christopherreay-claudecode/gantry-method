# {{name}} — seam table
*One row per PLANNED substitution point (doctrine: an interface exists only where an
implementation is scheduled to swap — no speculative interfaces). Freezing a seam requires
human sign-off: a closed `freeze-request` issue that refs the S#.*

| S# | seam name | implementations (now → scheduled) | freeze event |
|----|-----------|-----------------------------------|--------------|

Notes (not parsed): <why each seam exists; which constraint it serves>. Add each S# to
`seam_slugs` in `.gantry/adapter.json` (e.g. `"S1": "setpoint-iface"`).
