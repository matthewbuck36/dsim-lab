# Phase 08 Final Handoff

## Terminal disposition

**PHASE 08 CLOSED / BROAD SIMULATION-READY CLAIM FAILED / TWO-LIGHT
KNOWN-SUCCESS REPRODUCTION RETAINED / NO PHYSICAL HARDWARE RUN.**

The authoritative whole-phase narrative is:

- [Phase 08 final report](../validation/phase_08_final_report.md)

It supersedes stale navigation statements about the active Phase 08
subphase, but it does not overwrite or relabel any version-specific Plan,
handoff, failed result, scenario, bag, or external evidence root.

## Final evidence

The last empirical milestone was Phase 08.7 M4.8:

```text
17/17 selected historical case definitions executed once
13/17 formal combined pass
14/17 behavioral pass
16/17 Stage A and exact one-fill pass
14/16 Stage B pass after completed Stage A
17/17 collision/forbidden evidence pass
17/17 final-zero pass
17/17 cleanup pass
17/17 SQLite PRAGMA quick_check pass
```

This passes only the user-defined retrospective “most known-successes pass
again” observation. It is not an unbiased robustness denominator and does
not pass the historical 120-run simulation-readiness objective.

The fixed simulator-relative `400/1600` local/global inputs are the strongest
known two-light condition. The most defensible starting physical geometry is
the Phase 08.7 radius-1.5, 45-degree two-light family, with the 67.5-degree
family as a secondary layout. Physical transfer still requires Phase 09
sensor/light calibration.

## What is preserved

- `algorithm_profile=legacy` remains selectable and compatible.
- The historical centered world and all historical scenario identities remain
  immutable.
- The corner-origin world/profile is additive.
- `custom_controller` remains the sole `/cmd_vel` owner.
- Cost sign, units, topics, rotating-sensor startup, recorder, validator,
  analyzer, and shared simulation/physical algorithm ownership are preserved.
- Every failed v1-v6 and Phase 08.7 attempt remains failed evidence.
- No simulation-ready tag exists.

## Open technical risks

- convergence confirmation is sensitive enough that a same-seed case may fail
  before Stage A;
- post-recovery source direction and handoff geometry are not reliably
  repeatable;
- the M4.7 dynamic source-resume corridor passed source qualification but was
  not exercised by its one Gazebo probe;
- radius-2 behavior is not reliable;
- final M4.8 local recoveries were direct and did not exercise
  `ESCAPE_ASSIST`;
- three-light behavior and physical light/lux transfer are untested;
- no selection-blind 70-case acceptance result exists.

The late M4.6/M4.7 failures were not caused by wall-margin, collision, or
failsafe termination. They received the complete Stage B budget, remained
well within the physical room, and ended far from the global. Do not disable
physical-wall or collision protection based on those failures.

## Physical stop contract

The simulation-only `1.20 m` and `1.00 m` proximity monitors must not be
carried into the physical path.

Physical behavior continues until the operator judges the robot sufficiently
close and presses `Ctrl+C`. That signal must preserve readiness-false, stop,
final-zero, bag-finalization, and scoped-cleanup ordering. Global distance is
diagnostic only.

## Next permitted work

A separately requested Phase 09 Plan may inventory the real TurtleBot3
interfaces and design bounded two-light commissioning around the known-good
`1:4` response condition. Planning and static inventory do not authorize
hardware motion.

Before physical motion, Phase 09 must:

1. identify the actual physical launch, adapters, topics, sensor geometry,
   recorder, emergency-stop, and descendant-cleanup path;
2. declare how simulator-relative `400/1600` maps to measured physical
   response;
3. retain one controller owner and simulation/physical algorithm parity;
4. remove automatic global-distance termination from the physical path;
5. predeclare a small two-light test sequence, safety boundary, manual
   `Ctrl+C` procedure, and evidence contract;
6. receive explicit user authorization for physical motion.

Do not resume Phase 08, rerun a failed fixed version, create a simulation-ready
tag, infer three-light readiness, or launch hardware from this handoff alone.

## Git boundary

The final report, this handoff, live-status closeout, and Phase 08 checkpoint
are committed together after validation. The post-commit status record must
name the resulting commit and exact worktree state.
