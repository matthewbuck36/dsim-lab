# Phase 08.3 V3A Activation Failure Report

Outcome: **STOPPED / FAIL / NOT SIMULATION-READY**.

The first GUI-visible activation case ran once at committed HEAD `d69407b`.
The serial workflow then stopped exactly as required by the zero-tolerance
non-ground-collision rule. The remaining nine activation cases did not run.
No development, freeze, holdout, additional validation, reproducibility,
readiness tag, Phase 09, physical, or hardware action followed.

## Retained result

- Evidence root:
  `/home/mattb/Experiments/GESC-Gaussian/runs/phase08_v3`.
- Case: `v3a_goal_aggregate_direct`, seed `9301`.
- Run ID:
  `20260728T053833113025Z_simulation_phase08_v3_activation-v3a_goal_aggregate_direct-robust_gaussian_v1-acd554565b_92ee18ce`.
- Activation state SHA-256:
  `5fa0b4e91746bfadca363a7cdb8438d46488f4009c0bd31ae33f81d8a2457cc2`.
- Raw bag SHA-256:
  `bf07bcd3458e42b497d33fc302c2e018a68a1ce6636ab75b09af5ec26d405ae8`.
- Recording and cleanup passed. The post-activation functional suite passed
  `382` tests with `2` opt-in Gazebo tests skipped.
- The retained workflow reports `0/1` integrity passes, `0/1` contract
  passes, and nine `not_run` activation IDs.

## Root cause

The analyzer correctly reported `105` non-ground contact states. Read-only bag
inspection proved that every one involved
`phase08_contact_positive_control`; there were no other non-ground contact
pairs. The first occurred about `0.154 s` after readiness and the last about
`0.388 s` after readiness.

The schema-v4 launch builder incorrectly enabled the physical contact
positive-control probe for every case with a declared collision expectation,
including `collision_expected=false`. The validation node consequently
spawned a static `0.20 x 0.20 x 0.40 m` obstacle at the robot's live pose
after readiness. The resulting contact included a large physical impulse, so
the trajectory is instrumentation-contaminated.

The collision result must not be filtered away or relabeled as collision-free.
The later fill, escape, recenter, timeout, and failsafe trace also cannot be
used as independent algorithm-behavior evidence because it occurred after the
probe struck the robot.

The machine-readable audit is
`phase_08_v3a_contact_probe_contamination.json`.

## Disposition

The original activation state, progress, record, bag, analysis, and nine
`not_run` slots are immutable. This attempt is not eligible for the
pre-readiness infrastructure replacement policy, and the old activation root
will not be resumed or overwritten.

The bounded correction changes only probe dispatch:

- `collision_expected=true`: retain the real static positive-control probe;
- `collision_expected=false`: retain contact sensors, valid empty/ground-only
  negative evidence, and the unchanged zero-non-ground-contact gate, but do
  not spawn the probe.

Historical Phase 07.5 runtime evidence already proves both the explicit
positive control and the no-probe negative control. The analyzer, collision
threshold, activation cases, seeds, profiles, behavior thresholds, candidate
values, 120-slot population, allocations, denominators, early stops, and
replacement caps remain unchanged.

The correction changes a qualified runtime input, so the old qualification
cannot authorize another dispatch. A fresh `phase08_v3b` evidence root must
adopt the exact precommitted suite and commitment bytes, rerun qualification,
and rerun all ten GUI-visible activation cases from the beginning. V3A
evidence never enters the V3B denominator.
