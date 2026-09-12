# Visible03: completed analysis and fixed direction references

DEVELOPMENT_ANALYSIS_COMPLETE, 2026-09-10. Native analysis completed with a VALID
typed moving lifecycle and zero errors. The separately released reference job
passes the existing direction component thresholds on4 eligible exposed targets.
Both jobs are terminal/reaped and source/input integrity passes. This is selected
development evidence, not broad qualification or release of the16-run comparison.

The original03 acquisition verdict remains FAIL solely at its selected
`escape_command_ownership` predicate, whose recorded reason is "direct measured
fill-to-exit alignment is below 0.80". Stage A and post-recovery global arrival
both PASS. Successful arrival does not rewrite that original combined verdict.
Root/direction own the separate diagnosis of path alignment versus command
ownership. No source correction or gate change occurs in this analysis.

Authority: [03 prospective plan](../r3_visible_analysis_03_plan.md), reusing the
[generic prepared analysis contract](../r3_visible_analysis_01_plan.md). Root
released analysis only after terminal acquisition, COMPLETE recording, stable
212 acquisition pins and successful inner/outer cleanup.

## Exact jobs and identity

Input run directory:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_03/runs/2026-09-10/v2_method_development_D_20260910_03`.
Output roots are the attempt parent's new exclusive `analysis_v1/` and
`direction_reference_v1/`. Helpers remain under01 as preparation lineage;
actual metadata, input, output and receipt identity are03.

Four preparation pins and absent output/log were verified before dispatch.
Analysis ran exactly:

```bash
set -o noclobber
timeout --signal=INT --kill-after=2s 118s env -u PYTHONPATH bash -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/centered_runtime_v2/environment.sh; export PYTHONPATH=/home/mattb/dsim-lab/ros2_ws/src/ros_esc:$PYTHONPATH; export MPLBACKEND=Agg; exec python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_01/analysis/run_analysis.py --run-directory /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_03/runs/2026-09-10/v2_method_development_D_20260910_03 --output-root /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_03/analysis_v1 --expected-run-id v2_method_development_D_20260910_03' > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_03/analysis_execution_v1.log 2>&1
```

PTY58738 exited0/reaped, ANALYSIS_RETAINED in57.958212895s, under110s internal
and118+2s outer limits. Native `analysis.read_run_bag` took10.304562806s; the
unchanged analyzer-owned `validate_run._read_bag` took9.567219236s. Exactly two
decoded scans and one captured BagData occurred. Byte hashes are separate from
decoder scans. Supplemental exports cost1.659400537s and input normalization
10.259533059s. These additions are included in56.050382060s analyze_run wall
time and are not attributed to the native analyzer alone.

All54 emitted artifact hashes and28 selected source/input pins independently
verified; current_acquisition_source_changes=[], source_inputs_stable=true,
errors[]. Receipt SHA256:
`be170a728722a03afffced269961f076eb14b0830020c48c9a31a355fbe9b7a0`.
No extra bag read, source edit, replaced reader, bypassed validator or retry.

After root reviewed that integrity and released the separate reference job:

```bash
set -o noclobber
timeout --signal=INT --kill-after=2s 43s env -u PYTHONPATH bash -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/centered_runtime_v2/environment.sh; export PYTHONPATH=/home/mattb/dsim-lab/ros2_ws/src/ros_esc:$PYTHONPATH; export MPLBACKEND=Agg; exec python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_01/analysis/run_direction_reference.py --analysis-root /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_03/analysis_v1 --output-root /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_03/direction_reference_v1' > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_03/direction_reference_execution_v1.log 2>&1
```

PTY26499 exited0/reaped, REFERENCE_RETAINED in5.765196414s, under38s internal
and43+2s outer limits. It read only normalized/binding artifacts and selected
reference source/configuration, with no bag scan. All26 artifact hashes and12
source/input pins independently verified. Each of24 target outputs was saved
through the existing evaluator callback before the final summary.

## Detector and lifecycle evidence

Existing lifecycle status `valid`, errors[]. One confirmation, candidate
snapshot, preparation, prepared result and committed fill; two valid SEARCH
epochs. Numerical candidate source support ends78s and publication/acceptance
is78.1s. The actual admitted pose stamp is78.009s. The full diagnostic records:

- circle30s model history48-78s; persistence starts36s, count3;
- center(1.051500535,1.107993902)m;
- estimated center drift.000894413m/s; actual support radius.326393657m.

Collection is admitted84.6s. Snapshot93.5s is15.4s after candidate acceptance;
raw evidence covers85.428275181-93.308875468s with3 verification revolutions and
0 pretrigger revolutions. Cycle minima are[-.028568534,-.027803774,-.027452316],
candidate estimate-.027803774, MAD.000351458, lower/upper
[-.028858148,-.026749399]. Prepare93.5s, commit93.9s, first objective and
direction acknowledgement94.0s, escape-entry event94.1s, stable direct escape
exit/new SEARCH epoch115.4s. These are recorded source/publication joins, not
reconstructed callback receipt times or independent basin-entry labels.

The actual path is SEARCH→VERIFY→DESIGN→ESCAPE_REPULSE→SEARCH; no ESCAPE_ASSIST
is observed. The native analyzer counts1 successful state-based escape and0
failed escapes. The run's stricter combined predicate separately retains its
direct geometric alignment failure. Its record has1052 nonzero GESC controls,
426 repulse state/supervisor-command samples and364 mature radial-progress
samples; minimum mature progress.111564268m exceeds its.05m progress limit.
Those partial passed checks do not waive its failed alignment check.

The original scenario result has Stage A associationPASS and post-recovery
arrivalPASS, observing position(3.741228820,3.063644273)m at distance.498595692m
from declared global point(3.5,3.5)m inside the fixed.5m tolerance. Root's live
arrival-stop record gives ROS155.971s. No ranked goal or GOAL_HOLD is required
by the user. The unchanged analyzer's separate aggregate-target distance and
simulation_ground_truth_success remain unavailable because that legacy metric
expects an aggregate-target/tolerance binding; do not replace this result with
an invented analyzer success.

## Full timelines and actual commands

Closed typed exports retain3705 recurrent diagnostics,3131 guidance messages,
3132 state/epoch messages,8494 actual commands/control messages,16 events,
1 confirmation/snapshot and3 fill commands/results. Canonical payload encoding
explicitly uses integer-nanosecond Times and null inapplicable nonfinite values.

The event stream records actual candidate acceptance, collection admission,
local-fill decision, activation and stable direct exit; there is no verification
or fill rejection event. Explicit-stop SEARCH→FAILSAFE events at156.1s are
preserved outside the readiness interval. Full reset, fit rejection, guidance
and transition reasons remain in `recorded_reasons.jsonl` and their typed
streams; no missing callback reason is invented.

Descriptive exact-zero counts use the latest causal valid AlgorithmState bag
receipt within.5 wall seconds, not reconstructed controller callback ordering:

|State|Actual command records|Exact zero records|Zero fraction|
| --- | ---: | ---: | ---: |
|SEARCH|5719|0|0|
|VERIFY_EXTREMUM|939|180|.191693291|
|DESIGN_OR_MERGE_FILL|36|9|.25|
|ESCAPE_REPULSE|1052|0|0|

These counts describe all6 recorded Twist components, not inferred wheel
actuation or time fraction. They do not support an assertion that verification
and design remain in motion on every callback.

## Fixed direction-reference population

Input normalization is qualified:4595 observations,4497 readiness eligible,
0 integrity errors,3124 exact duplicate publications removed,6 diagnostics
skipped for no synchronized observation. Time origin3.005s; last retained
source156.481s; no GOAL_HOLD terminal censor. Source/config binding uses actual
selected cost, sensor transform and captured robot geometry. Complete recorded
augmented objectives are retained; reference truth is evaluator-only.

All24 fixed targets at15+30k seconds are reported. Five are exposed and input/
reference qualified/informative; four are eligible, paired and use averaging.
Nineteen are unexposed. Target4 occurs in valid ESCAPE_REPULSE/filter_state4
with blend_allowed=false, so it is excluded from the eligible error denominator.

|Target offset|Eligible|Recorded output error|Aligned instantaneous error|
| --- | --- | ---: | ---: |
|15s|yes|2.622617deg|47.779403deg|
|45s|yes|27.746008deg|74.871141deg|
|75s|yes|5.363562deg|62.952744deg|
|105s|no|51.240660deg|51.240660deg|
|135s|yes|5.285294deg|40.094927deg|

The native component result is PASS: eligible median5.324428320deg,
p9021.031274378deg, averaging availability1.0, median paired improvement
46.140959554deg;4 improved and0 degraded. The small exposed denominator and
selected development setting limit generalization. This comparator is the
recorded aligned instantaneous vector, not reconstruction of a historical
controller. The observed-phase reference does not feed runtime.

Reference result SHA256:
`8354b8f0166ea3c907d267b92caaea94a2b135cba680fcab281d34a96d299f3a`.
Reference receipt SHA256:
`48e604a99c4470f406a4fab67b6887071266b35339dd5eae03d51caa0a7b8244`.
Both wrappers remain DEVELOPMENT_ONLY, historical_experiment_membership=false,
with the unchanged m4-pilot-v1 normalization/reference protocol named honestly.
No failed prior run, gate, label or outcome is rewritten. Root owns acquisition
validation, status/handoff/checkpoint and any next release.
