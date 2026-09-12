# Prospective qualification and pilot release review

**PROPOSAL — no study selected or run by this review.** Read-only assessment on
2026-09-09 UTC while the parent task closes M3. This document changes no source,
threshold, label, grid, status, experiment release, or old evidence.

The smallest coherent next step is a **separate four-run primary-geometry
qualification study**, followed by one frozen confirmation analysis. Use fresh
source-correct observations to address both the detector's missing positive
exposure and direction's missing reference inputs. Do not spend more time trying
to recover acquisition provenance from the eight rejected historical bags.
Do not require M4's own holdout results before permitting M4 to test them.

## What is and is not unresolved

| Item | Existing result | Evidence still needed |
| --- | --- | --- |
| Detector numerical implementation | Implemented and tested; original and M1a finite calibrations remain failed, with no setting selected | A prospectively nominated setting must detect independently labeled, sufficiently long natural residence, with no declared-negative detections |
| Historical positive exposure | Seven12.070–34.136s residence intervals; zero54s common opportunities | New uninterrupted positive exposure; missing exposure cannot become measured zero sensitivity or a pass |
| M3 neighborhood | Explicit positive R/epsilon required; synthetic fixtures test correctness | Empirical candidate-centered position, cycle-centroid and sector-trajectory support under a frozen neighborhood choice |
| Direction implementation | Source-clock correction and bounded typed transport validated | Source-correct same-trajectory reference inputs, informative denominators, angular errors, availability and fallback/lag measurements |
| Historical direction reference | Version v1 closed EVIDENCE_UNAVAILABLE;8 rejected inputs and192 missing anchors | A fresh population with actual typed provenance; never rename or replace the closed192-slot population |
| Moving lifecycle | M3 implementation/transport/recording checks being closed by the parent | M3 handoff/checkpoint before a new study; real field behavior remains an empirical question |
| Pilot | Approved four development plus twelve holdout runs, not dispatched | Frozen qualification outcome and selected configuration, then an explicit recorded release of the existing pilot |

These distinctions follow [plan.md](plan.md),
[m1_to_m2_sequencing.md](m1_to_m2_sequencing.md),
[m1a_calibration.md](validation/m1a_calibration.md),
[m2_handoff.md](m2_handoff.md), and
[m2_reference_v1.md](validation/m2_reference_v1.md).

The historical54s criterion compared W=3/6/9 on common support. It is not a
universal detector requirement: the numerical history floors are18/36/54s.
Retrospectively shortening the old denominator is prohibited and would not
rescue M1a: every W=3 candidate failed the synthetic population and its longest
retained positive was shorter than36s. A new single-W study can prospectively
use that W's actual timing support and preserve all older failures.

## Proposed finite nomination before new data

Nominate **W=6s and detector score epsilon=0.30m** before acquisition. This is
an experimental nominee, not a selected or calibrated runtime default. The
existing analytic diagnosis bounds the declared small-circle score by
0.272229375505m and translating-circle score by at least0.542629797669m at W=6.
The nominee therefore has a reason independent of new detector outputs and
requires36s of numerical history. Its straight-drift resolution is
0.30/(5*6)=0.01m/s; this does not promise rejection of all slow drift.
See [m1a_plan.md](m1a_plan.md) and
[m1_centroid_grid_diagnosis.md](validation/m1_centroid_grid_diagnosis.md).

Freeze a small, explicitly new joint neighborhood comparison on discovery data:

- detector confinement R and M3 candidate radius use the same member of
  `{0.25,0.50,0.75}m`;
- M3 per-cycle centroid/sector tolerance uses one of `{0.05,0.10,0.15}m`;
- W, detector score epsilon, raw-profile information rule, MAD scale, direction
  blend/confidence rules, clocks, sensor geometry, gains and velocity ceilings
  are fixed. These nine neighborhood pairs are finite development candidates,
  not new claims about physical calibration.

The detector's sum-of-five-distances epsilon and M3's per-cycle/sector tolerance
have different meanings. Copying0.30m into both parameters would not calibrate
the latter. Evaluate the existing moving-evidence owner on each frozen candidate
center and its latest three qualifying cycles; do not substitute label-region
centers or choose older cycles for a favorable result. Choose the smallest R,
then smallest M3 tolerance among pairs satisfying every discovery requirement.
If none succeeds, retain a failed fresh version and do not inspect confirmation
data to choose a replacement. Preserve the original36-setting tables untouched.

## Four fresh observation runs, outside the sixteen-run pilot

Use the inherited **primary** field and exact selected model/sensor binding.
Keep the secondary pilot geometry and pilot seeds26090801–26090804 untouched.
This preserves the planned holdout's role; extending the earlier eight-run
option across secondary geometry is unnecessary for initial release.

| Partition | Role | Proposed fresh seed | Input-only start rule |
| --- | --- | ---: | --- |
| Discovery | Residence exposure | 26090911 | Interior of the independently qualified local enclosure, maximum boundary clearance with a fixed lexicographic tie rule |
| Discovery | Directed approach exposure | 26090912 | A predeclared collision-free approach outside all conservative exclusion masks, selected from geometry before trajectories |
| Confirmation | Residence exposure | 26090913 | A second interior start chosen by a predeclared opposite-side/farthest-point rule within the same accepted component |
| Confirmation | Directed approach exposure | 26090914 | A second predeclared approach direction outside the masks |

These seeds are proposals: the execution manifest must first verify they have
not been used, resolve exact XY/yaw values and record the deterministic rules.
No start is chosen from detector flags, observed settling or candidate outcomes.
Obstacle clearance and robot footprint must be checked with the existing
scenario geometry. If a required start cannot be defined, close that plan as
unavailable before running; do not improvise a favorable start after a failure.

Reuse existing qualified enclosure receipts only after exact source/model,
sensor geometry, bounds and full receipt-chain hashes match the new scenario.
Otherwise the same independent finite enclosure procedure needs a separately
bounded pre-acquisition computation. Preserve all holes, mixed cells,
segment-boundary uncertainty and possible-well exclusions. No new field is
designed merely to create a passing orbit.

Each run is proposed for120s of simulated observation after recording readiness,
with240s wall cap and a1200s total acquisition ceiling including bounded cleanup.
Use the existing runner, launch, source, controller and recorder. The first run
is visible, consistent with the development workflow. The study is one finite
four-run version, not “run until a long residence appears.” Safety/completeness/
cleanup failure stops dispatch; behavioral/exposure failure stays a result.

A small opt-in observation policy in the existing supervisor would suppress
detector-triggered VERIFY/fill/escape/GOAL transitions during this study while
retaining every safety stop. It must be reviewed, tested and recorded before any
Gazebo launch. Do not create another controller, command publisher or recorder.
Use the source-correct continuous graph to obtain actual M2 metadata; its moving
GESC trajectory is allowed to evolve naturally. State explicitly that this is
the continuous graph's trajectory, not an inherited-controller trajectory.
The inherited detector and new detector can be assessed in shadow/offline on
the same captured pose input without affecting the path. Neither holding the
robot in a basin nor suppressing a safety stop is permitted.

Only the two discovery bags are opened for parameter selection. Hash and seal
confirmation bags; freeze one selected joint configuration and its complete
analysis contract before opening them. Fixed run order, exact caps, defaults,
streams, scenarios, parameters, code/IDL hashes and exclusive artifact paths
belong in a new machine-readable contract and a pre-experiment checkpoint.

## Exposure and detector/neighborhood gate

Retain the input-only spatial definitions: continuous basin residence starts
at the first qualified in-region sample and must last at least12s; boundary
touches, holes, invalid inputs and excessive gaps interrupt it. Directed
negative progress is the exact six-second segment chain outside all qualified
possible-well masks, net travel>=0.12m and net/path ratio>=0.80. Unknown remains
unknown. Freeze spatial intervals before applying readiness/SEARCH masks or
evaluating any detector output.

For this proposed W=6-only study, require an independently labeled residence
opportunity with **42s uninterrupted eligible source support** in each residence
run. Six windows require36s; up to one extra6s allows the epoch's window lattice
to fall out of phase with basin entry. This is a prospective sufficient
observation opportunity, not a claim that42s is intrinsic latency, nor a
revision of the old54s population. Shorter genuine episodes remain censored;
do not join them or replace the first genuine opportunity within one observed
SEARCH epoch with a later favorable residence. A short first opportunity can
therefore make this finite run unavailable, honestly.

Before release require all of the following for the single nominated setting:

1. At least one uncensored first residence opportunity in **each** residence
   partition, with a detection during that residence. Missing exposure is
   EVIDENCE_UNAVAILABLE, not detector failure or success.
2. At least one independently labeled six-second progress interval in each
   approach partition and zero flags in every declared-negative interval.
   Report every positive, negative, unknown and censored output. Do not infer
   false-positive rates from quiet unlabeled time.
3. The frozen neighborhood pair supports the actual candidate-centered
   three-cycle verification within its original12s deadline for every required
   positive detection, preserving sector comparability and informative raw
   evidence. Negative/constant/noise safeguards remain the tested M3 contract;
   shadow acquisition does not measure real erroneous-fill incidence.
4. Confirmation data pass the same requirements without parameter changes.
   The final nomination and all denominators are recorded, independently of
   whether the expected latency improvement is already measurable.

Report matched inherited/new confirmation latency where both events are
observed. If the inherited event is censored, report the bound instead of
inventing a median. The>=30% latency improvement and absence of additional
erroneous fills/terminal decisions remain actual M4 acceptance outcomes; they
cannot be established merely by suppressing fill transitions in this study.

## Direction qualification on the same four inputs

Add a fresh typed-input adapter to the existing analyzer/reference owner, not a
new pipeline. Use actual `SourceSampleProvenance`, `SynchronizedObservation` and
`ObjectiveCostSample` schema2 source keys/objective configurations. Preserve
strict source-integrity quarantine and the complete acquisition/admission/
original-receipt distinction. Historical reconstruction proxies are unnecessary
for these new bags and cannot stand in for a missing new typed record.

Freeze twelve targets per run, T0+10k seconds for k=1..12, hence48 slots. Define
T0 by the first input-qualified synchronized source observation under fixed
identity/finite/alignment checks; confidence, averaging success and field
magnitude must not select it. Freeze target identities before method outputs
or field-reference calculations. Select the first qualified source observation
within50ms after each target; no replacements. End-of-run missing slots stay
missing. This fresh48-slot population never replaces the old192 missing slots.

Reuse [m2_reference_plan.md](m2_reference_plan.md)'s actual evaluator geometry,
signed world angular rate, continuous washout transfer function, independent
quadrature partitions/error limits and informative-reference floor. Match the
recorded augmented objective exactly, even when it happens to contain zero
active fills; do not silently substitute a raw reference. Compare inherited and
new filter responses on identical observations and anchors. Report translation,
rate variation, cadence sensitivity, angle errors, lag, fallback and confidence.
Constant-rate/reference failures remain unavailable, not permission to discard
the original CV<=0.10 rule or introduce nominal-phase references.

Propose at least six independently informative, input-covered reference anchors
in **each** confirmation bag, then require pooled confirmation median angular
error<=30deg, p90<=60deg and averaging availability>=80% over the complete
predeclared eligible denominator. Also report per-bag counts/results so one bag
cannot hide the other. Method weak vectors, disagreement and fallback remain
denominator outcomes. Empty or insufficient exposure cannot pass. This is
selected primary-field evidence, not broad angular accuracy or M4 holdout proof.

Cap the prospective reference analysis at one300s invocation and48 anchors;
retain per-anchor receipts, missing reasons and partial output on timeout.
Separately cap label/qualification analysis at600s. Freeze/source-test the typed
adapter before this job, and preserve an unsuccessful version without automatic
rerun, added anchors or changed numerical tolerance.

## Release decision and authorization boundary

The approved plan calls sixteen the **pilot size**, not a total lifetime cap on
necessary validation. It explicitly permits a documented bounded corrective
version after a failed gate. Under the user's authorized full implementation
task and repository autonomy rules, this finite prerequisite study can reasonably
be selected by the parent through an explicit amendment, source tests and a
checkpoint; it need not manufacture a new user permission step. This review
does not itself select or execute it. The older follow-up-options note likewise
did not authorize a launch merely by describing an option.

The parent must make the extra four-run/time cost visible and record its exact
release before starting. If a direct user instruction outside these reviewed
documents actually capped **all** new Gazebo executions at sixteen, that direct
limit takes precedence; a plan interpretation cannot expand it. No reviewed
document establishes that stricter total cap. Physical actions remain outside
scope regardless of simulation results.

Release the unchanged sixteen-run pilot only after: M3 closes with its required
transport/safety evidence; the source-correct study's integrity and cleanup pass;
the independent confirmation partition qualifies a frozen detector/neighborhood
and direction configuration; and the parent records the release/checkpoint and
unchanged four-arm matrix. Keep pilot development seed26090801, secondary seeds
26090802–26090804, disturbances, wall caps and holdout freeze exactly as approved.

If the four-run study lacks long natural residence or informative direction
anchors, close that study as unavailable. This is evidence about the chosen
study design, not proof of algorithm failure and not a permanent ban on the
user's goal. A later bounded proposal can diagnose the specific missing input
or reconsider an operational label in a **new** prospectively justified
contract. It cannot fill old annular holes, shorten old intervals, manufacture
positive exposure, retune from confirmation data or call synthetic correctness
scientific qualification. If actual component performance fails, preserve that
scientific failure and diagnose it before another version. Never conceal either
outcome by releasing M4 as if the gate passed.

The four-run design is a smallest coherent opportunity, not a promise that
natural trajectories supply its denominators. It preserves a finite route
forward and an honest failure route without turning a closed historical
comparison's missing exposure into an impossible permanent prerequisite.

## Concrete Q1 inputs and owner appendix — proposal only

This appendix resolves the proposed inputs from retained configuration and
qualified geometry receipts. It does not release or execute Q1. The read-only
work used file hashes, finite cell-mask geometry and source inspection; it did
not open bags, evaluate a field, replay trajectories or launch ROS/Gazebo.

### Primary field and immutable geometry

Use the field in
`ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/phase08_v8_10_primary_visible_probe.yaml`:
local source `(1.0606601717798214, 1.0606601717798212)` with400 relative lumen
input, global source `(3.5, 3.5)` with1600, declared evaluator bounds
`[-1, 5, -1, 5]`. Preserve these negative-cost model inputs; they are not
physical calibration. The selected model is
`ros2_ws/src/ros_esc/paper_recreations/heavy_ball_PDE_ESC/cost_function/multi_light_source_photoresistor.json`,
SHA256 `7a5f883e901070707bc37dc673bf27af6387fe650720fc0c84dca11767632741`.
Its current hash matches the qualified geometry input. Create a new Q1 scenario
identity rather than reuse the old suite's fill/escape/GOAL success criteria.
Acquisition completeness and the new qualification report are separate outcomes.

The matching retained group is
`/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_labels_v1/geometry_1.json`,
SHA256 `8f4f7fc53b67144317dd2e4640871c29ac5eb6c0d7e2cbc6ca3521a6c24788dd`.
Its recovery binding is retained in
`/home/mattb/Experiments/GESC-Gaussian/v2/replay/m1a_labels_v1_recovery1/labels.json`.
This group was selected by its exact sources/bounds/model/geometry inputs,
not by a favorable trajectory result. Both source enclosures are qualified.
The local mask has165 cells, area0.362548828125m², spacing0.046875m and grid
origin `(0.3106601717798214, 0.3106601717798212)`. Its enclosure identity is
`d96f364bb9e0638d26a60dcda839ec7850de7c47dd9b726d3833307cc9225583`.
The global mask has266 cells and enclosure identity
`40d19d8e93b7e412877f97f7c7bcbf7fc1a103806a1097771b0367c4831b38b8`.
Both retain their annular holes. The local area centroid
`(1.0914840354161846, 1.0914840354161846)` is a descriptor, not itself an
accepted positive start.

The2865 referenced primary point-receipt files under
`geometry_1_sources/source_1/` and `source_2/` were rehashed and matched their
stored references, without recalculating their field values. The current
`v2_enclosure.py`, `aggregate_field_truth.py`, model implementation,
`bag_reader.py`, robot URDF and sensor transform hashes match this group's
numerical provenance. The analyzer has since gained M2/M3 code; preserve its
original numerical-owner receipt and the existing recovery chain, and record
the new label/adapter owner separately. A Q1 loader must verify that chain and
the unchanged geometry-task body as the recovery owner already does; this
appendix does not replace that executable provenance check. See
[M1a calibration evidence](validation/m1a_calibration.md) for the original
qualification/recovery audit and closed unsuccessful calibration.

### Four deterministic starts

Coordinates below are proposed **world-frame spawn coordinates** in metres;
yaw is in radians. They were selected entirely from the frozen input geometry,
before any new trajectories or direction targets exist.

| Partition / exposure | Seed | x | y | yaw |
| --- | ---: | ---: | ---: | ---: |
| Discovery / residence | 26090911 | 0.8497226717798214 | 1.3184726717798212 | -0.8850668158886104 |
| Discovery / approach | 26090912 | 0 | 0 | 0.7853981633974482 |
| Confirmation / residence | 26090913 | 1.2715976717798214 | 0.8028476717798212 | 2.256525837701183 |
| Confirmation / approach | 26090914 | 0 | 2.1213203435596424 | -0.7853981633974482 |

Reproduce residence selection by enumerating centers of all165 accepted local
cells and the116 exposed axis-aligned cell edges, including edges around the
hole. A center's clearance is its minimum Euclidean distance to those closed
segments. For discovery, maximize clearance, treating distances within1e-12m
as ties, then choose lexicographically smallest `(x,y)`. This selects cell
`(x_index=11, y_index=21)` with clearance0.07411588266019639m. For confirmation,
retain centers whose clearance is at least `h-1e-12m`, and whose displacement
from the mask's area centroid has negative dot product with the discovery
start's displacement. From these26 centers choose the greatest Euclidean
distance from the discovery start, with the same tolerance/lexicographic tie
rule. This selects cell `(20,10)`, clearance0.0703125m. Both membership checks
pass the existing `v2_enclosure.point_in_positive` helper.

Set each yaw to `atan2(local_y-y, local_x-x)`. The approach starts are `(0,0)`
and its reflection across the horizontal line through the local source,
`(0,2*local_y)`. Both are outside every qualified source's conservative
exclusion mask. The straight0.6m geometric segments along their initial headings
end respectively at `(0.4242640687119285,0.42426406871192845)` and
`(0.4242640687119285,1.6970562748477138)`; existing
`segment_outside_exclusion` accepts both segments for both source masks.
These segments establish room for the proposed negative-exposure opportunity.
They are not drive commands or predictions that natural GESC follows them.
Likewise, accepted residence starts do not guarantee42s of natural residence.

The selected `gazebo_empty.world` contains ground and sun only. In
`ros2_ws/src/turtlebot3_rotating_sensor/models/light_source/model.sdf`, the
collision elements are commented out: the selected decorative source models
have no active collision shapes. The rotating sensor frame's URDF collision
box is0.39m by0.035m in plan; its swept horizontal disk radius is
`hypot(0.195,0.0175)=0.19578368164890556m`, larger than the other selected robot
collision extents. Its disk-to-declared-box clearances at seeds11/12/13/14 are
respectively1.6539389901309158m,0.8042163183510944m,1.6070639901309156m,
0.8042163183510944m. The declared box is an evaluator bound, not an actual wall.
This is a static source-geometry check; normal live spawn/contact validation and
installed asset/source binding still precede a recorded run.

One precise coordinate check remains before release: the selected robot URDF
publishes `/odom` with frame `odom` but does not explicitly set the Gazebo
diff-drive `odometry_source`. Nonzero spawn coordinates must correspond to the
world coordinates used by the model and frozen masks. Verify the selected
installed plugin's odometry-origin semantics, then record the first qualified
pose versus the requested spawn, including yaw. A matching frame string alone
does not prove matching origins. If an offset exists, declare and test an exact
input-coordinate transform prospectively; do not apply world masks directly
to an unverified local odometry origin or discover an offset from outcomes.

### Seed reservation evidence

A bounded manifest-only search found no occurrence of any of26090911–26090914
in1459 files totalling9,480,617 bytes under
`/home/mattb/Experiments/GESC-Gaussian`. The selection was `rg --files` with
include globs `metadata.yaml`, `resolved_scenario.yaml`, `scenario_result.yaml`,
`*summary*.yaml`, `*manifest*.json`, and exclusions `!**/bag/**`,
`!**/builds/**`, `!**/checkpoints/**`. A Python wrapper used a15s discovery
timeout and30s total command timeout, sorted/deduplicated the paths, and tested
file bytes with `(?<![0-9])2609091[1-4](?![0-9])`. The SHA256 of the sorted
newline-joined path list was
`fda51e2b1a326c3f5fdd5ff95caffb7b1b260834f5d259babfe906f2316a3869`.
This establishes nonuse in that retained manifest corpus, not every possible
location on the machine. Recheck immediately before dispatch and reserve four
new run IDs; do not overwrite any existing output directory.

### Selected runtime and smallest remaining source work

`scenario_runner/run_scenario.py` owns `MULTI_LIGHT_COST`, `GESC_CONTROLLER`,
`GESC_FILTER`, `SENSOR_GEOMETRY`, `build_v2_stream_config`,
`build_launch_command`, `build_metadata` and `build_record_command`. Reuse those
selected bindings rather than bare launch defaults. Their relevant inputs are:

| Owner / selected file under `ros2_ws/src/ros_esc/ros_esc/` | Q1 binding |
| --- | --- |
| `controller_node/controller_config_files/turtlebot_vehicle/gradient_methods/gesc_controller_full_rotation_voltage.json` | Directional controller; linear ceiling0.1m/s, angular ceiling0.5rad/s; existing final command saturation/sole publisher retained |
| `filter_node/filter_config_files/turtlebot_vehicle/gradient_methods/gesc_filter_full_rotation.json` | Existing GESC washout/demodulation, with the source-correct rolling mode explicitly selected |
| `rotate_frame_node/rotate_frame_config_files/turtlebot_vehicle/full_rotation.json` |20rpm nominal full rotation; use measured world phase, not nominal3s periods, in all qualification |
| `sensor_pose_node/transform_config_files/turtlebot_rotating_sensor.json` | Identity mount rotation, joint `[0,0,0.355]`, axis `[0,0,1]`, sensor offset `[0.18,0,0.015]` |
| `scenario_runner/run_scenario.py` and `gazebo.launch.xml` | Explicit `robust_gaussian_v1`, `rolling_gesc_v2`, shared unique run ID, schema2 `model_input_time` descriptor, channel0, `/odom`, zero introduced noise/delay, simulation clocks |

The descriptor resolves raw `/turtlebot3/cost_value_chatter`, source
`/gesc_gaussian/source_cost`, provenance
`/gesc_gaussian/v2/source_sample_provenance`, encoder
`/turtlebot3/encoder_chatter`, timekeeper `/turtlebot3/timekeeper_chatter`,
augmented `/cost_modified` and typed
`/gesc_gaussian/v2/objective_cost_samples`. Record all current required typed
direction/lifecycle topics and the actual resolved parameters. Preserve recorder
readiness and wall watchdogs; Q1 changes no physical profile or default mode.

The smallest observation-only policy belongs in the existing supervisor:
declare a default-false, simulation/robust/continuous-only qualification option,
wire it through the existing schema/runner/launch, and gate candidate acceptance
in `supervisor_node/v2_supervisor.py` as well as convergence transitions in
`StateMachine._step_search`. Preserve `StateMachine.step`'s earlier clock,
explicit-stop, controller, pose and source-fault checks; retain valid SEARCH
epoch heartbeats and recorded detector diagnostics. Do not return early from
the whole timer callback or bypass fault publication. This policy must suppress
PREPARE/ACTIVATE/classification and detector-triggered VERIFY while leaving
natural GESC command ownership and final-zero cleanup intact. Use current
controller behavior; do not add another motion node. Prove legacy defaults,
no lifecycle intervention under confirmations, and fault/final-zero behavior
with bounded owner tests before acquisition.

The proposed120 **simulated** seconds begin at the recorded ready/epoch boundary.
`record_run.py` currently implements `--duration-sec` with `time.monotonic()`
after readiness, so setting it to120 does not implement this study duration.
Add the simulation-clock completion condition to the existing recorder/runner
graceful-stop owner, alongside the independent240s wall ceiling. Existing
`run_record_process` and its scoped live-stop variants own process groups and
shutdown escalation. Test paused/slow clock, clock rollback, early target exit
and stop cleanup; record both clocks. Do not change existing duration semantics.

For analysis, add a versioned typed-input adapter in the existing
`plotting_scripts/gesc_gaussian_bag_analysis.py` owner. Its current
`prepare_v2_direction_replay_inputs` reconstructs historical proxies and
`freeze_v2_direction_references` fixes the old eight-bag/192-target contract;
neither should be repurposed to relabel that closed experiment. Reuse the
current bag reader's `records_for_alias` pattern, strict
`v2_stream_contract_errors`, and the lifecycle analyzer's typed stream loading.
Join exact source sequence/model-input timestamps and the recorded augmented
objective snapshot; retain integer time, original receipts, revocations and
causal support. Never substitute raw values for unavailable objective evidence.

The existing `v2_direction_reference.py` owns `augmented_objective`,
`stationary_reference`, `select_causal_anchor`, `qualify_cycle_rates`,
`reference_cycle` and matched-filter replay. Supply the new immutable48-target
manifest without altering the old24-target-per-bag selector's default contract.
Reuse `aggregate_field_truth.evaluate_raw_cost` and the selected model/geometry,
and reuse `label_v2_basin_intervals`/cell-mask segment membership through an
explicit Q1 temporal contract. Offline M3 evidence checks should call the
existing moving-evidence owner with the nine predeclared neighborhoods and
the same frozen confirmation centers/deadlines. These adapters, their strict
tests, fresh source/config hashes, the odometry-origin check, and a parent
release/checkpoint remain necessary work before any Q1 run or M4 release.
