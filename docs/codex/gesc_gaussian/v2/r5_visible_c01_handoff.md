# R5 visible C01: behavioral failure retained

2026-09-10: the new exposed C01 case failed before the R5 activation handoff.
[Exact validation and commands](validation/r5_visible_c01.md) and
[prospective protocol](r5_visible_c01_plan.md) remain authoritative.
Acquisition session97648 is terminal/reaped after229.426403s. Recording, final
zero, inner/outer cleanup and767 source pins passed; no fill or escape occurred.
PDE confirmation71.1s led to VERIFY71.2, ordinary approach cancellation79.1,
SEARCH79.1 and FAILSAFE79.2. Stage A expired at180.333s. No global arrival.

The unchanged0.08m collection admission was never reached. Across235 retained
odometry samples during verification, distance to the frozen center started at
0.098589m, reached0.093241m minimum and ended0.093937m, with0.222109m travel.
All158 VERIFY guidance publications were valid. This was moving approach
failure, not a missing command or stopped sensor acquisition.

Separately, the controller evaluated its last valid centered lease at its79.1s
deadline and reported a hard fault. The ordinary supervisor cancellation and
SEARCH publication followed5.760ms later in recorded receipt order. The hard
fault latch then forced FAILSAFE. Existing generic deadline/identity checking
conflates ordinary verification expiry with broken authority. Exact controller
callback identity is not established by the shared "controller watchdog" event
text. No source correction has yet been made for this newly observed mechanism.
R5's authenticated post-activation exemption was never exercised in C01.

Native analysis session19870 completed in64.377794s, with exactly two native
scans (12.371515s and11.779404s), stable inputs and no execution error. Fresh
recording validation and lifecycle joins are valid. Native status remains
PARTIAL because the designated escape case has no observed attempt, so its
escape applicability metrics are unavailable. Motion and arrival measurements
are complete: `OBSERVED_CONTINUOUS_VERIFY_ONLY`,16032 exact command/diagnostic
pairs, no arrival. This is not the required full VERIFY/DESIGN motion outcome.

Independent reference session90322 completed in6.283701s, all24 target outcomes
retained:6 exposed,18 unexposed,3 eligible informative with3 usable averaged
outputs. Median direction error22.061854deg, P90 73.223806deg;2/3 paired improved,
1 degraded. Its scientific summary is FAIL. Reference execution succeeded;
selected direction quality is not qualified.

External case root is
`/home/mattb/Experiments/GESC-Gaussian/v2/development/20260910/visible_integrated_C_01/`.
Read `cached_failure_audit_v1.json`, `analysis_v1/receipt.json`,
`analysis_v1/motion_arrival_development.json` and `direction_reference_v1/receipt.json`.
Do not decode or rerun this case to recover context. Preserve all failed outcomes.

Next: a prospective bounded correction for ordinary deadline handoff, with
immediate zero output and retained authority/freshness faults; independently
diagnose the actual approach law before changing its thresholds or time budget.
Use the existing controller/supervisor and numerical development owners. No
fresh runtime is released. The V11 comparison draft remains NOT_ADOPTED.
Branch V2 at3369cfc, all task changes uncommitted, no push or physical work.
