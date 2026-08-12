# Research Decisions and Assumptions

## Invariants and provisional policy

The fixed research invariants are robust autonomous escape, safe bounded
motion, avoidance of known minima, calibrated goal classification, complete
structured evidence, independently switchable cost contributions, selectable
legacy behavior, and shared simulation/physical algorithm semantics.

Pure-repulsion-first sequencing, one redesign before assistance, automatic
recentering, the current estimator/fit/grid/escalation mechanics, fill
retention, timeouts, and numeric thresholds are adopted engineering
hypotheses. They are configurable and may be replaced by evidence-backed,
versioned changes before formal freeze. Once a fixed-profile holdout starts,
code, scenarios, parameters, and acceptance thresholds remain immutable for
that experiment version.

This document resolves the uncertainties from the meetings into one adopted implementation plan.

## Phase 10 V1 evidence decision

The final V1 claim is a selected-scenario result, not a broad robustness claim.
Broad simulation readiness and broad physical readiness failed. The strongest
selected simulation evidence is v8.10 primary `11/11`, v8.11 secondary `6/6`,
and the v8.12 visible probe `14/14`. The first varied v8.12 case was `13/14`
against the frozen predicates; the other three varied cases were withheld
without retry.

The eighth retained physical run is the first two-basin behavioral success: it
converged at and classified the local basin, created one fill, used repulsive
and assisted escape, returned to `SEARCH`, and reacquired the stronger-light
region. It stopped before a second convergence or `GOAL_HOLD` and passed
`61/62` completeness checks because cross-topic shutdown evidence ordering
produced one retained false negative. Physical arrival remains manual operator
`Ctrl+C`; `GOAL_HOLD` does not terminate the physical process.

The LaTeX-typeset
[`FINAL_PROJECT_REPORT_V1.pdf`](../docs/codex/gesc_gaussian/FINAL_PROJECT_REPORT_V1.pdf),
with its `.tex` source and `.md` audit companion, is the authoritative
synthesis. Phase 10 changes documentation only and
authorizes neither hardware use nor a V2 implementation. Any future
`feature/gesc-gaussian-robustness-v2` work must preserve these V1 outcomes and
create new versioned hypotheses and evidence.

## Fixed research decisions

1. **Baseline controller:** gradient-descent extremum seeking control (GESC).
2. **Local-minimum method:** Gaussian augmentation/repulsion.
3. **Physical field:** light-source-generated cost field.
4. **Heavy-Ball ESC:** not part of the new implementation or experiment matrix.
5. **Future motivation:** reflective acoustic fields may contain many unknown local extrema, but acoustic sensing is not the present implementation target.
6. **Primary implementation environment:** Gazebo first, physical TurtleBot only after simulation gates.
7. **Repository policy:** preserve and extend existing `dsim-lab` conventions.

### Phase 09 selected-scenario amendment

The broad Phase 08 simulation-ready gate was not achieved and must not be
relabeled. The user nevertheless accepts the repeatable v8.10 primary
(`11/11`) and v8.11 secondary (`6/6`) two-source layouts as sufficient for a
selected-scenario physical demonstration. This authorizes Phase 09 planning
and no-hardware implementation in the local physical snapshot without a broad
`simulation_ready=true` tag.

This amendment does not authorize physical motion. Live Pi transfer and robot
motion require separate explicit authorization, live calibration,
emergency-stop and final-zero verification, complete recording, and an
operator-managed open test field. The controller may use the rotating
photoresistor, wheel odometry, required IMU data, and configured source count;
it may not use GPS, Vicon, source coordinates/roles/intensities, room
dimensions, or a coordinate-based physical arrival stop. Vicon may be retained
only for external recording and evaluation.

## Interpretation of the three cost components

The controller uses:

\[
J_{\mathrm{aug}} =
w_s J_{\mathrm{raw}} +
w_g J_{\mathrm{gaussian}} +
w_a J_{\mathrm{affine}}
\]

where:

- `J_raw` is the existing minimization cost derived from the light sensor.
- `J_gaussian` is the repulsive Gaussian fill contribution.
- `J_affine` is the directional/symmetry-breaking contribution.
- `w_s`, `w_g`, and `w_a` are published and recorded weights.

The sensor remains sampled and logged even when `w_s = 0`.

## Adopted switching policy

The nominal robust policy is not a permanent sum of all terms.

- During normal search:
  - `w_s = 1`
  - `w_g = 1` for previously registered fills
  - `w_a = 0`
- During initial escape:
  - `w_s = 0`
  - `w_g = 1`
  - `w_a = 0`
- During assisted escape after measured stall:
  - `w_s = 0`
  - `w_g = 1`
  - `w_a = 1`
- During bounded-environment recentering:
  - raw attraction remains off,
  - prior fills remain active,
  - the recenter controller supplies the motion objective.

## Adopted interpretation of Patrick's softmax formula

The whiteboard expression is treated as a smooth association rule:

\[
p_j(x) =
\frac{
\exp\left(-\|x-x_j^*\|^2/(2h^2)\right)
}{
\sum_i
\exp\left(-\|x-x_i^*\|^2/(2h^2)\right)
}
\]

It is used in two places:

1. **Kernel-weighted center refinement** using recent local-basin samples.
2. **Soft association of a new local-minimum estimate with existing fill clusters**, subject to a hard distance-overlap gate.

The hard distance gate is mandatory because softmax probabilities alone can assign a distant point to a cluster when only one cluster exists.

## Adopted strategy for imperfect fills

The current failure mode is treated as:

- a fill is too narrow, too weak, or miscentered;
- the augmented landscape develops small residual minima around the fill;
- the robot becomes trapped again or circles for too long.

The chosen response is:

- estimate the whole local basin rather than only one point;
- generate one wider adaptive fill;
- scale amplitude with width so the fill does not become too flat;
- numerically test a fitted local model for residual minima before publishing;
- merge overlapping nearby fills rather than stacking them.

## Goal-source classification

A controller cannot know a global optimum in an arbitrary unknown field without an acceptance rule.

For current light experiments, the adopted rule is a **calibrated source score**:

- Preserve the existing raw cost and sign convention.
- Publish a separate normalized `source_score` from 0 to 1.
- `source_score = 1` corresponds to the calibrated near-source condition.
- A converged extremum is accepted as the goal only when:
  - `source_score >= goal_score_threshold`,
  - the criterion is supported by the configured number of complete rotating
    sensor windows collected after entry to `VERIFY_EXTREMUM`,
  - for `goal_hold_sec` after those fresh windows are complete,
  - with valid sensor and pose data.

Otherwise, it is treated as an undesired local minimum.

The current default allows 12 seconds for two three-second rotations plus a
three-second goal/undesired dwell, leaving three seconds of scheduling margin.
A deliberately shorter timeout is permitted only for a declared safe-timeout
scenario and is reported as timing-insufficient configuration, not as a
reachable goal-classification setup.

Ground-truth source position may be used for evaluation in simulation, but not by the controller.

## Indoor policy

For a bounded laboratory or bounded Gazebo scene:

- Return to the configured safe center after each successful local escape.
- Keep all previous fills active.
- Do not immediately resume raw-cost following next to a wall.
- Use the existing planner if the repository already contains one.
- Otherwise implement a small bounded center-return controller in the existing control package.

## Data policy

Every transformation must expose and record its input and output.

Required chain:

```text
raw sensor
→ raw cost
→ Gaussian contribution
→ affine contribution
→ augmented cost
→ GESC output
→ supervisor/saturation output
→ actual robot response
```

All values must share a ROS time base.

## Limits of the robustness claim

The thesis should not claim guaranteed success for every arbitrary nonconvex function.

The supported claim should be:

> Robust performance over a documented family of bounded, experimentally relevant light-generated and synthetic multimodal cost fields under the tested source counts, separations, strengths, noise, delays, starting conditions, and robot constraints.
