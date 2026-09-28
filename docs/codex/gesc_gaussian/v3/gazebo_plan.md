# V3 Gazebo pilot — 2026-09-28

User authorized Gazebo iterations after the committed refactor. Start from
`73d1975` on `refactor/esc-v3`. The accepted refactor plan still owns algorithm
and environment boundaries. This milestone uses its bounded plan/status/diff
and external-receipt workflow, without rebuilding the retired scenario framework.

1. Run a visible, recorded nominal integration pilot using the selected 5 Hz
   profile, nominal 20 RPM and caps 0.05 m/s / 0.30 rad/s. Check startup, actual
   motion, observed rates, optional plotting/recording and SIGINT cleanup.
   Idealized baseline sensing is not physical-model qualification.
2. Attribute integration failures using closed bags and source. Preserve each
   failed run; make bounded corrections and focused regressions where needed.
3. Extend the observation model only where needed for independent, truthful
   acquisition/phase/pose timing and physical constraints. Validate each model
   before interpreting its navigation results. Ground truth stays evaluator-only.
4. Run longer moving-search pilots, then independent disturbances (arm-speed
   variation, timing/loss and computation pressure) once the baseline is
   understood. Report startup, protection/recovery, translation by activity,
   fill/escape/global approach, both time bases and final cleanup separately.

Use one isolated localhost ROS/Gazebo graph at a time. Every run has a finite
wall deadline and shutdown grace before launch. Root manages simulated run
termination; physical observation/Ctrl+C stays with the user. Interactive pilots
retain GUI/live Matplotlib; repeated controlled comparisons may be headless.
Ordinary algorithm behavior remains run-until-interrupted, with best-source
detection informational. No Pi inspection, transfer, build or motion is needed.
Preserve working physical V1, frozen refs, continuous moving verification/design
and failed evidence. Do not broaden readiness claims from one selected case.

See [live results](gazebo_status.md). This is an iterative pilot milestone;
software tests alone cannot close its behavioral or observation-model criteria.
