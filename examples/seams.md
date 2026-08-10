# widget-press — seam table (fullMethodology example)
*One row per planned substitution point (doctrine: an interface exists only where an
implementation is scheduled to swap). Freezing a seam requires human sign-off.*

| S# | seam name | implementations (now → scheduled) | freeze event |
|----|-----------|-----------------------------------|--------------|
| S1 | setpoint interface | `SetpointStub` → `SetpointSpline` | M1 |
| S2 | press driver | `AnalyticPress` → `RigidBodyPress` | Phase B |

Notes (not parsed): S1 is the operator→firmware boundary (constraint 4); it freezes at M1 once
firmware tracks real setpoints. S2 is the physics substitution; it stays provisional until the
rigid-body driver lands in Phase B.
