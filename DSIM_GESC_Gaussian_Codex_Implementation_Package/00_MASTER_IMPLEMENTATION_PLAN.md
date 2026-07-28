# Master Implementation Plan

## Phase ordering

| Phase | Purpose | Physical robot allowed? |
|---|---|---:|
| 00 | Read-only repository audit and exact architecture map | No |
| 01 | Common observability and ROS data interfaces | No |
| 02 | Explicit hybrid state machine and switchable cost terms | No |
| 03 | Robust basin estimator, adaptive Gaussian design, and fill merging | No |
| 04 | Escape progress, assisted escape, boundary safety, and recentering | No |
| 05 | Unified rosbag2 recording, run metadata, and sim/physical launch parity | No |
| 06 | Scenario definitions, automated Gazebo runs, and synthetic unit cases | No |
| 07 | Bag extraction, synchronized tables, plots, and diagnostics | No |
| 08 | Robustness matrix, parameter tuning, regression suite, and freeze | No |
| 09 | Physical integration and readiness-gated trials | Yes, after gate |
| 10 | Final cleanup, README updates, and thesis-facing documentation | Only as needed |

---

# Phase 00 — Repository audit

## Goal

Determine exactly how the current repository works before changing it.

## Required outputs

Codex must create a repository-specific audit containing:

- ROS workspace roots.
- Package names and dependencies.
- Existing GESC, Gaussian, affine, convergence, launch, data-saving, Vicon, odometry, and command nodes.
- Gazebo versus physical execution paths.
- Existing topic names and message types.
- Existing parameters and YAML files.
- Existing custom interface packages.
- Existing rosbag/data-collection scripts.
- Existing tests and launch tests.
- Existing algorithm behavior, including whether any discussed ideas are already implemented.
- Exact files proposed for each later phase.
- A compatibility strategy that reuses existing conventions.

No source edits are permitted in this phase.

---

# Phase 01 — Observability contract

## Goal

Make every important software block observable before changing behavior.

## Required behavior

Publish and log:

- Raw sensor value.
- Raw minimization cost.
- Calibrated source score.
- Gaussian contribution.
- Affine contribution.
- Final augmented cost.
- Cost weights.
- Gaussian parameters and active-fill registry.
- Algorithm mode.
- Convergence, fill, escape, recenter, goal, timeout, and failure events.
- Commands before and after saturation.
- Measured pose and velocity.
- Simulation/physical source selection.
- Relevant gain and threshold snapshots.

The same canonical topics must exist in simulation and physical modes.

---

# Phase 02 — Hybrid controller state machine

## Goal

Replace implicit timing and loosely coupled switches with an explicit, testable supervisor.

## Required states

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

## Required core policy

- `SEARCH`: raw cost on; existing fills on; affine off.
- `VERIFY_EXTREMUM`: keep sensing; discard SEARCH-era score history, then test
  the calibrated goal criterion using only complete fresh rotation windows and
  the configured score dwell.
- True source: transition to `GOAL_HOLD`.
- Undesired minimum: design/merge a fill.
- `ESCAPE_REPULSE`: raw-cost weight zero; fill repulsion on; affine off.
- On measurable stall: redesign/escalate once, then enter `ESCAPE_ASSIST`.
- `ESCAPE_ASSIST`: raw-cost weight zero; fill on; safe directional assistance on.
- After stable escape: recenter in bounded indoor mode.
- `RECENTER`: raw-cost attraction off; fills active; navigate to configured center.
- Resume `SEARCH` after reaching center.
- Any invalid data, timeout, or unsafe state: zero velocity and `FAILSAFE`.

---

# Phase 03 — Robust Gaussian redesign

## Goal

Stop narrow or miscentered fills from creating small secondary minima.

## Adopted design

1. Store a recent time window of synchronized pose and raw-cost samples.
2. Remove invalid data and robustly reject outliers.
3. Initialize the basin center at the lowest-cost valid sample.
4. Refine the center with a kernel- and cost-weighted mean-shift procedure.
5. Estimate a positive-semidefinite basin covariance.
6. Estimate basin depth and local curvature with a regularized quadratic fit.
7. Choose width from the estimated basin size.
8. Choose amplitude from both observed depth and curvature.
9. Test the fitted augmented model on a local grid for residual interior minima.
10. Escalate amplitude first; then increase width while scaling amplitude by width squared.
11. Merge nearby overlapping fill candidates into one cluster instead of stacking narrow fills.
12. Keep well-separated fill clusters active to prevent revisits.
13. Publish fill confidence and diagnostics.

---

# Phase 04 — Escape and indoor safety

## Goal

Make escape measurable, bounded, and safe.

## Adopted design

- Fix the active fill center during an escape attempt.
- Track radial progress away from the fill center.
- Declare escape only after:
  - the robot is beyond the configured support-scaled exit radius,
  - remains beyond it for a hold time,
  - and shows nonnegative outward progress.
- Detect stall from insufficient radial progress over a rolling window.
- Use pure repulsion first.
- On stall, activate a deterministic safe direction:
  - toward room center in bounded mode,
  - otherwise opposite the recent approach direction,
  - rejected or rotated if it points toward a wall or active fill.
- Use velocity and angular-rate saturation.
- Timeout safely instead of circling indefinitely.
- Recenter after each local escape in bounded indoor mode.

---

# Phase 05 — Unified data recording

## Goal

Create one experiment-recording workflow for Gazebo and physical runs.

## Adopted design

- Structured ROS messages are authoritative.
- Console logs are human-readable mirrors, not the data source.
- Use `rosbag2` with the repository's available default storage backend.
- Use an explicit required-topic manifest.
- Fail before a run if a required topic is missing.
- Save run metadata with Git commit, dirty state, parameters, scenario, launch mode, source configuration, and timestamps.
- Use the same algorithm topics in simulation and physical modes.
- Preserve `/tf`, `/tf_static`, pose, sensor, command, and event data.
- Record enough information to reconstruct every calculation and state transition.

---

# Phase 06 — Automated simulation scenarios

## Goal

Make robustness testing repeatable rather than manual.

## Scenario dimensions

- 2, 3, and 4 sources.
- Light levels 1–5 where the simulator supports those levels.
- Multiple source separations.
- Overlapping attraction regions.
- Local minima near walls and corners.
- Multiple close residual minima.
- Multiple starting positions and headings.
- Sensor noise and delay.
- Velocity-saturation cases.
- Legacy versus robust algorithm profile.
- Each controller-component ablation.

Every run receives a deterministic seed and a unique run ID.

---

# Phase 07 — Analysis pipeline

## Goal

Turn bags into synchronized, inspectable experimental evidence.

## Required outputs per run

- Aligned CSV tables.
- Raw and augmented cost plot.
- Separate contribution plot.
- State and event timeline.
- Component-weight timeline.
- Trajectory with source locations and fill ellipses.
- Unsaturated versus saturated command plot.
- Escape-distance and radial-progress plot.
- Gaussian parameter history.
- Summary metrics JSON/CSV.
- Automatic data-completeness report.

---

# Phase 08 — Validation and tuning

## Goal

Establish a fixed parameter set and prove performance within a declared robustness envelope.

## Historical v2 outcome

The exact 120-run v2 design is closed failed historical evidence. Its ten
activation attempts stopped the version before tuning; it must not be resumed,
overwritten, relabeled, or counted toward a future claim.

## Phase 08 recovery and future-version boundary

Phase 08.1 completed only the bounded recovery sequence:

1. Unit and synthetic tests.
2. Retained-bag diagnosis and bounded implementation corrections.
3. Diagnostic infrastructure/readiness and scenario-contract correction.
4. Two predeclared development probes retained regardless of outcome.
5. A closeout handoff reporting one full calibrated-goal pass and one mixed
   fill/escape-prefix pass whose later recenter lifecycle failed at timeout.

Phase 08.2 then completed the separately reviewed recenter correction. It
preserved the assist policy and hard safety geometry, passed deterministic
closed-loop and integration tests, and passed one predeclared full-path
development probe through `RECENTER -> SEARCH` without timeout, failsafe,
collision, recording, cleanup, or final-zero failure.

Those results validate recenter recovery but do not establish simulation
readiness. The active successor is the separately reviewed v3 acceptance Plan
with a new sealed contract, development/tuning boundary, clean freeze,
predeclared holdout, unique validation denominator, and reproducibility
evidence. Its user-authorized Amendment A1 makes the acceptance population
researcher-visible before activation and explicitly removes any
selection-blindness claim while preserving every numeric and behavioral gate.

The following are future-version steps, not Phase 08.1 completion criteria or
authorization:

1. Declare the bounded v3 development/tuning design and retain every attempt.
2. Declare and hash one machine-readable acceptance contract before freeze.
3. Freeze and commit one code/parameter/scenario set.
4. Run the fixed predeclared holdout and unique validation denominator once
   for that version, followed by separately reported repeats.
5. Run legacy regression and write a structured success/failure report.
6. Tag the simulation-ready commit only if every declared gate passes.

Development runs are bounded by their approved diagnostic plan but are not part
of the acceptance denominator. The former 120-run arithmetic is a historical
v2 design, not a permanent cap. A future acceptance sample must be
predeclared, stratified, and reported with uncertainty; it must not be selected
after observing results.

No physical trial before the gate in `06_TEST_MATRIX_AND_ACCEPTANCE_GATES.md` is satisfied.

---

# Phase 09 — Physical integration

## Goal

Run controlled light-source experiments using the same algorithm and data interfaces.

## Requirements

- Vicon and physical sensor adapters feed the canonical topics.
- Required-topic validation passes.
- Zero-command safety is tested.
- New lamps and calibration are documented.
- Start with low-speed one-source tests.
- Progress to two-source cases.
- Do not change parameters mid-matrix without creating a new experiment version.
- Every run is bagged and has metadata.

---

# Phase 10 — Final documentation

## Goal

Leave the package understandable and defensible.

## Required outputs

- Updated repository README.
- Algorithm math and state diagram.
- Topic/data dictionary.
- Launch instructions.
- Simulation and physical experiment instructions.
- Parameter reference.
- Test coverage and acceptance results.
- Known limitations.
- Thesis-ready method summary.
- Reproducibility checklist.
