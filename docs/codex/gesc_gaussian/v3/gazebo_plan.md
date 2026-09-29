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

## User amendment — test escape without direct assistance

On 2026-09-28 the user authorized a V3 Gazebo test with direct heading assistance
disabled. Add one boolean in the existing controller configuration and select
false for the V3 development profile. Preserve the enabled path for comparison.
Keep Gaussian plus affine cost shaping through GESC, affine magnitude 0.5,
selected 5 Hz/20 RPM, gains 0.5/5, caps 0.10/0.50, field/start pose and measured
stable-exit criteria unchanged. This isolates the direct-assistance selection;
do not simultaneously increase affine magnitude or change the progress window.

After focused core/configuration tests and an installed build, run one visible,
recorded pilot with a 600 s wall maximum and 20 s shutdown grace. The agent may
stop earlier after observing sustained stronger-source proximity, explicitly
reporting an observation stop rather than statistical convergence. If escape
does not finish within the experiment, preserve it as incomplete; do not add an
internal escape deadline or silently enable assistance. Record actual rates,
fill/escape/SEARCH transitions, zero assist events, commanded/measured motion,
trajectory, global proximity and shutdown independently. Read closed bags only.

The user's suggested 15 s stall window and shorter assistance distance are
conditional fallback ideas if unaided escape proves inadequate. They are not
changes in this pilot. A higher affine magnitude is likewise a later isolated
comparison if the recorded controls justify it. Higher-rate V2 successes are
historical comparisons, not proof that sampling caused the outcome. No Pi work.

## User amendment — one tenfold affine-slope experiment

The user requested one deliberately large affine-slope comparison, retaining
direct assistance off. Use magnitude 5.0 versus the previous 0.5 at the same
nominal 5 Hz/20 RPM, gains 0.5/5, caps 0.10/0.50, field/start, Gaussian rules and
measured exit. Expose this existing numerical coefficient through the existing
controller JSON, default 0.5. An external custom profile selects 5.0 for this one
run; the ordinary V3 profile retains 0.5 and direct assistance false.

Validate scalar plumbing/objective scaling, build, then launch exactly one
visible recorded run with 600 s wall maximum and 20 s shutdown grace. The agent
may interrupt after a sustained observed stronger-source interval. This is an
exploratory comparison against retained no-assist evidence, not a paired
statistical estimate: inspect pre-escape trajectory and fill differences too.
Compare escape duration/path, radial exit, saturation, signed command reversals,
measured translation, global proximity, acquisition cadence and shutdown.
Do not simultaneously tune gain, caps, stall windows, assistance distance or
sampling. Do not automatically launch another test if this case fails. Keep
all results, ordinary V3 defaults and physical V1 intact.

## User amendment — selected slope 2.0 and final evening run

After the 5.0 comparison, the user selected affine magnitude 2.0 for the V3
simulation profile and authorized exactly one more visible run before leaving.
This supersedes the preceding instruction to retain selected magnitude 0.5;
older custom profiles with the field omitted still resolve to 0.5. Direct
assistance remains off. Preserve gains, caps, nominal 5 Hz/20 RPM, field/start,
Gaussian/exit rules and all prior evidence. This is a configuration-only change.

Update the existing selected-profile expectations, run focused regressions and
an installed build, then one recorded GUI/live-plot trial with a 600 s wall
maximum and 20 s shutdown grace. Stop after sustained observed stronger-source
proximity or at the outer bound, and report the actual termination reason.
Compare closed-recording escape duration, command saturation, translation,
candidate/fill timing and global proximity against retained 0.5/5.0 runs.
Different pre-escape histories remain a causal-comparison limitation. Preserve
failure or incompleteness without launching another run. Finish analysis,
shutdown and the Git/evidence checkpoint; leave selected slope 2.0 for the next
session. No Pi actions or new physical qualification.

The user subsequently clarified that orbiting about 20–30 cm from the global
source is sufficiently close for the current testing goal. Treat that as
acceptable observed global-source vicinity; do not require convergence to the
exact source center. Preserve measured distances and internal-ranking evidence
separately. This evaluation preference does not add an automatic runtime stop.
