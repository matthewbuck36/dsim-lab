# R2 static correction after combined-model failure

ADOPTED 2026-09-10 prospectively before this finite calibration. The initial
runtime core failed one independent translating oscillation (P66s, phase.37,
amplitude.25m, translation.02m/s): static12 admitted at12s with measured
radius.026246882m and drift.001383909m/s. Retain that failure under
`development/20260910/recurrent_runtime_v1/initial_core_result.json`.
Circle/oscillation methods and all previous evidence remain unchanged.

Evaluate exactly two static alternatives:30s support, maximum radius .03m or
.04m, weighted linear drift<=.005m/s, one completed support, causal6s endpoints.
All original vertices/exact bracketed boundaries and source-gap<=.5s apply.
For a1D sinusoid of amplitude<=.25m translating at>=.02m/s, net30s displacement
is at least .60-.50=.10m; any enclosing radius is therefore>=.05m. Both candidate
radius bounds exclude this bounded family independent of period/phase. This
argument is model-specific and does not prove rejection of arbitrary motion.
The larger fixed radius is motivated by the already retained sigma.01m static
control; select the smaller candidate only if every static positive detects
and every declared negative rejects. No positive relabeling or threshold search.

Population: all99 retained arc controls (exact recorded samples), all96 retained
oscillation-v2 controls (same deterministic fixture generation, seed26091011;
execute only the saved fixture-construction AST, no prior measurement code),
the newP66/.37/.02 failure, and32 independent negatives: amplitude.25m translating
oscillations P54/60/66/72, phases k*pi/4 for k0..7, drift.02m/s, all120s atdt.1s.
Total228 family rows,159 negatives,4 static-positive rows (three unique fixtures;
noisy sigma.002/.01 remain in denominator),65 other/gray/out-of-scope rows.
Retain overlapping R1 rows under separate family IDs; do not inflate unique
fixture claims. Oscillations/circles remain outside this static component's
positive sensitivity denominator, but declared negatives must all reject.

Job directory `development/20260910/static_correction_v1/` external V2 root.
One118s SIGINT timeout with2s kill-after;110s internal limit. Save helper/plan/
selected source+fixture hashes before dispatch; use current pure support/model
owner for geometry and linear fit (static width30 passed explicitly). Save all
228 contracts, original source references, every support radius/drift/pass for
both fixed choices, first candidates, negatives/misses, elapsed time and hashes.
No unchanged numerical retry. This job precedes any runtime constant change.
If neither choice meets all static sensitivity/negative requirements, retain
failure and do not nominate the combined runtime. No simulation/bag/model or
holdout use. Existing runtime transport/source checks can continue independently.
