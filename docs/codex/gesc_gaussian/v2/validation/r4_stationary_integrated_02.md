# Stationary recurrent development02 — acquisition and analysis PASS

Selected development evidence, 2026-09-10, under
[the02 acquisition plan](../r4_stationary_integrated_02_plan.md) and
[the analysis invocation amendment](../r4_stationary_analysis_02_plan.md).
This establishes the missing recurrent/stationary pairing on exposed nominal
geometry. It does not establish the four-arm comparison or broad robustness.

## Acquisition and observed behavior

Case/run `v2_method_development_B_20260910_02`, seed26091003. External root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_integrated_02/`.
Run directory `runs/2026-09-10/v2_method_development_B_20260910_02/` under that root.

The recurrent detector, stationary verification, Gaussian parameters and nominal
geometry are unchanged from the01 preparation. The corrected runtime environment
uses complete Q5 installed entry-point metadata and its symlink to current
canonical source. The existing checker bound all21 console entries; real
scenario/recorder `--help` exited0 in0.966/0.515 s, total check2.861 s. New request
types still resolve to the new interface overlay. Original01 failure/env remain.
No source metadata cleanup or numerical retuning was performed.

Preparation resolved actual schema/launch/recording selection and froze284
source/scenario/interface/installed metadata/helper paths in2.584 s. Visible
acquisition used domain201, localhost only and existing subreaper_group_v3
ownership with180/120s simulated stages and420s root cap. Root session43518
is terminal/reaped after219.483315 s; all284 pins stable. Recording COMPLETE,
all required predicates PASS, inner and outer strict owned cleanup PASS.
No Gazebo/test/analysis process remains active after the completed work below.

| Observation | Selected ROS simulated time / measurement |
| --- | --- |
| Circle confirmation | Support72–102s; persistence began60s; count3/3; publication/admission102.1s |
| Actual latest detector pose | 102.016s, retained separately from102s model endpoint |
| Candidate center and motion | (1.174995,1.237388)m; drift0.002818834m/s; confinement0.370541m |
| VERIFY_EXTREMUM | Entered102.2s; three candidate cost rotations |
| Stationary request / DESIGN | 111.2s, retaining original102.1s receipt/admission;9.1s observed interval |
| Unique active fill | 111.3s; id/cluster/revision1; center(0.901703,1.044252)m |
| Repulsion / assisted escape | REPULSE111.4s; ASSIST114.5s; restored SEARCH131.8s |
| Live Stage A completion pose | 131.834s |
| First post-recovery global arrival | **172.634s**, distance**0.499270m**; actual pose(3.620107,3.015392)m |
| Final recorded evaluation pose | (3.625427,3.036353)m; distance0.480313m |

Live and retained evaluators agree on the same arrival pose; no interpolation,
GOAL_HOLD or second ranking was required. The nominal controller-goal diagnostic
remains false because no GOAL_REACHED occurred, and correctly does not gate this
selected arrival result. Every required predicate, including local fill,
cardinality, command ownership, post-recovery arrival and cleanup, passed.
Assisted ownership checked2237 fresh suppressed-GESC/owned-command samples,
returned ordinary GESC over5310 post-exit samples, and retained entry/exit handoff
delays0.008898/0.007298 s. Measured exit distance1.466384m and alignment0.997955;
alignment remains reported independently under the selected arrival criterion.

The native CSVs confirm the intended stationary baseline: all1524 VERIFY and
35 DESIGN final vehicle commands are zero in their selected state intervals.
Measured translational speed medians are0.000711/0.000691m/s, with maximum
VERIFY speed0.004252m/s including its boundary/coasting samples. This is the
stationary comparison arm; the earlier D cases establish continuous verification.
`stationary_motion_assessment.json` retains interval definitions, counts and
input CSV hashes. The native trajectory plot was visually inspected and shows
local circling, escape and the approach to the global source.

Exact acquisition command:

```sh
timeout --signal=INT --kill-after=5s 420s env -u PYTHONPATH ROS_DOMAIN_ID=201 ROS_LOCALHOST_ONLY=1 DISPLAY=:0 bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh; exec python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_integrated_02/run_attempt.py' > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_integrated_02/root_execution.log 2>&1
```

## Complete native analysis

One analysis invocation completed in**43.390555s** within120s. Root24153 is
terminal/reaped, exit0. Exactly two native decoder scans completed:
`analysis.read_run_bag`16.596647s and `validate_run._read_bag`15.027641s. No third
decode, moving normalization or reference job was performed. Native before/after
bag hashes and124 source/input pins stayed stable; no production analysis owner
changed since acquisition. Original helper stays pinned/unexecuted; v2 adds only
console/notes input hashes and its prospective amendment pin.

Both stored and fresh recording validation pass; native analysis status is
`complete`; stationary recurrent pipeline is `valid`, errors0. Native tables
contain1 confirmation,1 request,2 outcomes and2 timing intervals, with exact
diagnostic/request/fill/event joins. Twenty-nine artifacts are inventoried,
including9 native plots. Zero missing/retried/unterminated request outcomes.

```sh
timeout --signal=INT --kill-after=2s 118s env -u PYTHONPATH bash --noprofile --norc -c 'source /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_recurrent_pairing_v1/runtime_environment_v2.sh; exec python3 /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_integrated_02/analysis/run_analysis_v2.py --run-directory /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_integrated_02/runs/2026-09-10/v2_method_development_B_20260910_02 --output-root /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_integrated_02/analysis_v1' > /home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/stationary_integrated_02/analysis/analysis_v1.execution.log 2>&1
```

Receipt SHA256s:

- `prepared.json`: `2821aad5a92ca1eaf933a6d2293a8e5640552e16f1f2a6e8e0c5f383279de1f7`.
- `attempt_result.json`: `1742f76d05d3f23a65ec7e389de2dc1e113a1c7a8fd6572d13deb88e887d22eb`.
- `analysis_v1/receipt.json`: `ecd61297471e4c55d74ec821e4c3608095bb3e5b03558fadcf6fb2cf404adcb4`.
- `analysis_v1/analyzer/summary_metrics.json`: `514744649c482cd03eec99cc5587d18bb9c44a587dfd5b9bf93f047fd952fc85`.
- `stationary_motion_assessment.json`: `3c5e83131cff8400cb2d6ea67e25982dc76e92d6180533a653d4c81128b43937`.

No additional simulation is needed solely to improve this result's label.
Preserve01 and all older failures. Broader comparison, fresh confirmation,
paired detector latency and arbitrary-field direction reliability remain open.
Branch V2, HEAD3369cfc; source uncommitted. No physical/Pi/snapshot/V1 work.

Independent read-only review matched all five published hashes, receipt outcomes,
row/artifact counts and the exact helper amendment. Arrival and final distance
come from the retained scenario evaluator; native `convergence_time` is
`not_applicable` and `final_aggregate_target_distance` is `unavailable`.
