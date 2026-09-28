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

## User amendment — baseline speed, evidence-based verification, visible lights

On 2026-09-28 the user authorized matching the full-rotation light GESC speed
limits, removing the arbitrary eight-second approach limit, and restoring the
missing Gazebo light models. This is the next bounded development iteration,
ahead of the independent physical observation-model work. Earlier failed runs
remain failed under their original settings.

- Match the archived baseline light controller's 0.10 m/s and 0.50 rad/s caps
  in the V3 development profile. Keep its existing gain 0.5/5 for this change;
  the baseline's linear gain is 1.0, so this is a speed-limit match, not full
  controller parity. Physical V1 and its installed settings stay untouched.
- Remove elapsed approach/verification/coverage cancellation. Keep the 8 cm
  spatial entry criterion, actual translating motion, candidate neighborhood,
  valid observations and bounded numerical work. A valid moving candidate may
  take as long as needed; bounded automated test duration is external to the
  algorithm and does not cancel a candidate in normal operation.
- Restore the original visible light-source assets at positions derived from
  the same selected light-cost JSON. No extra scene truth enters the controller
  and no second source-coordinate configuration is introduced.
- Validate the changed contracts, rebuild installed resources, then run a
  visible recorded 600 s wall-bounded development pilot at nominal 20 RPM.
  Keep 5 Hz selection and unchanged source field/start pose; retain clocks,
  actual command caps, motion by state, fill/escape events and clean shutdown.
  The multi-change pilot is a development check, not single-factor causal
  evidence or physical qualification. Read closed bags only.

The subsequent timer audit found another arbitrary elapsed transition: ESCAPE
returned to SEARCH after 35 s and its affine term separately expired at 35 s.
The user's general instruction also applies here. After Run06 closes, remove
both V3 cutoffs (retain generic helper defaults and affine decay mathematics).
Escape completes on the existing measured stable-exit criterion; fresh-input,
authority, numerical-job and motion/progress checks remain. Record Run06's
earlier source separately. Validate long-lived escape and later spatial exit,
then use a fresh bounded pilot for the final source if required by the observed
escape outcome. No deadline is renamed or hidden in another owner.
