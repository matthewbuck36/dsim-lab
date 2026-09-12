# R12 measurement correction validation

Adopted [plan](../r12_measurement_correction_plan.md). No simulation, method
change or old-version rewrite. Work root:
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260911/r12_measurement_correction_v1/`.

## Held source and prospective validation

Root reviewed both held changes. Runner change is 22 added lines with existing
Git/module/conventional fallbacks retained; GIT_PAGER does not trigger fallback,
while repository/discovery/configuration overrides do. Arrival method is explicit
opt-in, requiring the exact recorded pose and independent valid live evidence.
Historical defaults and all V12 documents/results remain unchanged.

One seven-selection bundle is frozen in tests.json: the two R12 modules, existing
arbitrary-cwd scenario check, existing pure-worker child rejection check, and
V10/V11/V12 scientific regressions. Inner pytest 80s + 5s kill; outer
source-validation driver 95s + 5s kill, 100s inclusive. This is within the
prospective 90s work ceiling and leaves receipt time. Source/helper hashes and
21 installed entry points are checked before/after by the adapted existing
source-validation helper. No test has executed at this entry.

## Source and component results

Source session 9350 terminal/reaped 0: 129/129 passed, no skips, 6.896821716 s
outer / 4.58 s pytest. All 859 source/helper pins and 21 installed entry points
remained stable. Receipt SHA256:
`1178bfd14aa8ef589b3923f5cd25db45ff0e735c307ab15b85562be44c9f8685`.
No source correction or additional test run followed that bundle.

Import component session 36390 terminal/reaped 0: 1.384024080 s, zero audited
subprocesses, six source/helper/plan pins stable. Selected clean environment,
`python3 -B import_probe.py`, under SIGINT 15s plus kill 5s. The science purity
gate remains unchanged. Historical V12 unexpected-child verdict remains failed.

Arrival component session 36491 terminal/reaped 0: 3.003445456 s total; one
filtered pose/readiness read in 1.256667565 s, 8,352 pose and 2,924 readiness
records. Existing historical owner output exactly matched the saved unavailable
V12 result. Explicit corrected binding succeeded at 283.167 s (origin 0),
recorded ROS stamp 283167000000, exact evaluator bag stamp
1789099922881045690, distance 0.498218441926 m. The live-monitor position is
also present in the bag at ROS stamp 283201000000, 34 ms later. Both records
are /odom with odom frame and within readiness. No live-time substitution.

All 870 prepared source/small-input hashes remained stable (869 preparation
pins plus its receipt). Raw hashes were inherited from acquisition; raw stat
stability was checked, not misrepresented as a fresh raw hash. Probe command
uses `python3 -B arrival_probe.py --prepared arrival_prepared.json` under
SIGINT 25s plus kill 5s, internal work22s. Arrival receipt SHA256:
`e289ec69acc9e0b471dd0cdee9ac71d50fe8350e01443dd93672d32639f67d52`.

These are separate component results. No old experiment auto-selects the new
arrival binding and no V12 result/report was edited. A new prospective study
must explicitly select recorded_pose_arrival_v1. No simulation or method
change was executed. Independent cached review and material closeout follow.

Independent cached review PASS: 25 checks, 22 stable selected refs, 0.035785 s;
`component_review.json` SHA256
`fbe6e190ca0564d38bf0d41cfaf1006be7ccd4cf2c7d81a211af255211b18811`.
R12 COMPLETE; see [handoff](../r12_measurement_correction_handoff.md).

Context/diff/checkpoint PASS. Material archive `checkpoints/r12_measurement_correction_v1/`
verified 608 members in 0.848435 seconds; manifest SHA256
`a5561d82505c7d5bc834064757e9792357533bc2f712427dd42130bea3d0a503`.
This receipt postdates the immutable archive. R13 is separately adopted and
does not reopen V12 or auto-select the corrected arrival method in old versions.
