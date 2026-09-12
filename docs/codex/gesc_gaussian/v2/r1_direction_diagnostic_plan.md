# R1: direction measurements from retained development C

Status: ADOPTED, 2026-09-10 UTC, under
[the revised development amendment](method_development_20260910.md).
Simulation data only. V9 remains CLOSED_INCOMPLETE; this is a new diagnostic,
not a retry or completion of either historical labels/science block.

## Fixed input and question

Use only V9 nominal development C, run
`m4-pilot-v9-slot03-C-26090801`. Its completed partial artifact
`pilot/m4_pilot_v9/analysis/block_0/slot_3_normalized.json` under the external
V2 root has recorded SHA256
`0dd3c204e0e34f2d96574a995c0bb33b706130ad4791b63eefd8816abe013f17`.
The adjacent metrics file binds 10,605 qualified unique observations with no
integrity errors, selected configurations, geometry and acquisition receipt.
No bag, labels pipeline, confirmation input or holdout result is read.

Measure the recorded .75 moving-cycle blend against recorded instantaneous
GESC using an independently computed reference. Preserve all 24 existing
input-only target offsets, 15+30*k seconds for k=0..23, including unexposed and
unavailable rows. Do not select targets by confidence, method error or outcome.

## Existing owners and reference scope

Call `m4_pilot.evaluate_direction_targets` directly on the saved normalized
document. Reuse `aggregate_field_truth._model/evaluate_raw_cost` with the exact
recorded C sources and sensor binding, and the existing augmented-objective,
observed-phase-cycle/reference and angular-error owners. No D3 adapter or
`evaluate_m4.labels_stage` is imported or executed. Numerical owners stay held.

The independent reference is periodic stationary-position GESC response under
the actual observed phase-time waveform, with the complete recorded objective
frozen at the anchor position. It preserves negative cost, sensor geometry and
effective Gaussian/affine terms. It is not a spatial gradient or a physical
measurement. No ground truth enters runtime control.

## One finite attempt and outputs

New exclusive root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/direction_c_v1/`.
Save this plan, helper sources and a prepared source/input manifest before
execution. The helper uses clean Humble -> Q2 -> Q5 imports, adds the existing
extremum-seeking source path and never initializes ROS. Verify actual imported
numerical-owner paths, all prepared source pins, recorded normalized SHA and
selected configuration/acquisition/label receipts. Historical contract metadata
is read only to obtain the exact development C source configuration.

One wrapper has a 90-second inclusive ceiling, with child SIGINT at 80 seconds,
group SIGKILL at 87 seconds if necessary, reaping by 88 seconds and final
receipt publication reserved before 90 seconds. The outer invocation is
`timeout --signal=INT --kill-after=2s 88s python3 <root>/run_once.py`.
No automatic retry or budget extension. All failure/partial files remain.

Write each of all 24 target results incrementally and exclusively. Final
publication requires all 24 identities in original order and unchanged input/
numerical-source hashes. Record exact environment/argv, file receipts, imported
owner paths and timings for input preparation versus numerical evaluation.
The wrapper retains its terminal child return code and elapsed time.

## Decision rule and reporting

A completed usable measurement is the first objective. Report scheduled,
exposed, input-qualified, informative, eligible, output and paired denominators;
all rejection reasons; actual and instantaneous errors; median/P90 error and
averaging availability. Apply the existing <=30-degree median, <=60-degree P90
and >=0.8 averaging availability only as development diagnostics. Partial or
uninformative references remain unavailable, never a pass.

If accuracy fails despite high averaging availability, use the error pattern
for a separately saved method investigation before changing confidence gates.
If measurement fails, preserve the exact failing stage and diagnose that bounded
failure. Neither outcome releases a new matrix or establishes qualification.
Record the exact result in `validation/r1_direction_diagnostic.md`; parent owns
status/handoff updates and the material R1 checkpoint.
