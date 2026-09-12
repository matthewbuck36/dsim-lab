# R3 attempt02: completed analysis and direction evidence

DEVELOPMENT_ANALYSIS_COMPLETE, 2026-09-10. The existing single-run analyzer
completed with `analysis_status=complete`; its typed moving lifecycle is
`valid`, with zero errors. The separately released direction-reference job
passes its existing component thresholds on5 eligible exposed targets. Both
jobs are terminal/reaped; no source was edited and no bag was read by the
reference job. These are selected development results, not untouched holdouts.

Authority: [prepared analysis plan](../r3_visible_analysis_01_plan.md), including
its prospective two-native-scan and fresh-attempt amendments. The acquisition
owner supplied terminal readiness/completeness/cleanup evidence before release.
Attempt01's pre-readiness startup failure remains retained and unanalyzed.

## Exact jobs and identity

Run directory:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_02/runs/2026-09-10/v2_method_development_D_20260910_02`.
Output roots are its attempt parent's `analysis_v1/` and
`direction_reference_v1/`, both newly exclusive at dispatch. Prepared helpers
remain at `visible_integrated_01/analysis/`; their location records preparation
lineage, not the analyzed run's identity.

The analysis command used `env -u PYTHONPATH bash -c`, sourced
`development/20260910/centered_runtime_v2/environment.sh`, prepended
`/home/mattb/dsim-lab/ros2_ws/src/ros_esc` to PYTHONPATH, set MPLBACKEND=Agg and
executed:

```bash
set -o noclobber
timeout --signal=INT --kill-after=2s 118s env -u PYTHONPATH bash -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/centered_runtime_v2/environment.sh; export PYTHONPATH=/home/mattb/dsim-lab/ros2_ws/src/ros_esc:$PYTHONPATH; export MPLBACKEND=Agg; exec python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_01/analysis/run_analysis.py --run-directory /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_02/runs/2026-09-10/v2_method_development_D_20260910_02 --output-root /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_02/analysis_v1 --expected-run-id v2_method_development_D_20260910_02' > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_02/analysis_execution_v1.log 2>&1
```

The literal invocation and environment are recorded above;
`started.json` retains Python argv. Terminal0, `ANALYSIS_RETAINED`,71.973982530s,
within the110s internal/120s outer budget. Two existing native decoder scans
were observed unchanged: `analysis.read_run_bag`12.539270835s and fresh
`validate_run._read_bag`11.327201364s. No third scan occurred. Supplementary
exports cost1.994435229s; input normalization12.838270979s. These side effects
are included in the69.891962781s analyze_run wall measurement, not attributed
to the native analyzer alone. Ordinary byte-hash reads are distinct from these
two ROS decoder scans.

All54 emitted artifact hashes and28 selected source/input pins verified after
completion, with no acquisition-source changes. Analyzer freshness/completeness
checks were not replaced or bypassed. Receipt SHA256:
`f357e80b6bdaf23f1f1d72a954d1a343e703c5b2b46609509603f116ec6e3394`.
Log: `visible_integrated_02/analysis_execution_v1.log`.

## Detector, verification, fill and escape observations

Existing lifecycle verdict: **valid**, errors[]. Audit counts:1 confirmation,
1 candidate snapshot,1 preparation,1 prepared result,1 unique fill commit,
2 valid SEARCH epochs. Existing analyzer reports1 successful escape and0 failed
escapes. The terminal valid state is SEARCH; no GOAL_HOLD was observed.

The detector's confirming diagnostic uses the circle30s branch:

- model history48–78s; persistence history starts36s, count3;
- actual admitted pose source78.008s; model end/typed confirmation source78s;
  diagnostic/typed publication78.1s;
- estimated center(1.055385169,1.086221225)m, drift.002768034m/s,
  actual support confinement.317670982m.

Candidate acceptance78.1s; collection admission84.7s; snapshot92.3s,
14.2s after acceptance. The retained raw-cycle evidence spans84.253671024–
92.176873594s and has3 verification revolutions,0 pretrigger revolutions.
Raw minima are[-.028767652,-.028223953,-.026889546]; estimate-.028223953,
MAD.000543699, bounds[-.029855049,-.026592856]. Fill commit92.7s is.4s after
prepare; first objective and direction acknowledgement both92.8s. New SEARCH
epoch begins112.8s. These are existing source/publication joins, not reconstructed
subscriber callback receipt times or an independently labeled basin-entry latency.

The full canonical typed exports retain4527 recurrent diagnostics,3615 guidance
messages,3616 states and epoch contexts,9419 actual commands and control
diagnostics,18 algorithm events,1 typed confirmation/snapshot,3 fill commands
and3 fill results. ROS Times are explicitly encoded as integer nanoseconds;
inapplicable nonfinite fields become null via the existing canonical serializer.
`recorded_reasons.jsonl` and complete event/state/guidance/model records retain
all actual rejection/reset/detail text. Missing unrecorded reasons are not inferred.
The event stream records collection admission at84.7s and the counted-candidate
local-fill decision at92.3s, with no verification-rejection or fill-rejection
event. At95.9s it explicitly records radial progress below threshold and bounded
outward assist;112.8s records stable assisted escape exit. The explicit-stop
SEARCH-to-FAILSAFE/event at180.3s is retained outside the readiness interval,
explaining why in-readiness analyzer failure/timeout metrics do not count it.

## Actual final command observations

Descriptive grouping uses the latest causal valid AlgorithmState bag receipt
within.5 wall seconds; it does not assert controller callback ordering. Exact
all6-component `/cmd_vel` zeros are counted, not small commanded speeds or motor
actuation. Each command and state skew remains in `actual_command_by_state.jsonl`.

| State | Commands | Exact zeros | Zero fraction |
| --- | ---: | ---: | ---: |
| SEARCH | 7107 | 0 | 0 |
| VERIFY_EXTREMUM | 871 | 171 | .196326 |
| DESIGN_OR_MERGE_FILL | 38 | 11 | .289474 |
| ESCAPE_REPULSE | 148 | 0 | 0 |
| ESCAPE_ASSIST | 835 | 2 | .002395 |

These counts require the separate centered-guidance diagnosis before attributing
zeros to intentional stopping, missing companions or publication ordering. They
are not silently classified as continuous successful movement.

## Normalized inputs and released reference job

The existing augmented input owner qualified5312 observations,5247 within
readiness, with zero integrity errors and3610 exact repeated publications
removed. Four unsynchronized diagnostics remain explicitly counted as skipped.
The cap is40000 with no truncation. Complete recorded augmented objective
snapshots are retained, including interventions; source truth is evaluation-only.

The schema1 development wrapper explicitly identifies the actual fresh run and
`historical_experiment_membership=false`. The embedded `m4-pilot-v1` is the reused
normalization/reference protocol, not membership of historical M4. All24 fixed
offsets remain15+30k seconds:6 exposed,18 unexposed. First observed input origin
is1.712s. No result was promoted into a historical trial or holdout denominator.

After input/artifact/source verification and root release, D3 deferred its cached
job to avoid CPU overlap. Under the same overlay/PYTHONPATH/Agg environment:

```bash
set -o noclobber
timeout --signal=INT --kill-after=2s 43s env -u PYTHONPATH bash -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/centered_runtime_v2/environment.sh; export PYTHONPATH=/home/mattb/dsim-lab/ros2_ws/src/ros_esc:$PYTHONPATH; export MPLBACKEND=Agg; exec python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_01/analysis/run_direction_reference.py --analysis-root /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_02/analysis_v1 --output-root /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_02/direction_reference_v1' > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_02/direction_reference_execution_v1.log 2>&1
```

Terminal0, `REFERENCE_RETAINED`,6.761737705s within38s internal/45s outer. The
existing metric owner and actual selected cost/sensor/captured geometry produced
all24 per-target files, preserving unexposed targets. All26 output hashes and12
source/input/configuration pins verified. No new bag scan or target selection.

Six exposed targets are input/reference-qualified and informative. Target4 at
105s offset is retained but ineligible because its filter state is ESCAPE_ASSIST
and blending is not allowed. The five remaining targets are all SEARCH and all
have usable output/averaging. Thus the existing summary uses5 eligible targets,
not6 or24: median error12.307073512deg, p9034.940352791deg, averaging availability
1.0. All5 improve over their aligned instantaneous counterpart; median paired
improvement14.208664440deg,0 degraded. The existing component summary is PASS.

| Target / offset | Eligible | Output error | Instantaneous error |
| --- | --- | ---: | ---: |
| 1 / 15s | yes | 5.047951deg | 11.978948deg |
| 2 / 45s | yes | 34.859098deg | 71.486147deg |
| 3 / 75s | yes | 6.374746deg | 19.532147deg |
| 4 / 105s | no, ESCAPE_ASSIST | 19.975271deg | 19.975271deg |
| 5 / 135s | yes | 12.307074deg | 26.515738deg |
| 6 / 165s | yes | 34.994522deg | 74.714087deg |

Reference result SHA256:
`5dc3f91f9765edad35b64754d86dec1896d596098560996fea992108c65cde12`;
receipt `03bd2d3eb063c5b1c6a40521d433ea5e225c84e11fb0181dd23b35a53c2c32d2`.
Log: `visible_integrated_02/direction_reference_execution_v1.log`.

## Arrival criterion and historical limits

During analysis the user clarified that reaching the global minimum is the
success criterion; GOAL_HOLD is not required. Both dispatched analysis jobs
preserved their frozen functions, inputs and original monitor record. The
separate root arrival assessment uses the existing.5m declared global-proximity
tolerance and actual runner/pose evidence; it must not be replaced by the
analyzer's `complete` integrity status. This analyzer's aggregate-target distance
and simulation-ground-truth-success fields are unavailable for this scenario's
`declared_global_proximity` configuration, while terminal SEARCH and its raw
metrics remain recorded honestly. The earlier Stage A monitor failure remains
historical evidence to explain, not an erased result. Root owns the explicit
arrival-only amendment, integrated conclusion and material checkpoint.
