# M4 four-arm pilot preparation

Status: **PROSPECTIVE DRAFT ONLY. NOT ADOPTED. NOT DISPATCHABLE.**

This document records the population and execution constraints already approved
in [plan.md](plan.md), and the smallest implementation work needed to execute
them through existing owners. It does not resolve the methodological choice in
[q6_method_decision_plan.md](q6_method_decision_plan.md), authorize source edits,
release an experiment, or establish scientific qualification. Q5 is closed at
`checkpoints/q5_stationary_centroid_adapter_closed_v1/manifest.json`, SHA256
`308f86a68339b1430bf0e76b88e4617570c06be89f735a55004c351b94dc4a57`.
Q5 algorithm source remains held. The separate adopted
[m4a_execution_deadline_plan.md](m4a_execution_deadline_plan.md) permits only an
optional outer-process deadline capability while the method choice is pending;
it does not release this pilot. All closed Q1/Q2 and diagnostic versions remain
unchanged; their sealed confirmation inputs remain sealed.

## Fixed population and matching

Exactly sixteen fresh, serial runs are planned. These are logical slots; the
eventual contract must reserve unique run IDs and an exclusive external root
before dispatch. No replacement run, repeated seed/arm slot, imported old run,
or automatic retry is part of this draft.

| Order | Partition | Geometry | Condition | Seed | Arm | GUI |
|---:|---|---|---|---:|---|---|
| 1 | development | primary | nominal | 26090801 | A | visible |
| 2 | development | primary | nominal | 26090801 | B | visible |
| 3 | development | primary | nominal | 26090801 | C | visible |
| 4 | development | primary | nominal | 26090801 | D | visible |
| 5 | holdout | secondary | nominal | 26090802 | A | headless |
| 6 | holdout | secondary | nominal | 26090802 | B | headless |
| 7 | holdout | secondary | nominal | 26090802 | C | headless |
| 8 | holdout | secondary | nominal | 26090802 | D | headless |
| 9 | holdout | secondary | Gaussian sensor noise | 26090803 | A | headless |
| 10 | holdout | secondary | Gaussian sensor noise | 26090803 | B | headless |
| 11 | holdout | secondary | Gaussian sensor noise | 26090803 | C | headless |
| 12 | holdout | secondary | Gaussian sensor noise | 26090803 | D | headless |
| 13 | holdout | secondary | sensor and pose delay | 26090804 | A | headless |
| 14 | holdout | secondary | sensor and pose delay | 26090804 | B | headless |
| 15 | holdout | secondary | sensor and pose delay | 26090804 | C | headless |
| 16 | holdout | secondary | sensor and pose delay | 26090804 | D | headless |

Nominal means no injected noise or delay. Noise means the existing Gaussian
noise owner with `std_dev: 0.015` in existing minimization-cost units and zero
delay. Delay means zero injected noise and both `sensor_delay_sec: 0.10` and
`pose_delay_sec: 0.10`. The same block seed drives the existing Gazebo/noise
configuration for every arm; this does not claim identical callback timing or
identical realized noise at different trajectories.

| Arm | Detector selection | Search/verification selection |
|---|---|---|
| A | inherited `pde_mean_v1` | inherited `stationary_v1` |
| B | selected new positional detector, decision pending | `stationary_v1`, Q5 typed adapter |
| C | inherited `pde_mean_v1` | `rolling_gesc_v2` |
| D | selected new positional detector, decision pending | `rolling_gesc_v2` |

C/D use the closed Q2 `moving_cycle_coherence_v1` direction policy, including
its fixed numerical/configuration contract. A/B retain their inherited
direction path. B/D must share the same subsequently selected detector formula
and parameters. This document selects neither Q6 alternative and does not
silently rename or replace `centroid_windows_v2`.

All runs use the inherited start `(x,y,yaw)=(0,0,0)`, bounds
`[-1,5,-1,5]`, room center `(2,2)`, open-field world selection, and disabled
simulation contacts as in the source scenarios. Geometry inputs are:

| Geometry | Local source XY, m | Global source XY, m | Local/global lumen inputs |
|---|---|---|---|
| primary | `(1.0606601717798214, 1.0606601717798212)` | `(3.5,3.5)` | `400 / 1600` |
| secondary | `(0.5740251485476348, 1.38581929876693)` | `(3.5,3.5)` | `400 / 1600` |

The reusable scenario owners under
`ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenarios/` are:

- `phase08_v8_10_primary_visible_probe.yaml`, SHA256
  `c41eea1e6e10d8f736bb669fdf13db46eb8a6ed23b512a5827e8675d2d5c501b`.
- `phase08_v8_11_secondary_visible_probe.yaml`, SHA256
  `ce6b80c83cd52b5e665d22bc2867b1a8046d6c6a817f8427dd94ea062a9b76c0`.

Their `frozen_profile.launch_overrides` mappings are identical in the held
checkout. Reuse that common mapping, with only the explicitly declared arm
selectors and selected method parameters added. Preserve Gaussian fill/affine
assist enabled, recenter disabled, candidate ranking, verification/design and
escape timeouts, sensor geometry, nominal rotor setting, gains and command
limits. The selected controller JSON retains gains `k_vx=1`, `k_wz=5` and
ceilings `0.1 m/s`, `0.5 rad/s`. Freeze the exact selected JSON/model/launch/IDL
and runtime owner bytes rather than reconstructing their values from this prose.
The runner already resolves the selected files through `MULTI_LIGHT_COST`,
`GESC_FILTER`, `GESC_CONTROLLER` and `SENSOR_GEOMETRY`.

The secondary scenario's historical topology receipt binds nominal
disturbances. It cannot be copied unchanged as a qualification receipt for the
noise/delay rows. Preserve the existing `verified_trap` validation requirement;
the required exact disturbance-bound evaluator definition/receipt is pending
the separate prospective evaluator review. This is not authorization for a
new model or topology calculation.

## Execution, stopping and one-time holdout freeze

The inherited maxima remain **720 seconds recording**, **900 seconds overall
per run including shutdown**, and **15,300 seconds overall suite wall time**.
Use monotonic deadlines for these bounds and source/simulated time for algorithm
latencies. These are ceilings, not a promise of 720 seconds of valid exposure
after a late startup. A wall limit or incomplete recording is retained honestly.

The eventual dispatcher must establish one absolute suite deadline before the
first case, and a per-case deadline no later than both the case start plus900
seconds and the suite deadline. Preflight, recorder/target execution, graceful
stop, escalation, process reaping and cleanup evidence must fit inside that
case envelope; they must not each restart the900-second clock. The720-second
recorder maximum remains nested inside it. Do not import the Q1/Q2
125-simulated-second exposure contract.

Reserve shutdown time before the working deadline. The existing specialized
runner adds120s finalization to45s graceful shutdown before up to three5s
escalation waits: a potential180s inherited tail, not60s. Its native executor
teardown and bag extraction also run inside the child. M4A therefore adds an
optional deadline to the existing plain outer process owner, which supervises
one existing run_scenario CLI invocation. Keep specialized defaults unchanged.
The outer cancellation reserve is45+3*5=60s total, inside the case envelope;
cleanup requires a separately reviewed reserve there too. The same absolute
end bounds normal waits, cancellation and exception cleanup. The eventual
wrapper must verify the inner recorder session/cleanup receipt because the
outer session alone does not cover nested sessions. No current plain900s
wall_timeout is claimed to provide this inclusive guarantee. Refuse a new slot if its declared run/shutdown/cleanup
envelope no longer fits the suite deadline. Retain unstarted slots as such.

The first four runs are visible development. Retain all four outcomes and their
source/configuration receipts before considering the single holdout freeze.
The exact development acceptance/release criteria are **pending**; no
automatically inferred all-PASS condition or gate waiver is defined here.
There is no dispatch path into the twelve holdout slots without a separate
immutable freeze/release receipt naming the reviewed source/configuration and
development results. After that freeze, no tuning, replacements, favorable
subset selection or changes between holdout conditions are permitted. If
development requires further source work, stop at the recorded boundary; this
draft does not grant extra empirical slots or rewrite the four recorded runs.

Separate dispatch integrity from behavior:

- Abort further dispatch for the approved safety, recording-completeness or
  cleanup failures; also stop for malformed/missing identities, changed frozen
  inputs or source/configuration, failed readiness, or an exhausted deadline.
  Preserve original failure evidence and partial outputs.
- A complete, safe run that fails a behavioral target remains a failed outcome
  and does not alone abort the remaining frozen holdout population. Missed
  confirmation, rejected verification/fill or failure to rank the goal cannot
  be erased by relaunching a case.
- The eventual contract must map existing classification/integrity fields to
  these categories explicitly. Do not treat every `classification.passed=False`
  as a safety failure, or loosen an existing integrity validator to continue.

## Existing owners and minimal implementation

All paths below are repository-relative. Extend existing owners; do not add a
second runner, recorder, ROS monitor, controller, model or analysis pipeline.

| Owner | Reuse | Minimal M4 addition |
|---|---|---|
| `ros2_ws/src/ros_esc/ros_esc/scenario_runner/scenario_schema.py` and a new scenario resource beside existing YAMLs | `load_suite`, `expand_suite`, existing arm overrides and disturbance validation | Exact16-slot scenario population and matched-control checks; preserve old schema behavior |
| `.../scenario_runner/run_scenario.py` | `execute_suite`, `build_launch_command`, `build_record_command`, `resolved_noise_config`, `find_run_directory`, scoped process shutdown, `cleanup_evidence`, `classify_result` | M4A optional deadline on plain outer process/cancellation helpers; execute_suite and specialized defaults unchanged |
| `docs/codex/gesc_gaussian/v2/tools/` | Existing freezer/environment/receipt patterns; `q1_environment.py` installed/import/launch binding | One thin M4 contract/freezer/dispatcher around one-case `execute_suite` calls, exact identities, exclusive receipts, selective aborts and the single holdout seal |
| `.../experiment_recording/record_run.py`, topic manifest and validators | Actual endpoint/operational/controller-manager readiness, parameter capture, renewed readiness, pre-ready motion prohibition, typed lifecycle integrity, final zero, bag/target shutdown and completeness | Reuse unchanged unless a concrete selected M4 contract gap is found |
| `.../plotting_scripts/gesc_gaussian_bag_analysis.py` | `analyze_run`, `summarize_matrix`, existing state/event/fill/ranking metrics, `_v2_lifecycle_analysis`, `_stationary_centroid_analysis` | Shared typed-input extraction with an explicit M4 objective-law adapter, matched-arm/block report and complete/failed/unavailable denominators; independent labels/reference dispatch only after adoption |
| `.../plotting_scripts/v2_direction_reference.py` | Existing observed-phase numerical owner and objective/geometry/sign checks | Reuse the owner under a new explicitly frozen M4 evaluation contract; no default numerical change |
| `ros2_ws/src/ros_esc/setup.py` | Existing scenario resource installation and CLI entrypoints | Install the selected M4 scenario resource |

The existing command owners are `ros2 run ros_esc run_scenario`, `record_run`,
`analyze_run` and `summarize_matrix`. The dispatcher should invoke the existing one-case `run_scenario` CLI, which
calls `execute_suite` with the reserved `case_ids`, `run_id`, `runs_root`,
`summary_output` and visibility, inside the optional M4A plain process envelope. No executable M4
command is released by this draft.

`acquire_q1.py` cannot be called unchanged: it fixes four inputs, requires125
simulated seconds, and aborts every failed overall classification. Reuse its
exclusive receipt and environment-check pattern without changing its closed
study behavior. Recheck exact launch/resolved scenario and actual dated run
directory. The noise owner writes a temporary cost JSON and the runner retains
`resolved_cost_function.json`; freeze its intended content and verify the
retained bytes rather than treating its temporary path as a persistent source
owner. Never bypass source/configuration freshness checks to admit it.

The existing `prepare_moving_policy_direction_inputs` delegates to
`_prepare_policy_direction_inputs`, which enforces the Q1 observation-only
objective: no fills/affine terms and zero Gaussian/affine costs. It cannot be
reused unchanged for M4's actual fill/escape pipeline. Add a bounded M4 adapter
inside the existing analyzer, sharing typed provenance/clock/identity extraction
while preserving that old restriction for every Q1/Q2 route. Bind each new
target to its actual recorded objective revision, complete fill/affine snapshot
and weights. Construct `objective_at_angle` through the existing evaluators
using that frozen law. Post-intervention targets must not disappear merely
because the old adapter rejects a nonempty law. Missing or inconsistent
objective evidence remains unavailable/invalid under the prospective target
contract; no raw-only replacement or fabricated zero augmentation is allowed.

## Explicitly pending scientific definitions

Before an executable freeze, the parent method/evaluator review must resolve:

1. The positional detector formula and exact selected parameters, including
   any explicit methodological approval required to change the agreed score.
2. Independent sustained-entry/settling labels, negative exposure,
   censoring/first-opportunity rules and the latency comparison denominator.
   Historical goal `convergence_time`, SEARCH-to-confirmation timing and Q5
   request latency do not substitute for independent basin-entry latency.
   Preserve the old annular certified geometry and all its closed labels. A
   newly defined operational positional-confinement label would be a different
   claim; it cannot be described as certified near-minimum membership or proof
   of a cost basin. Its definition and relationship to the approved comparison
   remain pending, not an implicit relabeling of earlier evidence.
3. Direction target/interval population and timing, completeness and
   informative-reference eligibility, paired comparison, availability,
   jitter/lag and fallback-duration definitions. Do not copy the Q1/Q2
   48-target or125-second population, condition reference evaluation on a
   detector nominee, or filter targets using observed confidence/error.
4. The exact secondary disturbance-bound evaluator receipt and treatment of
   stationary-reference limitations. Do not assume the old nominal topology
   receipt qualifies a newly disturbed case.
5. Development release criteria, source/evaluation freeze receipts, and finite
   analysis/reference job bounds. **No evaluation sample count, numerical job
   budget or new release gate is invented in this draft.**

The research acceptance targets in plan.md remain targets:30% median detector
latency reduction without extra erroneous fills/terminal decisions;
direction median<=30degrees, p90<=60degrees and averaging availability>=80%;
zero mandatory stationary acquisition sweeps from direction uncertainty; and
the combined-arm fill/escape/SEARCH/stronger-candidate sequence in every
holdout condition. Report failures and denominators alongside path length,
time to goal, jitter/lag and fallback duration. No draft clause declares any
target achieved or waives unavailable evidence.

After adoption, focused source tests should cover exact16-slot expansion,
matched controls, old-route preservation, behavior-versus-integrity dispatch,
deadline/shutdown reservation, source/configuration mutation refusal and the
unopened holdout seal. No tests, builds, ROS processes, bags, model evaluations
or experimental runs were performed to create this document.
