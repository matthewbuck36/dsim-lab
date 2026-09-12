# M4 bounded source clarifications

Adopted 2026-09-09 within `m4_execution_evaluation_plan.md` before the named
corrections. These are Level B compatibility/performance fixes preserving the
two research goals, scientific definitions, controls, gates and old behavior.

1. The large21000-pose source fixture exposes quadratic conversion work in
   `_v2_search_eligibility`: repeated `np.searchsorted` calls convert entire
   Python integer timestamp lists. Replace those same sorted-list lookups with
   `bisect_right`, preserving exact right-side duplicate/boundary semantics.
   Retain the first bounded slow/failed fixture and verify numerical/output
   parity plus existing eligibility regressions. No label/gap/dwell change.

2. Existing runner Stage A extraction requires a legacy relative source stamp
   on `CONVERGENCE_CONFIRMED`; centroid events intentionally leave that field
   invalid and publish authoritative typed absolute diagnostics. M4 B/D must
   join the actual centroid diagnostic, exact event identity/center/score and
   original Timekeeper origin through a selected evaluator adapter before
   calling inherited staged-recovery helpers. A private normalized evaluator
   record may carry the bound relative coordinate with explicit provenance;
   never mutate public messages, invent an origin or reinterpret historical
   recordings. The existing live monitor may subscribe to these two existing
   topics within its current owner for the same finite join. Preserve all old
   route defaults, timestamps and gates; no new monitor/node/control publisher.
   Missing/ambiguous/conflicting typed support remains invalid evidence.

Both corrections require focused source/transport-shaped fixtures and the
relevant inherited regressions before the M4 source checkpoint. No extra
Gazebo acquisition, rerun, topology adjustment or acceptance waiver is granted.
