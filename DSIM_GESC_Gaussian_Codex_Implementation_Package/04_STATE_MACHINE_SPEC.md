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
- Evaluate calibrated source score.
- Do not create a fill immediately on one noisy sample.

### Goal criterion

```yaml
goal_score_threshold: 0.95
goal_hold_sec: 3.0
```

### Transitions

- Valid source score above threshold for hold time:
  - `VERIFY_EXTREMUM -> GOAL_HOLD`
- Otherwise, after verification window:
  - `VERIFY_EXTREMUM -> DESIGN_OR_MERGE_FILL`
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
