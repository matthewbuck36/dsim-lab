# R9 handoff: motion readiness correction complete

COMPLETE2026-09-11UTC. [Plan](r9_motion_readiness_plan.md) and
[validation](validation/r9_motion_readiness.md) record exact commands and hashes.
The private arrival-motion evaluator now pairs actual commands and diagnostics
only within the same recorded readiness interval, with unchanged strict validity,
count, vector, time and monotonicity checks. Outside-window counts remain visible.
No runtime controller, public interface or scientific threshold changed.

One focused bundle passed59 tests in2.099730s,304 stable pins; session54276 reaped0.
One separate filtered C component reassessment passed in6.018183s outer time,
334 stable pins; session69875 reaped0. No simulation is active. There are11493
exact readiness pairs and three fully covered continuous acquisition segments:
first VERIFY71.1–89.2s, second VERIFY156.5–171.0s and DESIGN171.0–171.6s. All
short zero-command pulses remain measured; no mandatory stopped sweep is inferred.
Independent review passed13 checks with59 stable small inputs. Original V11
closure inputs and all closed scientific verdicts remain unchanged.

External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/r9_motion_readiness_v1/`.
New C motion SHA256 `372bebaaf0ae21860058d857386d9fcca6f1823f6db33908911c8c985e62eebd`;
reassessment SHA256 `cb4a32bbbe84aaf38e8c5c1b3452676a403ac660734f808077d5d48dcbc4448f`.

The [V11 comparison](m4_pilot_v11_handoff.md) remains closed incomplete, with four
successful development arrivals and twelve confirmation runs unstarted. Its
original C motion result is unavailable; this is a separate corrected component
measurement. Both C and D now have selected continuous-motion evidence and passing
selected direction references. The original30% detector-latency target remains
unavailable because first positive-mask residence does not supply observed endpoints.

Next milestone is a prospective detector-measurement decision. The completed
[diagnosis](validation/m4_v11_measurement_diagnosis.md) shows fragmentation close
to the local source before verification. Do not relabel the old comparison or
use verification-controlled motion as independent pre-detection truth. A paired
shadow replay on identical uninterrupted development SEARCH trajectories is a
candidate, not yet adopted or implemented. V9 B's retained state summary confirms
SEARCH until its shutdown at360.9s; older B and Q1 discovery are possible separate
strata, while Q1/Q2 confirmation evidence stays sealed. Exact PDE transport history
and confirmation gates must be reused, not replaced with centroid replay.

V2/full goal remains IN_PROGRESS. Branchfeature/gesc-gaussian-robustness-v2 at
3369cfc; all task changes remain uncommitted. No physical/Pi/snapshot/V1,
commit or push action occurred. Source and helpers are held after this milestone.
