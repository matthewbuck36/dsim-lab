# Hybrid State Machine Specification

## Enumerated states

```text
SEARCH
VERIFY_EXTREMUM
DESIGN_OR_MERGE_FILL
ESCAPE_REPULSE
ESCAPE_ASSIST
RECENTER
GOAL_HOLD
FAILSAFE
```

The implementation may preserve existing names through a mapping, but these logical states must exist and be observable.

---

## SEARCH

### Weights

```text
sensor/raw cost: 1
active fills:    1
affine:          0
```

### Actions

- Continue acquiring and logging every signal.
- Run existing GESC with the augmented cost.
- Apply prior fills to avoid known minima.
- Monitor convergence detector.
- Monitor safety and data validity.

### Transition

`SEARCH -> VERIFY_EXTREMUM` when the existing convergence condition remains true for:

```yaml
convergence_hold_sec: 2.0
```

---

## VERIFY_EXTREMUM

### Actions

- Continue sensor and pose acquisition.
- Hold or use the repository's existing low-motion convergence behavior.
- Reset the rotation-score accumulator on entry; SEARCH-era approach samples
  cannot contribute to classification.
- Evaluate calibrated source score only from valid samples received while
  `VERIFY_EXTREMUM` is active.
- Do not create a fill immediately on one noisy sample.

### Goal criterion

```yaml
goal_score_threshold: 0.95
goal_score_rotation_period_sec: 3.0
goal_score_required_rotations: 2
goal_hold_sec: 3.0
undesired_score_hold_sec: 3.0
verification_max_sec: 12.0
```

Use the minimum of the maximum score observed in each complete rotation. Start
the goal or undesired dwell only after all required post-entry rotations are
complete. The default timing budget is:

```text
12 s timeout - (2 x 3 s rotations) - 3 s longest dwell = 3 s margin
```

A shorter override may be used for an explicitly declared safe-timeout test,
but the configuration must report that goal classification is not reachable
within that timeout.

### Transitions

- Fresh rotation score at or above threshold for hold time:
  - `VERIFY_EXTREMUM -> GOAL_HOLD`
- Fresh rotation score below threshold for the undesired hold time:
  - `VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL`
- Missing complete evidence through the bounded verification timeout:
  - `VERIFY_EXTREMUM -> FAILSAFE`
- Invalid sensor or pose:
  - `VERIFY_EXTREMUM -> FAILSAFE`

---

## DESIGN_OR_MERGE_FILL

### Actions

- Freeze the recent estimation window.
- Run the basin estimator.
- Associate with an existing fill cluster or create a new one.
- Design and validate the fill.
- Publish all parameters and diagnostics.

### Transitions

- Successful design:
  - `DESIGN_OR_MERGE_FILL -> ESCAPE_REPULSE`
- Failed design:
  - `DESIGN_OR_MERGE_FILL -> FAILSAFE`

---

## ESCAPE_REPULSE

### Weights

```text
sensor/raw cost: 0
active fills:    1
affine:          0
```

The sensor is still sampled and recorded.

### Actions

- Freeze the active escape fill center and exit radius.
- Use Gaussian repulsion.
- Measure radial distance and outward progress.
- Continue all safety limits.

### Progress

\[
d(t)=\|x(t)-\mu_{\mathrm{escape}}\|
\]

Use rolling progress:

\[
\Delta d = d(t)-d(t-T_{\mathrm{stall}})
\]

Initial defaults:

```yaml
stall_window_sec: 3.0
minimum_radial_progress_m: 0.05
escape_exit_hold_sec: 1.0
escape_max_sec: 20.0
```

### Transitions

- Beyond `r_exit`, held for 1 second, and outward progress nonnegative:
  - bounded indoor mode -> `RECENTER`
  - unbounded mode -> `SEARCH`
- Insufficient progress over stall window:
  - perform one fill escalation/redesign,
  - then `ESCAPE_REPULSE -> ESCAPE_ASSIST`
- Maximum time exceeded:
  - `ESCAPE_REPULSE -> FAILSAFE`

---

## ESCAPE_ASSIST

### Weights

```text
sensor/raw cost: 0
active fills:    1
affine:          1
```

### Direction policy

1. Bounded mode: preferred direction is toward configured room center.
2. Unbounded mode: preferred direction is opposite the recent approach vector.
3. Reject a direction that:
   - points within the avoidance cone of an active fill center,
   - violates wall margin,
   - points outside known bounds.
4. Search a small set of rotated candidate directions and choose the one with maximum predicted clearance.
5. Use the affine term only as a bounded symmetry breaker/escape assistance.

### Transitions

- Stable exit:
  - bounded mode -> `RECENTER`
  - unbounded mode -> `SEARCH`
- Timeout or invalid data:
  - `FAILSAFE`

---

## RECENTER

### Weights

```text
raw-cost attraction: 0
active fills:        1
affine/GESC search:  0
```

The recenter controller provides the motion command.

### Policy

- Use the repository's existing navigation/planning stack if one is already integrated and tested.
- Otherwise use a bounded go-to-center controller in the existing control package.
- Maintain configured wall margin.
- Stop if pose becomes stale.
- Prior fills remain active as avoidance terms.

Initial defaults:

```yaml
recenter_tolerance_m: 0.25
recenter_hold_sec: 1.0
wall_margin_m: 0.35
recenter_max_sec: 30.0
```

### Transition

- Inside center tolerance for hold time:
  - `RECENTER -> SEARCH`
- Timeout or safety failure:
  - `RECENTER -> FAILSAFE`

---

## GOAL_HOLD

### Actions

- Publish zero final command.
- Continue recording.
- Publish `goal_reached`.
- Preserve raw cost, source score, position, and active fills.
- Await explicit experiment shutdown/reset.

---

## FAILSAFE

### Actions

- Immediately publish zero velocity.
- Publish structured failure event and reason.
- Keep recording for post-failure diagnostics.
- Do not automatically restart without an explicit configured policy.
- No silent state reset.

---

## Command pipeline

### Phase 08.1 startup-authorization clarification

Simulation recording readiness is an external motion-authorization interlock,
not a supervisor state transition. While that required interlock is false,
missing, or stale, every command representation remains zero. Recoverable
robust-input gaps observed during this closed interval do not emit a latching
controller `FAILSAFE`; the timer and input-driven callback follow the same
rule.

The controller grants startup grace only until the complete robust input set
has once passed state, weight, numeric, and freshness checks. Before that latch,
missing or stale inputs inside `startup_timeout_sec` remain a zero-producing
startup wait. After the latch, freshness is strict immediately; a later stale
or backward receipt emits the normal watchdog failure even if the original
startup interval has not elapsed. A controller that never obtains a complete
set reports and latches the bounded startup-timeout fault only when the
recording interlock is not required or after the required interlock opens.
While the required interlock remains closed, the controller continues zero
output but suppresses the lifecycle fault so recorder startup cannot consume
behavioral time.

The simulation recorder may publish readiness true only after its graph,
controller-manager, fresh pose/source/filter/timekeeper and robust
state/command data, parameter-capture, and post-capture barriers pass. Robust
startup state must still be valid non-failsafe `SEARCH`; lifecycle evidence
cannot advance during a long preflight and then be admitted as a clean run.
The recorder permanently latches any pre-authorization non-`SEARCH`,
failsafe, prior-transition, active-fill, or active-escape state evidence,
including evidence seen before a fresh heartbeat epoch and followed by a later
clean `SEARCH`. This monitoring interval closes atomically at authorization or
when shutdown begins, so an expected explicit-stop transition is not
misreported as pre-authorization behavior.
The recorder performs one final callback-locked safety snapshot and changes
readiness atomically, so a pre-ready nonzero command or heartbeat race cannot
fit between the final check and authorization. These checks do not authorize
physical motion or change the Phase 09 physical integration boundary.
Authorization also rechecks the one absolute preflight deadline after the
controller-manager response; a response completed after that deadline cannot
open readiness.

Always publish:

```text
GESC command before saturation
escape/recenter/affine contribution
combined command before saturation
final command after saturation
measured velocity
```

The final command must be zero on:

- exception,
- stale pose,
- stale sensor when required,
- nonfinite value,
- state timeout,
- explicit stop,
- process shutdown.
